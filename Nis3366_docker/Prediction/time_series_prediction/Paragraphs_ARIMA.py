"""
分段ARIMA时间序列预测系统（多趋势参数版）
功能：基于趋势类型的分段ARIMA建模，适用于存在趋势突变的新闻热度预测
"""

import sqlite3
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from collections import Counter
import warnings
import ruptures as rpt

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

def classify_trend(segment, threshold=0.05):
    """
    判断时间序列分段的趋势类型
    参数：
        segment: 输入分段序列
        threshold: 趋势阈值（相对于均值的百分比）
    返回：
        str: 趋势类型（'up', 'down', 'flat'）
    """
    if len(segment) < 2:
        return 'flat'
    
    try:
        x = np.arange(len(segment))
        y = np.array(segment)
        slope = np.polyfit(x, y, 1)[0]
        mean = np.mean(y)
        
        if abs(mean) < 1e-6:  # 防止除以零
            return 'flat'
        
        slope_ratio = abs(slope) / abs(mean)
        if slope_ratio > threshold:
            return 'up' if slope > 0 else 'down'
        return 'flat'
    except:
        return 'flat'
def calculate_adaptive_pen(sequence):
    """
    基于序列统计特征计算自适应pen值
    参数：
        sequence: 输入时间序列
    返回：
        float: 自适应pen值
    """
    if len(sequence) < 5:
        return 2.0  # 默认值
    
    # 计算关键统计特征
    std_dev = np.std(sequence)
    mean_val = np.mean(sequence)
    autocorr = np.corrcoef(sequence[:-1], sequence[1:])[0,1]
    trend_strength = np.polyfit(range(len(sequence)), sequence, 1)[0]
    
    # 基于特征计算pen值
    # 1. 标准差越大，pen应越小（噪声大的序列需要更敏感）
    # 2. 自相关性越高，pen应越大（平稳序列需要更少变点）
    # 3. 趋势强度越大，pen应越小（强趋势序列需要更多变点）
    if mean_val <= 10:
        base_pen = mean_val  # 基准值
    else:
        if mean_val <= 1000:
            base_pen = mean_val * 0.025
        else:
            base_pen = mean_val * 0.0025
    print(mean_val)
    pen = base_pen * (1.0 / (1.0 + std_dev/mean_val))  # 标准化波动率影响
    pen *= (1.0 + abs(autocorr))  # 自相关影响
    pen *= (1.0 - 0.5 * abs(trend_strength)/mean_val)  # 趋势强度影响
    
    # 限制pen值在合理范围内
    return np.clip(pen, 1, 10.0)

def detect_changepoints(sequence, pen=None):
    """
    变点检测函数，支持自适应pen值
    参数：
        sequence: 输入时间序列
        pen: 可选，手动指定pen值；None表示自动计算
    返回：
        list: 变点位置列表（索引值）
    """
    try:
        signal = np.array(sequence).reshape(-1, 1)
        
        # 自动计算pen值
        if pen is None:
            pen = calculate_adaptive_pen(sequence)
            print(f"自动计算pen值: {pen:.2f}")
        
        # 使用更高效的Pelt算法
        algo = rpt.Pelt(model="rbf", min_size=3).fit(signal)
        return algo.predict(pen=pen)
        
    except Exception as e:
        print(f"变点检测失败: {str(e)}")
        return [len(sequence)]
    
def find_segmented_arima_order(sequences):
    """
    分段确定三种趋势类型的最佳ARIMA参数组合
    参数：
        sequences: 时间序列数据集
    返回：
        dict: 包含三个最佳参数组合的字典，键为'up', 'flat', 'down'
    """
    # ARIMA参数搜索空间
    p_values = [1, 2, 3, 4]
    d_values = [0, 1, 2]
    q_values = [1, 2, 3]

    up_counter = Counter()
    flat_counter = Counter()
    down_counter = Counter()

    for idx, seq in enumerate(sequences):
        print(f"\nAnalyzing sequence {idx+1}/{len(sequences)} (length={len(seq)})...")
        
        # 变点检测
        change_points = detect_changepoints(seq)
        print(f"Detected change points: {change_points}")
        
        # 处理所有分段
        start = 0
        for cp in change_points:
            process_segment(seq[start:cp], up_counter, flat_counter, down_counter, p_values, d_values, q_values)
            start = cp
        
        # 处理最后一个分段
        process_segment(seq[start:], up_counter, flat_counter, down_counter, p_values, d_values, q_values)

    # 获取各趋势类型的最佳参数
    default_order = (2, 1, 1)
    return {
        'up': up_counter.most_common(1)[0][0] if up_counter else default_order,
        'flat': flat_counter.most_common(1)[0][0] if flat_counter else default_order,
        'down': down_counter.most_common(1)[0][0] if down_counter else default_order
    }

