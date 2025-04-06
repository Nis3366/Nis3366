import sqlite3
import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.preprocessing import MinMaxScaler
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

def train_ets_model(sequence, seasonal_periods=None):
    """
    训练ETS指数平滑模型
    参数：
        sequence: 时间序列数据
        seasonal_periods: 季节性周期（可选）
    返回：
        训练好的ETS模型
    """
    # 自动检测最佳趋势类型
    model = ExponentialSmoothing(
        endog=sequence,
        trend='add',  # 使用加性趋势
        seasonal='add' if seasonal_periods else None,  # 自动判断季节性
        seasonal_periods=seasonal_periods,
        initialization_method="estimated"
    )
    return model.fit()

def predict_future(model, steps=5):
    """
    使用训练好的模型进行预测
    参数：
        model: 训练好的ETS模型
        steps: 预测步长
    返回：
        list: 预测结果列表
    """
    forecast = model.forecast(steps=steps)
    return [round(x, 4) for x in forecast]

def main():
    # 配置参数
    DB_PATH = "timeseries.db"
    TABLE_NAME = "hotness_records"  # 替换为实际表名
    MIN_LENGTH = 10  # 序列最小长度要求
    
    try:
        # 加载数据
        sequences = load_data_from_db(DB_PATH, TABLE_NAME)
        print(f"成功加载 {len(sequences)} 条时间序列")
        
        # 数据预处理示例（可选）
        scaler = MinMaxScaler()
        
        # 交互预测
        while True:
            print("\n请输入待预测序列（用逗号分隔的数字）或输入 quit 退出：")
            user_input = input().strip()
            
            if user_input.lower() == 'quit':
                break
                
            try:
                # 转换输入格式
                input_seq = [float(x) for x in user_input.split(',')]
                
                # 验证输入有效性
                if len(input_seq) < MIN_LENGTH:
                    raise ValueError(f"输入序列至少需要 {MIN_LENGTH} 个观测值")
                    
                # 数据标准化（可选）
                scaled_seq = scaler.fit_transform(np.array(input_seq).reshape(-1, 1)).flatten()
                
                # 训练ETS模型
                model = train_ets_model(scaled_seq)
                
                # 进行预测
                scaled_pred = predict_future(model)
                
                # 逆标准化（如果进行了标准化）
                predictions = scaler.inverse_transform(
                    np.array(scaled_pred).reshape(-1, 1)
                ).flatten().tolist()
                
                # 显示结果
                print("\n未来5个时间点的预测值：")
                for i, val in enumerate(predictions, 1):
                    print(f"第{i}步预测值: {val:.4f}")
                    
            except Exception as e:
                print(f"错误: {str(e)}")
                print("正确示例输入：12.3,15.0,14.5,18.6,17.9,16.2,15.8,17.3,18.9,19.2")
                
        print("程序已退出")
        
    except Exception as e:
        print(f"发生严重错误：{str(e)}")

if __name__ == "__main__":
    main()