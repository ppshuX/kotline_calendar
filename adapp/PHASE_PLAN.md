# KotlinCalendar - 全栈日历应用开发指南

> **核心理念**：边做边学，遇到问题就解决，写着写着就会了  
> **新目标**：前后端分离 + 多端同步 + 网络订阅

---

## 🎯 项目目标（已升级）

做一个**前后端分离的全栈日历应用**，完成作业要求并超越。

### ✅ 已完成的核心功能（Day 1-8）
- ✅ 日历显示（月视图）
- ✅ 日程管理（增删改查）
- ✅ 提醒通知
- ✅ RecyclerView 列表
- ✅ 时间选择器
- ✅ 编辑功能
- ✅ Room 数据库

### 🚀 新增目标（全栈架构）
- 🌐 Django 后端 API
- ☁️ 云端数据同步
- 📡 **网络日历订阅**（扩展要求 2）
- 🏮 **农历 API**（扩展要求 3）
- 📤 **导入导出**（扩展要求 1）
- 🖥️ Vue3 Web 管理端（可选）
- 💎 VIP 会员系统（可选）

---

## 🚀 开发路线图（已更新为全栈）

> 实际进度：2 天完成 8 天任务！现在升级为全栈项目！

### ✅ Day 1-8：Android 客户端（已完成）

#### Day 1 - 搭建基础界面
**目标**：能在手机上看到一个日历

**直接开始做**：
```kotlin
// 1. 确保项目能运行
// 2. 在 MainActivity 里添加 MaterialCalendarView
// 3. 能看到一个月历就算完成
```

**需要的代码**：
```xml
<!-- activity_main.xml -->
<com.prolificinteractive.materialcalendarview.MaterialCalendarView
    android:id="@+id/calendarView"
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />
```

```kotlin
// MainActivity.kt
calendarView.setOnDateChangedListener { widget, date, selected ->
    Toast.makeText(this, "选中了 ${date.date}", Toast.LENGTH_SHORT).show()
}
```

**可能遇到的问题**：
- 报错找不到 MaterialCalendarView？→ 检查 build.gradle.kts 里有没有这个依赖
- 模拟器启动慢？→ 用真机，或者等着，第一次慢很正常

---

#### Day 2 - 能添加和显示日程
**目标**：点击日期能弹出输入框，输入后能显示出来（先不管保存）

**直接开始做**：
```kotlin
// 1. 创建一个 Dialog 或新页面，有输入框
// 2. 点击日期时打开它
// 3. 用 List 临时存数据，显示在屏幕上
```

**需要的代码**：
```kotlin
// 临时存数据（先不用数据库）
val events = mutableListOf<String>()

// 点击添加
button.setOnClickListener {
    val title = editText.text.toString()
    events.add(title)
    updateList()  // 刷新列表显示
}
```

**可能遇到的问题**：
- 不知道怎么弹窗？→ 直接问我要代码
- 列表怎么显示？→ 先用 TextView 凑合，后面再优化

---

### Day 3-4：数据能保存

#### Day 3 - 接入数据库
**目标**：添加的日程重启 App 后还在

**直接开始做**：
```kotlin
// 1. 复制下面的 Room 数据库代码
// 2. 把之前的 List 改成从数据库读写
// 3. 测试：添加 → 关闭 App → 重开 → 数据还在
```

**复制就能用的代码**：
```kotlin
// Event.kt
@Entity(tableName = "events")
data class Event(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val title: String,
    val dateTime: Long,
    val description: String = ""
)

// EventDao.kt
@Dao
interface EventDao {
    @Query("SELECT * FROM events ORDER BY dateTime ASC")
    fun getAll(): Flow<List<Event>>
    
    @Insert
    suspend fun insert(event: Event)
    
    @Delete
    suspend fun delete(event: Event)
}

// AppDatabase.kt
@Database(entities = [Event::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun eventDao(): EventDao
    
    companion object {
        @Volatile private var INSTANCE: AppDatabase? = null
        fun getDatabase(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                Room.databaseBuilder(context, AppDatabase::class.java, "calendar_db")
                    .build().also { INSTANCE = it }
            }
        }
    }
}
```