def process_segment(segment, up_counter, flat_counter, down_counter, p_values, d_values, q_values):
    """处理单个分段并更新参数计数器"""
    if len(segment) < 5:
        return
    
    # 趋势分类
    trend = classify_trend(segment)
    
    # 参数搜索
    best_aic = np.inf
    best_order = (0, 0, 0)
    for p in p_values:
        for d in d_values:
            for q in q_values:
                try:
                    model = ARIMA(segment, order=(p, d, q))
                    results = model.fit()
                    if results.aic < best_aic:
                        best_aic = results.aic
                        best_order = (p, d, q)
                except:
                    continue
    
    # 更新对应计数器
    if trend == 'up':
        up_counter[best_order] += 1
    elif trend == 'down':
        down_counter[best_order] += 1
    else:
        flat_counter[best_order] += 1


def segmented_arima_predict(input_sequence, orders, steps=5):
    """
    改进版分段ARIMA滚动预测
    参数：
        input_sequence: 输入序列
        orders: 包含三种趋势参数的字典
        steps: 预测步数
    返回：
        list: 预测结果列表
    """
    # 变点检测
    change_points = detect_changepoints(input_sequence)
    print(f"Detected change points: {change_points}")
    
    # 获取最后有效分段
    last_segment = input_sequence[change_points[-1]:] if change_points else input_sequence
    if len(last_segment) < 3:
        last_segment = input_sequence[-5:]
    
    # 趋势分类
    trend_type = classify_trend(last_segment)
    print(f"Last segment trend: {trend_type}")
    selected_order = orders[trend_type]
    print(f"Using {trend_type} parameters: {selected_order}")
    
    # 滚动预测
    predictions = []
    history = list(last_segment)
    for _ in range(steps):
        try:
            model = ARIMA(history, order=selected_order)
            results = model.fit()
            pred = results.forecast()[0]
            predictions.append(pred)
            history.append(pred)
        except Exception as e:
            print(f"Prediction error: {str(e)}")
            predictions.append(np.nan)
    
    return predictions


def main():
    warnings.filterwarnings("ignore")
    db_path = "timeseries.db"
    table_name = "hotness_records"

    try:
        sequences = load_data_from_db(db_path, table_name)
        print(f"\nLoaded {len(sequences)} sequences")
        
        # 参数学习
        print("\nLearning trend-specific parameters...")
        best_orders = find_segmented_arima_order(sequences)
        print(f"""
Best parameters:
- Rising trend: {best_orders['up']}
- Stable trend: {best_orders['flat']}
- Falling trend: {best_orders['down']}
        """)
        
        # 交互预测
        while True:
            user_input = input("\nEnter time series (comma-separated) or 'quit': ")
            if user_input.lower() == 'quit':
                break
            
            try:
                input_seq = [float(x) for x in user_input.split(',')]
                if len(input_seq) < 5:
                    raise ValueError("Minimum 5 observations required")
                
                preds = segmented_arima_predict(input_seq, best_orders)
                
                # 显示预测结果
                print("\nPredictions:")
                for i, v in enumerate(preds, 1):
                    direction = "↑" if v > (preds[i-2] if i>1 else input_seq[-1]) else "↓"
                    print(f"Step {i}: {direction} {max(v, 0):.2f}")  # 热度值不小于0
            except Exception as e:
                print(f"Error: {str(e)}")

    except Exception as e:
        print(f"System error: {str(e)}")

if __name__ == "__main__":
    main()