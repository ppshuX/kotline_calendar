#!/bin/bash

# KotlinCalendar 后端部署脚本

echo "🚀 开始部署 KotlinCalendar Backend..."

# 1. 安装依赖
echo "📦 安装 Python 依赖..."
pip3 install -r requirements.txt

# 2. 数据库迁移
echo "💾 执行数据库迁移..."
python3 manage.py makemigrations
python3 manage.py migrate

# 3. 创建超级用户（可选）
# python3 manage.py createsuperuser

# 4. 创建日志目录
echo "📁 创建日志目录..."
mkdir -p logs

# 5. 停止旧进程
echo "🛑 停止旧进程..."
uwsgi --stop uwsgi.pid 2>/dev/null || true
pkill -f "uwsgi.*calendar_backend" || true

# 6. 启动 uWSGI
echo "🔥 启动 uWSGI..."
uwsgi --ini uwsgi.ini

echo "✅ 后端部署完成！"
echo "📍 API 地址：http://127.0.0.1:8000/api/"
echo "📝 查看日志：tail -f logs/uwsgi.log"

