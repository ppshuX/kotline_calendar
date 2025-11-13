# 🔍 Roamio 对接需求分析

> **分析日期**: 2025-11-08  
> **文档版本**: Roamio Integration Guide v1.0  
> **结论**: ✅ **基本满足，需要少量调整**

---

## 📊 需求对比总览

| 需求类别 | Roamio 要求 | Ralendar 现状 | 状态 | 工作量 |
|---------|------------|--------------|------|--------|
| **API 端点** | `/api/v1/events/` | `/api/events/` | ⚠️ 需调整 | 5 分钟 |
| **数据模型** | location/reminder 对象 | 独立字段 | ⚠️ 需调整 | 30 分钟 |
| **认证系统** | 共享数据库 + SECRET_KEY | 独立 SQLite | ⚠️ 需协调 | 1 小时 |
| **邮件提醒** | Celery 异步任务 | 未实现 | ❌ 缺失 | 2-3 小时 |
| **CORS 配置** | 允许 Roamio 域名 | 部分支持 | ⚠️ 需添加 | 5 分钟 |
| **地图集成** | Baidu Maps | 已支持 | ✅ 完全满足 | 0 |
| **错误处理** | 详细错误信息 | 基本支持 | ✅ 满足 | 0 |

**总体评估**: 🟡 **70% 满足，30% 需要调整**

---

## ✅ 已满足的需求

### 1. 数据模型基础字段 ✅

**他们要求的字段我们都有**：

| 字段 | Roamio 要求 | Ralendar 现状 | 状态 |
|------|------------|--------------|------|
| `title` | ✅ | ✅ `title` | ✅ 完全一致 |
| `description` | ✅ | ✅ `description` | ✅ 完全一致 |
| `start_time` | ✅ | ✅ `start_time` | ✅ 完全一致 |
| `end_time` | ✅ | ✅ `end_time` | ✅ 完全一致 |
| `latitude` | ✅ | ✅ `latitude` | ✅ 完全一致 |
| `longitude` | ✅ | ✅ `longitude` | ✅ 完全一致 |
| `source_app` | ✅ | ✅ `source_app` | ✅ 完全一致 |
| `source_event_id` | ✅ | ✅ `source_id` | ✅ 名称略不同 |
| `reminder_sent` | ✅ | ✅ `notification_sent` | ✅ 名称略不同 |

### 2. 地图集成 ✅

我们已经完整支持：
- ✅ `latitude`, `longitude` 字段
- ✅ `map_provider` 字段（baidu/amap/tencent）
- ✅ `map_url` 属性方法（自动生成导航链接）

### 3. 基础 API 端点 ✅

我们已经实现：
- ✅ `GET /api/events/` - 获取事件列表
- ✅ `POST /api/events/` - 创建事件
- ✅ `GET /api/events/{id}/` - 获取单个事件
- ✅ `PATCH /api/events/{id}/` - 更新事件
- ✅ `DELETE /api/events/{id}/` - 删除事件

### 4. JWT 认证 ✅

我们已经实现：
- ✅ `rest_framework_simplejwt` 
- ✅ Access Token + Refresh Token
- ✅ Bearer Token 认证

---

## ⚠️ 需要调整的部分

### 1. API 路径版本化 ⚠️

**他们的要求**：
```
POST /api/v1/events/
```

**我们现在**：
```
POST /api/events/
```

**解决方案（5 分钟）**：
```python
# backend/calendar_backend/urls.py

urlpatterns = [
    path('api/', include('api.urls')),           # 保留旧版本
    path('api/v1/', include('api.urls')),        # 添加 v1 版本
]
```

---

### 2. 响应格式调整 ⚠️

**他们期望的 location 格式**：
```json
{
  "location": {
    "name": "Eiffel Tower",
    "address": "Champ de Mars...",
    "latitude": 48.8584,
    "longitude": 2.2945
  }
}
```

**我们现在**：
```json
{
  "location": "Eiffel Tower",
  "latitude": 48.8584,
  "longitude": 2.2945
}
```

