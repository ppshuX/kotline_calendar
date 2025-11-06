# Day 09 开发日志 - Django 后端搭建

**日期**：____年____月____日

---

## 今天做了什么

- [ ] 创建 Django 项目
- [ ] 安装 Django REST Framework
- [ ] 设计 API 接口
- [ ] 实现日程 CRUD API
- [ ] 实现网络日历订阅 API
- [ ] 实现农历 API
- [ ] 部署到云服务器

---

## 写了哪些代码

### 1. 项目初始化

```bash
# 创建项目
django-admin startproject calendar_backend
cd calendar_backend

# 创建应用
python manage.py startapp api

# 安装依赖
pip install djangorestframework
pip install django-cors-headers
pip install python-lunar-calendar  # 农历库
```

---

### 2. Models（数据模型）

```python
# api/models.py
from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    """日程事件"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200, verbose_name='标题')
    description = models.TextField(blank=True, verbose_name='描述')
    date_time = models.DateTimeField(verbose_name='日期时间')
    reminder_minutes = models.IntegerField(default=0, verbose_name='提前提醒分钟数')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['date_time']
        verbose_name = '日程'
        verbose_name_plural = '日程列表'
    
    def __str__(self):
        return f"{self.title} - {self.date_time}"


class PublicCalendar(models.Model):
    """公开日历（用于订阅）"""
    name = models.CharField(max_length=100, verbose_name='日历名称')
    url_slug = models.SlugField(unique=True, verbose_name='URL标识')
    description = models.TextField(blank=True, verbose_name='描述')
    is_public = models.BooleanField(default=True, verbose_name='是否公开')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    events = models.ManyToManyField(Event, blank=True, related_name='calendars')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = '公开日历'
        verbose_name_plural = '公开日历列表'
    
    def __str__(self):
        return self.name
```

---

### 3. Serializers（序列化器）

```python
# api/serializers.py
from rest_framework import serializers
from .models import Event, PublicCalendar

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'date_time', 'reminder_minutes', 'created_at']
        read_only_fields = ['id', 'created_at']


class PublicCalendarSerializer(serializers.ModelSerializer):
    events_count = serializers.IntegerField(source='events.count', read_only=True)
    
    class Meta:
        model = PublicCalendar
        fields = ['id', 'name', 'url_slug', 'description', 'events_count', 'created_at']
```

---

### 4. Views（视图/API）

```python
# api/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Event, PublicCalendar
from .serializers import EventSerializer, PublicCalendarSerializer
import lunar  # 农历库

class EventViewSet(viewsets.ModelViewSet):
    """日程 CRUD API"""
    serializer_class = EventSerializer
    
    def get_queryset(self):
        # 只返回当前用户的日程
        return Event.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # 创建时自动关联当前用户
        serializer.save(user=self.request.user)


class PublicCalendarViewSet(viewsets.ReadOnlyModelViewSet):
    """公开日历 API（只读）"""
    queryset = PublicCalendar.objects.filter(is_public=True)
    serializer_class = PublicCalendarSerializer
    lookup_field = 'url_slug'
    
    @action(detail=True, methods=['get'])
    def feed(self, request, url_slug=None):
        """返回 iCalendar 格式的日历订阅"""
        calendar = self.get_object()
        ics_content = self.generate_ics(calendar)
        return Response(ics_content, content_type='text/calendar')
    
    def generate_ics(self, calendar):
        """生成 iCalendar 格式"""
        # TODO: 实现 iCalendar 格式生成
        return "BEGIN:VCALENDAR\nVERSION:2.0\nEND:VCALENDAR"


@api_view(['GET'])
def get_lunar_date(request):
    """农历 API"""
    date_str = request.GET.get('date')  # 格式：2025-11-05
    
    try:
        # 解析日期
        year, month, day = map(int, date_str.split('-'))
        
        # 转换为农历
        lunar_date = lunar.Lunar(year, month, day)
        
        return Response({
            'lunar_date': f"{lunar_date.lunarYear}年{lunar_date.lunarMonthCn}{lunar_date.lunarDayCn}",
            'year': lunar_date.lunarYear,
            'month': lunar_date.lunarMonthCn,
            'day': lunar_date.lunarDayCn,
            'zodiac': lunar_date.year_zodiac  # 生肖
        })
    except Exception as e:
        return Response({'error': str(e)}, status=400)
```

---

### 5. URLs（路由）

```python
# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('events', views.EventViewSet, basename='event')
router.register('calendars', views.PublicCalendarViewSet, basename='calendar')

urlpatterns = [
    path('', include(router.urls)),
    path('lunar/', views.get_lunar_date, name='lunar'),
]
```

```python
# calendar_backend/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api-auth/', include('rest_framework.urls')),
]
```

---

### 6. 部署配置

```bash
# 生成数据库
python manage.py makemigrations
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 运行服务器
python manage.py runserver 0.0.0.0:8000

# 生产环境部署
gunicorn calendar_backend.wsgi:application --bind 0.0.0.0:8000
```

---

## API 接口文档

### 日程管理

```
GET    /api/events/          # 获取所有日程
POST   /api/events/          # 创建日程
GET    /api/events/{id}/     # 获取单个日程
PUT    /api/events/{id}/     # 更新日程
DELETE /api/events/{id}/     # 删除日程
```

### 网络订阅

```
GET /api/calendars/                    # 获取公开日历列表
GET /api/calendars/{slug}/             # 获取单个日历详情
GET /api/calendars/{slug}/feed/        # 获取日历订阅（iCalendar）
```

### 农历

```
GET /api/lunar/?date=2025-11-05        # 获取农历日期
```

---

## 遇到的坑

**问题**：


**怎么解决的**：


---

**今天状态**：😊 顺利 / 😐 一般 / 😓 卡了好久

