# main.py
"""主预测模块，集成三种模型预测并可视化结果"""
import numpy as np
import matplotlib.pyplot as plt
from time_series_prediction.Paragraphs_ARIMA import segmented_arima_predict
from time_series_prediction.LSTM import predict_next_values, load_data_from_db as lstm_load, preprocess_data
from time_series_prediction.ETS import predict_future, train_ets_model
from Hotness.Hotness import load_local_json, calculate_hotness
import pickle
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler

from keras import losses

import warnings
from numpy.exceptions import RankWarning  

import matplotlib.pyplot as plt

def plot_hotness_trend(hotness_series, time_window, save_path):
    plt.style.use('dark_background')  # 使用暗色调背景
    plt.figure(figsize=(12, 6),dpi=100)
    hotness_series.plot()
    plt.title(f'Hotness Trend (Time interval: {time_window})', fontsize=14, pad=20)
    plt.xlabel('Time Sequence', fontsize=12)
    plt.ylabel('Hotness Value', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

def Comb_plot_prediction(history2, combined_pred, time_window):
    """
    绘制历史数据与融合预测结果的对比图
    参数：
        history2: 历史数据列表（最后10个观测值）
        combined_pred: 加权融合预测结果列表（5个预测值）
    """
    plt.figure(figsize=(12, 6), dpi=100)
    plt.style.use('dark_background')  # 使用暗色调背景
    # 生成坐标数据
    x_hist = list(range(-9, 1))  # 历史数据X轴坐标：-9到0
    x_pred = list(range(1, 6))    # 预测数据X轴坐标：1到5
    
    # 绘制历史数据（蓝色）
    plt.plot(x_hist, history2, 
             color='royalblue', 
             marker='o',
             linewidth=2,
             markersize=8,
             label='Historical Hotness')
    
    # 绘制预测数据（黄色），包含连接线
    plt.plot([0]+x_pred,  # X坐标包含now点和预测点
             [history2[-1]]+combined_pred,  # Y值包含最后一个历史点和预测点
             color='goldenrod',
             marker='o', 
             linewidth=2,
             markersize=8,
             linestyle='--',
             label='Predicted Hotness')
    
    # 设置坐标轴标签
    plt.xlabel('Time Sequence', fontsize=12)
    plt.ylabel('Hotness Value', fontsize=12)
    
    # 设置特殊刻度标签
    xticks = list(range(-9, 6))
    xlabels = [str(x) for x in xticks]
    xlabels[xticks.index(0)] = 'Analysis point'  # 将0点标记为now
    plt.xticks(xticks, xlabels, rotation=45)
    
    # 设置网格线
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # 添加图例
    plt.legend(fontsize=12)
    
    # 设置坐标轴范围
    plt.xlim(-9.5, 5.5)
    
    # 添加图表标题
    plt.title(f'Hotness Trend Prediction(Time interval: {time_window})', fontsize=14, pad=20)
    
    plt.savefig('prediction_result.png', dpi=300, bbox_inches='tight', transparent=True)
    # 显示图表
    ## plt.tight_layout()
    ## plt.show()
def load_models():
    """加载预训练模型和参数"""
    with open('best_arima_order.pkl', 'rb') as f:
        arima_order = pickle.load(f)
    
    # 修复：加载 LSTM 模型时明确指定损失函数
    lstm_model = load_model(
        'lstm_timeseries.h5',
        custom_objects={'mse': losses.mean_squared_error}
    )
    
    _, _, lstm_scaler = preprocess_data(lstm_load("time_series.db", "hotness_records"))
    return arima_order, lstm_model, lstm_scaler

def plot_predictions(history, arima_pred, lstm_pred, ets_pred, time_window):
    """生成三模型预测对比图（单图合并版）"""
    plt.style.use('dark_background')  # 使用暗色调背景
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 坐标设置
    x_hist = [-4, -3, -2, -1, 0]
    x_pred = [1, 2, 3, 4, 5]
    
    # 绘制历史数据（蓝色）
    ax.plot(x_hist, history, 'b-o', label='History', linewidth=2, markersize=8)
    
    # 定义三种预测的颜色和标签
    pred_config = [
        (arima_pred, 'ARIMA', 'coral', 's'),  # 珊瑚色，方形标记
        (lstm_pred, 'LSTM', 'darkred', '^'),     # 暗红色，三角形标记
        (ets_pred, 'ETS', 'violet', 'D')      # 紫色，菱形标记
    ]
    
    # 绘制每种预测结果
    for pred, label, color, marker in pred_config:
        # 绘制预测点
        ax.plot(x_pred, pred, color=color, marker=marker, 
                label=f'{label} Prediction', linestyle='--', linewidth=1.5, markersize=8)
        # 绘制连接线
        ax.plot([0, 1], [history[-1], pred[0]], color=color, 
                linestyle='--', linewidth=1.5)
    
    # 设置坐标轴标签
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('Hotness Value', fontsize=12)
    
    # 设置x轴刻度，将0改为"now"
    ax.set_xticks([-4, -3, -2, -1, 0, 1, 2, 3, 4, 5])
    ax.set_xticklabels(['-4', '-3', '-2', '-1', 'Analysis point', '1', '2', '3', '4', '5'])
    
    # 添加网格线和图例
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(fontsize=10)
    
    # 设置标题
    ax.set_title(f'Multi-Model Time Series Prediction(Time interval: {time_window})', fontsize=14, pad=20)
    
    # plt.tight_layout()
    
    # 保存图像（替换已存在的同名文件）
    plt.savefig('Multi_prediction_result.png', dpi=300, bbox_inches='tight', transparent=True)
    ##plt.show()


def calculate_statistical_features(sequence):
    """计算用于权重分配的统计特征"""
    features = {}
    seq_array = np.array(sequence, dtype=np.float64)  # 确保转换为浮点类型
    
    # 基本统计量
    features['std_dev'] = np.std(seq_array)
    
    # 趋势强度（使用更稳健的线性回归）
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RankWarning)
        try:
            # 使用更稳健的线性回归计算趋势
            slope, _ = np.polyfit(np.arange(len(seq_array)), seq_array, 1, cov=False)
            features['trend_strength'] = slope if not np.isnan(slope) else 0.0
        except:
            features['trend_strength'] = 0.0
    
    # 平稳性检测（优化计算方式）
    if len(seq_array) > 1:
        delta = np.diff(seq_array)
        std_ratio = np.std(delta, ddof=1) / (np.std(seq_array, ddof=1) + 1e-10)
        features['stationarity'] = 1 / (1 + std_ratio)
    else:
        features['stationarity'] = 0.5  # 默认中性值
    
    # 季节性检测（简化版自相关）
    if len(seq_array) > 2:
        try:
            autocorr = np.corrcoef(seq_array[:-1], seq_array[1:])[0, 1]
            features['seasonality'] = max(0, autocorr) if not np.isnan(autocorr) else 0.0
        except:
            features['seasonality'] = 0.0
    else:
        features['seasonality'] = 0.0
    
    return features

