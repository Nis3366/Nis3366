import threading
import streamlit as st
from Crawler.get_topic_posts import get_topic_posts
import pandas as pd
st.title("Explore the Topics You Want to Learn About")

# 添加搜索框
search_query = st.text_input("请输入搜索内容", placeholder="输入关键词...")
# 添加日期范围输入框
date_range = st.date_input("选择日期范围", [], help="选择开始日期和结束日期", key="date_range")
# 添加确认按钮
if st.button("确认"):
    if search_query: 
        topic_content = search_query
        start_time, end_time = [pd.to_datetime(date) for date in date_range] if len(date_range) == 2 else (None, None)
        if start_time and end_time:
            thread=threading.Thread(target=get_topic_posts, args=(topic_content, start_time, end_time))
        else:
            thread=threading.Thread(target=get_topic_posts, args=(topic_content,))
        thread.start()
        st.success(f"已确认并存入数据库：{topic_content}")
    else:
        st.warning("请输入搜索内容！")

 # details 按钮
if st.button("详情"):
    # 设置查询参数并跳转到 details.py
    st.session_state["details_topics"] = search_query
    st.page_link("pages/details.py", label="跳转到详情")