**依赖**（添加到 app/build.gradle.kts）：
```kotlin
dependencies {
    val room_version = "2.6.1"
    implementation("androidx.room:room-runtime:$room_version")
    implementation("androidx.room:room-ktx:$room_version")
    ksp("androidx.room:room-compiler:$room_version")
}

plugins {
    id("com.google.devtools.ksp") version "2.0.21-1.0.25"
}
```

**可能遇到的问题**：
- Gradle 同步失败？→ 贴错误信息给我
- 不知道 suspend 和 Flow 是啥？→ 不用管，先跑起来再说

---

#### Day 4 - 用列表显示日程
**目标**：选择日期后，下面显示该日期的所有日程

**直接开始做**：
```kotlin
// 1. 添加一个 RecyclerView
// 2. 复制下面的 Adapter 代码
// 3. 点击日期时查询数据库，刷新列表
```

**RecyclerView Adapter 模板**：
```kotlin
class EventAdapter(
    private var events: List<Event>,
    private val onItemClick: (Event) -> Unit
) : RecyclerView.Adapter<EventAdapter.ViewHolder>() {
    
    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val tvTitle: TextView = view.findViewById(R.id.tvTitle)
        val tvTime: TextView = view.findViewById(R.id.tvTime)
    }
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_event, parent, false)
        return ViewHolder(view)
    }
    
    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val event = events[position]
        holder.tvTitle.text = event.title
        holder.tvTime.text = formatTime(event.dateTime)
        holder.itemView.setOnClickListener { onItemClick(event) }
    }
    
    override fun getItemCount() = events.size
    
    fun updateEvents(newEvents: List<Event>) {
        events = newEvents
        notifyDataSetChanged()
    }
}
```

---

### Day 5-6：完善日程管理

#### Day 5 - 能编辑和删除
**目标**：点击日程能修改或删除它

**直接开始做**：
```kotlin
// 点击列表项 → 弹出编辑界面 → 修改后保存
// 长按列表项 → 弹出确认对话框 → 删除

// 删除对话框
AlertDialog.Builder(this)
    .setTitle("删除日程")
    .setMessage("确定删除吗？")
    .setPositiveButton("删除") { _, _ ->
        lifecycleScope.launch {
            database.eventDao().delete(event)
        }
    }
    .setNegativeButton("取消", null)
    .show()
```

---

#### Day 6 - 添加日期时间选择器
**目标**：添加日程时能选具体时间，不只是日期

**直接开始做**：
```kotlin
// 日期选择
val datePickerDialog = DatePickerDialog(this,
    { _, year, month, day ->
        selectedDate.set(Calendar.YEAR, year)
        selectedDate.set(Calendar.MONTH, month)
        selectedDate.set(Calendar.DAY_OF_MONTH, day)
    },
    year, month, day
)
datePickerDialog.show()

// 时间选择
val timePickerDialog = TimePickerDialog(this,
    { _, hour, minute ->
        selectedDate.set(Calendar.HOUR_OF_DAY, hour)
        selectedDate.set(Calendar.MINUTE, minute)
    },
    hour, minute, true
)
timePickerDialog.show()
```

---

### Day 7：多视图切换

#### Day 7 - 加上周视图和日视图
**目标**：能在月/周/日三种视图之间切换

