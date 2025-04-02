import pymongo
first_k = 200
def get_items(table_name:str = "myCollection"):
    # 1. 连接到 MongoDB
    client = pymongo.MongoClient("mongodb://localhost:27017/")

    # 2. 选择数据库和集合
    db = client["NIS3366"]
    collection = db[table_name]
    collection_size = collection.count_documents({})
    # 全部数据
    first_k = collection_size
    # 3. 查询并限制结果数量
    cursor = collection.find().limit(first_k)
    
    # 4. 逐条打印结果
    result = []
    for idx, doc in enumerate(cursor, start=1):
        print(f"第 {idx} 条文档：", doc)
        result.append(doc)
    return result, collection_size
