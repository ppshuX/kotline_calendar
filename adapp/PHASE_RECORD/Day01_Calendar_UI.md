# Day 01 开发日志 - 搭建基础日历界面

**日期**：2025年11月04日  
**用时**：约3小时（包括踩坑时间）  
**完成度**：✅ 100%

---

## 📋 今天做了什么

- [x] 成功运行 Android 项目
- [x] 日历完整显示（月视图）
- [x] 实现日期选择交互
- [x] 显示选中的日期（中文格式 + 星期）
- [x] 解决了依赖冲突问题

---

## 💻 完整代码实现

### 1. 布局文件 (activity_main.xml)

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    tools:context=".MainActivity">

    <!-- Android 原生日历 -->
    <CalendarView
        android:id="@+id/calendarView"
        android:layout_width="match_parent"
        android:layout_height="wrap_content" />

    <!-- 显示选中日期的文本 -->
    <TextView
        android:id="@+id/tvSelectedDate"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:padding="16dp"
        android:text="请选择日期"
        android:textSize="18sp"
        android:gravity="center" />

</LinearLayout>
```

**设计思路**：
- 用 `LinearLayout` 垂直布局，简单直接
- 日历占上半部分，自适应高度
- 下面用 `TextView` 显示选中的日期

---

### 2. 主程序 (MainActivity.kt)

```kotlin
package com.ncu.kotlincalendar

import android.os.Bundle
import android.widget.CalendarView
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import java.text.SimpleDateFormat
import java.util.*

class MainActivity : AppCompatActivity() {
    
    // 声明组件（lateinit = 延迟初始化，onCreate 时再赋值）
    private lateinit var calendarView: CalendarView
    private lateinit var tvSelectedDate: TextView
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        // 通过 findViewById 获取布局中的组件
        calendarView = findViewById(R.id.calendarView)
        tvSelectedDate = findViewById(R.id.tvSelectedDate)
        
        // 默认显示今天的日期
        showDate(System.currentTimeMillis())
        
        // 设置日期选择监听（Lambda 表达式）
        calendarView.setOnDateChangeListener { view, year, month, dayOfMonth ->
            // 创建 Calendar 对象
            val calendar = Calendar.getInstance()
            calendar.set(year, month, dayOfMonth)
            // 显示选中的日期
            showDate(calendar.timeInMillis)
        }
        
        Toast.makeText(this, "日历加载成功！点击日期试试", Toast.LENGTH_SHORT).show()
    }
    
    /**
     * 显示日期的辅助函数
     * @param timeInMillis 时间戳（毫秒）
     */
    private fun showDate(timeInMillis: Long) {
        // 创建日期格式化对象（yyyy年MM月dd日 星期X）
        val dateFormat = SimpleDateFormat("yyyy年MM月dd日 EEEE", Locale.CHINESE)
        val dateStr = dateFormat.format(Date(timeInMillis))
        tvSelectedDate.text = "选中日期：$dateStr"
    }
}
```

**代码要点**：
1. **`lateinit var`**：延迟初始化，在 `onCreate` 时赋值
2. **`findViewById<T>(R.id.xxx)`**：通过 ID 获取组件（类似 Web 的 `document.getElementById`）
3. **`setOnDateChangeListener`**：日期改变监听器（Lambda 表达式）
4. **`SimpleDateFormat`**：日期格式化工具，`EEEE` 表示完整的星期名
5. **`Locale.CHINESE`**：中文本地化

---

### 3. 颜色资源 (colors.xml)

```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="black">#FF000000</color>
    <color name="white">#FFFFFFFF</color>
    
    <!-- Material Design 主题色 -->
    <color name="purple_500">#FF6200EE</color>
    <color name="purple_700">#FF3700B3</color>
    <color name="teal_200">#FF03DAC5</color>
    <color name="teal_700">#FF018786</color>
    <color name="red">#FFF44336</color>
    <color name="blue">#FF2196F3</color>
    <color name="green">#FF4CAF50</color>
