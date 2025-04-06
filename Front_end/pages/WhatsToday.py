import streamlit as st
from Crawler.get_top_lists import get_top_lists
from Crawler.get_topic_posts import get_topic_posts_line
import threading

st.title("今日热点")
if "hot_topics" not in st.session_state:
    st.session_state["hot_topics"] = []
#if "detail_topics" not in st.session_state:
    #st.session_state["details_topics"] = []

# 爬取微博热点的按钮
if st.button("开始爬取今日微博热点"):
    # 模拟爬取热点数据
    st.session_state["selected_topic"] = []
    
    st.session_state["hot_topics"] = get_top_lists()
    st.success("爬取成功！")
    st.rerun()

if "selected_topic" not in st.session_state:
    st.session_state["selected_topic"] = []

# 展示热点并添加 keepintrack 按钮
if st.session_state["hot_topics"]:
    for topic in st.session_state["hot_topics"]:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f'{topic}:{st.session_state["hot_topics"][topic]}')
        with col2:
            if topic in st.session_state["selected_topic"]:
                if st.button("撤销", key=f"untrack_{topic}"):
                    st.session_state["selected_topic"].remove(topic)
                    st.rerun()

                # details 按钮
                if st.button("详情", key=f"details_{topic}"):
                    # 设置查询参数并跳转到 details.py
                    #st.session_state["details_topics"] = st.session_state["hot_topics"][topic]
                    st.session_state["details_topics"] = "#名侦探学院#"
                    st.page_link("pages/details.py", label="跳转到详情")

            else:
                if st.button("keepintrack", key=f"track_{topic}"):
                    st.session_state["selected_topic"].append(topic)
                    st.rerun()

selected_values = [st.session_state["hot_topics"][key] 
                  for key in st.session_state["selected_topic"] 
                  if key in st.session_state["hot_topics"]]

# 确认按钮
if st.session_state["hot_topics"]:
    if st.button("确认"):
        thread=threading.Thread(target=get_topic_posts_line, args=(selected_values,))
        thread.start()
        st.success("已确认并存入数据库")
        st.session_state["selected_topic"]=[]
        st.rerun()

