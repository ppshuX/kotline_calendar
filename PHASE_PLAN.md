# KotlinCalendar - 10 天实战开发指南

> **核心理念**：边做边学，遇到问题就解决，写着写着就会了

---

## 🎯 项目目标

做一个能用的 Android 日历应用，完成作业要求。

### 必做功能
- ✅ 日历显示（月/周/日视图）
- ✅ 日程管理（增删改查）
- ✅ 提醒通知

### 选做功能（做 1-2 个就行）
- 📤 导入导出
- 🔍 搜索
- 🏮 农历

---

## 🚀 10 天开发路线图

> 不用严格按天数，能做多快做多快，卡住了就问

### Day 1-2：把项目跑起来

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

### Day 10：收尾和提交

#### Day 10 - 写报告、录视频、提交
**目标**：完成文档和演示

**要做的事**：
1. **写产品报告**（Word/PPT）
   - 截几张界面图
   - 写功能介绍
   - 画个架构图（UI → 逻辑 → 数据库）
   - 说说技术亮点

2. **录演示视频**（5-10 分钟）
   - OBS Studio / 手机录屏
   - 演示添加、编辑、删除、提醒

3. **提交材料**
   ```
   南昌大学+姓名+Android+KotlinCalendar.zip
   ├── 产品报告.pdf
   ├── 演示录屏.mp4
   └── 源代码链接.txt (GitHub/Gitee)
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

**砍功能，保核心**：
- 周视图/日视图可以不做
- 扩展功能一个都不做也行
- UI 难看点没关系，能用就行

---

## 📚 需要时再查的资源

### 卡住了去这里找
- [Android 开发者官网](https://developer.android.google.cn/)
- [Kotlin 文档](https://kotlinlang.org/docs/home.html)
- Stack Overflow
- 直接问 ChatGPT / Cursor

### 别把时间花在
- ❌ 从头到尾看文档
- ❌ 系统学习理论
- ❌ 研究最佳实践
- ✅ 有问题就查，能跑就行

---

## 🎯 核心理念

> **"边做边学，遇到问题就解决"**  
> **"能跑起来 > 写得漂亮"**  
> **"完成 > 完美"**

**记住**：
- 代码不需要一次写对，能跑就往下做
- 报错是正常的，解决了就是成长
- 不用都懂，会用就行
- AI 是你的工具，大胆用

---

**准备好了吗？直接开始 Day 1，把日历显示出来！** 🚀
