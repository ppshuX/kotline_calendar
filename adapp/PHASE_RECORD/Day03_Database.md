# Day 03 开发日志 - Room 数据库集成

**日期**：2025年11月05日  
**用时**：约2小时（包括模拟器配置时间）  
**完成度**：✅ 100%

---

## 📋 今天做了什么

- [x] 添加 Room 数据库依赖和 KSP 插件
- [x] 创建 Event 实体类
- [x] 创建 EventDao 数据访问接口
- [x] 创建 AppDatabase 单例类
- [x] 改造 MainActivity 使用数据库存储
- [x] 测试数据持久化成功（真机 + 虚拟机）
- [x] 配置轻量级虚拟机（Pixel 2 API 30）

---

## 💻 写了哪些代码

### 1. Event 实体类 (Event.kt)

```kotlin
@Entity(tableName = "events")
data class Event(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    
    val title: String,              // 标题
    val description: String = "",   // 描述
    val dateTime: Long,             // 日期时间（时间戳）
    val createdAt: Long = System.currentTimeMillis()  // 创建时间
)
```

**类似 Django**：
```python
class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date_time = models.DateTimeField()
```

---

### 2. EventDao 接口 (EventDao.kt)

```kotlin
@Dao
interface EventDao {
    // 查询所有日程
    @Query("SELECT * FROM events ORDER BY dateTime ASC")
    suspend fun getAllEvents(): List<Event>
    
    // 插入日程
    @Insert
    suspend fun insert(event: Event): Long
    
    // 更新日程
    @Update
    suspend fun update(event: Event)
    
    // 删除日程
    @Delete
    suspend fun delete(event: Event)
}
```

**类似 Django**：
```python
Event.objects.all()           # getAllEvents()
Event.objects.create(...)     # insert()
event.save()                  # update()
event.delete()                # delete()
```

---

### 3. AppDatabase 类 (AppDatabase.kt)

```kotlin
@Database(entities = [Event::class], version = 1, exportSchema = false)
abstract class AppDatabase : RoomDatabase() {
    abstract fun eventDao(): EventDao
    
    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null
        
        fun getDatabase(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "calendar_database"
                ).build()
                INSTANCE = instance
                instance
            }
        }
    }
}
```

**单例模式**：确保全局只有一个数据库实例

---

### 4. MainActivity 改造

```kotlin
// 初始化数据库
database = AppDatabase.getDatabase(this)
eventDao = database.eventDao()

// 加载数据
private fun loadAllEvents() {
    lifecycleScope.launch(Dispatchers.IO) {
        val events = eventDao.getAllEvents()
        withContext(Dispatchers.Main) {
            eventsList.clear()
            eventsList.addAll(events)
            updateEventsList()
        }
    }
}

// 添加日程（保存到数据库）
private fun addEvent(title: String, description: String = "") {
    lifecycleScope.launch(Dispatchers.IO) {
        val event = Event(
            title = title,
            description = description,
            dateTime = selectedDateMillis
        )
        eventDao.insert(event)
        
        // 重新加载
        val events = eventDao.getAllEvents()
        withContext(Dispatchers.Main) {
            eventsList.clear()
            eventsList.addAll(events)
            updateEventsList()
            Toast.makeText(this@MainActivity, "✅ 添加成功！", Toast.LENGTH_SHORT).show()
        }
    }
}
```

---

## 🐛 遇到的坑

### 坑 1：模拟器配置太高导致电脑卡死

**问题现象**：
- Medium Phone API 36.1 运行后电脑直接卡死
- 内存占用 94%，强制重启电脑

**原因分析**：
- API 36 是最新版本，资源占用高
- 电脑内存不足（Chrome + Android Studio + 模拟器 > 可用内存）

**解决方案**：
1. ✅ 先用真机测试（华为手机 API 29）
2. ✅ 创建轻量级虚拟机（Pixel 2 API 30）
3. ✅ 降低虚拟机 RAM 配置

**学到的经验**：
- 开发时优先考虑硬件资源
- 真机调试效率更高
- 虚拟机要选择合适的配置

---

### 坑 2：协程和线程调度

**问题**：
- 数据库操作必须在后台线程
- UI 更新必须在主线程

**解决方案**：
```kotlin
lifecycleScope.launch(Dispatchers.IO) {  // 后台线程
    val events = eventDao.getAllEvents()
    
    withContext(Dispatchers.Main) {      // 切换到主线程
        updateEventsList()
    }
}
```

