import streamlit as st
from pymongo import MongoClient
import pandas as pd
from datetime  import timedelta
from pyecharts import options as opts
from pyecharts.charts import Pie, Map, Line
import streamlit.components.v1 as components
from Data_management import get_emotion
st.title("details")

# 连接到MongoDB
client = MongoClient('localhost', 27017)
db = client['NIS3366']

if "details_topics" not in st.session_state:
   # 获取数据库中的所有集合名称（表名）
   collection_names = db.list_collection_names()
   # 如果数据库中没有集合，提示用户
   if not collection_names:
      st.write("数据库中没有集合！")
   else:
      # 创建一个下拉菜单，供用户选择表名
      topic = st.selectbox("请选择一个话题", collection_names)
      st.session_state["show"]=topic
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
         st.title(f"{st.session_state["show"]}")
   else:
         st.error(f"集合 '{st.session_state["show"]}' 不存在！")

if 'publish_time' in df.columns:
   # 将 'publish_time' 转换为 datetime 类型
   df['publish_time'] = pd.to_datetime(df['publish_time'])
   # 提取日期
   df['Date'] = df['publish_time'].dt.date
   daily_counts = df['Date'].value_counts().sort_index()
   daily_counts_df = pd.DataFrame({'Date': daily_counts.index, 'Count': daily_counts.values})
   min_date = daily_counts_df['Date'].min()
   max_date = daily_counts_df['Date'].max()
   if (max_date - min_date).days < 6:
      max_date = min_date + timedelta(days=6)
   # 生成完整的日期范围
   full_date_range = pd.date_range(start=min_date, end=max_date, freq='D')
   full_dates_df = pd.DataFrame({'Date': full_date_range.date})
   merged_df = pd.merge(full_dates_df, daily_counts_df, on='Date', how='left').fillna(0)
   st.write("每日发布数量统计：")
   st.write(merged_df)
   # 绘制折线图
   st.line_chart(merged_df.set_index('Date'))
   df['Date'] = df['publish_time'].dt.date  # 提取日期
   df['Hour'] = df['publish_time'].dt.hour  # 提取小时
   hourly_counts = df.groupby(['Date', 'Hour']).size().reset_index(name='Count')
   hourly_counts['DateTime'] = pd.to_datetime(hourly_counts['Date'].astype(str) + ' ' + hourly_counts['Hour'].astype(str) + ':00')
   st.write("每小时发布数量统计：")
   st.write(hourly_counts[['DateTime', 'Count']])
   st.line_chart(hourly_counts.set_index('DateTime')['Count'])
else:
   st.error("数据框中缺少 'publish_time' 列！")

if 'content_all' in df.columns:
    # 对内容进行情感分析
    if 'publish_time' in df.columns:
        try:
            # 转换时间戳并提取日期和小时
            df['publish_time'] = pd.to_datetime(df['publish_time'])
            df['date'] = df['publish_time'].dt.date
            df['hour'] = df['publish_time'].dt.hour  # 提取小时
            
            # 确保数据有效
            if len(df) == 0 or df['emotion'].isnull().all():
                st.warning("没有可用的有效情感数据。")
            
            # 调试信息
            st.write("预览按小时和按天分组前的数据:", df[['date', 'hour', 'emotion']].head())
            
            # 按小时分组
            try:
                # 按小时和情感分组
                emotion_counts_hour = df.groupby(['hour', 'emotion']).size()
                emotion_over_time_hour = emotion_counts_hour.unstack(fill_value=0)
                
                # 计算百分比
                emotion_over_time_hour = emotion_over_time_hour.div(emotion_over_time_hour.sum(axis=1), axis=0) * 100
                
                if not emotion_over_time_hour.empty:
                    # 创建按小时的折线图
                    line_chart_hour = Line()
                    hours = emotion_over_time_hour.index.astype(str).tolist()
                    
                    for emotion in emotion_over_time_hour.columns:
                        line_chart_hour.add_xaxis(hours)
                        line_chart_hour.add_yaxis(
                            emotion,
                            emotion_over_time_hour[emotion].tolist(),
                            label_opts=opts.LabelOpts(is_show=False),
                        )
                    
                    line_chart_hour.set_global_opts(
                        title_opts=opts.TitleOpts(title="不同情感随时间(小时)变化的占比"),
                        xaxis_opts=opts.AxisOpts(name="小时"),
                        yaxis_opts=opts.AxisOpts(name="占比 (%)"),
                        legend_opts=opts.LegendOpts(pos_top="10%"),
                        tooltip_opts=opts.TooltipOpts(trigger="axis"),
                    )
                    
                    line_html_hour = line_chart_hour.render_embed()
                    st.subheader("按小时的情感变化")
                    components.html(line_html_hour, height=500)
                else:
                    st.warning("没有可用于绘制按小时折线图的情感数据。")
            
            except Exception as e:
                st.error(f"按小时分组数据时出错: {str(e)}")
                st.write("调试信息 - 情感值计数:", df['emotion'].value_counts())
                st.write("调试信息 - 小时值计数:", df['hour'].value_counts())
            
            # 按天分组
            try:
                # 按天和情感分组
                emotion_counts_date = df.groupby(['date', 'emotion']).size()
                emotion_over_time_date = emotion_counts_date.unstack(fill_value=0)
                
                # 计算百分比
                emotion_over_time_date = emotion_over_time_date.div(emotion_over_time_date.sum(axis=1), axis=0) * 100
                
                if not emotion_over_time_date.empty:
                    # 创建按天的折线图
                    line_chart_date = Line()
                    dates = emotion_over_time_date.index.astype(str).tolist()
                    
                    for emotion in emotion_over_time_date.columns:
                        line_chart_date.add_xaxis(dates)
                        line_chart_date.add_yaxis(
                            emotion,
                            emotion_over_time_date[emotion].tolist(),
                            label_opts=opts.LabelOpts(is_show=False),
                        )
                    
                    line_chart_date.set_global_opts(
                        title_opts=opts.TitleOpts(title="不同情感随时间(天)变化的占比"),
                        xaxis_opts=opts.AxisOpts(name="日期"),
                        yaxis_opts=opts.AxisOpts(name="占比 (%)"),
                        legend_opts=opts.LegendOpts(pos_top="10%"),
                        tooltip_opts=opts.TooltipOpts(trigger="axis"),
                    )
                    
                    line_html_date = line_chart_date.render_embed()
                    st.subheader("按天的情感变化")
                    components.html(line_html_date, height=500)
                else:
                    st.warning("没有可用于绘制按天折线图的情感数据。")
            
            except Exception as e:
                st.error(f"按天分组数据时出错: {str(e)}")
                st.write("调试信息 - 情感值计数:", df['emotion'].value_counts())
                st.write("调试信息 - 日期值计数:", df['date'].value_counts())
                
        except Exception as e:
            st.error(f"处理时间戳时出错: {str(e)}")
            st.write("示例时间戳值:", df['publish_time'].head().tolist())
    else:
        st.warning("数据框中缺少时间戳列 'publish_time'，无法绘制时间变化图。")
