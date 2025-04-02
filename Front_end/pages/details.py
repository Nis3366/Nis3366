import streamlit as st
from Crawler.get_top_lists import get_top_lists
from Crawler.get_topic_posts import get_topic_posts
from pymongo import MongoClient
import pandas as pd
from datetime  import timedelta
from pyecharts import options as opts
from pyecharts.charts import Map
import streamlit.components.v1 as components

st.title("details")

# 连接到MongoDB
client = MongoClient('localhost', 27017)
db = client['NIS3366']

st.title("话题详情")

if "details_topics" not in st.session_state:
    st.write("今日热点未加载")
else:
   # 获取传递的话题名字
   topic = st.session_state["details_topics"]
   st.title(f"话题详情: {topic}")
   # 获取集合
   # collection = db["#东部战区海报毁瘫#"]
   if topic in db.list_collection_names():
         collection = db[topic]
         # 查询所有数据
         data = list(collection.find())
         df = pd.DataFrame(data)
         st.write(f"成功访问集合: {topic}")
   else:
         st.error(f"集合 '{topic}' 不存在！")

   if 'publish_time' in df.columns:
      # 将 'publish_time' 转换为 datetime 类型
      df['publish_time'] = pd.to_datetime(df['publish_time'])
      
      # 提取日期
      df['Date'] = df['publish_time'].dt.date
      
      # 统计每日发布数量
      daily_counts = df['Date'].value_counts().sort_index()
      
      # 将统计结果转换为 DataFrame
      daily_counts_df = pd.DataFrame({'Date': daily_counts.index, 'Count': daily_counts.values})
      
      # 确定最小日期和最大日期
      min_date = daily_counts_df['Date'].min()
      max_date = daily_counts_df['Date'].max()
      
      # 如果数据不足 7 天，扩展日期范围
      if (max_date - min_date).days < 6:
         max_date = min_date + timedelta(days=6)
      
      # 生成完整的日期范围
      full_date_range = pd.date_range(start=min_date, end=max_date, freq='D')
      
      # 将完整日期范围转换为 DataFrame
      full_dates_df = pd.DataFrame({'Date': full_date_range.date})
      
      # 合并完整日期范围和统计结果，填充缺失日期为 0
      merged_df = pd.merge(full_dates_df, daily_counts_df, on='Date', how='left').fillna(0)
      
      # 显示统计结果
      st.write("每日发布数量统计：")
      st.write(merged_df)
      
      # 绘制折线图
      st.line_chart(merged_df.set_index('Date'))
      
      # 提取日期和小时
      df['Date'] = df['publish_time'].dt.date  # 提取日期
      df['Hour'] = df['publish_time'].dt.hour  # 提取小时
      
      # 按日期和小时分组统计
      hourly_counts = df.groupby(['Date', 'Hour']).size().reset_index(name='Count')
      
      # 将 Date 和 Hour 组合成一个 datetime 列
      hourly_counts['DateTime'] = pd.to_datetime(hourly_counts['Date'].astype(str) + ' ' + hourly_counts['Hour'].astype(str) + ':00')
      
      # 显示统计结果
      st.write("每小时发布数量统计：")
      st.write(hourly_counts[['DateTime', 'Count']])
      
      # 绘制折线图
      st.line_chart(hourly_counts.set_index('DateTime')['Count'])
   else:
      st.error("数据框中缺少 'publish_time' 列！")


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