</resources>
```

**为什么添加这些颜色**：
- Material Design 标准色
- 后面会用到（按钮、提示等）

---

## 🐛 遇到的坑（详细版）

### 坑 1：第三方日历库依赖冲突

**问题现象**：
```
ClassNotFoundException: Didn't find class "android.support.v4.widget.EdgeEffectCompat"
```

**原因分析**：
- `material-calendarview:1.4.3` 是 2016 年的库
- 内部使用旧的 Support Library
- 我们项目用的是新的 AndroidX
- 两者不兼容，导致运行时找不到类

**尝试的解决方案**：
1. ❌ 排除冲突依赖 → 还是报错
2. ❌ 换 `kizitonwose.calendar` → IDE 识别不了
3. ✅ **最终方案**：用 Android 原生 `CalendarView`

**学到的经验**：
- 第三方库要看维护情况，太老的别用
- AndroidX 和 Support Library 不能混用
- 遇到依赖问题，原生 API 是最稳的

---

### 坑 2：颜色资源找不到

**问题现象**：
```
error: resource color/purple_500 not found
```

**原因**：
- 项目初始 `colors.xml` 只有黑白两色
- 布局里用了 `@color/purple_500` 但没定义

**解决方案**：
- 在 `app/src/main/res/values/colors.xml` 里添加颜色定义

**学到的**：
- Android 资源都要预先定义
- 颜色、字符串、尺寸等都在 `res/values/` 下

---

### 坑 3：Gradle 同步问题

**问题现象**：
- 修改 `build.gradle.kts` 后，IDE 报红色波浪线
- `Unresolved reference`

**解决方案**：
1. 点击 "Sync Now"
2. 或 File → Sync Project with Gradle Files
3. 必要时 Clean Project + Rebuild

**学到的**：
- 每次改依赖都要同步 Gradle
- 缓存问题可以 Invalidate Caches

---

## 📚 今天学到的知识点

### Kotlin 语法

1. **lateinit var**
   ```kotlin
   private lateinit var calendarView: CalendarView
   // 声明但不初始化，后面再赋值
   ```

2. **Lambda 表达式**
   ```kotlin
   setOnDateChangeListener { view, year, month, day ->
       // 相当于 JavaScript 的箭头函数
   }
   ```

3. **字符串模板**
   ```kotlin
   tvSelectedDate.text = "选中日期：$dateStr"
   // 类似 JS 的 `选中日期：${dateStr}`
   ```

### Android 基础

1. **Activity 生命周期**
   - `onCreate()` - 创建时调用，类似 Vue 的 `mounted`

2. **findViewById**
   - 通过 ID 获取布局中的组件
   - 类似 `document.getElementById`

3. **布局文件 (XML)**
   - UI 用 XML 定义，类似 HTML
   - `android:id="@+id/xxx"` 定义 ID
   - `android:layout_width/height` 设置宽高

4. **监听器 (Listener)**
   - `setOnDateChangeListener` - 日期改变监听
   - 类似 Web 的 `addEventListener`

### 对比 Web 开发

| Android | Web | 说明 |
|---------|-----|------|
| `findViewById` | `getElementById` | 获取元素 |
| `setOnClickListener` | `addEventListener('click')` | 点击事件 |
| `TextView` | `<div>` / `<p>` | 文本显示 |
| `LinearLayout` | `flex-direction: column` | 垂直布局 |
| `activity_main.xml` | `index.html` | 界面文件 |
| `MainActivity.kt` | `main.js` | 逻辑代码 |

---

## 🎯 今日成果

### 功能演示
- ✅ 日历显示：November 2025
- ✅ 日期选择：点击任意日期，高亮显示
- ✅ 日期展示：选中日期: 2025年11月04日 星期二
- ✅ Toast 提示：日历加载成功

### 代码统计
- 新增文件：3 个
- 修改文件：2 个
- 代码行数：约 50 行

---

## 💡 心得体会

### 进展顺利的地方
- Kotlin 语法和 JavaScript 很像，上手快
- Android Studio 提示很智能，写代码很流畅
- 原生 CalendarView 简单好用

### 遇到的挑战
- 依赖冲突踩了不少坑
- 第一次接触 Gradle，同步概念需要理解
- XML 布局方式和 Web 不同，需要适应

### 经验总结
1. **遇到库冲突，优先考虑原生 API**
2. **每次改依赖记得 Sync Gradle**
3. **报错先看 Logcat，找关键信息**
4. **边做边学比看完教程再做更有效**

---

## 📝 明日计划

**Day 2 目标**：实现添加和显示日程

核心任务：
- [ ] 创建添加日程的界面
- [ ] 能添加日程（标题、时间）
- [ ] 在列表中显示日程
- [ ] 点击日期弹出添加界面

预计难度：⭐⭐⭐  
预计用时：3-4 小时

---

## 📸 截图记录

**最终效果**：
- 日历月视图 ✅
- 选中日期显示 ✅
- 中文日期格式 ✅

---

**Day 1 完成！明天继续加油！** 💪

**今日评分**：⭐⭐⭐⭐ (4/5) - 有坑但都解决了，收获满满！

