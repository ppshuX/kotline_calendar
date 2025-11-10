# 🗄️ Ralendar 独立数据库设置指南

> **目标**: 在腾讯云服务器上创建 Ralendar 独立 MySQL 数据库

---

## 📋 操作步骤

### **第一步：SSH 连接服务器**

```bash
ssh acs@app7626.acapp.acwing.com.cn
```

---

### **第二步：创建 MySQL 数据库和用户**

```bash
# 1. 登录 MySQL（使用 root 用户）
mysql -u root -p
```

**在 MySQL 中执行：**

```sql
-- 1. 创建 Ralendar 独立数据库
CREATE DATABASE ralendar_production 
  DEFAULT CHARACTER SET utf8mb4 
  DEFAULT COLLATE utf8mb4_unicode_ci;

-- 2. 创建 Ralendar 专用用户
CREATE USER 'ralendar_user'@'localhost' IDENTIFIED BY 'YOUR_STRONG_PASSWORD_HERE';

-- 3. 授予权限（仅限 ralendar_production 数据库）
GRANT ALL PRIVILEGES ON ralendar_production.* TO 'ralendar_user'@'localhost';

-- 4. 刷新权限
FLUSH PRIVILEGES;

-- 5. 验证数据库和用户
SHOW DATABASES;
SELECT User, Host FROM mysql.user WHERE User = 'ralendar_user';

-- 6. 退出 MySQL
EXIT;
```

**生成强密码（推荐）：**

```bash
# 生成 32 位随机密码
openssl rand -base64 32
```

**示例密码：**
```
KZp8y3mN9LqX2wR5tH7vB4cD6fG8hJ0k
```

**⚠️ 请保存好密码，后面需要用到！**

---

### **第三步：测试数据库连接**

```bash
# 使用刚创建的用户登录
mysql -u ralendar_user -p ralendar_production

# 输入刚才设置的密码
```

**在 MySQL 中执行：**

```sql
-- 查看当前数据库
SELECT DATABASE();

-- 查看表（应该为空）
SHOW TABLES;

-- 退出
EXIT;
```

✅ **如果能成功登录，说明数据库创建成功！**

---

### **第四步：更新 .env 文件**

```bash
# 编辑环境变量文件
cd ~/kotlin_calendar/backend
vim .env
```

**添加/修改以下内容：**

```bash
# ==================== Django Config ====================
DEBUG=False
SECRET_KEY=django-insecure-#6avwo7=$9vse4txxj!phdfx5-ql(bc5otpoiw@x)u0i+^1-5h
ENVIRONMENT=production  # ← 新增：启用生产环境（MySQL）

# ==================== Database Config ====================
DB_NAME=ralendar_production  # ← 新增
DB_USER=ralendar_user        # ← 新增
DB_PASSWORD=YOUR_PASSWORD_HERE  # ← 替换为第二步设置的密码
DB_HOST=localhost            # ← 新增
DB_PORT=3306                 # ← 新增

# ... 其他配置保持不变 ...
```

**保存并退出：**
```
:wq
```

---

### **第五步：运行数据库迁移**

```bash
cd ~/kotlin_calendar/backend

# 1. 激活虚拟环境（如果有）
source venv/bin/activate  # 或者你的虚拟环境路径

# 2. 生成迁移文件
python3 manage.py makemigrations

# 你应该看到类似输出：
# Migrations for 'api':
#   api/migrations/0009_holiday_lunarcalendar_dailyfortune_userfortune_datasynclog.py
#     - Create model Holiday
#     - Create model LunarCalendar
#     - Create model DailyFortune
#     - Create model UserFortune
#     - Create model DataSyncLog

# 3. 执行迁移
python3 manage.py migrate

# 你应该看到类似输出：
# Running migrations:
#   Applying api.0009_holiday_lunarcalendar_dailyfortune_userfortune_datasynclog... OK
```

---

### **第六步：验证数据表**

```bash
# 登录 MySQL
mysql -u ralendar_user -p ralendar_production
```

**在 MySQL 中执行：**

