# import folium
# import pandas as pd
# from geopy.geocoders import Nominatim
# from collections import Counter

# # 假设你有一个包含中国地址的列表
# addresses = [
#     '北京市, 中国',
#     '上海市, 中国',
#     '广州市, 中国',
#     '深圳市, 中国',
#     '成都市, 中国',
#     '北京市, 中国',
#     '广州市, 中国'
# ]

# # 统计每个地址的出现次数
# address_count = Counter(addresses)

# # 创建一个DataFrame来存储地址和对应的地理位置
# data = []

# geolocator = Nominatim(user_agent="geoapiExercises")

# for address, count in address_count.items():
#     try:
#         location = geolocator.geocode(address)
#         if location:
#             data.append({
#                 'address': address,
#                 'latitude': location.latitude,
#                 'longitude': location.longitude,
#                 'count': count
#             })
#     except Exception as e:
#         print(f"Error fetching data for address: {address}, {e}")

# df = pd.DataFrame(data)

# # 创建一个Folium地图对象
# m = folium.Map(location=[35, 105], zoom_start=4)

# # 添加地址的位置到地图上，并根据出现次数调整颜色深浅
# for idx, row in df.iterrows():
#     folium.CircleMarker(
#         location=[row['latitude'], row['longitude']],
#         radius=5,
#         color='blue',
#         fill=True,
#         fill_color='blue',
#         fill_opacity=min(1, 0.1 + row['count']*0.1)  # 根据出现次数调整颜色深浅
#     ).add_to(m)

# # 保存地图
# m.save('address_map.html')
# print("Map has been saved as 'address_map.html'")

# import plotly.express as px
# import pandas as pd

# # 城市名称列表
# cities = ['北京', '上海', '广州', '北京', '上海', '深圳', '北京']

# # 统计每个城市出现的次数
# city_counts = pd.Series(cities).value_counts().reset_index()
# city_counts.columns = ['城市', '出现次数']

# # 使用 Plotly 创建条形图
# fig = px.bar(city_counts, 
#              x='城市', 
#              y='出现次数', 
#              color='出现次数', 
#              color_continuous_scale=px.colors.sequential.Blues,
#              title='城市出现次数')

# # 显示图形
# fig.show()
import folium
import pandas as pd

# 城市名称列表
cities = ['北京', '上海', '广州', '北京', '上海', '深圳', '北京']

# 统计每个城市出现的次数
city_counts = pd.Series(cities).value_counts().reset_index()
city_counts.columns = ['城市', '出现次数']

# 创建地图
m = folium.Map(location=[35, 105], zoom_start=5)  # 中心位置为中国

# 城市坐标字典，您可以根据需要添加更多城市坐标
city_locations = {
    '北京': [39.9042, 116.4074],
    '上海': [31.2304, 121.4737],
    '广州': [23.1291, 113.2644],
    '深圳': [22.5431, 114.0579]
}

# 根据城市出现次数添加标记
for index, row in city_counts.iterrows():
    city = row['城市']
    count = row['出现次数']
    location = city_locations.get(city)
    
    if location:
        folium.CircleMarker(
            location=location,
            radius=count * 5,  # 圆的大小与出现次数成正比
            color='blue',
            fill=True,
            fill_color='blue',
            fill_opacity=0.6,
            popup=f"{city}: {count}次"
        ).add_to(m)

# 保存并展示地图
m.save('city_map.html')