import sqlite3
import os
from Hotness.Hotness import load_local_json, calculate_hotness

def create_table_if_not_exists(conn):
    """创建数据表，包含length和val1-val1005列"""
    cursor = conn.cursor()
    columns = ["length INTEGER"]
    columns.extend([f"val{i} REAL" for i in range(1, 1006)])
    
    create_sql = f"CREATE TABLE IF NOT EXISTS hotness_records ({', '.join(columns)})"
    cursor.execute(create_sql)
    conn.commit()

def import_hotness_to_db(json_filename, db_path='time_series.db'):
    """
    将JSON文件的热度数据导入数据库
    参数：
        json_filename: JSON文件名
        db_path: 数据库路径
    """
    # 加载并计算热度
    df = load_local_json(json_filename)
    if df.empty:
        raise ValueError("加载数据失败")
    
    hotness_series, time_window = calculate_hotness(df)
    if hotness_series.empty:
        raise ValueError("热度计算失败")
    
    # 准备数据
    values = hotness_series.tolist()
    length = len(values)
    if length > 1005:
        raise ValueError("时间序列过长（最大支持1005个值）")
    
    # 构建插入语句
    conn = sqlite3.connect(db_path)
    create_table_if_not_exists(conn)
    cursor = conn.cursor()
    
    # 动态生成列名和占位符
    columns = ['length'] + [f'val{i+1}' for i in range(length)]
    placeholders = ', '.join(['?'] * (length + 1))
    
    # 填充不足的值为NULL
    full_values = [length] + values + [None]*(1005-length)
    
    # 执行插入
    sql = f"INSERT INTO hotness_records ({', '.join(columns)}) VALUES ({placeholders})"
    cursor.execute(sql, full_values[:length+1])
    conn.commit()
    conn.close()
    
    print(f"成功导入数据，时间窗口：{time_window}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("用法：python Historical_data_entry.py <json文件名>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    try:
        import_hotness_to_db(json_file)
    except Exception as e:
        print(f"错误：{str(e)}")