```sql
-- 查看所有表
SHOW TABLES;

-- 你应该看到类似输出：
-- +-------------------------------------+
-- | Tables_in_ralendar_production       |
-- +-------------------------------------+
-- | api_event                           |
-- | auth_user                           |
-- | allauth_socialaccount               |
-- | calendar_holidays                   |  ← 新表
-- | calendar_lunar_calendars            |  ← 新表
-- | calendar_fortunes                   |  ← 新表
-- | calendar_user_fortunes              |  ← 新表
-- | calendar_data_sync_logs             |  ← 新表
-- | ... 其他表 ...                      |
-- +-------------------------------------+

-- 查看节假日表结构
DESCRIBE calendar_holidays;

-- 退出
EXIT;
```

✅ **如果看到新表，说明迁移成功！**

---

### **第七步：重启服务**

```bash
# 1. 重启 uWSGI
pkill -HUP uwsgi

# 2. 重启 Celery
pkill -f "celery -A calendar_backend"
cd ~/kotlin_calendar/backend
bash start_celery.sh
```

---

### **第八步：测试 API**

```bash
# 测试节假日 API
curl https://app7626.acapp.acwing.com.cn/api/v1/holidays/today/

# 预期输出（目前数据库为空）：
# {
#   "date": "2025-11-10",
#   "holiday": null,
#   "traditional_festivals": [],
#   "international_festivals": []
# }
```

✅ **如果 API 正常返回（即使是空数据），说明一切配置正确！**

---

## 📊 数据迁移（可选）

### **如果你之前在 roamio_production 有数据，需要迁移**

```bash
# 1. 导出旧数据
mysqldump -u root -p roamio_production \
  api_event \
  auth_user \
  allauth_socialaccount \
  > /tmp/ralendar_backup.sql

# 2. 导入到新数据库
mysql -u ralendar_user -p ralendar_production < /tmp/ralendar_backup.sql

# 3. 删除备份文件
rm /tmp/ralendar_backup.sql
```

---

## 🔍 故障排查

### **问题 1：Migration 失败**

**错误信息：**
```
django.db.utils.OperationalError: (1045, "Access denied for user 'ralendar_user'@'localhost'")
```

**解决方案：**
1. 检查 `.env` 文件中的 `DB_PASSWORD` 是否正确
2. 确认 MySQL 用户权限：
   ```sql
   SHOW GRANTS FOR 'ralendar_user'@'localhost';
   ```

---

### **问题 2：表已存在**

**错误信息：**
```
django.db.utils.ProgrammingError: (1050, "Table 'calendar_holidays' already exists")
```

**解决方案：**
1. 删除旧表：
   ```sql
   DROP TABLE IF EXISTS calendar_holidays;
   DROP TABLE IF EXISTS calendar_lunar_calendars;
   DROP TABLE IF EXISTS calendar_fortunes;
   DROP TABLE IF EXISTS calendar_user_fortunes;
   DROP TABLE IF EXISTS calendar_data_sync_logs;
   ```
2. 重新运行 `python3 manage.py migrate`

---

### **问题 3：无法连接 MySQL**

**错误信息：**
```
django.db.utils.OperationalError: (2002, "Can't connect to local MySQL server through socket")
```

**解决方案：**
1. 检查 MySQL 是否运行：
   ```bash
   sudo systemctl status mysql
   ```
2. 如果没有运行，启动它：
   ```bash
   sudo systemctl start mysql
   ```

---

## ✅ 验证清单

完成后，请确认：

- [ ] MySQL 数据库 `ralendar_production` 已创建
- [ ] MySQL 用户 `ralendar_user` 已创建并授权
- [ ] `.env` 文件已更新（`ENVIRONMENT=production` 和数据库配置）
- [ ] 数据库迁移成功（`python3 manage.py migrate`）
- [ ] 新表已创建（`calendar_*` 表）
- [ ] uWSGI 和 Celery 已重启
- [ ] API 测试正常

---

## 📝 后续步骤

1. **导入节假日数据**
   - 参考：`docs/database/CALENDAR_DATA_MODELS.md`
   - 运行数据同步任务

2. **配置数据自动更新**
   - Celery Beat 定时任务
   - 每年自动更新节假日数据

3. **开发黄历和运势功能**
   - API 端点
   - 前端 UI

---

## 📞 联系方式

**遇到问题？**
- 在项目根目录创建 Issue
- 或联系核心团队

---

**🎉 恭喜！Ralendar 独立数据库已配置完成！**

