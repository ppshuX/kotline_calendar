#!/bin/bash

# 初始化公开日历数据
# 用法：ssh到服务器后执行：bash deploy_public_calendars.sh

echo "🚀 初始化公开日历数据..."

# 1. 进入项目目录
cd ~/kotlin_calendar || exit 1

# 2. 拉取最新代码
echo "📥 拉取代码..."
git pull origin master

# 3. 进入后端目录
cd backend || exit 1

# 4. 初始化公开日历数据
echo "📅 初始化公开日历..."
python3 manage.py init_public_calendars

# 5. 重启服务（尝试多种方式）
echo "🔄 重启服务..."
if command -v systemctl &> /dev/null; then
    sudo systemctl restart gunicorn
elif command -v supervisorctl &> /dev/null; then
    sudo supervisorctl restart gunicorn
else
    pkill -HUP gunicorn || echo "⚠️  请手动重启服务"
fi

echo "✅ 部署完成！"
echo ""
echo "📊 可用的订阅日历："
echo "  - china-holidays: 中国法定节假日 (7个)"
echo "  - lunar-festivals: 农历传统节日 (8个)"
echo "  - world-days: 国际纪念日 (10个)"
echo ""
echo "🧪 测试URL："
echo "  https://app7626.acapp.acwing.com.cn/api/calendars/china-holidays/feed/"

