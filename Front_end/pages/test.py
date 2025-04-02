from pyecharts import options as opts
from pyecharts.charts import Map

# 示例数据
data_for_map = [
    ('广东', 13), ('江苏', 13), ('北京', 11), ('浙江', 10), ('山东', 10), ('河南', 10),
    ('上海', 10), ('福建', 6), ('山西', 5), ('湖北', 5), ('四川', 4), ('重庆', 4),
    ('海南', 4), ('江西', 3), ('陕西', 3), ('台湾', 3), ('辽宁', 3), ('黑龙江', 3),
    ('河北', 3), ('湖南', 3), ('甘肃', 2), ('吉林', 2), ('贵州', 2), ('广西', 2),
    ('宁夏', 2), ('云南', 2), ('安徽', 1), ('天津', 1), ('香港', 1), ('新疆', 1)
]

# 绘制地图
map_chart = (
    Map()
    .add(
        series_name="数据密度",
        data_pair=data_for_map,
        maptype="china",
        is_roam=True,
    )
    .set_global_opts(
        title_opts=opts.TitleOpts(title="中国各省数据密度"),
        visualmap_opts=opts.VisualMapOpts(
            min_=min(count for _, count in data_for_map),
            max_=max(count for _, count in data_for_map),
            is_piecewise=False,
            range_color=["#f0f9e8", "#08589e"],  # 颜色从浅到深
        ),
    )
)

# 在 Jupyter Notebook 中显示地图
map_chart.render_notebook()