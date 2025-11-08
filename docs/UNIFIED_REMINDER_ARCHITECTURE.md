# 🔔 统一提醒系统架构设计

> **创建日期**: 2025-11-08  
> **版本**: v1.0  
> **目标**: 统一 Web、Android、Roamio 三端的提醒和认证系统

---

## 🎯 核心问题

1. ❓ 用户没有设置邮箱怎么办？
2. ❓ Android 版如何调用系统闹钟？
3. ❓ 如何统一不同平台的提醒机制？
4. ❓ 如何与 Roamio 统一邮箱和登录信息？

---

## 🏗️ 架构设计方案

### 1️⃣ **多层级提醒系统（推荐）**

```
提醒优先级（自动降级）:
┌─────────────────────────────────────────┐
│ Level 1: 邮件提醒（需要邮箱）             │
│   ↓ 如果没有邮箱，降级到                  │
│ Level 2: 站内通知（Web + Android）       │
│   ↓ 如果未登录，降级到                    │
│ Level 3: 本地提醒（仅 Android）          │
│   - 系统闹钟                              │
│   - 系统通知                              │
└─────────────────────────────────────────┘
```

---

## 📋 详细方案

### 方案 A：扩展 Event 模型（推荐）

#### 数据库设计

```python
class Event(models.Model):
    # ... 现有字段 ...
    
    # ===== 提醒配置字段（扩展版）=====
    reminder_type = models.CharField(
        max_length=20,
        choices=[
            ('email', '邮件提醒'),
            ('notification', '站内通知'),
            ('alarm', '系统闹钟'),
            ('all', '全部提醒'),
        ],
        default='email',
        verbose_name='提醒类型'
    )
    
    email_reminder = models.BooleanField(default=False, verbose_name='邮件提醒')
    push_notification = models.BooleanField(default=False, verbose_name='推送通知')
    system_alarm = models.BooleanField(default=False, verbose_name='系统闹钟')
    
    # 提醒状态跟踪
    email_sent = models.BooleanField(default=False, verbose_name='邮件已发送')
    notification_sent = models.BooleanField(default=False, verbose_name='通知已发送')
    alarm_set = models.BooleanField(default=False, verbose_name='闹钟已设置')
```

---

### 方案 B：智能提醒策略

#### 前端逻辑（自动选择提醒方式）

```javascript
// 创建事件时，根据用户状态智能选择提醒方式
const determineReminderType = () => {
  const hasEmail = currentUser.value.email
  const platform = getPlatform()  // 'web' or 'android'
  
  if (platform === 'android') {
    // Android 优先使用系统闹钟
    return {
      email_reminder: hasEmail,
      push_notification: true,
      system_alarm: true,
      reminder_type: 'all'
    }
  } else {
    // Web 端
    if (hasEmail) {
      return {
        email_reminder: true,
        push_notification: true,
        system_alarm: false,
        reminder_type: 'email'
      }
    } else {
      return {
        email_reminder: false,
        push_notification: true,
        system_alarm: false,
        reminder_type: 'notification'
      }
    }
  }
}
```

#### 后端逻辑（Celery 任务扩展）

```python
@shared_task
def send_reminder(event_id):
    """统一的提醒发送任务"""
    event = Event.objects.get(id=event_id)
    user = event.user
    
    reminder_sent = False
    
    # 1. 尝试邮件提醒
    if event.email_reminder and user.email:
        try:
            send_email_reminder(event)
            event.email_sent = True
            reminder_sent = True
        except:
            pass  # 邮件失败，继续尝试其他方式
    
    # 2. 站内通知（WebSocket 或数据库通知表）
    if event.push_notification:
        create_in_app_notification(event)
        event.notification_sent = True
        reminder_sent = True
    
    # 3. Android 推送（FCM - Firebase Cloud Messaging）
    if event.system_alarm and user.fcm_token:
        send_fcm_notification(event, user.fcm_token)
        event.alarm_set = True
        reminder_sent = True
    
    event.save()
    return reminder_sent
```

---

## 📱 Android 系统闹钟集成

### Kotlin 实现示例

