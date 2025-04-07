# NIS3366：舆情监控预测系统
## ✈️ 介绍
项目是一个舆情监控预测系统。整个项目分成Crawler(爬虫)，Data_management(数据管理与处理)，Front_end(前端展示)，Prediction(热度计算与趋势预测)。整体采用streanlit进行框架搭建，具有高移植性，经测验，可在Windosw，macOS，Ubuntu，WSL(Ubuntu)等主流系统上良好运行。
## 🧩 模块分析与设计
### 🐛 爬虫模块
    微博数据采集功能通过 weibo_crawler 模块实现，支持话题微博的爬取、解析和存储。
### 📊 数据管理与处理
#### - ❤️ 情感分析
    采用通义千问实验室StructBERT情绪分类-中文-七分类-base模型，对微博及其评论进行情感分析，包含恐惧、愤怒、厌恶、喜好、悲伤、高兴、惊讶七种情绪。
### 📈 前端展示
    采用strealit框架构建web应用程序，支持热搜查询，话题热度追踪和话题情感分析展示，支持用户自主选择话题。
### 🧙 热度计算与趋势预测

## 项目效果

## ⚙️ 运行
### 💻 本地直接运行
    conda create -n  NIS3366
    pip install -r requirements.txt
    python ./Front_end/main.py
### 🐳 Docker 运行
    cd ./Nis3366_docker
    # 需要打开本地docker，然后执行下面步骤
    docker-compose up --build
