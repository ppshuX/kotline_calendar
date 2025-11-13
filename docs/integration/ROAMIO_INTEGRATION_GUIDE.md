# 🤝 Roamio × Ralendar 对接指南

> **文档版本**: v2.0  
> **更新日期**: 2025-11-08  
> **对接方式**: 共享数据库方案（深度集成）  
> **Ralendar 团队**: ppshuX  
> **联系方式**: 2064747320@qq.com

---

## 🎯 对接方案确定

### ✅ **采用方案：共享 Roamio 数据库**

经过讨论，我们决定采用**深度集成方案**：
- ✅ Ralendar **直接使用** Roamio 的数据库（腾讯云）
- ✅ 共享 `auth_user` 表，实现账号完全统一
- ✅ 共享 `SECRET_KEY`，实现 Token 互认
- ✅ 使用 QQ UnionID 识别同一用户

### 优势

| 优势 | 说明 |
|------|------|
| 🔐 **账号完全统一** | 用户在 Roamio 和 Ralendar 是同一个账号 |
| 📧 **邮箱自动统一** | 邮箱信息在 `auth_user` 表中共享 |
| 🔑 **Token 互认** | 在 Roamio 登录后，直接可以访问 Ralendar |
| 🗄️ **数据零同步** | 不需要 API 调用同步，直接读写同一数据库 |
| ⚡ **性能最优** | 无需跨服务调用，直接数据库查询 |

---

## 📋 目录

