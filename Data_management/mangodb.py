import pymongo

def insert_item_to_mongodb():
    """插入指定 JSON 数据到 MongoDB 的示例函数。"""

    # TODO: 将以下连接字符串更改为你自己的 MongoDB 连接信息
    # 如果你使用的是本地 MongoDB，请使用 mongodb://localhost:27017/
    # 如果你使用远程 MongoDB 或者 MongoDB Atlas，请替换为你的连接 URI
    client = pymongo.MongoClient("mongodb://localhost:27017/")

    # 选择数据库和集合（不存在时会自动创建）
    db = client["myDatabase"]         # TODO: 替换为你的数据库名称
    collection = db["myCollection"]   # TODO: 替换为你的集合名称

    # 你的 JSON 数据，可以直接粘贴进来
    item = {
      "_id": {
        "$oid": "67eb8066b4b1033e7c6e0167"
      },
      "mid": "5150248738489414",
      "uid": "6605403387",
      "mblogid": "Pl5clzCu2",
      "personal_name": "动漫学院吧",
      "personal_href": "https://weibo.com/6605403387?refer_flag=1001030103_",
      "weibo_href": "https://weibo.com/6605403387/Pl5clzCu2?refer_flag=1001030103_",
      "publish_time": "2025-03-31 13:20:00",
      "content_from": "微博视频号",
      "content_all": "#姜萍# 这样的霸总，能不能也给我一个呢！ L动漫学院吧的微博视频",
      "retweet_num": 0,
      "comment_num": 0,
      "star_num": 1,
      "location": "北京"
    }

    # 如果 _id 已经包含 $oid，可能需要做处理。
    # 可以将 $oid 提取出来，手动转换成 ObjectId 类型，示例如下：
    from bson.objectid import ObjectId
    item["_id"] = ObjectId(item["_id"]["$oid"])

    # 插入数据
    try:
        result = collection.insert_one(item)
        print(f"插入成功，插入的文档 _id 为：{result.inserted_id}")
    except pymongo.errors.DuplicateKeyError:
        print("插入失败，已存在相同 _id 的文档。")

if __name__ == "__main__":
    insert_item_to_mongodb()
