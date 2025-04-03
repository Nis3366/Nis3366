import json
from bson import json_util
import pymongo

def insert_json_to_mongodb():
    # 1. 连接数据库（请根据实际连接字符串替换）
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["NIS3366"]
    collection = db["姜萍"]

    # 2. 打开并读取 JSON 文件
    file_path = "Data_management/crawl_result/NIS3366.姜萍.json"
    with open(file_path, 'r', encoding='utf-8') as f:
        # 如果 JSON 里有 MongoDB 特殊字段（如 $oid），可用 json_util.loads()
        data = json_util.loads(f.read())

    # 3. 判断 JSON 是单个文档还是数组文档
    # 如果是单个文档（dict），直接 insert_one
    if isinstance(data, dict):
        result = collection.insert_one(data)
        print("插入单个文档成功，_id = ", result.inserted_id)

    # 如果是数组（list），需要批量插入
    elif isinstance(data, list):
        result = collection.insert_many(data)
        print("插入多个文档成功，共计 = ", len(result.inserted_ids))
    else:
        print("JSON 格式不符合预期。请确认文件格式。")

if __name__ == "__main__":
    insert_json_to_mongodb()