**解决方案（30 分钟）**：
```python
# backend/api/serializers.py

class EventSerializer(serializers.ModelSerializer):
    location_obj = serializers.SerializerMethodField()
    reminder_obj = serializers.SerializerMethodField()
    
    def get_location_obj(self, obj):
        if obj.latitude and obj.longitude:
            return {
                "name": obj.location,
                "address": obj.location,  # 如果有单独的地址字段可以用
                "latitude": obj.latitude,
                "longitude": obj.longitude
            }
        return None
    
    def get_reminder_obj(self, obj):
        return {
            "enabled": obj.email_reminder,
            "minutes_before": obj.reminder_minutes,
            "sent": obj.notification_sent
        }
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 
            'start_time', 'end_time',
            'location_obj',  # 嵌套对象格式
            'reminder_obj',  # 嵌套对象格式
            'source_app', 'source_id',
            # ... 其他字段
        ]
```

---

### 3. 认证系统整合 ⚠️

**他们的要求**：
- 共享 PostgreSQL 数据库
- 相同的 SECRET_KEY

**我们现在**：
- SQLite 数据库（独立）
- 不同的 SECRET_KEY

**解决方案 A：共享数据库（推荐）** ⭐⭐⭐⭐⭐

```python
# settings.py (Ralendar)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'roamio_db',  # 与 Roamio 共享
        'USER': 'roamio_user',
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# 使用相同的 SECRET_KEY
SECRET_KEY = os.environ.get('SHARED_SECRET_KEY', 'your-shared-secret-key')
```

**优势**：
- ✅ 一个账号，两个产品
- ✅ JWT Token 互通
- ✅ 无需用户映射表

**解决方案 B：保持独立，API 互调（备选）** ⭐⭐⭐

保持各自的数据库，通过 API 验证 Token：
```python
# Ralendar 调用 Roamio API 验证 Token
response = requests.get(
    'https://roamio.cn/api/auth/verify-token/',
    headers={'Authorization': f'Bearer {token}'}
)
```

---

### 4. 邮件提醒功能 ❌

**他们的要求**：
- Celery 异步任务队列
- 定时发送邮件提醒

**我们现在**：
- ❌ 没有 Celery
- ❌ 没有邮件发送功能

**解决方案（2-3 小时）**：

**Step 1: 安装依赖**
```bash
pip install celery redis django-celery-beat
```

**Step 2: 配置 Celery**
```python
# backend/calendar_backend/celery.py

from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calendar_backend.settings')

app = Celery('calendar_backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

**Step 3: 实现提醒任务**
```python
# backend/api/tasks.py

from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from .models import Event

@shared_task
def send_event_reminder(event_id):
    event = Event.objects.get(id=event_id)
    
    if event.notification_sent:
        return
    
    send_mail(
        subject=f'📅 提醒：{event.title}',
        message=f'您的日程 {event.title} 将在 {event.reminder_minutes} 分钟后开始',
        from_email='noreply@ralendar.com',
        recipient_list=[event.user.email],
    )
    
    event.notification_sent = True
    event.save()
```

**Step 4: 在创建事件时调度任务**
```python
from datetime import timedelta
from .tasks import send_event_reminder

def create(self, request):
    event = Event.objects.create(...)
    
    if event.email_reminder:
        reminder_time = event.start_time - timedelta(minutes=event.reminder_minutes)
        send_event_reminder.apply_async((event.id,), eta=reminder_time)
    
    return Response(...)
```

---

### 5. CORS 配置 ⚠️

**需要添加 Roamio 域名**：

```python
# settings.py