**学到的**：
- `Dispatchers.IO` - 用于数据库、网络操作
- `Dispatchers.Main` - 用于 UI 更新
- `withContext()` - 切换线程

---

### 坑 3：从 Flow 到 List 的简化

**最初设计**：
```kotlin
fun getAllEvents(): Flow<List<Event>>  // Flow 响应式
```

**简化版本**：
```kotlin
suspend fun getAllEvents(): List<Event>  // 简单查询
```

**原因**：
- Flow 适合实时监听数据变化
- 对于简单场景，直接查询更稳定
- 避免复杂性导致的问题

---

## 📚 今天学到的知识

### Room 数据库三件套

1. **Entity（实体）**
   - 用 `@Entity` 注解
   - 对应数据库的表
   - 类似 Django 的 Model

2. **DAO（数据访问对象）**
   - 用 `@Dao` 注解
   - 定义 CRUD 操作
   - 类似 Django 的 QuerySet

3. **Database（数据库）**
   - 用 `@Database` 注解
   - 单例模式
   - 类似 Django 的 settings.DATABASES

---

### 协程（Coroutines）

```kotlin
lifecycleScope.launch {
    // 异步操作
}
```

**对比 JavaScript**：
```javascript
async function addEvent() {
    await db.insert(event)
}
```

**类似 Python**：
```python
async def add_event():
    await db.insert(event)
```

---

### Room vs Django ORM

| 特性 | Django | Room |
|------|--------|------|
| **定义模型** | `class Event(models.Model)` | `@Entity data class Event` |
| **自动 ID** | `id = AutoField()` | `@PrimaryKey(autoGenerate=true)` |
| **查询所有** | `Event.objects.all()` | `@Query("SELECT * FROM events")` |
| **插入** | `Event.objects.create()` | `@Insert suspend fun insert()` |
| **删除** | `event.delete()` | `@Delete suspend fun delete()` |
| **SQL 生成** | 自动 | 手动写 SQL |

---

## 🎯 数据持久化原理

### **为什么能持久化**：

```
添加日程
    ↓
Room 框架
    ↓
执行 SQL: INSERT INTO events (...)
    ↓
写入 SQLite 文件
    ↓
文件存储在手机：
/data/data/com.ncu.kotlincalendar/databases/calendar_database
    ↓
关闭 App（进程结束，内存清空）
    ↓
文件还在硬盘上 ✅
    ↓
重新打开 App
    ↓
Room 读取 SQLite 文件
    ↓
执行 SQL: SELECT * FROM events
    ↓
数据恢复！
```

**就像**：
- Django 的 `db.sqlite3` 文件
- MySQL 的数据文件
- 你保存的 Word 文档

---

## 💡 架构理解

### **移动端 vs Web 端**

**Web 应用（集中式）**：
```
用户 A ↘
用户 B → 云服务器 → 一个数据库
用户 C ↗
```

**移动应用（分布式）**：
```
用户 A 手机 → SQLite A
用户 B 手机 → SQLite B
用户 C 手机 → SQLite C
（每个人的数据独立）
```

**如果需要同步**：
```
用户 A 手机 (SQLite A) ←→ API ←→ 云端 MySQL
用户 B 手机 (SQLite B) ←→ API ←→ 云端 MySQL
```

---

## 📊 今日成果

### 功能完成
- ✅ 数据库增删查改（CRUD）
- ✅ 数据持久化存储
- ✅ 协程异步处理
- ✅ 真机 + 虚拟机测试通过

### 代码统计
- 新增文件：3 个（Event.kt, EventDao.kt, AppDatabase.kt）
- 修改文件：2 个（MainActivity.kt, build.gradle.kts）
- 代码行数：约 100 行

### 测试结果
- ✅ 真机测试：华为手机 API 29 - 成功
- ✅ 虚拟机测试：Pixel 2 API 30 - 成功
- ✅ 数据持久化：重启应用数据保留 - 成功

---

## 📝 明日计划

**Day 4 目标**：优化列表显示（RecyclerView）

- [ ] 用 RecyclerView 替代 TextView
- [ ] 实现列表项点击查看详情
- [ ] 优化列表性能和样式
- [ ] 添加滑动删除功能

预计难度：⭐⭐⭐  
预计用时：2-3 小时

---

**Day 3 完成！数据库搞定，应用已经能真正使用了！** 🎉

**今日评分**：⭐⭐⭐⭐⭐ (5/5) - 虽然遇到硬件问题，但最终完美解决！


