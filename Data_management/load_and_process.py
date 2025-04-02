import process_simple_text as pst
import process_complex_text as pct
import get_item_mongodb as get_item
import sys
from pathlib import Path
import pymongo

# 初始化MongoDB连接
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["NIS3366"]

# 获取所有集合名称（表名）
table_names = db.list_collection_names()

# 检查是否为空
if not table_names:
    print("数据库中没有找到任何集合（表）！")
    sys.exit(1)

# 初始化统计字典
emotion_count = {}
location_count = {}

# 处理每个表的数据
for table_name in table_names:
    print(f"\n正在处理集合: {table_name}")
    
    item_list, batch_size = get_item.get_items(table_name)
    for i, item in enumerate(item_list):
        try:
            # 情感分析
            emotion_result = pct.get_emotion(item['content_all'])
            emotion_max_index = emotion_result['scores'].index(max(emotion_result['scores']))
            emotion_max = emotion_result['labels'][emotion_max_index]
            
            print(f"第 {i+1} 条文档：", item['content_all'][:50] + "...", '\n情感:', emotion_max)
            
            # 统计计数
            emotion_count[emotion_max] = emotion_count.get(emotion_max, 0) + 1
            location_count[item.get('location', '未知')] = location_count.get(item.get('location', '未知'), 0) + 1
            
        except KeyError as e:
            print(f"文档格式异常，缺少字段: {e}")
            continue
        except Exception as e:
            print(f"处理文档时出错: {e}")
            continue

# 输出最终统计结果
print("\n===== 情感统计 =====")
for emotion, count in emotion_count.items():
    print(f"{emotion}: {count}次")

print("\n===== 地点统计 =====")
for location, count in location_count.items():
    print(f"{location}: {count}次")