def compute_dynamic_weights(features, seq_array):
    """动态权重计算"""
    # 基础权重配置
    base_weights = {
        'arima': 0.4,  # ARIMA基础权重
        'lstm': 0.3,   # LSTM基础权重
        'ets': 0.3      # ETS基础权重
    }
    
    # 特征归一化处理
    safe_div = lambda x, y: x / (y + 1e-10)  # 安全除法函数
    
    # ARIMA权重调整（平稳性主导）
    arima_adjust = 0.15 * features['stationarity'] - 0.004 * np.abs(features['trend_strength'])
    
    # ETS权重调整（季节性主导）
    ets_adjust = 0.2 * features['seasonality']+ 0.004 * np.abs(features['trend_strength'])
    
    # LSTM权重调整（波动率主导）
    rel_volatility = safe_div(features['std_dev'], np.mean(np.abs(seq_array)))
    lstm_adjust = 0.15 * rel_volatility
    
    # 应用调整（带边界检查）
    final_weights = {
        'arima': max(0.1, min(0.6, base_weights['arima'] + arima_adjust)),
        'lstm': max(0.1, min(0.6, base_weights['lstm'] + lstm_adjust)),
        'ets': max(0.1, min(0.6, base_weights['ets'] + ets_adjust))
    }
    
    # 归一化处理
    total = sum(final_weights.values())
    return {k: v/total for k, v in final_weights.items()}
def predict_hotness(json_filename):
    df = load_local_json(json_filename)
    if df.empty:
        raise ValueError("无效输入数据")
    
    hotness_series, time_window = calculate_hotness(df)
    if hotness_series.empty:
        raise ValueError("无法计算热度")
    
    # 生成热度趋势图
    plot_hotness_trend(hotness_series, time_window, 'hotness_trend.png')
    
    # 调用预测主程序
    input_sequence = hotness_series.tolist()
    if len(input_sequence) < 30:
        raise ValueError("至少需要30个历史值")

    arima_order, lstm_model, lstm_scaler = load_models()
    input_seq = ','.join(map(str, input_sequence))    
        
    try:
        # 数据预处理
        sequence = [float(x) for x in input_seq.split(',')]
        if len(sequence) < 30:
            raise ValueError("至少需要30个观测值")
            
        history = sequence[-5:]  # 最后5个历史值
            
        # ARIMA预测
        arima_pred = segmented_arima_predict(sequence, arima_order)
            
        # LSTM预测
        lstm_pred = predict_next_values(lstm_model, sequence)
            
        # ETS预测（带标准化）
        ets_scaler = MinMaxScaler()
        scaled_seq = ets_scaler.fit_transform(np.array(sequence).reshape(-1, 1)).flatten()
        ets_model = train_ets_model(scaled_seq)
        ets_pred = ets_scaler.inverse_transform(
            np.array(predict_future(ets_model)).reshape(-1, 1)
        ).flatten()

        # 结果可视化
        plot_predictions(history, arima_pred[:5], lstm_pred[:5], ets_pred[:5], time_window)

        # 计算统计特征
        features = calculate_statistical_features(sequence)
        print(f"统计特征: {features}")
            
        # 计算动态权重
        weights = compute_dynamic_weights(features,np.array(sequence))
        print(f"\n模型权重分配 - ARIMA: {weights['arima']:.2f}, LSTM: {weights['lstm']:.2f}, ETS: {weights['ets']:.2f}")

        # 加权融合预测
        combined_pred = [
            weights['arima']*arima_pred[i] + 
            weights['lstm']*lstm_pred[i] + 
            weights['ets']*ets_pred[i] 
            for i in range(5)
        ]

        history2 = sequence[-10:]  # 最后10个历史值
        Comb_plot_prediction(history2, combined_pred, time_window)    


    except Exception as e:
        print(f"错误: {str(e)}\n示例输入: 0.1,0.5,0.3,0.7,0.6,...（至少30个值）")

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("用法：python prediction_main.py <json文件名>")
        sys.exit(1)
    json_file = sys.argv[1]
    try:
        predict_hotness(json_file)
    except Exception as e:
        print(f"错误：{e}")