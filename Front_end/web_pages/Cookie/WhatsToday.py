import streamlit as st

# 示例数据
hot_topics = [
    {"title": "热点1"},
    {"title": "热点2"},
    {"title": "热点3"},
    {"title": "热点4"},
    {"title": "热点5"},
    {"title": "热点6"},
    {"title": "热点7"},
    {"title": "热点8"},
    {"title": "热点9"},
    {"title": "热点10"},
]

st.title("今日热点")

# 爬取微博热点的按钮
if st.button("开始爬取今日微博热点"):
    st.session_state["hot_topics"] = hot_topics
    st.experimental_rerun()

# 展示热点并添加 keepintrack 按钮
if "hot_topics" in st.session_state:
    for index, topic in enumerate(st.session_state["hot_topics"], start=1):
        cols = st.columns([10, 1])
        cols[0].write(f"{index}. {topic['title']}")
        if cols[1].button("Keep in Track", key=f"track_{index}"):
            st.session_state["selected_topic"] = topic
            st.experimental_rerun()

# 跳转到数据分析页
if "selected_topic" in st.session_state:
    st.write("跳转到数据分析页...")
    st.query_params(page="data_analysis")