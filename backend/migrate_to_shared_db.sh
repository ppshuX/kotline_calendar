#!/bin/bash
# Ralendar 迁移到共享数据库脚本

echo "=========================================="
echo "🔄 Ralendar 迁移到 Roamio 共享数据库"
echo "=========================================="
echo ""

# 1. 安装 MySQL 驱动
echo "📦 步骤 1: 安装 MySQL 驱动..."
pip3 install --user mysqlclient

if [ $? -ne 0 ]; then
    echo "❌ MySQL 驱动安装失败！"
    echo "可能需要先安装系统依赖："
    echo "  Ubuntu/Debian: sudo apt install libmysqlclient-dev python3-dev"
    echo "  CentOS/RHEL: sudo yum install mysql-devel python3-devel"
    exit 1
fi

echo "✅ MySQL 驱动安装成功"
echo ""

# 2. 备份 SQLite 数据
echo "💾 步骤 2: 备份当前数据..."
if [ -f "db.sqlite3" ]; then
    timestamp=$(date +%Y%m%d_%H%M%S)
    cp db.sqlite3 "db.sqlite3.backup_${timestamp}"
    echo "✅ SQLite 数据已备份到: db.sqlite3.backup_${timestamp}"
else
    echo "⚠️  未找到 SQLite 数据库文件，跳过备份"
fi
echo ""

# 3. 复制配置文件
echo "⚙️  步骤 3: 配置环境变量..."
if [ ! -f ".env" ]; then
    echo "⚠️  未找到 .env 文件"
    read -p "是否从示例文件创建？(y/n): " create_env
    if [ "$create_env" = "y" ]; then
        cp .env.shared_db.example .env
        echo "✅ .env 文件已创建，请编辑并填写实际值"
        echo "⚠️  特别注意：SECRET_KEY 必须与 Roamio 相同！"
        read -p "按 Enter 继续..."
    else
        echo "❌ 需要 .env 文件才能继续"
        exit 1
    fi
fi
echo ""

# 4. 测试数据库连接
echo "🔍 步骤 4: 测试数据库连接..."
python3 manage.py check --database default

if [ $? -ne 0 ]; then
    echo "❌ 数据库连接测试失败！"
    echo "请检查 .env 中的数据库配置"
    exit 1
fi

echo "✅ 数据库连接成功"
echo ""

# 5. 运行迁移
echo "🗄️  步骤 5: 运行数据库迁移..."
echo "这会在 Roamio 数据库中创建 Ralendar 需要的表"
echo ""
read -p "确认继续？(y/n): " confirm_migrate

if [ "$confirm_migrate" != "y" ]; then
    echo "❌ 迁移已取消"
    exit 1
fi

python3 manage.py migrate

if [ $? -ne 0 ]; then
    echo "❌ 数据库迁移失败！"
    exit 1
fi

echo "✅ 数据库迁移成功"
echo ""

# 6. 验证表结构
echo "✅ 步骤 6: 验证数据库表..."
python3 manage.py shell << EOF
from django.db import connection
cursor = connection.cursor()
cursor.execute("SHOW TABLES")
tables = cursor.fetchall()
print(f"数据库中共有 {len(tables)} 个表")
print("\nRalendar 的表:")
for table in tables:
    if 'api_' in table[0] or 'celery' in table[0]:
        print(f"  ✅ {table[0]}")
print("\n共享的表:")
for table in tables:
    if table[0].startswith('auth_') or table[0].startswith('django_'):
        print(f"  🔗 {table[0]}")
EOF

echo ""
echo "=========================================="
echo "✅ 迁移完成！"
echo "=========================================="
echo ""
echo "📝 下一步："
echo "1. 重启 uwsgi: sudo pkill -f uwsgi && uwsgi --ini scripts/uwsgi.ini"
echo "2. 重启 nginx: sudo /etc/init.d/nginx restart"
echo "3. 测试登录和功能"
echo ""
echo "🔗 现在 Ralendar 和 Roamio 已共享数据库！"
echo "   - 用户账号完全统一"
echo "   - Token 可以互认"
echo "   - 邮箱自动同步"
echo ""

