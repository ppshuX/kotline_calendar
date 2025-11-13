FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements并安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 安装uWSGI（如果使用）
RUN pip install uwsgi

# 复制项目文件
COPY . .

# 创建必要的目录
RUN mkdir -p /app/static /app/media /app/logs

# 暴露端口
EXPOSE 8000

# 启动命令（默认使用uWSGI，如果使用Gunicorn请修改）
CMD ["uwsgi", "--ini", "uwsgi.ini"]

