#!/bin/bash

# ====================================
# 🚀 部署邮件提醒修复
# ====================================

echo "======================================"
echo "🚀 部署邮件提醒修复"
echo "======================================"
echo ""

cd ~/kotlin_calendar

echo "===== 1. 拉取最新代码 ====="
git pull
echo ""

echo "===== 2. 重启 Celery 服务 ====="
cd backend

# 停止旧进程（使用 -9 强制终止，确保完全停止）
echo "停止旧的 Celery 进程..."
sudo pkill -9 -f 'celery worker'
sudo pkill -9 -f 'celery beat'
sleep 3

# 再次检查是否还有残留进程
if ps aux | grep -v grep | grep 'celery' > /dev/null; then
    echo "⚠️ 发现残留进程，再次清理..."
    sudo pkill -9 -f celery
    sleep 2
fi

# 创建日志目录
mkdir -p logs

# 启动新进程（使用 --concurrency=1 确保单进程，避免重复发送）
echo "启动 Celery Worker (单进程模式)..."
nohup python3 -m celery -A calendar_backend worker --concurrency=1 --loglevel=info > logs/celery_worker.log 2>&1 &
WORKER_PID=$!

echo "启动 Celery Beat..."
nohup python3 -m celery -A calendar_backend beat --loglevel=info > logs/celery_beat.log 2>&1 &
BEAT_PID=$!

sleep 2

echo ""
echo "===== 3. 验证服务状态 ====="
if ps -p $WORKER_PID > /dev/null; then
    echo "✅ Celery Worker 正在运行 (PID: $WORKER_PID)"
else
    echo "❌ Celery Worker 启动失败"
fi

if ps -p $BEAT_PID > /dev/null; then
    echo "✅ Celery Beat 正在运行 (PID: $BEAT_PID)"
else
    echo "❌ Celery Beat 启动失败"
fi

echo ""
echo "======================================"
echo "🎉 部署完成"
echo "======================================"
echo ""
echo "✅ 修复内容："
echo "   1. 邮件提醒现在会严格按照你设置的时间发送"
echo "      - 设置提前1分钟 → 提前1分钟发送"
echo "      - 设置提前5分钟 → 提前5分钟发送"
echo ""
echo "   2. 发件人显示为 'Ralendar <2064747320@qq.com>'"
echo "      而不是 '2064747320@qq.com'"
echo ""
echo "💡 测试方法："
echo "   1. 创建一个5分钟后的事件，设置提前1分钟提醒"
echo "   2. 等待4分钟，不应该收到邮件"
echo "   3. 再等1分钟（事件前1分钟），应该收到邮件"
echo "   4. 检查邮件发件人是否显示为 'Ralendar'"
echo ""
echo "📝 查看实时日志："
echo "   tail -f ~/kotlin_calendar/backend/logs/celery_worker.log"
echo ""
echo "======================================"

