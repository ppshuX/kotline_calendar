# 📧 邮件提醒功能快速部署

## ⚡ 快速开始（5 分钟）

### 1. 安装 Redis

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis

# 验证
redis-cli ping  # 应该返回 PONG
```

### 2. 安装 Python 依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 配置环境变量

创建 `backend/.env` 文件（如果不存在）：

```bash
# Gmail 配置（推荐）
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password  # ⚠️ 需要生成应用专用密码
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Celery/Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# 提醒设置
REMINDER_ADVANCE_MINUTES=15  # 提前15分钟提醒
```

**⚠️ Gmail 应用专用密码获取：**
1. https://myaccount.google.com/security
2. 开启"两步验证"
3. 搜索"应用专用密码" → 生成新密码
4. 将 16 位密码填入配置

### 4. 数据库迁移

```bash
python manage.py migrate
```

### 5. 启动服务

**开发环境（3 个终端）：**

```bash
# 终端 1: Django
python manage.py runserver 0.0.0.0:8000

# 终端 2: Celery Worker
celery -A calendar_backend worker --loglevel=info

# 终端 3: Celery Beat
celery -A calendar_backend beat --loglevel=info
```

**生产环境（推荐使用 Supervisor）：**
详见 `docs/EMAIL_REMINDER_GUIDE.md`

---

## ✅ 快速测试

```bash
python manage.py shell
```

```python
from api.tasks import send_event_reminder_email
from api.models import Event
from datetime import timedelta
from django.utils import timezone

# 创建测试事件
event = Event.objects.create(
    user_id=1,  # 替换为实际用户ID
    title="测试提醒",
    start_time=timezone.now() + timedelta(minutes=10),
    end_time=timezone.now() + timedelta(hours=1),
    email_reminder=True,
    notification_sent=False
)

# 发送测试邮件
send_event_reminder_email.delay(event.id)
```

查看 Celery Worker 输出，应该看到：
```
✅ 成功发送提醒邮件：测试提醒 -> user@example.com
```

---

## 📊 监控

查看日志：
```bash
# Celery Worker 输出
celery -A calendar_backend worker --loglevel=info

# Celery Beat 输出
celery -A calendar_backend beat --loglevel=info
```

查看任务执行情况：
```bash
python manage.py shell
>>> from django_celery_beat.models import PeriodicTask
>>> PeriodicTask.objects.all()
```

---

## 🐛 常见问题

**Q: 收不到邮件？**
- 检查用户邮箱已设置
- 检查 `email_reminder=True`
- 检查 `notification_sent=False`
- 检查邮件配置正确

**Q: Celery Worker 启动失败？**
- 检查 Redis 是否运行：`redis-cli ping`
- 检查配置：`CELERY_BROKER_URL`

**Q: 权限错误？**
- 检查 Redis 连接权限
- 检查日志目录可写

---

详细文档：`docs/EMAIL_REMINDER_GUIDE.md`