CORS_ALLOWED_ORIGINS = [
    'https://app7626.acapp.acwing.com.cn',  # Ralendar
    'https://www.acwing.com',
    'https://roamio.cn',  # 🆕 Roamio 生产环境（已迁移）
    'http://localhost:8080',                 # 🆕 Roamio 开发环境
    'http://localhost:5173',                 # Ralendar 开发
]
```

---

## 📋 需要完成的任务清单

### 🔴 高优先级（必须完成）

- [ ] **数据库迁移** - 从 SQLite 迁移到 PostgreSQL（与 Roamio 共享）
- [ ] **SECRET_KEY 统一** - 协调使用相同的密钥
- [ ] **实现 Celery** - 邮件提醒功能
- [ ] **配置邮件服务** - SMTP 设置

### 🟡 中优先级（建议完成）

- [ ] **API 版本化** - 添加 `/api/v1/` 路由
- [ ] **Serializer 调整** - location 和 reminder 嵌套格式
- [ ] **CORS 配置** - 添加 Roamio 域名
- [ ] **错误处理优化** - 返回更详细的错误信息

### 🟢 低优先级（可选）

- [ ] **API 文档** - 生成 Swagger/OpenAPI 文档
- [ ] **监控日志** - 添加集成调用日志
- [ ] **性能优化** - 批量创建事件接口优化

---

## 🎯 快速适配方案

### 方案 A：最小调整（推荐）⭐⭐⭐⭐⭐

**工作量**: 3-4 小时  
**难度**: 中等

**调整清单**：
1. ✅ 添加 `/api/v1/` 路由别名（5 分钟）
2. ✅ Serializer 添加嵌套格式字段（30 分钟）
3. ✅ CORS 添加 Roamio 域名（5 分钟）
4. ✅ 实现简单的邮件提醒（不用 Celery，用 Django 内置）（1 小时）
5. ⚠️ 协调 SECRET_KEY（需要 Roamio 团队配合）

**优势**：
- 快速上线
- 无需大规模重构
- 保持系统独立性

### 方案 B：完全对接（理想）⭐⭐⭐⭐⭐

**工作量**: 1-2 天  
**难度**: 高

**调整清单**：
1. 迁移到 PostgreSQL
2. 统一 SECRET_KEY
3. 实现完整的 Celery 任务队列
4. 配置 Redis
5. 数据库迁移脚本

**优势**：
- 完全符合要求
- 长期可维护
- 功能完整

---

## 💡 我的建议

### 立即可以开始对接（快速方案）

即使不做任何调整，**我们现在就可以支持 70% 的功能**：

#### ✅ 现在就能用的功能

1. **创建事件** ✅
   ```python
   # Roamio 调用
   response = requests.post(
       'https://app7626.acapp.acwing.com.cn/api/events/',  # Ralendar API地址保持不变
       headers={'Authorization': f'Bearer {token}'},
       json={
           'title': 'Visit Eiffel Tower',
           'start_time': '2025-12-25T18:00:00Z',
           'location': 'Eiffel Tower',
           'latitude': 48.8584,
           'longitude': 2.2945,
           'source_app': 'roamio',
           'source_id': '456'
       }
   )
   ```
   
2. **更新/删除事件** ✅
   ```python
   # 完全支持 PATCH 和 DELETE
   ```

3. **地图导航** ✅
   ```python
   # 我们的 map_url 属性可以直接用
   event.map_url  # 自动生成百度地图链接
   ```

#### ⚠️ 需要调整的功能

1. **嵌套的 location 格式**
   ```json
   // 他们期望
   {"location": {"name": "...", "latitude": 48.8584}}
   
   // 我们现在返回
   {"location": "...", "latitude": 48.8584}
   
   // 解决：添加一个 location_detail 字段
   ```

2. **邮件提醒**
   - 暂时可以不实现
   - 或者先实现简单版本（不用 Celery）

---

## 🔧 快速适配代码

### 1. 添加 v1 API 路由（5 分钟）

```python
# backend/calendar_backend/urls.py

from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),      # 保留旧版本
    path('api/v1/', include('api.urls')),   # 🆕 添加 v1 版本（相同路由）
]
```

### 2. 扩展 Serializer（30 分钟）

```python
# backend/api/serializers.py

class EventSerializer(serializers.ModelSerializer):
    # 保留原有字段
    # ... 
    
    # 🆕 添加 Roamio 兼容格式
    location_detail = serializers.SerializerMethodField()
    reminder_detail = serializers.SerializerMethodField()
    
    def get_location_detail(self, obj):
        """返回嵌套的 location 对象（Roamio 格式）"""
        if obj.has_location:
            return {
                "name": obj.location,
                "address": obj.location,
                "latitude": float(obj.latitude),
                "longitude": float(obj.longitude)
            }
        return None
    
    def get_reminder_detail(self, obj):
        """返回嵌套的 reminder 对象（Roamio 格式）"""
        return {
            "enabled": obj.email_reminder,
            "minutes_before": obj.reminder_minutes,
            "sent": obj.notification_sent
        }
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description',
            'start_time', 'end_time',
            # 原有格式（保持兼容）
            'location', 'latitude', 'longitude',
            'reminder_minutes', 'email_reminder',
            # 🆕 Roamio 兼容格式
            'location_detail',
            'reminder_detail',
            # 其他字段
            'source_app', 'source_id', 'map_url',
        ]
```

### 3. 添加 CORS 域名（5 分钟）

```python
# settings.py

CORS_ALLOWED_ORIGINS = [
    'https://app7626.acapp.acwing.com.cn',
    'https://www.acwing.com',
    'https://roamio.cn',  # 🆕 Roamio（已迁移）
    'http://localhost:8080',                 # 🆕 Roamio 开发
    'http://localhost:5173',
]
```

### 4. 简单邮件提醒（1 小时，不用 Celery）

```python
# backend/api/views/events.py

