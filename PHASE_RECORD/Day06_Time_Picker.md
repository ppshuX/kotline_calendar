# Day 06 开发日志 - 时间选择器

**日期**：2025年11月05日  
**用时**：约30分钟  
**完成度**：✅ 100%

---

## 📋 今天做了什么

- [x] 在对话框中添加时间输入框
- [x] 实现 TimePickerDialog 时间选择器
- [x] 添加/编辑时能选具体时间（小时:分钟）
- [x] 时间格式化显示（yyyy-MM-dd HH:mm）
- [x] 卡片和详情都显示具体时间

---

## 💻 写了哪些代码

### 1. 对话框添加时间输入框

```xml
<!-- dialog_add_event.xml -->
<TextInputLayout
    android:hint="时间"
    app:startIconDrawable="@android:drawable/ic_menu_recent_history">
    
    <TextInputEditText
        android:id="@+id/etTime"
        android:focusable="false"
        android:clickable="true" />
</TextInputLayout>
```

**关键属性**：
- `focusable="false"` - 不能输入，只能点击
- `clickable="true"` - 可以点击弹出选择器

---

### 2. TimePickerDialog 实现

```kotlin
// 显示时间选择器
private fun showTimePicker(calendar: Calendar, onTimeSelected: (Int, Int) -> Unit) {
    val hour = calendar.get(Calendar.HOUR_OF_DAY)
    val minute = calendar.get(Calendar.MINUTE)
    
    TimePickerDialog(
        this,                        // Context
        { _, selectedHour, selectedMinute ->
            onTimeSelected(selectedHour, selectedMinute)
        },
        hour,                        // 初始小时
        minute,                      // 初始分钟
        true                         // 24小时制
    ).show()
}

// 更新时间显示
private fun updateTimeDisplay(editText: TextInputEditText?, calendar: Calendar) {
    val timeFormat = SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault())
    editText?.setText(timeFormat.format(calendar.time))
}
```

---

### 3. 在对话框中使用

```kotlin
// 显示初始时间
updateTimeDisplay(etTime, calendar)

// 点击时间框弹出选择器
etTime?.setOnClickListener {
    showTimePicker(calendar) { hour, minute ->
        calendar.set(Calendar.HOUR_OF_DAY, hour)
        calendar.set(Calendar.MINUTE, minute)
        updateTimeDisplay(etTime, calendar)
    }
}
```

---

## 🎨 TimePickerDialog 特点

### **系统自带的优势**：
- ✅ Material Design 风格
- ✅ 圆形时钟界面
- ✅ 自动适配主题色
- ✅ 支持 12/24 小时制切换
- ✅ 键盘输入模式（点击键盘图标）
- ✅ 无需第三方库

### **对比 Web**：
```html
<!-- Web 需要这样 -->
<input type="time">  <!-- 各浏览器样式不统一 -->

<!-- 或用第三方库 -->
<el-time-picker />
<VueDatePicker />
```

**Android 一行搞定**：
```kotlin
TimePickerDialog(...).show()  // 完美！
```

---

## 💡 学到的知识

### 系统对话框组件

| 组件 | 用途 | 代码 |
|------|------|------|
| `TimePickerDialog` | 选择时间 | `TimePickerDialog(...).show()` |
| `DatePickerDialog` | 选择日期 | `DatePickerDialog(...).show()` |
| `AlertDialog` | 通用对话框 | `AlertDialog.Builder().show()` |

### Lambda 回调

```kotlin
showTimePicker(calendar) { hour, minute ->
    // 选择后的回调
    calendar.set(Calendar.HOUR_OF_DAY, hour)
    calendar.set(Calendar.MINUTE, minute)
}
```

**类似 JavaScript**：
```javascript
showTimePicker(calendar, (hour, minute) => {
    // 回调函数
})
```

---

## 📊 今日成果

### 功能完成
- ✅ 时间选择器集成
- ✅ 支持选择具体时间（小时:分钟）
- ✅ 时间格式化显示
- ✅ 编辑模式预填充时间

### 用户体验提升
- ✅ 添加日程时能选具体时间
- ✅ 编辑时能修改时间
- ✅ 时间显示更精确（到分钟）
- ✅ Material Design 统一风格

---

**Day 5-6 完成！编辑 + 时间选择器全部搞定！** 🎉

**今日评分**：⭐⭐⭐⭐⭐ (5/5) - 系统组件太方便了！