```kotlin
// Android 端：设置系统闹钟
import android.app.AlarmManager
import android.app.PendingIntent
import android.content.Intent

class ReminderManager(private val context: Context) {
    
    fun setEventAlarm(event: Event) {
        val alarmManager = context.getSystemService(Context.ALARM_SERVICE) as AlarmManager
        
        val intent = Intent(context, EventReminderReceiver::class.java).apply {
            putExtra("event_id", event.id)
            putExtra("event_title", event.title)
            putExtra("event_time", event.startTime)
        }
        
        val pendingIntent = PendingIntent.getBroadcast(
            context,
            event.id.hashCode(),
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        
        // 设置精确闹钟
        val triggerTime = event.startTime - (event.reminderMinutes * 60 * 1000)
        
        alarmManager.setExactAndAllowWhileIdle(
            AlarmManager.RTC_WAKEUP,
            triggerTime,
            pendingIntent
        )
    }
}

// BroadcastReceiver：处理闹钟触发
class EventReminderReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val title = intent.getStringExtra("event_title")
        val eventTime = intent.getLongExtra("event_time", 0)
        
        // 显示系统通知
        showNotification(context, title, eventTime)
        
        // 可选：播放闹钟铃声
        playAlarmSound()
    }
}
```

---

## 🔗 Roamio 统一认证方案

### 方案 1：共享数据库 + UnionID（推荐）

#### 架构图

```
┌──────────────────────────────────────────────────┐
│           QQ 互联平台（统一身份源）                │
│                                                  │
│  UnionID: 同一用户在不同应用的统一标识             │
└────────────┬─────────────────────┬───────────────┘
             │                     │
    ┌────────▼──────┐     ┌────────▼──────┐
    │   Ralendar    │     │    Roamio     │
    │   QQ_APPID_1  │     │  QQ_APPID_2   │
    └────────┬──────┘     └────────┬──────┘
             │                     │
             └──────────┬──────────┘
                        │
           ┌────────────▼────────────┐
           │   共享 PostgreSQL 数据库  │
           │                         │
           │  User 表（统一用户表）    │
           │  ├─ id (主键)            │
           │  ├─ username            │
           │  ├─ email               │
           │  ├─ qq_unionid (唯一)   │
           │  └─ ...                 │
           └─────────────────────────┘
```

#### 实现步骤

1. **两个项目使用同一个数据库**
   ```python
   # Ralendar 和 Roamio 的 settings.py
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'unified_calendar_db',  # 同一个数据库
           'USER': 'calendar_user',
           'PASSWORD': 'same_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

2. **统一 SECRET_KEY**
   ```python
   # 两个项目使用同一个 SECRET_KEY
   SECRET_KEY = 'shared-secret-key-for-both-projects'
   ```

3. **使用 QQ UnionID 识别同一用户**
   ```python
   # QQ 登录时获取 UnionID
   unionid_url = f"https://graph.qq.com/oauth2.0/me?access_token={access_token}&unionid=1"
   
   # 查找或创建用户（基于 UnionID）
   user = User.objects.filter(qq_profile__unionid=unionid).first()
   ```

---

### 方案 2：API 网关 + Token 共享（简单）

```
用户登录 Ralendar
  ↓
生成 JWT Token
  ↓
Token 包含 user_id + qq_unionid
  ↓
Roamio 验证 Token（共享 SECRET_KEY）
  ↓
识别为同一用户
```

**优点**：
- ✅ 不需要共享数据库
- ✅ 项目独立性强
- ✅ 实现简单

**缺点**：
- ⚠️ 需要同步用户数据
- ⚠️ 需要 API 互相调用

---

## 💡 前端提醒交互设计

### UI/UX 优化

#### 场景 1：用户没有邮箱

```vue
<el-form-item label="邮件提醒">
  <el-checkbox v-model="formData.emailReminder" :disabled="!hasEmail">
    事件开始前发送邮件提醒
  </el-checkbox>
  
  <!-- 如果没有邮箱，显示提示 -->
  <div v-if="!hasEmail" class="email-hint">
    <i class="bi bi-exclamation-circle"></i>
    <span>请先在<router-link to="/profile">个人中心</router-link>设置邮箱</span>
  </div>
