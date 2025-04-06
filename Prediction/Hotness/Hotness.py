"""
社交媒体话题热度分析工具
功能：从JSON数据加载话题互动记录，动态计算时间窗口内的热度值（基于加权互动和指数衰减模型）
输入：包含发布时间(publish_time)、转发(retweet_num)、评论(comment_num)、点赞(star_num)的JSON文件
输出：按时间窗口划分的热度趋势序列
"""

import pandas as pd
import numpy as np
import json
import os
from pandas import json_normalize
from datetime import datetime, timedelta

def get_optimal_time_window(data, time_col="publish_time"):
    """
    动态计算最佳分析时间窗口
    策略：根据数据时间跨度自动选择窗口大小，平衡分析粒度和计算效率
    
    参数：
        data: 包含时间列的DataFrame
        time_col: 时间列名
    
    返回：
        str: 时间窗口字符串（如'30T'表示30分钟）
    """
    # 空数据返回默认窗口
    if data.empty:
        return '30T'
    
    # 计算数据时间跨度（小时）
    min_time = data[time_col].min()
    max_time = data[time_col].max()
    total_span = (max_time - min_time).total_seconds() / 3600  # 转换为小时数
    
    # 窗口数量限制参数
    min_windows = 60    # 最小时间窗口数
    max_windows = 1000  # 最大时间窗口数（防止过多细碎窗口）

    # 当总时间跨度较小时，使用最小窗口保证基础分析粒度
    #if total_span < min_windows * 0.5:  # 0.5小时*30窗口=15小时
    #    return f"{min_windows}T"
    
    # 计算动态窗口长度（秒）
    window_length_seconds = total_span * 3600  # 总秒数
    
    # 计算窗口数量，限制在[min_windows, max_windows]之间
    n = min(max_windows, max(min_windows, int(window_length_seconds / (60 * 60))))  # 60分钟基准

    # 计算最终窗口长度（小时）
    optimal_window_length = window_length_seconds / (n * 3600)

    # 格式化窗口字符串（H=小时，T=分钟） 
    if optimal_window_length < 1/6:
        optimal_window_str = f"{int(60*optimal_window_length)+1}T"
    else:
        if optimal_window_length < 1/2:
            optimal_window_str = f"{(int(6*optimal_window_length)+1)*10}T"
        else:
            if optimal_window_length < 1:  
                optimal_window_str = f"{(int(4*optimal_window_length)+1)*15}T"
            if optimal_window_length >= 1:    
                optimal_window_str = f"{int(optimal_window_length)+1}H"
   
    return optimal_window_str

def load_local_json(filename):
    """
    加载并预处理本地JSON数据
    
    处理流程：
        1. 检查文件是否存在
        2. 修复常见JSON格式问题
        3. 解析并转换为DataFrame
        4. 数据清洗和过滤
    
    参数：
        filename: JSON文件名
    
    返回：
        pd.DataFrame: 预处理后的数据集
    """
    try:
        # 获取脚本所在目录的绝对路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, filename)
        
        # 文件存在性检查
        if not os.path.isfile(file_path):
            print(f"Error: File {filename} not found")
            return pd.DataFrame()
            
        # 读取并修复JSON格式
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = f.read()
            
            # 处理非标准JSON格式（如多行记录无外层列表）
            if not raw_data.startswith('['):
                raw_data = '[' + raw_data + ']'  # 包裹成数组格式
            raw_data = raw_data.replace('\n', '').replace('\t', '')  # 移除空白干扰符
            
            data = json.loads(raw_data)

            # 校验必需字段
            required_columns = ['publish_time', 'retweet_num', 'comment_num', 'star_num']
            df = json_normalize(data)  # 展开嵌套结构
            
            # 检查缺失字段
            missing_cols = [col for col in required_columns if col not in df.columns]
            if missing_cols:
                print(f"Missing required columns: {missing_cols}")
                return pd.DataFrame()

            # 数据清洗
            processed_df = df[required_columns].copy()
            
            # 转换发布时间为datetime类型，错误值设为NaT
            processed_df['publish_time'] = pd.to_datetime(
                processed_df['publish_time'], 
                errors='coerce'  # 无效时间转为NaT
            )
            
            # 转换数值列，非数值转为0
            numeric_cols = ['retweet_num', 'comment_num', 'star_num']
            processed_df[numeric_cols] = processed_df[numeric_cols].apply(
                pd.to_numeric, 
                errors='coerce'  # 转换失败设为NaN
            ).fillna(0)
            
            # 过滤低互动记录
            if not processed_df.empty:
                # 计算总互动量（转发+评论+点赞）
                processed_df['total_interaction'] = processed_df[numeric_cols].sum(axis=1)
                
                # 仅保留高于平均互动的记录
                threshold = processed_df['total_interaction'].mean()
                processed_df = processed_df[processed_df['total_interaction'] >= threshold]
            
            # 去除无效时间记录
            return processed_df.dropna(subset=['publish_time'])
            
    except Exception as e:
        print(f"Data loading error: {str(e)}")
        return pd.DataFrame()


