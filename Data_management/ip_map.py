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