1. [Ralendar 需要的信息](#ralendar-需要的信息)
2. [Roamio 需要提供的资源](#roamio-需要提供的资源)
3. [配置步骤](#配置步骤)
4. [数据库表结构](#数据库表结构)
5. [QQ UnionID 统一方案](#qq-unionid-统一方案)
6. [邮箱统一策略](#邮箱统一策略)
7. [测试验证](#测试验证)

---

## 🔑 Ralendar 需要的信息

### **必须提供（P0 - 紧急）**

| 信息项 | 说明 | 示例 | 用途 |
|--------|------|------|------|
| **数据库类型** | PostgreSQL/MySQL | `postgresql` | Django ENGINE 配置 |
| **DB_HOST** | 数据库服务器地址 | `rm-xxx.mysql.rds.aliyuncs.com` | 连接地址 |
| **DB_PORT** | 数据库端口 | `3306` (MySQL) 或 `5432` (PostgreSQL) | 连接端口 |
| **DB_NAME** | 数据库名称 | `roamio_production` | 数据库名 |
| **DB_USER** | 数据库用户名 | `roamio_user` | 连接用户 |
| **DB_PASSWORD** | 数据库密码 | `xxx` | 连接密码 |
| **SECRET_KEY** | Django 密钥 | `django-insecure-xxx` | JWT Token 互认 |

### **推荐提供（P1 - 重要）**

| 信息项 | 说明 | 用途 |
|--------|------|------|
| **QQ_UNIONID 开启状态** | 是否申请了 UnionID 权限 | 识别同一用户 |
| **Redis 配置** | 如果 Ralendar 也用同一个 Redis | Celery 和缓存 |
| **服务器 IP 白名单** | 数据库是否限制 IP | 需要添加 Ralendar 服务器 IP |

---

## 🎁 Roamio 需要提供的资源

### **1. 数据库访问权限**

#### 选项 A：创建 Ralendar 专用账号（推荐）

```sql
-- 在 Roamio 数据库中创建新用户
CREATE USER 'ralendar_user'@'47.121.137.60' IDENTIFIED BY 'ralendar_secure_password';

-- 授予必要权限
GRANT SELECT, INSERT, UPDATE, DELETE ON roamio_production.* TO 'ralendar_user'@'47.121.137.60';

-- 特别注意：需要访问 auth_user 表
GRANT ALL ON roamio_production.auth_user TO 'ralendar_user'@'47.121.137.60';
```

**提供给 Ralendar：**
```
DB_USER=ralendar_user
DB_PASSWORD=ralendar_secure_password
```

#### 选项 B：使用 Roamio 现有账号

直接提供 Roamio 当前使用的数据库账号密码。

---

### **2. SECRET_KEY 共享**

**从 Roamio 的 `settings.py` 中获取：**

```python
# roamio_backend/settings.py
SECRET_KEY = 'django-insecure-xxxxxx'  # 就是这个！
```

**提供给 Ralendar 团队，或者两边都改成相同的新 KEY。**

---

### **3. 腾讯云数据库白名单配置**

**在腾讯云控制台添加 Ralendar 服务器 IP：**

```
47.121.137.60  # Ralendar 服务器 IP（已迁移到阿里云）
```

**步骤：**
1. 登录腾讯云控制台
2. 进入云数据库 → 实例列表
3. 找到 Roamio 使用的数据库实例
4. 安全组/白名单 → 添加 IP：`47.121.137.60`

---

## ⚙️ 配置步骤

### **Ralendar 端配置（我们来做）**

#### 1. 更新 `backend/.env` 文件

```bash
# ==================== 数据库配置（使用 Roamio 数据库）====================
DB_ENGINE=postgresql  # 或 mysql
DB_HOST=rm-xxx.mysql.rds.aliyuncs.com  # Roamio 提供
DB_PORT=3306  # 或 5432
DB_NAME=roamio_production  # Roamio 提供
DB_USER=ralendar_user  # Roamio 提供
DB_PASSWORD=xxx  # Roamio 提供

# ==================== 共享密钥（与 Roamio 相同）====================
SECRET_KEY=roamio-的-SECRET_KEY

# ==================== Redis（可选：共用 Roamio 的 Redis）====================
REDIS_HOST=127.0.0.1  # 或 Roamio 的 Redis 地址
REDIS_PORT=6379
REDIS_PASSWORD=  # 如果有密码

# ==================== QQ OAuth ====================
QQ_APPID=102818448  # Ralendar 的
QQ_APPKEY=sZ0B7nDQP8Bzb1JP

# ==================== 邮件配置（共用 Roamio 的）====================
EMAIL_HOST=smtp.qq.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=2064747320@qq.com
EMAIL_HOST_PASSWORD=vnfmjisfmflqcdgf
DEFAULT_FROM_EMAIL=Ralendar <2064747320@qq.com>

# ==================== Celery ====================
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0
```

#### 2. 更新 `settings.py`

```python
# backend/calendar_backend/settings.py
DATABASES = {
    'default': {
        'ENGINE': f'django.db.backends.{os.environ.get("DB_ENGINE", "postgresql")}',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}

# 与 Roamio 共享 SECRET_KEY
SECRET_KEY = os.environ.get('SECRET_KEY')
```

#### 3. 运行数据库迁移

```bash
cd ~/kotlin_calendar/backend
python3 manage.py migrate
```

这会在 Roamio 的数据库中创建 Ralendar 需要的表：
- `api_event`
- `api_acwinguser`
- `api_qquser`
- `api_usermapping`
- ...

---

## 🔗 QQ UnionID 统一方案

### **问题：两个不同的 QQ_APPID**

```
Ralendar: 102818448
Roamio:   102813859
```

同一个 QQ 用户在两个应用中的 `openid` **不同**！

### **解决：使用 QQ UnionID**

#### Roamio 需要做的：

**1. 在 QQ 互联平台申请 UnionID 权限**
- 登录 https://connect.qq.com
- 两个应用都在同一个开发者账号下
- 申请"获取 UnionID"权限

**2. QQ 登录时获取 UnionID**

```python
# roamio_backend/views/auth.py (修改 QQ 登录逻辑)

# 在获取 OpenID 时，添加 unionid=1 参数
unionid_url = f"https://graph.qq.com/oauth2.0/me?access_token={access_token}&unionid=1"

# 返回结果会包含 unionid
{
  "client_id": "102813859",
  "openid": "B624064BA12345...",
  "unionid": "UID_123456789ABCDEF"  # ← 这个是关键！
}

# 保存 UnionID
qq_user.unionid = unionid
qq_user.save()
```

**3. 登录时优先通过 UnionID 查找用户**

```python
# 先尝试通过 UnionID 查找
user = User.objects.filter(qq_profile__unionid=unionid).first()

# 如果找到，说明用户已在 Ralendar 注册
# 直接登录，实现账号互通
```

---

## 📧 邮箱统一策略

### **当前情况**

从你提供的配置看：
```
Roamio 邮箱: 2064747320@qq.com (已配置)
Ralendar 邮箱: 将共用 Roamio 的配置
```

### **实施方案**

**1. 共享 `auth_user` 表后，邮箱自动统一** ✅

```sql
-- auth_user 表（Django 标准表）
CREATE TABLE auth_user (
    id INT PRIMARY KEY,
    username VARCHAR(150),
    email VARCHAR(254),  -- ← 邮箱字段共享
    ...
);
```

**2. QQ 登录时自动设置邮箱**

Ralendar 已实现（代码已推送）：
```python
# 登录时自动设置
user.email = f"{openid[:10]}@qq.com"
```

Roamio 也建议添加相同逻辑。

---

## 📝 Ralendar 需要 Roamio 提供的信息清单

### **数据库连接信息**

```bash
# 请 Roamio 团队提供以下信息：

# 1. 数据库类型
DATABASE_TYPE=postgresql  # 或 mysql

# 2. 腾讯云数据库连接信息
DB_HOST=rm-xxxxx.mysql.rds.tencentcdb.com
DB_PORT=3306  # MySQL 默认，或 5432 (PostgreSQL)
DB_NAME=roamio_production
DB_USER=roamio_user  # 或为 Ralendar 创建新用户
DB_PASSWORD=********

# 3. SSL/TLS 配置（如果有）
DB_SSL_ENABLED=True/False
```

### **Django 配置**

```bash
# 4. SECRET_KEY（必须相同！）
SECRET_KEY=roamio-的-django-secret-key

# 5. QQ OAuth UnionID
QQ_UNIONID_ENABLED=True/False  # 是否已申请 UnionID 权限
```

### **Redis 配置（可选）**

```bash
# 6. Redis 信息（Celery 使用）
REDIS_HOST=127.0.0.1  # 或腾讯云 Redis 地址
REDIS_PORT=6379
REDIS_PASSWORD=  # 如果有密码
```

### **服务器信息**

```bash
# 7. Roamio 服务器信息
ROAMIO_SERVER_IP=xxx.xxx.xxx.xxx
ROAMIO_DOMAIN=app7508.acapp.acwing.com.cn
```

---

## 🔧 Roamio 需要做的配置

### **1. 数据库白名单（必须）**

**在腾讯云控制台：**

1. 登录：https://console.cloud.tencent.com/cdb
2. 进入云数据库 MySQL/PostgreSQL
3. 找到 Roamio 使用的实例
4. 安全组设置 → 入站规则
5. **添加 Ralendar 服务器 IP：**
   ```
   47.121.137.60  (Ralendar 服务器，已迁移到阿里云)
   ```

---

### **2. 创建 Ralendar 数据库用户（推荐）**

**为安全考虑，建议为 Ralendar 创建独立账号：**

```sql
-- 连接到 Roamio 数据库
-- 创建 Ralendar 专用用户
CREATE USER 'ralendar'@'47.121.137.60' IDENTIFIED BY 'secure_password_here';

-- 授予必要权限
-- 需要读写 auth_user 表（用户表）
GRANT ALL ON roamio_production.auth_user TO 'ralendar'@'47.121.137.60';
GRANT ALL ON roamio_production.auth_permission TO 'ralendar'@'47.121.137.60';
GRANT ALL ON roamio_production.auth_group TO 'ralendar'@'47.121.137.60';
GRANT ALL ON roamio_production.django_session TO 'ralendar'@'47.121.137.60';

-- Ralendar 自己的表（可以完全控制）
GRANT ALL ON roamio_production.api_* TO 'ralendar'@'47.121.137.60';

-- 刷新权限
FLUSH PRIVILEGES;
```

**或者直接提供 Roamio 现有的数据库账号。**

---

### **3. 共享 SECRET_KEY（必须）**

**选择一个方案：**

#### 方案 A：两边都改成新的（推荐）

```python
# 生成一个新的强密钥
import secrets
new_secret = secrets.token_urlsafe(50)
print(new_secret)
# 输出类似：'xK8nP2mQ4vL9sR7tY6wZ3cV5bN1aM0hG...'

# Roamio settings.py
SECRET_KEY = 'xK8nP2mQ4vL9sR7tY6wZ3cV5bN1aM0hG...'

# Ralendar settings.py
SECRET_KEY = 'xK8nP2mQ4vL9sR7tY6wZ3cV5bN1aM0hG...'  # 相同！
```

#### 方案 B：Ralendar 使用 Roamio 的

```python
# Roamio 团队提供当前的 SECRET_KEY
# Ralendar 直接使用
```

---

### **4. QQ OAuth UnionID 权限（推荐）**

**在 QQ 互联平台：**

1. 登录：https://connect.qq.com
2. 确认两个应用在**同一个开发者账号**下：
   - Ralendar (AppID: 102818448)
   - Roamio (AppID: 102813859)
3. 申请"获取用户 UnionID"权限
4. 审核通过后，修改登录代码（见上面）

---

## 📊 数据库表结构

### **Ralendar 会创建的表（不影响 Roamio）**

```
api_event              # 日程事件表
api_acwinguser         # AcWing OAuth 用户
api_qquser             # QQ OAuth 用户
api_usermapping        # 用户映射表
api_publiccalendar     # 公共日历
django_celery_beat_*   # Celery 定时任务表
```

### **共享的 Django 标准表**

```
auth_user              # 用户表（共享！）
auth_permission        # 权限表（共享）
auth_group             # 用户组（共享）
django_session         # Session 表（共享）
django_content_type    # 内容类型（共享）
django_migrations      # 迁移记录（共享）
```

### **Roamio 现有的表（不受影响）**

```
roamio_trip            # 旅行表
roamio_photo           # 照片表
roamio_comment         # 评论表
...                    # 其他 Roamio 的表
```

**所有表可以和平共存！** ✅

---

## 🔐 认证流程

### **用户在 Roamio 登录**

```
1. 用户点击"QQ登录"
2. 获取 openid + unionid
3. 在 auth_user 表中查找用户（通过 unionid）
4. 如果用户已在 Ralendar 注册，直接登录（账号统一！）
5. 如果是新用户，创建账号
6. 生成 JWT Token（使用共享 SECRET_KEY）
```

### **用户访问 Ralendar**

```
1. 携带 Token 访问 Ralendar
2. Ralendar 验证 Token（使用共享 SECRET_KEY）
3. Token 有效 → 直接登录
4. 从共享的 auth_user 表读取用户信息
5. 显示用户的日程（来自 api_event 表）
```

**无缝切换！用户感觉不到是两个项目！** ✨

---

## 📧 邮箱统一实施

### **当前状态**

```
Roamio 邮件配置: 
  EMAIL_HOST_USER=2064747320@qq.com
  EMAIL_HOST_PASSWORD=vnfmjisfmflqcdgf
  
Ralendar 邮件配置:
  将使用相同的配置
```

### **实施方案**

**1. Ralendar 复用 Roamio 的邮件配置**

```python
# Ralendar .env
EMAIL_HOST=smtp.qq.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=2064747320@qq.com
EMAIL_HOST_PASSWORD=vnfmjisfmflqcdgf  # 与 Roamio 相同
DEFAULT_FROM_EMAIL=Ralendar <2064747320@qq.com>
```

**2. 发件人名称区分**

```
Roamio 发送邮件: Roamio <2064747320@qq.com>
Ralendar 发送邮件: Ralendar <2064747320@qq.com>
```

用户收到邮件时能区分来自哪个系统。

---

## 🧪 测试流程

### **测试 1：数据库连接**

```bash
# Ralendar 服务器上
cd ~/kotlin_calendar/backend
python3 manage.py shell
```

```python
from django.db import connection
connection.ensure_connection()
print("✅ 数据库连接成功！")

# 查看 Roamio 的用户
from django.contrib.auth.models import User
users = User.objects.all()
print(f"共有 {users.count()} 个用户")
for u in users[:5]:
    print(f"  - {u.username} ({u.email})")
exit()
```

### **测试 2：Token 互认**

```bash
# 1. 在 Roamio 登录，获取 Token
# 2. 用这个 Token 访问 Ralendar API
curl -H "Authorization: Bearer ROAMIO_TOKEN" \
  https://app7626.acapp.acwing.com.cn/api/v1/events/
  
# 应该返回 200，不是 401
```

### **测试 3：创建事件并提醒**

```python
# 在 Ralendar 创建事件
from api.models import Event
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

user = User.objects.first()  # Roamio 的用户
event = Event.objects.create(
    user=user,
    title='跨项目测试事件',
    start_time=timezone.now() + timedelta(minutes=12),
    email_reminder=True
)

print(f"✅ 事件已创建，将发送邮件到: {user.email}")
exit()
```

---

## 🚨 注意事项

### **1. 数据库迁移顺序**

```
⚠️ 重要：Ralendar 的迁移不会影响 Roamio 现有表
✅ Django 迁移是安全的，只创建不存在的表
❌ 不要运行 manage.py flush 或 manage.py reset_db
```

### **2. SECRET_KEY 修改影响**

```
⚠️ 修改 SECRET_KEY 后，所有现有的 Token 会失效
✅ 用户需要重新登录
📝 建议在非高峰时段修改
```

### **3. 备份**

```bash
# 修改前先备份数据库
mysqldump -h DB_HOST -u DB_USER -p DB_NAME > backup.sql
```

---

## 📞 需要 Roamio 团队协调确认

### **紧急需要（今天/明天）**

- [ ] 提供数据库连接信息（HOST, PORT, NAME, USER, PASSWORD）
- [ ] 提供当前的 SECRET_KEY
- [ ] 在腾讯云添加 Ralendar 服务器 IP 白名单

### **重要需要（本周）**

- [ ] 确认数据库类型（PostgreSQL/MySQL）
- [ ] 确认是否需要创建 Ralendar 专用账号
- [ ] 确认 QQ UnionID 权限状态

### **可选讨论（下周）**

- [ ] Redis 是否共用
- [ ] 邮件发送策略
- [ ] 双向数据同步需求

---

## 📋 对接时间表（更新）

### **Phase 1：基础配置（1-2天）**
- Day 1：Roamio 提供数据库信息
- Day 1：Ralendar 配置数据库连接
- Day 1：测试连接和迁移
- Day 2：验证用户表共享

### **Phase 2：功能测试（2-3天）**
- Day 3：测试 Token 互认
- Day 4：测试事件创建
- Day 5：测试邮件提醒

### **Phase 3：UnionID 统一（3-5天）**
- Day 6-7：申请 UnionID 权限
- Day 8-9：实现 UnionID 登录
- Day 10：全面测试

---

## 🎯 Ralendar 团队承诺

### **我们提供**

- ✅ 完整的 API 文档
- ✅ 邮件提醒系统（已实现并运行）
- ✅ 地图集成（已完成）
- ✅ Celery 异步任务系统
- ✅ 技术支持和协助

### **我们需要**

- 🔑 Roamio 数据库访问权限
- 🔑 SECRET_KEY 共享
- 🔑 腾讯云白名单配置

### **我们保证**

- ✅ 不修改 Roamio 现有表
- ✅ 不影响 Roamio 现有功能
- ✅ 数据库迁移安全可靠
- ✅ 提供完整的回滚方案

---

## 📞 联系方式

**Ralendar 开发团队**
- 负责人：ppshuX
- QQ/邮箱：2064747320@qq.com
- GitHub：https://github.com/ppshuX/Ralendar
- 服务器：app7626.acapp.acwing.com.cn

**期待与 Roamio 团队紧密合作！** 🤝

---

## 📝 待办事项

### Roamio 团队 TODO

- [ ] 阅读本对接指南
- [ ] 提供数据库连接信息
- [ ] 提供 SECRET_KEY
- [ ] 配置数据库白名单（添加 47.121.137.60）
- [ ] 确认 QQ UnionID 权限状态
- [ ] 确定对接开始时间

### Ralendar 团队 TODO

- [ ] 收到信息后，配置数据库连接
- [ ] 运行数据库迁移测试
- [ ] 验证 Token 互认
- [ ] 部署到生产环境
- [ ] 协助联调测试

---

**准备就绪！等待 Roamio 团队提供数据库信息！** 🚀

---

## ✅ Ralendar 已提供的能力

### 1. RESTful API 端点

#### 基础路径
```
生产环境: https://app7626.acapp.acwing.com.cn/api/v1/
开发环境: http://localhost:8000/api/v1/
```

#### 核心端点

| 方法 | 端点 | 功能 | 认证 |
|------|------|------|------|
| `POST` | `/events/` | 创建单个事件 | ✅ 需要 |
| `POST` | `/events/batch/` | 批量创建事件 | ✅ 需要 |
| `GET` | `/events/trip/{slug}/` | 获取旅行相关事件 | ✅ 需要 |
| `DELETE` | `/events/trip/{slug}/` | 删除旅行所有事件 | ✅ 需要 |
| `GET` | `/events/with-location/` | 获取有地理位置的事件 | ✅ 需要 |
| `GET` | `/events/from-roamio/` | 获取来自Roamio的事件 | ✅ 需要 |
| `POST` | `/auth/token/` | 获取 JWT Token | ❌ 不需要 |

---

### 2. 数据模型

#### Event 模型字段

```json
{
  "id": 1,
  "title": "抵达昆明",
  "description": "飞机 CA1234，提前2小时到达",
  "start_time": "2025-11-15T10:00:00+08:00",
  "end_time": "2025-11-15T12:00:00+08:00",
  "location": "昆明长水国际机场",
  
  // 地图信息
  "latitude": 25.1019,
  "longitude": 102.9292,
  "map_provider": "baidu",
  "map_url": "https://api.map.baidu.com/marker?...",
  "has_location": true,
  
  // 提醒配置
  "reminder_minutes": 120,
  "email_reminder": true,
  "notification_sent": false,
  
  // 来源追踪（重要！）
  "source_app": "roamio",
  "source_id": "activity_456",
  "related_trip_slug": "yunnan-trip-2025",
  
  // 系统字段
  "username": "张三",
  "created_at": "2025-11-08T14:00:00+08:00",
  "updated_at": "2025-11-08T14:00:00+08:00",
  "is_from_roamio": true
}
```

---

## 🔧 Roamio 需要做的改动

### 改动 1：旅行详情页添加"添加到日历"按钮

#### UI 设计建议

```vue
<!-- Roamio 旅行详情页 -->
<template>
  <div class="trip-detail">
    <h1>{{ trip.title }}</h1>
    
    <!-- 新增：同步到日历按钮 -->
    <el-button 
      type="primary" 
      @click="syncToCalendar"
      :loading="syncing"
    >
      <i class="bi bi-calendar-plus"></i>
      同步到 Ralendar 日历
    </el-button>
    
    <!-- 行程列表 -->
    <div v-for="day in itinerary" :key="day.date">
      <h3>{{ day.date }}</h3>
      
      <div v-for="activity in day.activities" :key="activity.id">
        <h4>{{ activity.title }}</h4>
        
        <!-- 新增：单个活动添加到日历 -->
        <el-button 
          size="small" 
          @click="addActivityToCalendar(activity)"
        >
          添加到日历
        </el-button>
      </div>
    </div>
  </div>
</template>
```

---

### 改动 2：实现 Ralendar API 调用

#### 创建 API 模块

**文件：`roamio_frontend/src/api/ralendar.js`**

```javascript
import axios from 'axios'

const RALENDAR_BASE_URL = 'https://app7626.acapp.acwing.com.cn/api/v1'

// 创建 axios 实例
const ralendar = axios.create({
  baseURL: RALENDAR_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器：添加认证 token
ralendar.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const ralendar = {
  /**
   * 批量创建事件（推荐）
   */
  async batchCreateEvents(tripSlug, tripTitle, activities) {
    const events = activities.map(activity => ({
      title: `${tripTitle} - ${activity.title}`,
      description: activity.description || '',
      start_time: `${activity.date}T${activity.time || '09:00'}:00+08:00`,
      location: activity.location || '',
      latitude: activity.latitude || null,
      longitude: activity.longitude || null,
      reminder_minutes: 120,  // 提前2小时
      email_reminder: true,   // 启用邮件提醒
    }))
    
    return await ralendar.post('/events/batch/', {
      source_app: 'roamio',
      source_id: tripSlug,
      related_trip_slug: tripSlug,
      events: events
    })
  },
  
  /**
   * 创建单个事件
   */
  async createEvent(eventData) {
    return await ralendar.post('/events/', {
      ...eventData,
      source_app: 'roamio'
    })
  },
  
  /**
   * 获取旅行相关的所有事件
   */
  async getTripEvents(tripSlug) {
    return await ralendar.get(`/events/trip/${tripSlug}/`)
  },
  
  /**
   * 删除旅行的所有事件
   */
  async deleteTripEvents(tripSlug) {
    return await ralendar.delete(`/events/trip/${tripSlug}/`)
  }
}

export default ralendar
```

---

### 改动 3：在旅行详情页中集成

**文件：`roamio_frontend/src/views/TripDetail.vue`**

```vue
<script setup>
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import ralendar from '@/api/ralendar'

const trip = ref(null)  // 当前旅行数据
const syncing = ref(false)

/**
 * 同步整个旅行到日历
 */
const syncToCalendar = async () => {
  try {
    // 1. 确认操作
    await ElMessageBox.confirm(
      `将 ${trip.value.itinerary.length} 天行程（共 ${getTotalActivities()} 个活动）同步到 Ralendar 日历？`,
      '同步确认',
      { type: 'info' }
    )
    
    syncing.value = true
    
    // 2. 提取所有活动
    const activities = []
    trip.value.itinerary.forEach(day => {
      day.activities.forEach(activity => {
        activities.push({
          ...activity,
          date: day.date
        })
      })
    })
    
    // 3. 调用 Ralendar API
    const response = await ralendar.batchCreateEvents(
      trip.value.slug,
      trip.value.title,
      activities
    )
    
    ElMessage.success(`✅ 成功同步 ${response.data.created_count} 个事件到日历`)
    
    // 4. 可选：在页面上显示同步状态
    trip.value.calendar_synced = true
    trip.value.calendar_sync_time = new Date()
    
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('同步失败：' + error.message)
    }
  } finally {
    syncing.value = false
  }
}

/**
 * 添加单个活动到日历
 */
const addActivityToCalendar = async (activity, dayDate) => {
  try {
    const response = await ralendar.createEvent({
      title: `${trip.value.title} - ${activity.title}`,
      description: activity.description || '',
      start_time: `${dayDate}T${activity.time || '09:00'}:00+08:00`,
      location: activity.location || '',
      latitude: activity.latitude || null,
      longitude: activity.longitude || null,
      reminder_minutes: 120,
      email_reminder: true,
      source_app: 'roamio',
      source_id: activity.id,
      related_trip_slug: trip.value.slug
    })
    
    ElMessage.success('✅ 已添加到日历')
    
    // 标记该活动已同步
    activity.calendar_synced = true
    
  } catch (error) {
    ElMessage.error('添加失败：' + error.message)
  }
}

const getTotalActivities = () => {
  return trip.value.itinerary.reduce((sum, day) => sum + day.activities.length, 0)
}
</script>
```

---

## 🔐 认证方案

### 方案 1：Token 传递（临时方案，快速实现）

#### Roamio 端实现

```javascript
// 用户在 Roamio 登录后，获取 access_token
const token = localStorage.getItem('access_token')

// 调用 Ralendar API 时，传递相同的 token
axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
```

**前提条件**：
- ✅ 两个项目使用同一个 `SECRET_KEY`
- ✅ 两个项目使用同一个数据库（或用户表同步）

#### Ralendar 端（无需改动）

已支持 JWT 认证，只要 token 有效即可。

---

### 方案 2：共享数据库（长期方案，强烈推荐）

#### 统一数据库配置

**两个项目的 `settings.py` 都改为：**

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'unified_ecosystem_db',  # 统一数据库名
        'USER': 'ecosystem_user',
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': 'your-db-server.com',  # 共享数据库服务器
        'PORT': '5432',
    }
}

# 统一 SECRET_KEY（重要！）
SECRET_KEY = os.environ.get('SHARED_SECRET_KEY', 'your-shared-secret-key')
```

#### 优点
- ✅ 用户数据完全统一
- ✅ Token 互认
- ✅ 不需要数据同步
- ✅ 用户在 Ralendar 和 Roamio 是同一个账号

#### 迁移步骤

1. **准备共享数据库**
   ```bash
   # 创建 PostgreSQL 数据库
   createdb unified_ecosystem_db
   ```

2. **导出现有数据**
   ```bash
   # Roamio
   python manage.py dumpdata > roamio_data.json
   
   # Ralendar
   python manage.py dumpdata > ralendar_data.json
   ```

3. **合并用户表（基于 QQ UnionID）**
   ```python
   # 数据迁移脚本（由我们协助完成）
   ```

4. **更新配置并测试**

---

## 🔗 Roamio 需要做的改动

### 改动清单（按优先级）

| 优先级 | 改动项 | 工作量 | 说明 |
|--------|--------|--------|------|
| 🔴 P0 | 添加"同步到日历"按钮 | 30分钟 | 在旅行详情页 |
| 🔴 P0 | 实现 Ralendar API 调用 | 1小时 | 创建 api 模块 |
| 🟡 P1 | 显示同步状态 | 30分钟 | 标记已同步的活动 |
| 🟡 P1 | 支持单个活动同步 | 30分钟 | 每个活动旁边加按钮 |
| 🟢 P2 | 双向同步 | 2小时 | Ralendar 改了也更新 Roamio |
| 🟢 P2 | 共享数据库迁移 | 4小时 | 长期方案 |

---

## 📝 详细改动说明

### 改动 1：添加"同步到日历"功能

#### 文件位置（参考）
```
roamio_frontend/
├── src/
│   ├── api/
│   │   └── ralendar.js          # 新增：Ralendar API 模块
│   ├── views/
│   │   └── TripDetail.vue       # 修改：添加同步按钮
│   └── components/
│       └── CalendarSyncButton.vue  # 新增（可选）：同步按钮组件
```

#### 示例代码

**1. 创建 API 模块**（见上面的 `ralendar.js`）

**2. 修改旅行详情页**（见上面的 `TripDetail.vue`）

**3. 添加同步状态显示**

```vue
<template>
  <!-- 显示同步状态 -->
  <el-tag v-if="trip.calendar_synced" type="success" size="small">
    <i class="bi bi-check-circle"></i>
    已同步到日历
  </el-tag>
  
  <!-- 显示同步时间 -->
  <span v-if="trip.calendar_sync_time" class="sync-time">
    最后同步：{{ formatTime(trip.calendar_sync_time) }}
  </span>
</template>
```

---

### 改动 2：处理跨域请求（CORS）

#### Roamio 前端配置

如果 Roamio 是单独的域名（如 `roamio.example.com`），需要：

**方式 A：前端代理（开发环境）**

```javascript
// vite.config.js 或 vue.config.js
export default {
  server: {
    proxy: {
      '/ralendar-api': {
        target: 'https://app7626.acapp.acwing.com.cn',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/ralendar-api/, '/api/v1')
      }
    }
  }
}
```

**方式 B：直接调用（生产环境）**

Ralendar 的 CORS 已配置，支持跨域请求，可以直接调用。

---

### 改动 3：认证 Token 传递

#### 场景 A：用户先登录 Roamio

```javascript
// 用户在 Roamio 登录后
const token = loginResponse.data.access_token

// 存储到 localStorage
localStorage.setItem('access_token', token)

// 后续调用 Ralendar API 时，会自动携带这个 token
// （前提：两个项目共享 SECRET_KEY）
```

#### 场景 B：用户未登录 Roamio，但登录了 Ralendar

```javascript
// 跳转到 Ralendar 登录页
window.location.href = 'https://app7626.acapp.acwing.com.cn/login?redirect=roamio'

// 登录成功后，Ralendar 重定向回 Roamio 并传递 token
// http://roamio.example.com/callback?token=xxx
```

---

## 📡 API 调用示例

### 示例 1：批量同步旅行行程

#### 请求

```javascript
POST https://app7626.acapp.acwing.com.cn/api/v1/events/batch/

Headers:
{
  "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGc...",
  "Content-Type": "application/json"
}

Body:
{
  "source_app": "roamio",
  "source_id": "trip_123",
  "related_trip_slug": "yunnan-trip-2025",
  "events": [
    {
      "title": "抵达昆明",
      "description": "飞机 CA1234",
      "start_time": "2025-11-15T10:00:00+08:00",
      "end_time": "2025-11-15T12:00:00+08:00",
      "location": "昆明长水国际机场",
      "latitude": 25.1019,
      "longitude": 102.9292,
      "reminder_minutes": 120,
      "email_reminder": true
    },
    {
      "title": "游览石林",
      "start_time": "2025-11-15T14:00:00+08:00",
      "location": "石林风景区",
      "latitude": 24.8138,
      "longitude": 103.2891,
      "reminder_minutes": 30,
      "email_reminder": true
    }
  ]
}
```

#### 响应

```json
{
  "success": true,
  "created_count": 2,
  "skipped_count": 0,
  "events": [
    {
      "id": 101,
      "title": "抵达昆明",
      "start_time": "2025-11-15T10:00:00+08:00",
      "map_url": "https://api.map.baidu.com/marker?...",
      "is_from_roamio": true
    },
    {
      "id": 102,
      "title": "游览石林",
      ...
    }
  ]
}
```

---

### 示例 2：查询已同步的事件

#### 请求

```javascript
GET https://app7626.acapp.acwing.com.cn/api/v1/events/trip/yunnan-trip-2025/

Headers:
{
  "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### 响应

```json
{
  "count": 2,
  "trip_slug": "yunnan-trip-2025",
  "events": [
    {
      "id": 101,
      "title": "抵达昆明",
      "source_app": "roamio",
      "notification_sent": true,
      ...
    }
  ]
}
```

---

### 示例 3：删除旅行的所有事件

#### 请求

```javascript
DELETE https://app7626.acapp.acwing.com.cn/api/v1/events/trip/yunnan-trip-2025/

Headers:
{
  "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### 响应

```json
{
  "success": true,
  "deleted_count": 2
}
```

---

## 🔐 认证统一方案

### 推荐方案：共享数据库 + QQ UnionID

#### 实现步骤

**步骤 1：两个项目共享数据库**

```python
# Ralendar settings.py
# Roamio settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'unified_ecosystem_db',
        'USER': 'ecosystem_user',
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': 'shared-db-host',
        'PORT': '5432',
    }
}
```

**步骤 2：统一 SECRET_KEY**

```python
# 两个项目使用同一个
SECRET_KEY = os.environ.get('SHARED_SECRET_KEY')
```

**步骤 3：QQ OAuth 获取 UnionID**

```python
# QQ 登录时，额外请求 UnionID
unionid_url = f"https://graph.qq.com/oauth2.0/me?access_token={access_token}&unionid=1"

# 保存到数据库
qq_user.unionid = unionid
qq_user.save()
```

**步骤 4：用户匹配逻辑**

```python
# 在任一项目登录时，根据 UnionID 查找用户
user = User.objects.filter(qq_profile__unionid=unionid).first()

# 如果找到，说明用户已在另一个项目注册
# 直接登录，实现账号互通
```

---

## 📧 邮箱统一方案

### 问题：两个项目的用户邮箱可能不一致

#### 解决方案

**1. QQ 登录时自动设置邮箱**（Ralendar 已实现 ✅）

```python
# QQ 登录时
user.email = f"{openid[:10]}@qq.com"  # 默认格式
user.save()
```

**2. Roamio 同步用户邮箱**

```python
# Roamio 也实现相同逻辑
# 或者：从 Ralendar 获取用户邮箱
ralendar_user = get_ralendar_user_by_unionid(unionid)
if ralendar_user and ralendar_user.email:
    current_user.email = ralendar_user.email
    current_user.save()
```

**3. 用户在任一平台修改邮箱，自动同步**

```python
# User 模型添加 signal
from django.db.models.signals import post_save

@receiver(post_save, sender=User)
def sync_email_across_apps(sender, instance, **kwargs):
    if instance.email:
        # 如果两个项目共享数据库，自动同步
        # 如果分离，通过 API 同步
        pass
```

---

## 🧪 测试流程

### 测试环境准备

**1. Roamio 团队需要：**
- Ralendar 测试账号（或使用自己的 QQ 登录）
- Ralendar API 文档（本文档）
- Ralendar 的 `access_token`（用于测试）

**2. 测试步骤**

#### Step 1：获取测试 Token

```bash
# 在 Ralendar 登录后
# 打开浏览器开发者工具（F12）
# Application → Local Storage → access_token

# 或者通过 API 获取：
POST https://app7626.acapp.acwing.com.cn/api/auth/token/
{
  "username": "test_user",
  "password": "test_password"
}
```

#### Step 2：测试单个事件创建

```bash
curl -X POST https://app7626.acapp.acwing.com.cn/api/v1/events/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Roamio 测试事件",
    "start_time": "2025-11-10T15:00:00+08:00",
    "location": "测试地点",
    "source_app": "roamio",
    "source_id": "test_001",
    "email_reminder": true
  }'
```

#### Step 3：验证事件已创建

访问 Ralendar 日历页面，应该能看到刚创建的事件。

---

## 🚀 部署清单

### Roamio 端需要部署的文件

```
roamio_frontend/
├── src/
│   ├── api/
│   │   └── ralendar.js          # 新增
│   └── views/
│       └── TripDetail.vue       # 修改
├── .env                         # 更新：添加 RALENDAR_API_URL
└── package.json                 # 无需修改
```

### 环境变量

**Roamio 的 `.env` 文件添加：**

```bash
# Ralendar API 配置
RALENDAR_API_URL=https://app7626.acapp.acwing.com.cn/api/v1

# 如果共享数据库
SHARED_SECRET_KEY=your-shared-secret-key
DB_HOST=shared-db-host
DB_NAME=unified_ecosystem_db
DB_USER=ecosystem_user
DB_PASSWORD=your-db-password
```

---

## 📞 协调事项

### 需要 Ralendar 团队提供

- ✅ API 文档（本文档）
- ✅ 测试账号和 Token
- ✅ CORS 配置（已完成）
- ⏳ 共享数据库服务器信息（如果采用方案2）

### 需要 Roamio 团队确认

- ❓ 选择哪种认证方案？（Token 传递 vs 共享数据库）
- ❓ 是否需要双向同步？（Ralendar 改了通知 Roamio）
- ❓ 用户邮箱如何统一？
- ❓ 预计何时开始对接？

---

## 🎨 UI/UX 建议

### Roamio 旅行详情页

```
┌────────────────────────────────────────────┐
│  云南之旅 2025                              │
│  2025-11-15 至 2025-11-20                  │
│                                            │
│  [📅 同步到日历] [✏️ 编辑] [🗑️ 删除]       │
│                                            │
│  第 1 天 (11月15日)                         │
│  ├─ 10:00 抵达昆明 [✅ 已同步]              │
│  │  📍 昆明长水国际机场                     │
│  │  [➕ 添加到日历]                         │
│  │                                         │
│  ├─ 14:00 游览石林 [➕ 添加到日历]          │
│  └─ 18:00 品尝过桥米线                      │
│                                            │
│  第 2 天 (11月16日)                         │
│  ...                                       │
└────────────────────────────────────────────┘
```

---

## 🐛 常见问题

### Q1: Token 认证失败 401

**原因**：
- SECRET_KEY 不一致
- Token 过期
- 用户不存在

**解决**：
1. 确认两个项目的 SECRET_KEY 相同
2. 刷新 token
3. 检查数据库中用户是否存在

---

### Q2: 创建事件失败 400

**原因**：
- 数据格式不正确
- 必填字段缺失

**检查**：
- `title`: 必填
- `start_time`: 必填，格式为 ISO 8601
- `latitude` 和 `longitude` 必须同时存在或同时为空

---

### Q3: 邮件提醒未发送

**原因**：
- 用户没有设置邮箱
- `email_reminder` 为 false
- Celery 服务未运行

**解决**：
1. 确保用户邮箱已设置
2. 创建事件时 `email_reminder: true`
3. 联系 Ralendar 团队确认 Celery 服务状态

---

## 📅 对接时间表（建议）

### Week 1: API 调用测试
- Day 1-2: Roamio 实现 API 调用模块
- Day 3-4: 测试单个事件创建
- Day 5: 测试批量创建

### Week 2: UI 集成
- Day 1-2: 添加同步按钮
- Day 3-4: 实现同步逻辑
- Day 5: UI/UX 优化

### Week 3: 认证统一
- Day 1-2: 讨论方案（Token 或共享数据库）
- Day 3-4: 实施统一认证
- Day 5: 测试跨项目登录

### Week 4: 上线部署
- Day 1-2: 联调测试
- Day 3-4: 修复问题
- Day 5: 正式上线

---

## 📖 参考资源

### Ralendar 相关

- **生产地址**：https://app7626.acapp.acwing.com.cn
- **API Base URL**：https://app7626.acapp.acwing.com.cn/api/v1
- **GitHub**：https://github.com/ppshuX/Ralendar
- **联系方式**：2064747320@qq.com

### API 测试工具

- **Postman**：导入 API 文档进行测试
- **curl**：命令行快速测试
- **浏览器开发者工具**：查看网络请求

---

## ✅ 检查清单

### Ralendar 团队（已完成）

- ✅ API 端点开发
- ✅ CORS 配置
- ✅ JWT 认证
- ✅ 邮件提醒功能
- ✅ 地图集成
- ✅ 数据模型扩展

### Roamio 团队（待完成）

- [ ] 阅读本文档
- [ ] 创建 ralendar.js API 模块
- [ ] 在旅行详情页添加同步按钮
- [ ] 测试 API 调用
- [ ] 确定认证方案（Token 或共享数据库）
- [ ] 统一邮箱策略
- [ ] 联调测试

---

## 📞 联系我们

如有任何问题，请联系：

- **Ralendar 开发者**：ppshuX
- **QQ/邮箱**：2064747320@qq.com
- **GitHub**：https://github.com/ppshuX

我们随时准备协助对接！🤝

---

**期待与 Roamio 团队的合作！** 🚀✨