**直接开始做**：
```kotlin
// 1. 用 ViewPager2 + TabLayout
// 2. 创建 3 个 Fragment（复制月视图的代码改改）
// 3. 周视图显示本周，日视图显示今天

// ViewPager Adapter
class ViewPagerAdapter(activity: FragmentActivity) : FragmentStateAdapter(activity) {
    override fun getItemCount() = 3
    override fun createFragment(position: Int) = when(position) {
        0 -> MonthFragment()
        1 -> WeekFragment()
        2 -> DayFragment()
        else -> MonthFragment()
    }
}

// 关联 Tab
TabLayoutMediator(tabLayout, viewPager) { tab, pos ->
    tab.text = when(pos) {
        0 -> "月"
        1 -> "周"  
        2 -> "日"
        else -> ""
    }
}.attach()
```

---

### Day 8：提醒功能

#### Day 8 - 能发通知提醒
**目标**：到时间了能收到通知

**直接开始做**：
```kotlin
// 1. 复制下面的通知代码
// 2. 添加日程时顺便设置提醒
// 3. 到时间了就会弹通知

// 设置提醒
val alarmManager = getSystemService(Context.ALARM_SERVICE) as AlarmManager
val intent = Intent(this, AlarmReceiver::class.java)
val pendingIntent = PendingIntent.getBroadcast(this, 0, intent, 0)

alarmManager.setExactAndAllowWhileIdle(
    AlarmManager.RTC_WAKEUP,
    reminderTime,
    pendingIntent
)
```

**别忘了**：
```xml
<!-- AndroidManifest.xml -->
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
<uses-permission android:name="android.permission.SCHEDULE_EXACT_ALARM" />

<receiver android:name=".AlarmReceiver" android:enabled="true" />
```

---

### Day 9：优化和扩展

#### Day 9 - 做点锦上添花的功能
**目标**：选 1-2 个扩展功能实现，或者优化 UI

**选项 1 - 搜索**：
```kotlin
@Query("SELECT * FROM events WHERE title LIKE '%' || :keyword || '%'")
fun search(keyword: String): Flow<List<Event>>
```

**选项 2 - 导出（iCalendar）**：
```kotlin
fun exportToICS(events: List<Event>): String {
    return buildString {
        appendLine("BEGIN:VCALENDAR")
        appendLine("VERSION:2.0")
        events.forEach { event ->
            appendLine("BEGIN:VEVENT")
            appendLine("SUMMARY:${event.title}")
            appendLine("DTSTART:${formatICalDate(event.dateTime)}")
            appendLine("END:VEVENT")
        }
        appendLine("END:VCALENDAR")
    }
}
```

**选项 3 - 农历**：
```kotlin
// 添加依赖
implementation("com.nlf:calendar:1.3.0")

// 使用
val solar = Solar.fromYmd(2025, 1, 1)
val lunar = solar.lunar
println("${lunar.monthInChinese}月${lunar.dayInChinese}")
```

**或者优化 UI**：
- 加点颜色和图标
- 加空状态提示
- 优化列表样式

---

### Day 9：Django 后端开发（NEW！）

#### Day 9 - 搭建云端后台
**目标**：实现前后端分离架构，支持网络订阅和云端同步

**直接开始做**：
```python
# 1. 创建 Django 项目
django-admin startproject calendar_backend

# 2. 安装 Django REST Framework
pip install djangorestframework
pip install django-cors-headers

# 3. 创建 API
python manage.py startapp api
```

**核心 API**：
```python
# api/models.py
class Event(models.Model):
    user = models.ForeignKey(User)
    title = models.CharField(max_length=200)
    description = models.TextField()
    date_time = models.DateTimeField()
    reminder_minutes = models.IntegerField(default=0)

class PublicCalendar(models.Model):
    name = models.CharField()  # "中国法定节假日"
    url_slug = models.SlugField()
    events = models.ManyToManyField(Event)
    is_public = models.BooleanField(default=True)

# api/views.py
class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

@api_view(['GET'])
def get_calendar_feed(request, slug):
    # 返回 iCalendar 格式
    calendar = PublicCalendar.objects.get(url_slug=slug)
    ics_content = generate_ics(calendar.events.all())
    return Response(ics_content)

@api_view(['GET'])
def get_lunar_date(request):
    date = request.GET.get('date')
    # 调用农历库或第三方 API
    lunar = calculate_lunar(date)
    return Response({'lunar': lunar})
```

