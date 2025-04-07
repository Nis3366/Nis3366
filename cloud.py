from wordcloud import WordCloud
import jieba
from collections import Counter
from imageio import imread
import matplotlib.pyplot as plt
import json
import pymongo
import jieba.posseg as pseg
# 连接本地 MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
# 选择数据库
db = client["NIS3366"]

def word_cloud(collection_name):
    collection = db[collection_name]
    data = collection.find().sort("publish_time", pymongo.DESCENDING).limit(300)
    # 拼接所有文本
    content_all = " ".join([item['content_all'] for item in data])
    # 使用词性标注进行分词
    words_temp = pseg.cut(content_all)
    # 去除副词（词性为 'd'）
    excluded_flags = {'d', 'zg'}
    words_temp = [word for word, flag in pseg.cut(content_all) if flag not in excluded_flags]
    words = []
    """读取停用词"""
    with open("stopwords_hit.txt", "r", encoding="utf-8") as fp:
        stopwords = [s.rstrip() for s in fp.readlines()]
        stopwords.append(collection_name)
    """去掉切分词语中的停用词"""
    for w in words_temp:
        if w not in stopwords:
            words.append(w)

    frequency = dict(Counter(words))  # 去停用词之后的词频统计结果

    font = "simfang.ttf"
    wc = WordCloud(font_path=font,
                  background_color="white",)

    wc.fit_words(frequency)  # 基于前面的词频统计
    wc.to_file("word_cloud.png")
