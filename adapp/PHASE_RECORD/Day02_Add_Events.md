# Day 02 开发日志 - 添加和显示日程

**日期**：2025年11月04日  
**用时**：约2小时  
**完成度**：✅ 100%

---

## 📋 今天做了什么

- [x] 实现添加日程对话框（Material Design 风格）
- [x] 支持输入标题 + 描述
- [x] 日程列表卡片式显示
- [x] 实现长按删除功能
- [x] 优化界面样式和用户体验

---

## 💻 写了哪些代码

### 1. 自定义对话框布局 (dialog_add_event.xml)
```xml
<LinearLayout>
    <!-- Material 输入框 -->
    <com.google.android.material.textfield.TextInputLayout
        android:hint="日程标题"
        app:boxBackgroundMode="outline">
        <TextInputEditText android:id="@+id/etTitle" />
    </TextInputLayout>
    
    <com.google.android.material.textfield.TextInputLayout
        android:hint="详细描述（可选）">
        <TextInputEditText android:id="@+id/etDescription" />
    </TextInputLayout>
</LinearLayout>
```

### 2. 添加和删除功能
```kotlin
// 添加日程
private fun addEvent(title: String, description: String = "") {
    val event = buildString {
        append("┌────────────────────────\n")
        append("│ 📅 $dateStr\n")
        append("│ 📝 $title\n")
        if (description.isNotEmpty()) {
            append("│ 💬 $description\n")
        }
        append("└────────────────────────")
    }
    eventsList.add(event)
    updateEventsList()
}

// 长按删除
tvEvents.setOnLongClickListener {
    showDeleteDialog()
    true
}
```

---

## 🎨 优化了什么

1. **Material Design 输入框** - 更专业的 UI
2. **卡片式布局** - 用边框包围每个日程
3. **Emoji 图标** - 📅📝💬 让信息更清晰
4. **长按删除** - 更符合移动端操作习惯
5. **等宽字体** - 让框线对齐美观
6. **浅灰背景 + 白色卡片** - 层次分明

---

## 💡 学到的知识

### 自定义布局的引入
```kotlin
// 1. 创建 XML 布局文件
// 2. 用 layoutInflater.inflate() 加载
val view = layoutInflater.inflate(R.layout.dialog_add_event, null)

// 3. 获取控件
val input = view.findViewById<EditText>(R.id.xxx)

// 4. 使用
AlertDialog.Builder().setView(view).show()
```

### Kotlin 实用技巧
- `buildString {}` - 构建字符串
- `isNotEmpty()` - 判断非空
- `trim()` - 去除首尾空格
- `mapIndexed {}` - 带索引的 map

---

## 📝 明日计划

**Day 3 目标**：Room 数据库 - 让数据永久保存

- [ ] 添加 Room 依赖
- [ ] 创建 Event 实体类
- [ ] 实现数据库 CRUD
- [ ] 重启 App 数据还在

---

**Day 2 完成！界面美观功能完整！** 🎉

**今日评分**：⭐⭐⭐⭐⭐ (5/5) - 超出预期！

