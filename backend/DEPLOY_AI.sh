#!/bin/bash

# AI功能部署脚本
# 使用方法：在服务器上执行此脚本

echo "🤖 开始部署AI功能..."

# 1. 配置API Key
echo "📝 配置通义千问API Key..."
cd ~/kotlin_calendar/backend

# 检查.env文件是否存在
if [ ! -f .env ]; then
    echo "创建.env文件..."
    touch .env
fi

# 添加或更新API Key
if grep -q "QWEN_API_KEY" .env; then
    echo "更新现有API Key..."
    sed -i 's/^QWEN_API_KEY=.*/QWEN_API_KEY=YOUR_API_KEY_HERE/' .env
else
    echo "添加新API Key..."
    echo "QWEN_API_KEY=YOUR_API_KEY_HERE" >> .env
fi

# 2. 拉取最新代码
echo "📥 拉取最新代码..."
cd ~/kotlin_calendar
git pull origin master

# 3. 激活虚拟环境并重启服务
echo "🔄 重启服务..."
cd backend
source ~/kotlin_calendar/venv/bin/activate

# 4. 收集静态文件
python manage.py collectstatic --noinput

# 5. 重启Gunicorn
sudo systemctl restart gunicorn

# 6. 检查服务状态
echo "✅ 检查服务状态..."
sudo systemctl status gunicorn --no-pager | head -n 10

echo ""
echo "🎉 AI功能部署完成！"
echo ""
echo "📡 测试AI API："
echo "curl -X POST https://app7626.acapp.acwing.com.cn/api/ai/chat/ \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"message\":\"你好\",\"context\":{\"current_date\":\"2025-11-12\"}}'"

