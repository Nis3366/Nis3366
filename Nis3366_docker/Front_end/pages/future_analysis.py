import streamlit as st
from pymongo import MongoClient
import pandas as pd
from datetime import timedelta
from pyecharts import options as opts
from pyecharts.charts import Pie, Map, Line
import streamlit.components.v1 as components
from Data_management import get_emotion
from Prediction.prediction_main import predict_hotness
st.title("数据预测")

import os
# 连接本地 MongoDB
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client['NIS3366']

if "details_topics" not in st.session_state:
    # 获取数据库中的所有集合名称（表名）
    collection_names = db.list_collection_names()
    # 如果数据库中没有集合，提示用户
    if not collection_names:
        st.write("数据库中没有集合！")
    else:
        # 创建一个下拉菜单，供用户选择表名
        topic = st.selectbox("请选择一个话题", collection_names, index=len(collection_names) - 1)
        st.session_state["show"] = topic
        # 显示用户选择的话题
        st.title(f"{topic}")
        # 获取用户选择的集合
        collection = db[topic]
        # 查询所有数据
        data = list(collection.find())
        # 将数据转换为 DataFrame
        df = pd.DataFrame(data)
else:
    # 从热点页面跳转过来的请求
    st.session_state["show"] = st.session_state["details_topics"]
    del st.session_state["details_topics"]
    # 获取数据库中的所有集合名称（表名）
    collection_names = db.list_collection_names()
    # 如果数据库中没有集合，提示用户
    if not collection_names:
        st.write("数据库中没有集合！")
    else:
        # 创建一个下拉菜单，供用户选择表名
        st.selectbox("请选择一个话题", collection_names)
    # 获取集合
    if st.session_state["show"] in db.list_collection_names():
        collection = db[st.session_state["show"]]
        # 查询所有数据
        data = list(collection.find())
        df = pd.DataFrame(data)
        st.title(f"{st.session_state['show']}")
    else:
        st.error(f"集合 '{st.session_state['show']}' 不存在！")

if st.button("开始预测"):
    predict_hotness(df)
    st.rerun()

# 展示预测结果图片
# 展示预测结果图片
st.markdown("## 热度趋势图")
st.image('Prediction/hotness_trend.png')
st.markdown("## 多维预测图")
st.image('Prediction/Multi_prediction_result.png')
st.markdown("## 综合预测图")
st.image('Prediction/prediction_result.png')