</el-form-item>
```

#### 场景 2：Android 版提醒选项

```vue
<el-form-item label="提醒方式">
  <el-checkbox-group v-model="reminderTypes">
    <el-checkbox value="email" :disabled="!hasEmail">
      📧 邮件提醒
    </el-checkbox>
    <el-checkbox value="notification">
      🔔 站内通知
    </el-checkbox>
    <el-checkbox value="alarm" v-if="isAndroid">
      ⏰ 系统闹钟
    </el-checkbox>
  </el-checkbox-group>
</el-form-item>
```

---

## 🔄 统一提醒系统实现路线图

### Phase 1：Web 端完善（当前）
- ✅ 邮件提醒（已完成）
- ⏳ 站内通知系统
- ⏳ 邮箱设置提示

### Phase 2：Android 端实现
- ⏳ 系统闹钟 API
- ⏳ 本地通知
- ⏳ FCM 推送

### Phase 3：跨项目统一
- ⏳ 共享数据库
- ⏳ UnionID 映射
- ⏳ Token 互认

---

## 📝 建议的优先级

### 立即做（今天/明天）

**1. 添加邮箱设置提示（30分钟）**
```vue
<!-- 创建事件时，如果没有邮箱，提示用户 -->
<el-alert v-if="!currentUser.email" type="warning" :closable="false">
  <template #title>
    📧 设置邮箱后可接收提醒邮件
  </template>
  <el-button size="small" @click="goToProfile">
    去设置邮箱
  </el-button>
</el-alert>
```

**2. 为现有用户自动设置默认邮箱（数据迁移）**
```python
# 一次性脚本：为所有 QQ 用户生成默认邮箱
from django.contrib.auth.models import User
from api.models import QQUser

qq_users = QQUser.objects.all()
for qq in qq_users:
    if not qq.user.email:
        qq.user.email = f"{qq.openid[:10]}@qq.com"
        qq.user.save()
        print(f"✅ {qq.user.username}: {qq.user.email}")
```

---

### 近期做（本周）

**3. 创建站内通知表**
```python
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

**4. WebSocket 实时通知（可选）**
- 使用 Django Channels
- 实时推送提醒到已登录用户

---

### 中期做（下周）

**5. Android 系统闹钟集成**
```kotlin
// 在 Android 端实现
ReminderManager.setAlarm(event)
```

**6. FCM 推送通知**
```python
# 后端发送推送
from firebase_admin import messaging

def send_fcm_notification(event, fcm_token):
    message = messaging.Message(
        notification=messaging.Notification(
            title=f"📅 {event.title}",
            body=f"即将开始：{event.start_time}"
        ),
        token=fcm_token
    )
    messaging.send(message)
```

---

### 长期做（与 Roamio 对接时）

**7. 统一认证系统**

#### 数据库统一
```python
# 两个项目共享同一个数据库
# settings.py (Ralendar & Roamio)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'unified_ecosystem_db',
        'USER': 'ecosystem_user',
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': 'shared-db-server.com',
        'PORT': '5432',
    }
}

# 同一个 SECRET_KEY
SECRET_KEY = os.environ.get('SHARED_SECRET_KEY')
```

#### QQ UnionID 映射
```python
class QQUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    openid = models.CharField(max_length=100)  # 应用内唯一
    unionid = models.CharField(max_length=100, unique=True)  # 跨应用唯一
    
    # 用户在 Ralendar 登录时
    # 根据 unionid 查找，如果已在 Roamio 注册过，直接关联
```

---

## 🎨 前端 UI 优化建议

### 创建事件对话框

