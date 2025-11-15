#!/bin/bash
# 查找 Ralendar 日志文件

echo "=========================================="
echo "🔍 查找 Ralendar 日志文件"
echo "=========================================="
echo ""

# 1. 检查 Gunicorn 日志
echo "1️⃣ 检查 Gunicorn 日志："
if [ -f "/var/log/gunicorn/error.log" ]; then
    echo "✅ 找到: /var/log/gunicorn/error.log"
    ls -lh /var/log/gunicorn/error.log
else
    echo "❌ 未找到: /var/log/gunicorn/error.log"
    echo "   尝试查找其他位置..."
    find /var/log -name "*gunicorn*" -o -name "*ralendar*" 2>/dev/null | head -5
fi
echo ""

# 2. 检查 Nginx 日志
echo "2️⃣ 检查 Nginx 日志："
if [ -f "/var/log/nginx/access.log" ]; then
    echo "✅ 找到: /var/log/nginx/access.log"
    ls -lh /var/log/nginx/access.log
fi
if [ -f "/var/log/nginx/error.log" ]; then
    echo "✅ 找到: /var/log/nginx/error.log"
    ls -lh /var/log/nginx/error.log
fi
echo ""

# 3. 检查项目目录下的 logs/ 目录
echo "3️⃣ 检查项目 logs/ 目录："
PROJECT_DIRS=(
    "$HOME/ralendar"
    "$HOME/kotlin_calendar"
    "/home/acs/ralendar"
    "/home/acs/kotlin_calendar"
)

for dir in "${PROJECT_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "   检查: $dir"
        if [ -d "$dir/backend/logs" ]; then
            echo "   ✅ 找到: $dir/backend/logs"
            ls -lh "$dir/backend/logs/" 2>/dev/null
        fi
    fi
done
echo ""

# 4. 检查 systemd 服务日志
echo "4️⃣ 检查 systemd 服务日志："
if systemctl is-active --quiet gunicorn; then
    echo "✅ Gunicorn 服务正在运行"
    echo "   查看日志: sudo journalctl -u gunicorn -f"
elif systemctl is-active --quiet ralendar; then
    echo "✅ Ralendar 服务正在运行"
    echo "   查看日志: sudo journalctl -u ralendar -f"
else
    echo "   检查服务状态..."
    systemctl list-units --type=service | grep -E "gunicorn|ralendar|uwsgi" || echo "   未找到相关服务"
fi
echo ""

# 5. 检查 supervisor 日志
echo "5️⃣ 检查 supervisor 日志："
if command -v supervisorctl &> /dev/null; then
    if [ -d "/etc/supervisor/conf.d" ]; then
        echo "✅ Supervisor 已安装"
        echo "   配置文件目录: /etc/supervisor/conf.d"
        echo "   查看服务: sudo supervisorctl status"
        echo "   查看日志: sudo supervisorctl tail -f ralendar"
    fi
fi
echo ""

# 6. 检查 uwsgi 日志（如果使用）
echo "6️⃣ 检查 uwsgi 日志："
if [ -d "/var/log/uwsgi" ]; then
    echo "✅ 找到 uwsgi 日志目录"
    ls -lh /var/log/uwsgi/ 2>/dev/null | head -5
fi
echo ""

echo "=========================================="
echo "📝 推荐的日志查看命令："
echo "=========================================="
echo ""
echo "如果使用 Gunicorn:"
echo "  sudo tail -f /var/log/gunicorn/error.log | grep -E 'OAuth|redirect'"
echo ""
echo "如果使用 systemd:"
echo "  sudo journalctl -u gunicorn -f | grep -E 'OAuth|redirect'"
echo ""
echo "如果使用 supervisor:"
echo "  sudo supervisorctl tail -f ralendar | grep -E 'OAuth|redirect'"
echo ""
echo "查看 Nginx 访问日志（包含 OAuth 请求）:"
echo "  sudo tail -f /var/log/nginx/access.log | grep oauth"
echo ""
echo "查看 Nginx 错误日志:"
echo "  sudo tail -f /var/log/nginx/error.log"
echo ""

