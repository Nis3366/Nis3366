import pymongo
# 连接本地 MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
# 选择数据库
db = client["NIS3366"]
# 选择集合
def insert_one(collection_name: str, document: dict):
    collection = db[collection_name]
    collection.insert_one(document)

def insert_many(collection_name: str, documents: list):
    collection = db[collection_name]
    collection.insert_many(documents)

def find_one(collection_name: str, query: dict):
    collection = db[collection_name]
    return collection.find_one(query)

def find_all(collection_name: str, query: dict):
    collection = db[collection_name]
    return collection.find(query)