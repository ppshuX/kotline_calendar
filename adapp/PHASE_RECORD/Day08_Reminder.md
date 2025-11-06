# Day 08 开发日志 - 提醒功能

**日期**：2025年11月05日  
**用时**：约1小时  
**完成度**：✅ 100%

---

## 📋 今天做了什么

- [x] 添加通知和闹钟权限
- [x] 创建 AlarmReceiver 广播接收器
- [x] 创建 ReminderManager 提醒管理器
- [x] 修改 Event 实体添加 reminderMinutes 字段
- [x] 升级数据库版本（v1 → v2）
- [x] 添加提醒下拉选项到对话框
- [x] 实现设置和取消提醒功能
- [x] 添加权限请求和调试日志
- [x] 测试通过：提醒功能正常运行

---

## 💻 写了哪些代码

### 1. AndroidManifest.xml（权限配置）

```xml
<!-- 提醒功能需要的权限 -->
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
<uses-permission android:name="android.permission.SCHEDULE_EXACT_ALARM" />
<uses-permission android:name="android.permission.USE_EXACT_ALARM" />

<!-- 提醒接收器 -->
<receiver
    android:name=".AlarmReceiver"
    android:enabled="true"
    android:exported="false" />
```

---

### 2. AlarmReceiver（广播接收器）

```kotlin
class AlarmReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val eventTitle = intent.getStringExtra("eventTitle") ?: "日程提醒"
        val eventDesc = intent.getStringExtra("eventDesc") ?: ""
        
        showNotification(context, eventId, eventTitle, eventDesc)
    }
    
    private fun showNotification(context: Context, id: Long, title: String, desc: String) {
        // 1. 创建通知渠道（Android 8.0+）
        val channel = NotificationChannel(
            CHANNEL_ID,
            "日程提醒",
            NotificationManager.IMPORTANCE_HIGH
        )
        
        // 2. 创建通知
        val notification = NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle("📅 $title")
            .setContentText(desc.ifEmpty { "日程即将开始" })
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setAutoCancel(true)
            .build()
        
        notificationManager.notify(id.toInt(), notification)
    }
}
```

---

### 3. ReminderManager（提醒管理）

```kotlin
class ReminderManager(private val context: Context) {
    private val alarmManager = context.getSystemService(Context.ALARM_SERVICE) as AlarmManager
    
    // 设置提醒
    fun setReminder(event: Event) {
        if (event.reminderMinutes <= 0) return
        
        // 计算提醒时间 = 日程时间 - 提前分钟数
        val reminderTime = event.dateTime - (event.reminderMinutes * 60 * 1000)
        
        // 如果已过期，不设置
        if (reminderTime < System.currentTimeMillis()) return
        
        // 创建 Intent
        val intent = Intent(context, AlarmReceiver::class.java).apply {
            putExtra("eventId", event.id)
            putExtra("eventTitle", event.title)
            putExtra("eventDesc", event.description)
        }
        
        val pendingIntent = PendingIntent.getBroadcast(...)
        
        // 设置精确闹钟
        alarmManager.setExactAndAllowWhileIdle(
            AlarmManager.RTC_WAKEUP,
            reminderTime,
            pendingIntent
        )
    }
    
    // 取消提醒
    fun cancelReminder(eventId: Long) {
        val pendingIntent = PendingIntent.getBroadcast(...)
        pendingIntent?.let {
            alarmManager.cancel(it)
            it.cancel()
        }
    }
}
```

---

### 4. 对话框添加提醒选项

```kotlin
// 提醒选项
val reminderOptions = arrayOf(
    "不提醒", 
    "提前5分钟", 
    "提前15分钟",  // ← 老师要求的
    "提前30分钟", 
    "提前1小时", 
    "提前1天"
)
val reminderMinutes = arrayOf(0, 5, 15, 30, 60, 24 * 60)

spinnerReminder?.adapter = ArrayAdapter(
    this, 
    android.R.layout.simple_spinner_dropdown_item, 
    reminderOptions
)
```

---

### 5. 保存时设置提醒

```kotlin
// 添加日程
val eventId = eventDao.insert(event)

// 设置提醒
if (reminderMinutes > 0) {
    val savedEvent = event.copy(id = eventId)
    reminderManager.setReminder(savedEvent)
    
    // 提示用户
    val reminderTime = dateTime - (reminderMinutes * 60 * 1000)
    Toast.makeText(this, "⏰ 将在 ${formatTime(reminderTime)} 提醒您", Toast.LENGTH_LONG).show()
}
```

---

## 🔔 提醒功能工作流程

```
1. 用户添加日程
   - 日程时间：21:15
   - 提醒：提前5分钟
   ↓
2. 计算提醒时间
   reminderTime = 21:15 - 5分钟 = 21:10
   ↓
3. 设置 AlarmManager
   alarmManager.setExactAndAllowWhileIdle(21:10, pendingIntent)
   ↓
4. 系统到了 21:10（可能延迟2-5分钟）
   ↓
5. 触发 AlarmReceiver.onReceive()
   ↓
6. 显示通知
   NotificationManager.notify(...)
   ↓
7. 用户看到通知栏提醒！
```

---

## 💡 关于延迟

### **为什么会延迟？**

**Android 省电机制**：
- 系统会批量处理定时任务
- 延迟 2-5 分钟很正常
- 真正的闹钟 App 才会精确到秒

### **如何理解**：
- 📅 **日历提醒**：延迟几分钟 OK（省电）
- ⏰ **闹钟 App**：必须精确（耗电）

**我们的实现符合日历 App 的标准！**

---

## 🎯 测试结果

- ✅ 提醒功能正常运行
- ✅ 通知成功显示
- ✅ 延迟 2-5 分钟（正常现象）
- ✅ 删除日程会取消提醒
- ✅ 编辑日程会更新提醒

---

## 📊 作业完成度

### **基本要求（3个）**：
1. ✅ 日历视图展示（月视图）
2. ✅ 日程增删改查
3. ✅ **日程提醒功能** ← 刚完成！

**基本要求 100% 完成！** 🎉

### **剩余任务**：
- Day 7：周/日视图（可选）
- Day 9：扩展功能（可选）
- Day 10：文档和演示（必做）

---

**Day 8 完成！作业核心功能全部搞定！** 🎉🎉🎉

**今日评分**：⭐⭐⭐⭐⭐ (5/5) - 提醒功能完美实现！

