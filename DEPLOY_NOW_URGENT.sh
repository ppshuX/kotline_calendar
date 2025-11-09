#!/bin/bash
# 🚨 紧急部署 Ralendar - Roamio 团队正在等待！
# 时间：2025-11-09 11:30

echo "🚨 紧急部署开始！"
echo "📍 服务器: app7626.acapp.acwing.com.cn"
echo ""

# 1. 进入项目目录
cd ~/kotlin_calendar || exit 1
echo "✅ 已进入项目目录"

# 2. 拉取最新代码
echo "📦 拉取最新代码..."
git pull
echo "✅ 代码已更新"
echo ""

# 3. 显示最新的 5 个提交
echo "📝 最新提交："
git log --oneline -5
echo ""

# 4. 激活虚拟环境
echo "🐍 激活虚拟环境..."
source backend/venv/bin/activate || exit 1
cd backend
echo "✅ 虚拟环境已激活"
echo ""

# 5. 检查待执行的迁移
echo "🔍 检查待执行的迁移..."
python manage.py showmigrations api | grep "\[ \]"
echo ""

# 6. 执行数据库迁移
echo "🗄️ 执行数据库迁移..."
python manage.py migrate
echo "✅ 数据库迁移完成"
echo ""

# 7. 检查 unionid 字段是否存在
echo "🔍 验证 UnionID 字段..."
python manage.py shell << 'PYEOF'
from django.db import connection
cursor = connection.cursor()
cursor.execute("DESCRIBE api_qquser")
for row in cursor.fetchall():
    if 'unionid' in row[0]:
        print(f"✅ 找到 UnionID 字段: {row}")
PYEOF
echo ""

# 8. 重启 uWSGI
echo "🔄 重启 uWSGI..."
pkill -f uwsgi
sleep 2
uwsgi --ini uwsgi.ini &
sleep 3
echo "✅ uWSGI 已重启"
echo ""

# 9. 检查服务状态
echo "🔍 检查服务状态..."
ps aux | grep uwsgi | grep -v grep
echo ""

# 10. 测试 API 可用性
echo "🧪 测试 API..."
echo "基础 API:"
curl -s -o /dev/null -w "  Status: %{http_code}\n" https://app7626.acapp.acwing.com.cn/api/v1/events/

echo "Fusion API (需要认证，应该返回 401 而不是 404):"
curl -s -o /dev/null -w "  Status: %{http_code}\n" https://app7626.acapp.acwing.com.cn/api/v1/fusion/events/batch/
echo ""

echo "🎉 部署完成！"
echo ""
echo "📋 接下来："
echo "1. 通知 Roamio 团队（QQ: 2064747320）"
echo "2. 让他们重新测试'添加到 Ralendar'功能"
echo "3. 如果还有问题，查看日志: tail -f ~/kotlin_calendar/backend/logs/django.log"
echo ""

