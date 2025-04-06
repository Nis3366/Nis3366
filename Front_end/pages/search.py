import threading
import streamlit as st
from Crawler.get_topic_posts import get_topic_posts

st.title("Explore the Topics You Want to Learn About")

# 添加搜索框
search_query = st.text_input("请输入搜索内容", placeholder="输入关键词...")

# 添加确认按钮
if st.button("确认"):
    if search_query: 
        topic_content = search_query
        thread=threading.Thread(target=get_topic_posts, args=(topic_content,))
        thread.start()
        st.success(f"已确认并存入数据库：{topic_content}")
        if "selected_topic" in st.session_state:
            print(st.session_state["selected_topic"])
    else:
        st.warning("请输入搜索内容！")

 # details 按钮
if st.button("详情"):
    # 设置查询参数并跳转到 details.py
    st.session_state["details_topics"] = search_query
    st.page_link("pages/details.py", label="跳转到详情")
