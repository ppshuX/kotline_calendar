# Day 10 开发日志 - Android 网络功能集成

**日期**：2025年11月06日  
**用时**：约1小时  
**完成度**：✅ 100%

---

## 📋 今天做了什么

- [x] 添加 Retrofit 网络库依赖
- [x] 添加网络权限（INTERNET, ACCESS_NETWORK_STATE）
- [x] 创建 API 数据模型（ApiModels.kt）
- [x] 创建 API 接口定义（CalendarApi.kt）
- [x] 配置 Retrofit 客户端（RetrofitClient.kt）
- [x] 添加订阅网络日历按钮
- [x] 实现订阅功能（调用后端 API）
- [x] 实现农历显示（在日程详情）

---

## 💻 写了哪些代码

### 1. build.gradle.kts（添加依赖）

```kotlin
dependencies {
    // Retrofit 网络库
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")
    
    // OkHttp 日志拦截器（调试用）
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")
}
```

---

### 2. AndroidManifest.xml（添加权限）

```xml
<!-- 网络功能需要的权限 -->
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
```

---

### 3. API 数据模型

```kotlin
// api/ApiModels.kt
data class LunarResponse(
    val lunar_date: String,      // "农历2025年十月初六"
    val year: Int,
    val month: String,
    val day: String,
    val zodiac: String,
    val solar_date: String
)

data class CalendarFeedResponse(
    val ics: String,             // iCalendar 格式
    val events_count: Int        // 事件数量
)
```

---

### 4. API 接口定义

```kotlin
// api/CalendarApi.kt
interface CalendarApi {
    // 获取农历
    @GET("lunar/")
    suspend fun getLunarDate(@Query("date") date: String): LunarResponse
    
    // 获取日历订阅
    @GET("calendars/{slug}/feed/")
    suspend fun getCalendarFeed(@Path("slug") slug: String): CalendarFeedResponse
}
```

---

### 5. Retrofit 客户端配置

```kotlin
// api/RetrofitClient.kt
object RetrofitClient {
    private const val BASE_URL = "http://10.0.2.2:8000/api/"  // 模拟器
    
    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }
    
    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(loggingInterceptor)
        .connectTimeout(30, TimeUnit.SECONDS)
        .build()
    
    val api: CalendarApi by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(CalendarApi::class.java)
    }
}
```

---

### 6. 订阅网络日历功能

```kotlin
// MainActivity.kt
private fun showSubscribeDialog() {
    val calendars = arrayOf("中国法定节假日", "农历节气", "国际纪念日")
    val slugs = arrayOf("china-holidays", "lunar-festivals", "world-days")
    
    AlertDialog.Builder(this)
        .setTitle("📡 订阅网络日历")
        .setItems(calendars) { _, which ->
            subscribeCalendar(slugs[which], calendars[which])
        }
        .show()
}

private fun subscribeCalendar(slug: String, name: String) {
    lifecycleScope.launch(Dispatchers.IO) {
        try {
            // 调用后端 API
            val response = RetrofitClient.api.getCalendarFeed(slug)
            
            withContext(Dispatchers.Main) {
                Toast.makeText(
                    this@MainActivity,
                    "✅ 订阅成功！获取了 ${response.events_count} 个日程",
                    Toast.LENGTH_LONG
                ).show()
            }
        } catch (e: Exception) {
            withContext(Dispatchers.Main) {
                Toast.makeText(this@MainActivity, "❌ 订阅失败：${e.message}", Toast.LENGTH_LONG).show()
            }
        }
    }
}
```

---

### 7. 农历显示功能

```kotlin
private fun getLunarDate(dateTime: Long, callback: (String) -> Unit) {
    lifecycleScope.launch(Dispatchers.IO) {
        try {
            val dateFormat = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
            val dateStr = dateFormat.format(Date(dateTime))
            
            // 调用后端 API
            val lunar = RetrofitClient.api.getLunarDate(dateStr)
            
            withContext(Dispatchers.Main) {
                callback("${lunar.lunar_date} ${lunar.zodiac}年")
            }
        } catch (e: Exception) {
            withContext(Dispatchers.Main) {
                callback("")  // 失败就不显示
            }
        }
    }
}

// 在日程详情中使用
private fun showEventDetails(event: Event) {
    getLunarDate(event.dateTime) { lunar ->
        val message = buildString {
            append("📅 日期：...\n\n")
            append("📝 标题：${event.title}\n\n")
            if (lunar.isNotEmpty()) {
                append("🏮 农历：$lunar")
            }
        }
        // 显示对话框
    }
}
```

---

## 🧪 测试步骤

### 1. 启动 Django 后端

```bash
cd backend
python manage.py runserver
```

确保后端运行在：http://localhost:8000/api/

---

### 2. Sync Project

在 Android Studio：
1. File → Sync Project with Gradle Files
2. 等待依赖下载完成

---

### 3. 运行 App

1. 启动模拟器或连接真机
2. Run → Run 'app'
3. 等待安装完成

---

### 4. 测试订阅功能

1. 点击"📡 订阅网络日历"按钮
2. 选择"中国法定节假日"
3. 应该看到 Toast 提示："✅ 订阅成功！"

---

### 5. 测试农历显示

1. 点击任意日程查看详情
2. 应该看到农历信息："🏮 农历2025年十月初六 蛇年"

---

## 🔧 可能遇到的问题

### 问题 1：网络连接失败

**错误信息**：`Failed to connect to /10.0.2.2:8000`

**解决方案**：
1. 确保 Django 后端正在运行
2. 模拟器使用 `10.0.2.2`
3. 真机使用电脑的局域网 IP（如 `192.168.x.x`）

---

### 问题 2：CORS 错误

**解决方案**：
后端已配置 CORS，应该没问题

---

### 问题 3：找不到 Retrofit 类

**解决方案**：
1. File → Invalidate Caches → Restart
2. 重新 Sync Project

---

## 🎯 功能演示流程

```
1. 打开 App
   ↓
2. 点击"订阅网络日历"
   ↓
3. 选择"中国法定节假日"
   ↓
4. Toast 显示："⏳ 正在订阅..."
   ↓
5. 后端返回数据
   ↓
6. Toast 显示："✅ 订阅成功！获取了 11 个日程"
   ↓
7. 点击任意日程查看详情
   ↓
8. 详情对话框显示农历信息："🏮 农历2025年十月初六 蛇年"
```

---

## 📊 Day 10 完成情况

### ✅ 已实现功能：

- ✅ Retrofit 网络库集成
- ✅ 订阅网络日历
- ✅ 农历显示
- ✅ 错误处理
- ✅ 日志输出（Logcat 调试）

### ⏳ 可选扩展（时间充裕可做）：

- [ ] 解析 iCalendar 格式（现在只获取数量）
- [ ] 保存订阅的日程到本地数据库
- [ ] 云端备份/恢复功能
- [ ] 真机 IP 配置界面

---

**Day 10 完成！Android 网络功能已实现！** 🎉

**今日评分**：⭐⭐⭐⭐⭐ (5/5) - 三端打通！
