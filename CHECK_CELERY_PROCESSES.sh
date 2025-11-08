#!/bin/bash

# ====================================
# 🔍 检查 Celery 进程状态
# ====================================

echo "======================================"
echo "🔍 Celery 进程诊断"
echo "======================================"
echo ""

echo "===== 1. 检查 Celery Worker 进程数量 ====="
echo ""
WORKER_COUNT=$(ps aux | grep 'celery worker' | grep -v grep | wc -l)
echo "🔍 Celery Worker 进程数: $WORKER_COUNT"

if [ $WORKER_COUNT -gt 1 ]; then
    echo "⚠️ 警告：发现多个 Worker 进程！这会导致邮件重复发送！"
    echo ""
    ps aux | grep 'celery worker' | grep -v grep
else
    echo "✅ Worker 进程数量正常"
fi
echo ""

echo "===== 2. 检查 Celery Beat 进程数量 ====="
echo ""
BEAT_COUNT=$(ps aux | grep 'celery beat' | grep -v grep | wc -l)
echo "🔍 Celery Beat 进程数: $BEAT_COUNT"

if [ $BEAT_COUNT -gt 1 ]; then
    echo "⚠️ 警告：发现多个 Beat 进程！这会导致任务重复调度！"
    echo ""
    ps aux | grep 'celery beat' | grep -v grep
else
    echo "✅ Beat 进程数量正常"
fi
echo ""

echo "===== 3. 检查 Celery Worker 并发设置 ====="
echo ""
echo "默认情况下，Celery Worker 会启动多个子进程处理任务。"
echo "如果是单核服务器或任务较少，建议使用 --concurrency=1"
echo ""

echo "===== 4. 检查最近的日志（查找重复执行） ====="
echo ""
cd ~/kotlin_calendar/backend

if [ -f "logs/celery_worker.log" ]; then
    echo "🔍 最近 30 行 Worker 日志："
    tail -n 30 logs/celery_worker.log | grep -E "(发送提醒|send_event_reminder_email|notification_sent)"
else
    echo "❌ 找不到 logs/celery_worker.log"
fi
echo ""

echo "======================================"
echo "💡 修复方案"
echo "======================================"
echo ""

if [ $WORKER_COUNT -gt 1 ] || [ $BEAT_COUNT -gt 1 ]; then
    echo "🔧 发现多个进程，建议执行以下命令修复："
    echo ""
    echo "   # 1. 停止所有 Celery 进程"
    echo "   sudo pkill -9 -f celery"
    echo ""
    echo "   # 2. 等待 2 秒"
    echo "   sleep 2"
    echo ""
    echo "   # 3. 重新启动（单进程模式）"
    echo "   cd ~/kotlin_calendar/backend"
    echo "   nohup python3 -m celery -A calendar_backend worker --concurrency=1 --loglevel=info > logs/celery_worker.log 2>&1 &"
    echo "   nohup python3 -m celery -A calendar_backend beat --loglevel=info > logs/celery_beat.log 2>&1 &"
    echo ""
else
    echo "✅ 进程数量正常，可能是其他原因导致重复。"
    echo ""
    echo "🔧 建议："
    echo "   1. 检查事件的 notification_sent 字段是否正确更新"
    echo "   2. 查看 Celery 日志，确认是否有任务重试"
    echo "   3. 考虑使用 --concurrency=1 限制并发"
fi

echo ""
echo "======================================"

