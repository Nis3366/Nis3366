FROM python:3.12

# 设置工作目录
WORKDIR /nis3366_docker_image
COPY . /nis3366_docker_image
# 复制依赖文件
# COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码


EXPOSE 8501
# 设置容器启动命令
CMD ["streamlit", "run", "./Front_end/main.py"]