**部署**：
```bash
# 部署到你的云服务器
gunicorn calendar_backend.wsgi
nginx 反向代理
SSL 证书配置
```

---

### Day 10：Android 对接后端（NEW！）

#### Day 10 - 网络功能集成
**目标**：App 对接后端 API，实现订阅和云同步

**添加依赖**：
```kotlin
// Retrofit 网络库
implementation("com.squareup.retrofit2:retrofit:2.9.0")
implementation("com.squareup.retrofit2:converter-gson:2.9.0")
```

**API 接口定义**：
```kotlin
interface CalendarApi {
    @GET("events/")
    suspend fun getEvents(): List<Event>
    
    @POST("events/")
    suspend fun createEvent(@Body event: Event): Event
    
    @GET("calendars/{slug}/feed")
    suspend fun getCalendarFeed(@Path("slug") slug: String): String
    
    @GET("lunar/")
    suspend fun getLunarDate(@Query("date") date: String): LunarInfo
}
```

**订阅功能**：
```kotlin
// 订阅网络日历
fun subscribeCalendar(url: String) {
    lifecycleScope.launch {
        val events = api.getCalendarFeed("china-holidays")
        
        // 解析 iCalendar 格式
        val parsedEvents = parseICS(events)
        
        // 保存到本地
        parsedEvents.forEach { eventDao.insert(it) }
        
        Toast.makeText(this, "✅ 订阅成功！", Toast.LENGTH_SHORT).show()
    }
}

// 显示农历
fun showLunar(dateTime: Long) {
    lifecycleScope.launch {
        val lunar = api.getLunarDate(formatDate(dateTime))
        tvLunar.text = lunar.lunarDate  // "农历十月初五"
    }
}
```

---

### Day 11：文档和演示（NEW！）

#### Day 11 - 写报告、录视频、提交
**目标**：完成文档和演示，重点展示全栈架构

**要做的事**：
1. **写产品报告**（Word/PPT）
   - 截图展示界面（Android App + Web 端）
   - **重点强调全栈架构**
   - 前后端分离架构图
   - 技术栈：Kotlin + Django + Vue3（可选）
   - 画个架构图（UI → 逻辑 → 数据库）
   - 说说技术亮点

2. **录演示视频**（10 分钟）
   - **Part 1：Android 基础功能**（3 分钟）
     - 手机录屏：日历视图、添加日程
     - 编辑删除、提醒通知
   
   - **Part 2：后端和订阅功能**（5 分钟）★ 重点！
     - 展示订阅网络日历
     - 演示农历显示
     - 展示云端同步（可选）
     - 打开浏览器访问 API 接口
   
   - **Part 3：技术架构**（2 分钟）
     - 展示代码结构
     - 前后端分离架构图
     - 技术亮点总结

3. **提交材料**
   ```
   南昌大学+姓名+Android+KotlinCalendar.zip
   ├── 产品报告.pdf
   ├── 演示录屏.mp4
   ├── 源代码链接.txt (GitHub - Android + Backend)
   ├── API 文档.pdf
   └── 架构设计图.png
   ```

---

## 💡 实战技巧

### 遇到问题怎么办？

**第一步**：看报错信息，复制到 Google/ChatGPT
**第二步**：问我，贴上代码和报错
**第三步**：换个思路，先绕过去做其他的

### 不会的东西？

**不要先学，直接问要代码**：
- "我要实现 XX 功能，给我代码"
- "这个报错怎么解决？"
- "这段代码怎么改？"

### 时间不够？

**现在时间充裕，全栈开发**：
- ✅ Android 核心功能已完成
- 🚀 现在加上后端，展示全栈能力
- 💎 扩展功能全部实现

---

## 🏗️ 新架构设计（全栈）

