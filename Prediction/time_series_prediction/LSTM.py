import sqlite3
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import warnings
warnings.filterwarnings("ignore")

# 已提供的数据库加载函数
def load_data_from_db(db_path, table_name):
    """
    从指定数据库表加载时间序列数据
    参数：
        db_path: 数据库文件路径
        table_name: 目标数据表名称
    返回：
        list: 时间序列列表，每个元素为一个序列的数值列表
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 验证表是否存在
        cursor.execute(f"SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        if cursor.fetchone()[0] == 0:
            raise ValueError(f"表 {table_name} 不存在")

        # 获取表结构信息
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        if len(columns) < 2 or columns[0].lower() != 'length':
            raise ValueError("表结构不符合要求，第一列必须为length字段")

        # 读取数据
        cursor.execute(f"SELECT * FROM {table_name}")
        data = cursor.fetchall()
        
        sequences = []
        for row in data:
            # 数据格式验证：第一列为长度，后续为数值
            length = int(row[0])
            if length > len(row)-1:
                raise ValueError(f"记录长度{length}超过实际列数{len(row)-1}")
                
            seq = list(row[1:length+1])  # 根据长度字段截取有效数据
            sequences.append(seq)
            
        return sequences
        
    finally:
        conn.close()

# 数据预处理函数
# 修改后的数据预处理函数
def preprocess_data(sequences, time_steps=30):
    """
    独立处理每个序列生成训练样本
    返回：
        X, y: 训练数据和标签
        scalers: 每个序列的标准化器列表
    """
    X = []
    y = []
    scalers = []
    
    for seq in sequences:
        if len(seq) < time_steps + 5:
            continue
        
        # 每个序列独立标准化
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(np.array(seq).reshape(-1, 1))
        scalers.append(scaler)
        
        # 生成当前序列的训练样本
        seq_X, seq_y = [], []
        for i in range(len(scaled_data) - time_steps - 5):
            seq_X.append(scaled_data[i:i+time_steps, 0])
            seq_y.append(scaled_data[i+time_steps:i+time_steps+5, 0])
        
        X.extend(seq_X)
        y.extend(seq_y)
    
    # 转换为numpy数组
    X = np.array(X)
    y = np.array(y)
    
    # 转换为LSTM需要的三维输入 [样本数, 时间步长, 特征数]
    X = X.reshape(X.shape[0], X.shape[1], 1)
    return X, y, scalers

# LSTM模型构建函数
def build_lstm_model(input_shape):
    """
    构建LSTM模型
    参数：
        input_shape: 输入数据的形状 (time_steps, features)
    返回：
        编译好的LSTM模型
    """
    model = Sequential()
    model.add(LSTM(64, return_sequences=True, input_shape=input_shape))
    model.add(LSTM(32))
    model.add(Dense(5))  # 输出5个预测值
    model.compile(optimizer='adam', loss='mse')
    return model
# 修改后的预测函数（独立标准化）
def predict_next_values(model, input_sequence, time_steps=30):
    """
    使用训练好的模型进行预测（独立标准化版本）
    参数：
        model: 训练好的模型
        input_sequence: 输入序列
        time_steps: 时间窗口大小
    返回：
        预测的后5个值（原始量纲）
    """
    # 验证输入长度
    if len(input_sequence) < time_steps:
        raise ValueError(f"输入序列至少需要 {time_steps} 个观测值")
    
    # 独立标准化流程
    local_scaler = MinMaxScaler(feature_range=(0, 1))
    
    # 注意：这里使用fit_transform而不是transform
    scaled_input = local_scaler.fit_transform(
        np.array(input_sequence).reshape(-1, 1)
    )
    
    # 准备最后可用的时间窗口数据
    model_input = scaled_input[-time_steps:].reshape(1, time_steps, 1)
    
    # 进行预测
    scaled_pred = model.predict(model_input)[0]
    
    # 逆标准化
    return local_scaler.inverse_transform(
        scaled_pred.reshape(-1, 1)
    ).flatten().tolist()

def main():
    # 配置参数
    DB_PATH = "Prediction/time_series.db"
    TABLE_NAME = "hotness_records"  # 替换为实际表名
    TIME_STEPS = 30  # 使用过去30个时间点预测未来5个
    EPOCHS = 50
    BATCH_SIZE = 32
    
    try:
        # 加载数据
        sequences = load_data_from_db(DB_PATH, TABLE_NAME)
        print(f"成功加载 {len(sequences)} 条时间序列")
        
        # 预处理数据
        X, y, scaler = preprocess_data(sequences, TIME_STEPS)
        print(f"训练数据形状：{X.shape}, 标签形状：{y.shape}")
        
        # 构建模型
        model = build_lstm_model((TIME_STEPS, 1))
        
        # 训练模型
        print("开始训练模型...")
        model.fit(X, y, epochs=EPOCHS, batch_size=BATCH_SIZE, verbose=1)
        print("模型训练完成")
        
        # 保存模型和标准化器
        model.save("Prediction/lstm_timeseries.h5")
        print("模型已保存为 lstm_timeseries.h5")
        
        # 示例预测
        test_sequence = sequences[0][-50:]  # 取第一条序列的最后50个值作为测试
        print("\n测试序列（最后10个值）：", test_sequence[-10:])
        
        # 进行预测
        predictions = predict_next_values(model, test_sequence, TIME_STEPS)
        print("未来5个时间点的预测值：", predictions)
        
    except Exception as e:
        print(f"程序运行出错：{str(e)}")

if __name__ == "__main__":
    main()