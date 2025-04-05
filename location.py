import json
from DrissionPage import *
from Front_end.config_front import cookies_config
from Data_management import get_emotion

tab = Chromium().latest_tab
tab.get("https://weibo.com/u/1784473157")
tab.set.cookies(cookies_config.cookies)

import pymongo
# 连接本地 MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
# 选择数据库
db = client["NIS3366"]
# 选择集合
collections = db.list_collection_names()

def get_all_emotions(collection_names):
    for collection_name in collection_names:
        collection = db[collection_name]
        empty_emotions = collection.find({"emotion": {"$exists": False}})
        for empty_emotion in empty_emotions:
            if 'emotion' not in empty_emotion:
                final_emotion = get_emotion(empty_emotion['content_all'])
                empty_emotion['emotion'] = final_emotion
                collection.update_one({'_id': empty_emotion['_id']}, {'$set': empty_emotion}, upsert=True)

for collection in collections:
    collection_obj = db[collection]
    empty_location_docs = collection_obj.find({"location": ""})
    for empty_location_doc in empty_location_docs:
        url="https://weibo.com/u/"+empty_location_doc["uid"]
        tab.get(url)
        tab.wait(0.5)
        try:
            elements = tab.eles('@class=woo-box-flex woo-box-alignStart')
            location_not_filered = elements[-1].text
            if ("IP属地：" not in location_not_filered):
                print(empty_location_doc["uid"] + "没有获取到IP属地")
                continue
            else:
                print("获取到" + empty_location_doc["uid"] + "的" + elements[-1].text)
            location=location_not_filered.replace("IP属地：", "")
            empty_location_doc["location"]=location
            collection_obj.update_one({"_id": empty_location_doc["_id"]}, {"$set": empty_location_doc})
        except Exception as e:
            print(f"Error: {e}")
            continue

    empty_emotions=collection_obj.find({"emotion": {"$exists": False}})
    for empty_emotion in empty_emotions:
        print(empty_emotion)
        if 'emotion' not in empty_emotion:
            final_emotion = get_emotion(empty_emotion['content_all'])
            empty_emotion['emotion'] = final_emotion
            collection_obj.update_one({'_id': empty_emotion['_id']}, {'$set': empty_emotion}, upsert=True)