else:
    st.warning("数据框中缺少 'content_all' 列，无法进行情感分析。")

# 标准化省份名称
df['location'] = df['location'].fillna("未知")  # 处理空值
# 将非标准名称转换为官方名称
official_names = {
   "北京": "北京市",
   "天津": "天津市",
   "河北": "河北省",
   "山西": "山西省",
   "内蒙古": "内蒙古自治区",
   "辽宁": "辽宁省",
   "吉林": "吉林省",
   "黑龙江": "黑龙江省",
   "上海": "上海市",
   "江苏": "江苏省",
   "浙江": "浙江省",
   "安徽": "安徽省",
   "福建": "福建省",
   "江西": "江西省",
   "山东": "山东省",
   "河南": "河南省",
   "湖北": "湖北省",
   "湖南": "湖南省",
   "广东": "广东省",
   "广西": "广西壮族自治区",
   "海南": "海南省",
   "重庆": "重庆市",
   "四川": "四川省",
   "贵州": "贵州省",
   "云南": "云南省",
   "西藏": "西藏自治区",
   "陕西": "陕西省",
   "甘肃": "甘肃省",
   "青海": "青海省",
   "宁夏": "宁夏回族自治区",
   "新疆": "新疆维吾尔自治区",
   "台湾": "台湾省",
   "香港": "香港特别行政区",
   "澳门": "澳门特别行政区",
}
df['location'] = df['location'].replace(official_names)

# 过滤掉非标准名称（如“日本”、“美国”、“未知”等）
valid_provinces = list(official_names.values())
df = df[df['location'].isin(valid_provinces)]

# 统计每个省份的数量
province_counts = df['location'].value_counts().reset_index()
province_counts.columns = ['province', 'count']

# 转换为 pyecharts 需要的格式 [(省份, 数量), ...]
data_for_map = list(zip(province_counts['province'], province_counts['count']))

# 检查是否有有效数据
if not data_for_map:
   st.error("没有有效的地图数据！")
elif province_counts.empty:
   st.error("没有有效的省份数据！")
else:
   # 绘制地图
   map_chart = (
      Map()
      .add(
            "数据密度",
            data_for_map,
            maptype="china",
            is_roam=True,  # 允许地图缩放和拖动
      )
      .set_global_opts(
            title_opts=opts.TitleOpts(title="中国各省数据密度"),
            visualmap_opts=opts.VisualMapOpts(
               min_=min(province_counts['count']),
               max_=max(province_counts['count']),
            ),
      )
   )
   # 生成 HTML
   html = map_chart.render_embed()
   # 渲染地图到 Streamlit
   components.html(html, height=600)

   # 创建下载按钮
   st.write("")  # 空行分隔
   col1, col2 = st.columns([0.9, 0.1])  # 将页面分为两列，地图占 90%，按钮占 10%
   with col1:
      st.write("")  # 占位符
   with col2:
      # 将 province_counts 转换为 CSV 文件
      csv = province_counts.to_csv(index=False).encode('utf-8')
      # 添加下载按钮，使用经典图标 📥
      st.download_button(
            label="📥",  # 使用图标作为按钮
            data=csv,
            file_name="province_counts.csv",
            mime="text/csv",
            key="download_button",
      )