```vue
<template>
  <el-form-item label="提醒设置">
    <!-- 提醒时间 -->
    <el-select v-model="reminderMinutes">
      <el-option label="不提醒" :value="0" />
      <el-option label="提前15分钟" :value="15" />
      ...
    </el-select>
    
    <!-- 提醒方式（根据用户状态动态显示）-->
    <div v-if="reminderMinutes > 0" class="reminder-options">
      <!-- 邮件提醒 -->
      <el-checkbox 
        v-model="emailReminder" 
        :disabled="!currentUser.email"
      >
        📧 邮件提醒
        <el-tooltip v-if="!currentUser.email" content="请先设置邮箱">
          <i class="bi bi-question-circle"></i>
        </el-tooltip>
      </el-checkbox>
      
      <!-- 站内通知（始终可用）-->
      <el-checkbox v-model="pushNotification">
        🔔 站内通知
      </el-checkbox>
      
      <!-- 系统闹钟（仅 Android）-->
      <el-checkbox v-if="isAndroid" v-model="systemAlarm">
        ⏰ 系统闹钟
      </el-checkbox>
    </div>
    
    <!-- 友好提示 -->
    <el-alert 
      v-if="reminderMinutes > 0 && !currentUser.email" 
      type="info" 
      :closable="false"
      class="mt-2"
    >
      <template #title>
        💡 提示：设置邮箱后可接收邮件提醒
      </template>
      <el-button type="primary" size="small" link @click="goToProfile">
        立即设置邮箱 →
      </el-button>
    </el-alert>
  </el-form-item>
</template>
```

---

## 🗺️ 最终架构图

```
┌─────────────────────────────────────────────────────────┐
│                    QQ 互联平台                           │
│            (UnionID 作为唯一用户标识)                     │
└────────────┬────────────────────────┬───────────────────┘
             │                        │
    ┌────────▼─────────┐    ┌────────▼─────────┐
    │    Ralendar      │    │     Roamio       │
    │   (日历系统)      │    │   (旅行日志)      │
    └────────┬─────────┘    └────────┬─────────┘
             │                        │
             └────────┬───────────────┘
                      │
         ┌────────────▼────────────┐
         │  共享 PostgreSQL 数据库   │
         │                         │
         │  ┌──────────────────┐   │
         │  │  User 表         │   │
         │  │  - qq_unionid    │   │
         │  │  - email         │   │
         │  └──────────────────┘   │
         │                         │
         │  ┌──────────────────┐   │
         │  │  Event 表        │   │
         │  │  - source_app    │   │
         │  │  - reminder_type │   │
         │  └──────────────────┘   │
         └─────────────────────────┘
                      │
         ┌────────────▼────────────┐
         │   统一提醒调度系统        │
         │   (Celery + Redis)      │
         └─┬─────────┬──────────┬──┘
           │         │          │
    ┌──────▼──┐  ┌──▼───┐  ┌──▼────┐
    │  Email  │  │ 站内  │  │ FCM   │
    │  (Web)  │  │ 通知  │  │(安卓) │
    └─────────┘  └──────┘  └───────┘
```

---

## 📊 实施计划

### 本周末（紧急）
- [ ] 添加邮箱设置提示
- [ ] 运行数据迁移脚本（为现有用户设置邮箱）
- [ ] 修复下拉菜单遮挡

### 下周（重要）
- [ ] 创建站内通知表
- [ ] 实现站内通知功能
- [ ] Android 闹钟 API 开发

### 下下周（与 Roamio 对接）
- [ ] 共享数据库迁移
- [ ] UnionID 映射实现
- [ ] 跨项目认证测试

---

## 🎯 当前推荐方案（最快实现）

### 1. **立即：为现有用户设置默认邮箱**

在服务器上运行：
```bash
cd ~/kotlin_calendar/backend
python3 manage.py shell
```

```python
from django.contrib.auth.models import User
from api.models import QQUser

# 为所有 QQ 用户设置邮箱
qq_users = QQUser.objects.all()
updated = 0

for qq in qq_users:
    if not qq.user.email:
        qq.user.email = f"{qq.openid[:10]}@qq.com"
        qq.user.save()
        updated += 1
        print(f"✅ {qq.user.username}: {qq.user.email}")

print(f"\n✅ 共更新 {updated} 个用户的邮箱")
exit()
```

### 2. **前端添加友好提示**

我现在就可以实现！

---

**要不要我现在就实现"邮箱设置提示"功能？只需要5分钟！** 💡