from django.core.mail import send_mail
from threading import Timer

class EventViewSet(viewsets.ModelViewSet):
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        event = Event.objects.get(id=response.data['id'])
        
        # 🆕 如果需要邮件提醒，调度任务
        if event.email_reminder and event.user.email:
            self.schedule_reminder(event)
        
        return response
    
    def schedule_reminder(self, event):
        """简单的提醒调度（不用 Celery）"""
        from datetime import datetime, timedelta
        
        reminder_time = event.start_time - timedelta(minutes=event.reminder_minutes)
        delay_seconds = (reminder_time - datetime.now()).total_seconds()
        
        if delay_seconds > 0:
            # 使用 Timer 延迟执行
            timer = Timer(delay_seconds, self.send_reminder_email, [event])
            timer.daemon = True
            timer.start()
    
    def send_reminder_email(self, event):
        """发送提醒邮件"""
        try:
            send_mail(
                subject=f'📅 提醒：{event.title}',
                message=f'您的日程 "{event.title}" 将在 {event.reminder_minutes} 分钟后开始。',
                from_email='noreply@ralendar.com',
                recipient_list=[event.user.email],
                fail_silently=True,
            )
            event.notification_sent = True
            event.save()
        except Exception as e:
            print(f"邮件发送失败: {e}")
```

---

## 📝 给 Roamio 团队的反馈

### ✅ 我们已经满足的

1. ✅ **数据模型完整** - 所有必需字段都有
2. ✅ **JWT 认证** - 完全支持 Bearer Token
3. ✅ **RESTful API** - 标准的增删改查
4. ✅ **地图集成** - Baidu Maps 已集成
5. ✅ **CORS 支持** - 可以添加你们的域名

### ⚠️ 需要协调的

1. **数据库** - 建议使用共享 PostgreSQL
2. **SECRET_KEY** - 需要统一（非常重要！）
3. **API 版本** - 我们添加 /api/v1/ 即可

### ❌ 需要实现的

1. **Celery 异步任务** - 可以先用简单方案
2. **邮件配置** - 需要 SMTP 设置

---

## 🚀 快速上线计划（半天）

### 上午（2 小时）

1. ✅ 添加 `/api/v1/` 路由（5 分钟）
2. ✅ 扩展 Serializer 兼容格式（30 分钟）
3. ✅ CORS 添加 Roamio 域名（5 分钟）
4. ✅ 实现简单邮件提醒（1 小时）

### 下午（2 小时）

5. ⚠️ 与 Roamio 协调 SECRET_KEY（30 分钟沟通）
6. ⚠️ 讨论数据库方案（30 分钟）
7. ✅ 测试 API 对接（30 分钟）
8. ✅ 编写对接文档（30 分钟）

**总工作量**: 4 小时

**完成后**: 可以立即开始对接！

---

## 💬 我的评估

### 📊 满足度评分

```
总体满足度: 70/100

├─ 数据模型:    90/100 ✅ (只需微调格式)
├─ API 端点:    85/100 ✅ (添加版本号)
├─ 认证系统:    60/100 ⚠️ (需要协调)
├─ 邮件提醒:    30/100 ❌ (需要实现)
└─ 其他功能:    95/100 ✅ (地图、CORS等)
```

### 🎯 结论

**可以对接！** 但建议：

1. **短期方案**（本周完成）：
   - 添加 v1 路由
   - 调整 Serializer 格式
   - 实现简单邮件提醒
   - 先不用 Celery

2. **长期方案**（下周完成）：
   - 迁移到 PostgreSQL
   - 统一 SECRET_KEY
   - 实现完整的 Celery
   - 生产级邮件队列

**建议先用短期方案快速上线，后续再优化！**

---

## 📞 需要与 Roamio 团队沟通的问题

1. **SECRET_KEY 如何统一？**
   - 他们提供给我们？
   - 还是我们协商一个新的？

2. **数据库共享方案？**
   - 他们的数据库信息？
   - 还是我们单独运行，API 互调？

3. **邮件服务器？**
   - 使用谁的 SMTP 服务？
   - 发件人地址是什么？

4. **测试环境？**
   - 开发环境 API 地址？
   - 测试账号？

---

**准备好回复 Roamio 团队了吗？我可以帮你起草回复邮件！** 📧
