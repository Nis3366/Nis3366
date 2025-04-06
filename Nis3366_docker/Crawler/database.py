import json

import pymongo
import os
# 连接本地 MongoDB
MONGO_URI = os.getenv("MONGO_URI")
client = pymongo.MongoClient(MONGO_URI)
# 选择数据库
db = client["NIS3366"]
# 选择集合
def insert_one(collection_name: str, document: dict):
    collection = db[collection_name]
    try:
        collection.update_one({'mblogid': document['mblogid']}, {'$set': document}, upsert=True)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")


def insert_many(collection_name: str, documents: list):
    collection = db[collection_name]
    collection.insert_many(documents)

def find_one(collection_name: str, query: dict):
    collection = db[collection_name]
    return collection.find_one(query)

def find_all(collection_name: str, query: dict):
    collection = db[collection_name]
    return collection.find(query)
