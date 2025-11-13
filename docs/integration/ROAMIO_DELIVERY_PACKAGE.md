# 📦 Ralendar × Roamio 集成交付包

**交付时间**: 2025-11-08  
**Ralendar 版本**: v1.0  
**状态**: ✅ 已准备就绪

---

## 🎯 快速导航

| 文档 | 用途 | 优先级 |
|------|------|--------|
| [5分钟快速开始](#-5分钟快速开始) | 最快上手方式 | ⭐⭐⭐⭐⭐ |
| [API 端点清单](#-api-端点清单) | 所有可用接口 | ⭐⭐⭐⭐⭐ |
| [前端集成代码](#-前端集成示例vue-3) | Vue 组件示例 | ⭐⭐⭐⭐ |
| [后端集成代码](#-后端集成示例django) | Django API 调用 | ⭐⭐⭐⭐ |
| [测试环境](#-测试环境) | 测试账号和 Token | ⭐⭐⭐⭐ |
| [常见问题](#-常见问题) | 疑难解答 | ⭐⭐⭐ |

---

## ⚡ 5分钟快速开始

### 步骤 1: 获取配置信息

**Ralendar API 基础 URL**:
```
https://app7626.acapp.acwing.com.cn/api/v1
```

**认证方式**: JWT Token（与 Roamio 共享）
- 使用用户登录后获取的 `access_token`
- 请求头: `Authorization: Bearer {access_token}`

**共享 SECRET_KEY**（重要！）:
```python
SECRET_KEY = 'django-insecure-#6avwo7=$9vse4txxj!phdfx5-ql(bc5otpoiw@x)u0i+^1-5h'
```
> ⚠️ **必须在两个项目中使用相同的 SECRET_KEY，否则 Token 无法互认！**

### 步骤 2: 测试 API 连接

```bash
# 使用测试 Token 调用 API
curl -X GET \
  https://app7626.acapp.acwing.com.cn/api/v1/events/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 步骤 3: 创建第一个事件

```bash
curl -X POST \
  https://app7626.acapp.acwing.com.cn/api/v1/events/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试事件（来自 Roamio）",
    "start_time": "2025-11-20T10:00:00+08:00",
    "end_time": "2025-11-20T12:00:00+08:00",
    "source_app": "roamio",
    "related_trip_slug": "test-trip-123"
  }'
```

---

## 📡 API 端点清单

### 1️⃣ 批量创建事件（推荐）

**用途**: 一次性为旅行计划创建多个日程事件

```
POST /api/v1/fusion/events/batch/
```

**请求头**:
```
Authorization: Bearer {user_access_token}
Content-Type: application/json
```

**请求体**:
```json
{
  "source_app": "roamio",
  "related_trip_slug": "yunnan-trip-2025",
  "events": [
    {
      "title": "抵达昆明",
      "description": "航班 CA1234",
      "start_time": "2025-11-15T10:00:00+08:00",
      "end_time": "2025-11-15T12:00:00+08:00",
      "location": "昆明长水国际机场",
      "latitude": 25.1019,
      "longitude": 102.9292,
      "reminder_minutes": 120,
      "email_reminder": true
    },
    {
      "title": "入住酒店",
      "start_time": "2025-11-15T14:00:00+08:00",
      "end_time": "2025-11-15T15:00:00+08:00",
      "location": "昆明希尔顿酒店"
    }
  ]
}
```

**响应示例**:
```json
{
  "success": true,
  "created_count": 2,
  "skipped_count": 0,
  "events": [
    {
      "id": 123,
      "title": "抵达昆明",
      "start_time": "2025-11-15T10:00:00+08:00",
      "end_time": "2025-11-15T12:00:00+08:00",
      "source_app": "roamio",
      "related_trip_slug": "yunnan-trip-2025",
      "created_at": "2025-11-08T23:00:00Z"
    },
    ...
  ]
}
```

---

### 2️⃣ 创建单个事件

```
POST /api/v1/events/
```

**请求体**:
```json
{
  "title": "参观石林",
  "description": "世界自然遗产",
  "start_time": "2025-11-16T09:00:00+08:00",
  "end_time": "2025-11-16T17:00:00+08:00",
  "location": "石林风景区",
  "latitude": 24.8122,
  "longitude": 103.2838,
  "reminder_minutes": 60,
  "email_reminder": false,
  "source_app": "roamio",
  "related_trip_slug": "yunnan-trip-2025"
}
```

---

### 3️⃣ 获取旅行计划的所有事件

```
GET /api/v1/fusion/events/trip/{trip_slug}/
```

**示例**:
```bash
GET /api/v1/fusion/events/trip/yunnan-trip-2025/
```

**响应**:
```json
{
  "count": 8,
  "trip_slug": "yunnan-trip-2025",
  "events": [...]
}
```

---

### 4️⃣ 删除旅行计划的所有事件

```
DELETE /api/v1/fusion/events/trip/{trip_slug}/
```

**响应**:
```json
{
  "success": true,
  "deleted_count": 8,
  "trip_slug": "yunnan-trip-2025"
}
```

---

### 5️⃣ 更新单个事件

```
PUT /api/v1/events/{event_id}/
PATCH /api/v1/events/{event_id}/
```

---

### 6️⃣ 删除单个事件

```
DELETE /api/v1/events/{event_id}/
```

---

### 7️⃣ 获取有位置信息的事件（地图展示用）

```
GET /api/v1/fusion/events/with-location/
```

---

## 🎨 前端集成示例（Vue 3）

### 方案 A: 在旅行详情页添加"添加到日历"按钮

```vue
<template>
  <div class="trip-detail">
    <!-- 旅行信息 -->
    <div class="trip-header">
      <h1>{{ trip.title }}</h1>
      <p>{{ trip.destination }} · {{ trip.days }} 天</p>
    </div>
    
    <!-- 添加到日历按钮 -->
    <el-button 
      type="primary" 
      icon="Calendar"
      @click="addToCalendar"
      :loading="adding"
    >
      添加到 Ralendar
    </el-button>
    
    <!-- 成功提示 -->
    <el-alert 
      v-if="addedCount > 0"
      type="success" 
      :closable="false"
      style="margin-top: 10px"
    >
      ✅ 已成功添加 {{ addedCount }} 个日程到日历
    </el-alert>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api'  // 你们的 axios 实例

const props = defineProps({
  trip: Object  // 旅行计划对象
})

const adding = ref(false)
const addedCount = ref(0)

const addToCalendar = async () => {
  adding.value = true
  
  try {
    // 构造事件数据
    const events = props.trip.itinerary.flatMap(day => {
      return day.activities.map(activity => ({
        title: `${props.trip.title} - ${activity.title}`,
        description: activity.description || '',
        start_time: `${day.date}T${activity.time || '09:00'}:00+08:00`,
        end_time: `${day.date}T${activity.endTime || '18:00'}:00+08:00`,
        location: activity.location || '',
        latitude: activity.latitude,
        longitude: activity.longitude,
        reminder_minutes: 60,  // 提前1小时提醒
        email_reminder: true
      }))
    })
    
    // 调用 Ralendar API
    const response = await api.post('/ralendar/events/batch/', {
      source_app: 'roamio',
      related_trip_slug: props.trip.slug,
      events: events
    })
    
    addedCount.value = response.created_count
    ElMessage.success(`成功添加 ${response.created_count} 个日程！`)
    
  } catch (error) {
    console.error('添加到日历失败:', error)
    ElMessage.error('添加失败：' + (error.response?.data?.error || error.message))
  } finally {
    adding.value = false
  }
}
</script>
```

---

### 方案 B: 日历小组件（嵌入到旅行页面）

```vue
<template>
  <div class="calendar-widget">
    <div class="widget-header">
      <h3>📅 日程安排</h3>
      <el-button size="small" @click="syncToCalendar">
        同步到日历
      </el-button>
    </div>
    
    <div class="events-list">
      <div 
        v-for="event in events" 
        :key="event.id"
        class="event-item"
      >
        <span class="event-time">
          {{ formatTime(event.start_time) }}
        </span>
        <span class="event-title">{{ event.title }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const props = defineProps({
  tripSlug: String
})

const events = ref([])

const fetchEvents = async () => {
  try {
    const response = await api.get(`/ralendar/events/trip/${props.tripSlug}/`)
    events.value = response.events
  } catch (error) {
    console.error('获取日程失败:', error)
  }
}

const syncToCalendar = async () => {
  // 同步逻辑...
}

onMounted(() => {
  fetchEvents()
})
</script>

<style scoped>
.calendar-widget {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
}

.widget-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.event-item {
  padding: 8px;
  margin: 4px 0;
  background: #f5f5f5;
  border-radius: 4px;
}
</style>
```

---

## 🔧 后端集成示例（Django）

### 在 Roamio 创建 API 代理（推荐）

**文件**: `roamio/api/ralendar_proxy.py`

```python
import requests
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

RALENDAR_API_URL = 'https://app7626.acapp.acwing.com.cn/api/v1'

def get_ralendar_headers(request):
    """构造 Ralendar API 请求头"""
    # 从请求中获取用户的 access_token
    auth_header = request.headers.get('Authorization', '')
    return {
        'Authorization': auth_header,
        'Content-Type': 'application/json'
    }


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_trip_to_calendar(request, trip_slug):
    """
    将旅行计划添加到 Ralendar
    
    前端调用:
    POST /api/trips/yunnan-trip-2025/add-to-calendar/
    """
    try:
        # 从数据库获取旅行计划
        trip = Trip.objects.get(slug=trip_slug, user=request.user)
        
        # 构造事件数据
        events = []
        for day in trip.itinerary.all():
            for activity in day.activities.all():
                events.append({
                    'title': f"{trip.title} - {activity.title}",
                    'description': activity.description or '',
                    'start_time': f"{day.date}T{activity.time or '09:00'}:00+08:00",
                    'end_time': f"{day.date}T{activity.end_time or '18:00'}:00+08:00",
                    'location': activity.location or '',
                    'latitude': activity.latitude,
                    'longitude': activity.longitude,
                    'reminder_minutes': 60,
                    'email_reminder': True
                })
        
        # 调用 Ralendar API
        headers = get_ralendar_headers(request)
        response = requests.post(
            f'{RALENDAR_API_URL}/fusion/events/batch/',
            json={
                'source_app': 'roamio',
                'related_trip_slug': trip_slug,
                'events': events
            },
            headers=headers,
            timeout=10
        )
        
        response.raise_for_status()
        result = response.json()
        
        return Response({
            'success': True,
            'message': f"成功添加 {result['created_count']} 个日程",
            'created_count': result['created_count'],
            'details': result
        })
        
    except Trip.DoesNotExist:
        return Response(
            {'error': '旅行计划不存在'},
            status=status.HTTP_404_NOT_FOUND
        )
    except requests.exceptions.RequestException as e:
        return Response(
            {'error': f'Ralendar API 调用失败: {str(e)}'},
            status=status.HTTP_502_BAD_GATEWAY
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_trip_calendar_events(request, trip_slug):
    """
    获取旅行计划的日历事件
    
    GET /api/trips/yunnan-trip-2025/calendar-events/
    """
    try:
        headers = get_ralendar_headers(request)
        response = requests.get(
            f'{RALENDAR_API_URL}/fusion/events/trip/{trip_slug}/',
            headers=headers,
            timeout=10
        )
        
        response.raise_for_status()
        return Response(response.json())
        
    except requests.exceptions.RequestException as e:
        return Response(
            {'error': f'获取日历事件失败: {str(e)}'},
            status=status.HTTP_502_BAD_GATEWAY
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_trip_from_calendar(request, trip_slug):
    """
    从日历中删除旅行计划的所有事件
    
    DELETE /api/trips/yunnan-trip-2025/calendar-events/
    """
    try:
        headers = get_ralendar_headers(request)
        response = requests.delete(
            f'{RALENDAR_API_URL}/fusion/events/trip/{trip_slug}/',
            headers=headers,
            timeout=10
        )
        
        response.raise_for_status()
        result = response.json()
        
        return Response({
            'success': True,
            'message': f"已删除 {result['deleted_count']} 个日程",
            'deleted_count': result['deleted_count']
        })
        
    except requests.exceptions.RequestException as e:
        return Response(
            {'error': f'删除失败: {str(e)}'},
            status=status.HTTP_502_BAD_GATEWAY
        )
```

**配置 URL**:

```python
# roamio/urls.py
from api.ralendar_proxy import (
    add_trip_to_calendar,
    get_trip_calendar_events,
    remove_trip_from_calendar
)

urlpatterns = [
    # ...其他路由
    
    # Ralendar 集成
    path('api/trips/<slug:trip_slug>/add-to-calendar/', add_trip_to_calendar),
    path('api/trips/<slug:trip_slug>/calendar-events/', get_trip_calendar_events),
    path('api/trips/<slug:trip_slug>/remove-from-calendar/', remove_trip_from_calendar),
]
```

---

## 🧪 测试环境

### 测试账号

**方式 1: 使用现有账号**
- 在 Ralendar 和 Roamio 都使用 QQ 登录
- 两边自动共享用户（基于 QQ UnionID）

**方式 2: 测试 Token（开发用）**
```bash
# 获取测试 Token
curl -X POST https://app7626.acapp.acwing.com.cn/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "password": "test_password"
  }'

# 返回:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "test_user",
    "email": "test@example.com"
  }
}
```

### 测试数据

**示例旅行计划** (`yunnan-trip-2025`):
```json
{
  "title": "云南秘境探索",
  "slug": "yunnan-trip-2025",
  "days": 7,
  "itinerary": [
    {
      "day": 1,
      "date": "2025-11-15",
      "activities": [
        {
          "time": "10:00",
          "title": "抵达昆明",
          "location": "昆明长水国际机场",
          "latitude": 25.1019,
          "longitude": 102.9292
        }
      ]
    }
  ]
}
```

---

## 📊 数据格式规范

### Event 对象完整字段

```typescript
interface Event {
  // 必填字段
  title: string;                  // 事件标题
  start_time: string;             // 开始时间 (ISO 8601格式)
  
  // 可选字段
  end_time?: string;              // 结束时间
  description?: string;           // 描述
  location?: string;              // 地点名称
  latitude?: number;              // 纬度 (-90 到 90)
  longitude?: number;             // 经度 (-180 到 180)
  reminder_minutes?: number;      // 提前多少分钟提醒 (默认15)
  email_reminder?: boolean;       // 是否发送邮件提醒 (默认false)
  
  // 来源标识（重要！）
  source_app?: string;            // 来源应用 (固定填 "roamio")
  source_id?: string;             // 来源应用中的ID
  related_trip_slug?: string;     // 关联的旅行计划 slug
  
  // 只读字段（API返回）
  id?: number;                    // 事件ID
  user?: number;                  // 用户ID
  created_at?: string;            // 创建时间
  updated_at?: string;            // 更新时间
  notification_sent?: boolean;    // 是否已发送提醒
}
```

### 时间格式

**推荐使用 ISO 8601 格式 with Timezone**:
```
2025-11-15T10:00:00+08:00  ✅ 推荐（带时区）
2025-11-15T10:00:00Z       ✅ UTC时间
2025-11-15 10:00:00        ❌ 不带时区（会有歧义）
```

**Python 示例**:
```python
from datetime import datetime
from django.utils import timezone

# 创建带时区的时间
start_time = timezone.now().isoformat()
# 输出: '2025-11-08T23:30:00+08:00'
```

**JavaScript 示例**:
```javascript
// 创建带时区的时间
const startTime = new Date('2025-11-15 10:00').toISOString()
// 输出: '2025-11-15T02:00:00.000Z'  (UTC)

// 或者使用本地时区
const localTime = new Date('2025-11-15 10:00')
  .toLocaleString('sv-SE', { timeZone: 'Asia/Shanghai' })
  .replace(' ', 'T') + '+08:00'
// 输出: '2025-11-15T10:00:00+08:00'
```

---

## ⚠️ 常见问题

### Q1: 401 Unauthorized - Token 验证失败

**可能原因**:
1. `SECRET_KEY` 不一致
2. Token 已过期（默认24小时）
3. 请求头格式错误

**解决方案**:
```bash
# 1. 检查 SECRET_KEY
# Roamio settings.py
SECRET_KEY = 'django-insecure-#6avwo7=$9vse4txxj!phdfx5-ql(bc5otpoiw@x)u0i+^1-5h'

# 2. 检查请求头
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
# 注意：Bearer 后面有空格！

# 3. 刷新 Token
POST /api/v1/auth/token/refresh/
{
  "refresh": "refresh_token_here"
}
```

---

### Q2: CORS 错误

**现象**: 
```
Access to fetch at 'https://app7626.acapp.acwing.com.cn/api/v1/events/' 
from origin 'https://roamio.cn' has been blocked by CORS policy
```

**解决方案**:

Ralendar 已配置允许 Roamio 的域名：
```python
# Ralendar settings.py
CORS_ALLOWED_ORIGINS = [
    'https://roamio.cn',  # Roamio
    'http://localhost:5173',
]
```

如果还有问题，请联系 Ralendar 团队添加白名单。

---

### Q3: 事件时间显示错误

**问题**: 创建的事件时间比预期早/晚 8 小时

**原因**: 时区处理问题

**解决方案**:
```javascript
// ❌ 错误：没有指定时区
const event = {
  start_time: '2025-11-15 10:00:00'  // 会被当作 UTC
}

// ✅ 正确：明确指定时区
const event = {
  start_time: '2025-11-15T10:00:00+08:00'  // 北京时间
}
```

---

### Q4: 批量创建时部分失败

**响应示例**:
```json
{
  "success": true,
  "created_count": 8,
  "skipped_count": 2,
  "errors": [
    {
      "index": 3,
      "title": "某个事件",
      "errors": {
        "start_time": ["该字段是必填项"]
      }
    }
  ]
}
```

**处理建议**:
- 检查 `errors` 数组，修正失败的事件
- 重新提交失败的事件

---

### Q5: 如何避免重复创建？

**方案 1: 使用 `related_trip_slug`**
```python
# 创建前检查
existing = Event.objects.filter(
    user=request.user,
    related_trip_slug='yunnan-trip-2025'
).exists()

if existing:
    return {'error': '该旅行计划已同步'}
```

**方案 2: 使用 `source_id`**
```python
# 为每个活动分配唯一ID
event_data = {
    'source_app': 'roamio',
    'source_id': f"trip_{trip.id}_activity_{activity.id}",
    ...
}
```

---

## 📞 联系支持

### Ralendar 团队

- **负责人**: ppshuX
- **QQ/邮箱**: 2064747320@qq.com
- **服务器**: app7626.acapp.acwing.com.cn

### 技术支持

- **API 文档**: 本文档 + [ROAMIO_INTEGRATION_GUIDE.md](./ROAMIO_INTEGRATION_GUIDE.md)
- **问题反馈**: GitHub Issues
- **紧急联系**: QQ 2064747320

---

## ✅ 集成验收清单

完成以下步骤，确认集成成功：

- [ ] 在 Roamio `.env` 中配置 `SECRET_KEY`（与 Ralendar 相同）
- [ ] 能够调用 Ralendar API（返回 200/201，不是 401/403）
- [ ] 能够为旅行计划批量创建事件
- [ ] 创建的事件能在 Ralendar 中正常显示
- [ ] 时间显示正确（没有时区偏移）
- [ ] 地图位置正常显示（如果有坐标）
- [ ] 能够删除旅行计划的所有事件
- [ ] 前端"添加到日历"按钮正常工作
- [ ] 错误处理友好（显示清晰的错误信息）

---

## 🎉 准备就绪！

所有资源已准备完毕，Roamio 团队可以开始集成了！

**预计集成时间**: 2-4 小时  
**如有问题**: 随时联系 Ralendar 团队

**祝集成顺利！** 🚀