def load_local_df(df_input):
    """
    加载并预处理本地JSON数据

    处理流程：
        1. 检查文件是否存在
        2. 修复常见JSON格式问题
        3. 解析并转换为DataFrame
        4. 数据清洗和过滤

    参数：
        filename: JSON文件名

    返回：
        pd.DataFrame: 预处理后的数据集
    """
    try:
        # 校验必需字段
        required_columns = ['publish_time', 'retweet_num', 'comment_num', 'star_num']
        # 检查缺失字段
        missing_cols = [col for col in required_columns if col not in df_input.columns]
        if missing_cols:
            print(f"Missing required columns: {missing_cols}")
            return pd.DataFrame()

        # 数据清洗
        processed_df = df_input[required_columns].copy()

        # 转换发布时间为datetime类型，错误值设为NaT
        processed_df['publish_time'] = pd.to_datetime(
            processed_df['publish_time'],
            errors='coerce'  # 无效时间转为NaT
        )

        # 转换数值列，非数值转为0
        numeric_cols = ['retweet_num', 'comment_num', 'star_num']
        processed_df[numeric_cols] = processed_df[numeric_cols].apply(
            pd.to_numeric,
            errors='coerce'  # 转换失败设为NaN
        ).fillna(0)

        # 过滤低互动记录
        if not processed_df.empty:
            # 计算总互动量（转发+评论+点赞）
            processed_df['total_interaction'] = processed_df[numeric_cols].sum(axis=1)

            # 仅保留高于平均互动的记录
            threshold = processed_df['total_interaction'].mean()
            processed_df = processed_df[processed_df['total_interaction'] >= threshold]

        # 去除无效时间记录
        return processed_df.dropna(subset=['publish_time'])

    except Exception as e:
        print(f"Data loading error: {str(e)}")
        return pd.DataFrame()

def calculate_hotness(data, time_col="publish_time", 
                     metrics=["retweet_num", "comment_num", "star_num"],
                     weights=[0.4, 0.3, 0.3],
                     decay_rate=0.5):
    """
    计算时间窗口热度值
    
    算法逻辑：
        1. 计算每条记录的加权互动得分
        2. 根据时间跨度生成分析窗口
        3. 应用指数衰减模型计算窗口热度
    
    参数：
        data: 输入数据集
        time_col: 时间列名
        metrics: 互动指标列
        weights: 各指标权重（总和建议为1）
        decay_rate: 衰减系数（值越大衰减越快）
    
    返回：
        pd.Series: 按时间窗口索引的热度值
    """
    if data.empty:
        return pd.Series(dtype=float)
    
    df = data.copy()
    # 确保时间类型并排序
    df[time_col] = pd.to_datetime(df[time_col])
    df = df.sort_values(time_col)
    
    # 计算加权互动得分（向量化运算提升效率）
    df["interaction_score"] = df[metrics].apply(
        lambda x: np.dot(x, weights),  # 点积计算加权得分
        axis=1
    )
    
    # 获取最佳时间窗口
    time_window = get_optimal_time_window(df, time_col)
    print(time_window)
    

    # 安全限制窗口类型（可扩展更多选项）
    #if time_window not in ['30T', '1H', '2H']:
        # time_window = '30T'
    
    # 生成时间分箱（确保覆盖全部数据）
    min_time = df[time_col].min().floor(time_window)
    max_time = df[time_col].max().ceil(time_window)
    time_bins = pd.date_range(min_time, max_time, freq=time_window)
    
    # 初始化热度序列（索引为窗口起始时间）
    hotness = pd.Series(0.0, index=time_bins[:-1], name="hotness")
    
    # 遍历每条记录计算贡献
    for _, row in df.iterrows():
        post_time = row[time_col]
        score = row["interaction_score"]
        
        # 遍历所有时间窗口
        for window_start in time_bins[:-1]:
            window_end = window_start + pd.Timedelta(time_window)
            
            # 跳过早于当前窗口的记录（因数据已排序，可优化提前终止）
            if window_end <= post_time:
                continue
                
            # 计算时间差（小时）并应用指数衰减
            delta =int((window_end - post_time).total_seconds() / pd.Timedelta(time_window).total_seconds()+1)
            decay = np.exp(-decay_rate * delta)  # 指数衰减模型
            hotness.loc[window_start] += score * decay
    
    return hotness, time_window

if __name__ == "__main__":
    """
    主程序执行流程：
        1. 尝试加载数据文件
        2. 检查数据有效性
        3. 计算并输出热度趋势
    """
    try:
        # 加载指定话题数据文件（示例文件名为微博话题格式）
        df_input = load_local_json("NIS3366.#手机价格不超6000元可获补贴#.json")
    except Exception as e:
        print(f"Critical error: {str(e)}")
        df_input = pd.DataFrame()
    
    # 数据有效性检查
    if df_input.empty:
        print("Failed to load valid data")
    else:
        print("Successfully loaded data samples:")
        print(df_input.head(3))  # 展示前3条有效记录
        
        # 计算热度趋势
        hotness , _ = calculate_hotness(df_input)
        
        # 输出结果
        if not hotness.empty:
            print("\nHotness trend (top 5 intervals):")
            print(hotness)
        else:
            print("No hotness data calculated")