```
┌─────────────────────────────────────────────────────┐
│                   Android App                        │
│  ┌──────────────┐  ┌──────────────┐                 │
│  │ UI (Activity)│  │ RecyclerView │                 │
│  └──────┬───────┘  └──────┬───────┘                 │
│         │                 │                          │
│  ┌──────▼─────────────────▼───────┐                 │
│  │   ViewModel (Coroutines)       │                 │
│  └──────┬───────────────┬─────────┘                 │
│         │               │                            │
│  ┌──────▼───────┐  ┌───▼─────────┐                 │
│  │ Room (Local) │  │ Retrofit API│                  │
│  └──────────────┘  └───┬─────────┘                  │
└─────────────────────────┼──────────────────────────┘
                          │ HTTPS
                          ▼
┌─────────────────────────────────────────────────────┐
│              Django Backend (云服务器)               │
│  ┌──────────────────────────────────────┐           │
│  │   Django REST Framework              │           │
│  │   ┌────────────┐  ┌────────────┐    │           │
│  │   │ Event API  │  │ Calendar   │    │           │
│  │   │ (CRUD)     │  │ Subscribe  │    │           │
│  │   └────────────┘  └────────────┘    │           │
│  │   ┌────────────┐  ┌────────────┐    │           │
│  │   │ Lunar API  │  │ User/VIP   │    │           │
│  │   └────────────┘  └────────────┘    │           │
│  └──────────┬───────────────────────────┘           │
│             ▼                                        │
│  ┌──────────────────────┐                           │
│  │  PostgreSQL/MySQL    │                           │
│  └──────────────────────┘                           │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────┐
│           Vue3 Web Admin (可选)                      │
│  ┌──────────────────────────────────────┐           │
│  │   FullCalendar.js                    │           │
│  │   Axios API 调用                     │           │
│  │   数据统计和分析                     │           │
│  └──────────────────────────────────────┘           │
└─────────────────────────────────────────────────────┘
```

---

## 🎯 扩展要求完成情况

| 要求 | 功能 | 实现方式 | 状态 |
|-----|------|---------|------|
| 扩展 1 | 导入导出 | 云端备份/恢复 | 🚀 计划中 |
| 扩展 2 | **网络订阅** | Django 提供 iCalendar 订阅 | 🚀 计划中 |
| 扩展 3 | **农历** | Django 封装农历 API | 🚀 计划中 |

**所有扩展要求都将满足！** 🏆

---

## 💎 商业化可能性（可选）

### VIP 功能设计
```
免费版：
- ✅ 基础日历
- ✅ 本地日程（限 50 条）
- ✅ 基础提醒

VIP 会员 (¥9.9/月)：
- 💎 无限日程
- 💎 云端同步
- 💎 网络订阅
- 💎 农历黄历
- 💎 数据导出
- 💎 AI 智能建议
```

---

## 📚 推荐资源

**Android**：
- 官方文档：https://developer.android.com
- Kotlin 中文站：https://www.kotlincn.net
- Room 数据库：https://developer.android.com/training/data-storage/room

**Django**：
- Django REST Framework：https://www.django-rest-framework.org
- Django 中文文档：https://docs.djangoproject.com/zh-hans

**前后端对接**：
- Retrofit 官方文档：https://square.github.io/retrofit
- iCalendar 格式：https://icalendar.org

---

## 🎯 核心理念（已升级）

> **"边做边学，遇到问题就解决"**  
> **"能跑起来 > 写得漂亮"**  
> **"全栈开发 = 真正的产品"**  
> **"完成 > 完美"**

**记住**：
- 代码不需要一次写对，能跑就往下做
- 报错是正常的，解决了就是成长
- 全栈不可怕，一步步来
- 有云服务器就要用上，展示真实力
- AI 是你的工具，大胆用

---

**准备好了吗？明天开始 Day 9，搭建 Django 后端！** 🚀

**目标：做一个真正有商业价值的全栈日历应用！** 💎
