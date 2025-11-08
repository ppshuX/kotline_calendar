#!/bin/bash
# ==================== Ralendar QQ UnionID 部署脚本 ====================
# 使用方法：复制下面的命令到服务器执行
# ==============================================================================

# 1. SSH 登录服务器
# ssh acs@app7626.acapp.acwing.com.cn

# 2. 拉取最新代码
cd ~/kotlin_calendar
git pull

# 3. 检查代码是否更新成功
echo "==> 检查最新提交："
git log -1 --oneline
# 应该看到：feat: add QQ UnionID support...

# 4. 进入后端目录
cd backend

# 5. 执行数据库迁移
echo "==> 执行数据库迁移..."
python manage.py migrate

# 6. 验证迁移
echo "==> 验证 unionid 字段..."
python manage.py dbshell << EOF
DESCRIBE api_qquser;
EOF

# 7. 重启 uWSGI
echo "==> 重启 uWSGI..."
pkill -f uwsgi
sleep 2
uwsgi --ini uwsgi.ini &

# 8. 重启 Celery（如果在运行）
echo "==> 重启 Celery..."
pkill -f celery
sleep 2
./start_celery.sh

# 9. 检查服务状态
echo "==> 检查服务状态..."
sleep 3
ps aux | grep uwsgi | grep -v grep
ps aux | grep celery | grep -v grep

# 10. 测试 API
echo "==> 测试健康检查..."
curl -s https://app7626.acapp.acwing.com.cn/api/v1/ | head -n 5

echo ""
echo "==> 部署完成！"
echo ""
echo "下一步："
echo "1. 用 QQ 登录测试：https://app7626.acapp.acwing.com.cn/login"
echo "2. 查看日志：tail -f ~/kotlin_calendar/backend/logs/django.log"
echo "3. 应该看到：[QQ Login] OpenID: xxx..., UnionID: yyy..."
echo ""

