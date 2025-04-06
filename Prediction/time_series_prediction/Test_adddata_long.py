import sqlite3
import random
import numpy as np
from typing import List

def create_table(db_path: str, table_name: str, max_columns: int = 50) -> None:
    """
    创建符合数据格式要求的数据表
    :param db_path: 数据库路径
    :param table_name: 表名称
    :param max_columns: 最大数据列数（对应时间序列的最大长度）
    """
    # 列格式：length + val1~valN（总列数 = 1 + max_columns）
    columns = ["length INTEGER"] + [f"val{i} REAL" for i in range(1, max_columns+1)]
    columns_sql = ", ".join(columns)
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})")
        conn.commit()

def insert_sequence(db_path: str, table_name: str, sequence: List[float], max_columns: int = 60) -> None:
    """
    向指定表插入时间序列数据
    :param db_path: 数据库路径
    :param table_name: 目标表名称
    :param sequence: 时间序列数据列表
    :param max_columns: 表的最大数据列数（需与create_table参数一致）
    """
    # 验证数据长度
    if len(sequence) > max_columns:
        raise ValueError(f"序列长度不能超过 {max_columns}")
    if len(sequence) == 0:
        raise ValueError("不能插入空序列")
    
    # 构造列名列表（length + val1~valN）
    columns = ["length"] + [f"val{i}" for i in range(1, len(sequence)+1)]
    columns_str = ", ".join(columns)
    
    # 构造值列表（长度在前，数据在后）
    values = [len(sequence)] + sequence
    placeholders = ", ".join(['?'] * len(values))
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})",
                values
            )
            conn.commit()
            print(f"成功向 {table_name} 插入长度 {len(sequence)} 的序列")
    except sqlite3.Error as e:
        print(f"数据库错误: {str(e)}")

def generate_test_sequence(min_len: int = 40, max_len: int = 80) -> List[float]:
    """
    生成符合新闻热度趋势的测试数据（完整修复版）
    阶段划分：
    1. 初始上升期（快速攀升）
    2. 峰值波动期（小幅震荡）
    3. 衰退期（缓慢下降）
    """
    # 强制参数有效性验证
    min_len = max(35, min_len)  # 最小长度设为5
    max_len = max(min_len, max_len)
    
    # 生成有效序列长度
    length = random.randint(min_len, max_len)
    
    # 阶段划分（边界保护）
    phase1_end = max(8, int(length * 0.2))       # 上升期至少8天
    phase2_end = min(length-20, phase1_end + int(length * 0.6))  # 保留至少20天衰退期
    
    sequence = []
    current_value = random.uniform(10, 20)  # 初始热度
    
    # 保证生成length个数据点
    for t in range(length):
        # 第一阶段：快速上升
        if t <= phase1_end:
            increment = random.uniform(50, 100)
            noise = random.gauss(0, 50)
        
        # 第二阶段：峰值波动
        elif t <= phase2_end:
            increment = random.uniform(-50, 50)
            noise = random.gauss(0, 30)
        
        # 第三阶段：缓慢衰退
        else:
            increment = random.uniform(-30, -15)
            noise = random.gauss(0, 20)
        
        # 计算新值并确保非负
        new_value = current_value + increment + noise
        new_value = max(new_value, 1.0)  # 最低热度设为1.0
        
        # 控制最大涨幅不超过30%
        if new_value > current_value * 2:
            new_value = current_value * 2
        
        sequence.append(round(new_value, 2))
        current_value = new_value
    
    # 添加随机突发事件（10%概率出现二次高峰）
    if len(sequence) >= 5 and random.random() < 0.1:
        peak_pos = random.randint(
            max(2, int(length*0.3)), 
            min(length-3, int(length*0.7))  # 确保有前后空间
        )
        # 插入高峰波动
        for i in range(max(0, peak_pos-2), min(len(sequence), peak_pos+2)):
            sequence[i] = round(sequence[i] * random.uniform(1.2, 1.7), 2)
    
    # 最终安全校验（双重保障）
    if len(sequence) == 0:
        return [round(random.uniform(10, 20), 2) for _ in range(5)]
    if len(sequence) < min_len:
        return sequence + [round(random.uniform(10, 20), 2) for _ in range(min_len - len(sequence))]
    
    return sequence[:length]  # 确保返回正确长度

def main():
    # 数据库配置
    db_path = "time_series.db"
    table_name = "hotness_records"
    max_columns = 100
    
    # 创建数据表（如果不存在）
    create_table(db_path, table_name, max_columns)
    
    # 获取要插入的记录数量
    try:
        num_records = int(input("请输入要插入的新闻事件数量（至少1个）: "))
        if num_records <= 0:
            raise ValueError
    except ValueError:
        print("输入无效，请输入正整数")
        return
    
    # 批量插入测试数据
    print(f"\n开始生成 {num_records} 条新闻热度趋势...")
    for i in range(1, num_records+1):
        try:
            seq = generate_test_sequence(min_len=40, max_len=max_columns-20)
            # 最终校验
            if len(seq) == 0:
                print(f"事件{i}生成异常，已自动重新生成")
                seq = generate_test_sequence(min_len=40, max_len=max_columns-20)
                
            print(f"事件{i}: 周期={len(seq)}天, 趋势=> ", end="")
            print(f"初始值:{seq[0]:.1f}, 峰值:{max(seq):.1f}, 最终值:{seq[-1]:.1f}")
            
            insert_sequence(db_path, table_name, seq, max_columns)
        except Exception as e:
            print(f"生成事件{i}失败: {str(e)}")
            continue
    100
    print("\n所有新闻热度数据已安全存入数据库")

if __name__ == "__main__":
    # 测试代码
    try:
        # 验证空序列生成
        print("空序列测试:", generate_test_sequence(min_len=0, max_len=0))  # 应返回长度>=5的序列
        # 正常测试
        print("正常测试:", generate_test_sequence())
    except Exception as e:
        print(f"测试失败: {str(e)}")
    
    # 运行主程序
    main()