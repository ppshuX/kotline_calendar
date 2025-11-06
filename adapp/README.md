
# 📅 Kotlin Calendar App

一个基于 **MaterialCalendarView** 实现的 Android 日历应用，使用 Kotlin 构建，支持 Material 3 主题，适合入门项目练习与功能扩展。

---

## 🚀 功能特性

- 基于 `MaterialCalendarView` 的日历视图
- 支持 Material 设计风格
- Kotlin 语言编写
- AndroidX + ViewCompat 边缘适配
- 适配 Android API 24~36

---

## 📁 项目结构

```

KotlinCalendar/
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/ncu/kotlincalendar/
│   │   │   │   └── MainActivity.kt      # 主界面逻辑
│   │   │   ├── res/
│   │   │   │   └── layout/activity_main.xml  # 主界面布局
│   │   │   └── AndroidManifest.xml
├── build.gradle.kts
└── settings.gradle.kts

````

---

## 🧩 使用的依赖

```kotlin
// 核心依赖
implementation(libs.androidx.core.ktx)
implementation(libs.androidx.appcompat)
implementation(libs.material)
implementation(libs.androidx.activity)
implementation(libs.androidx.constraintlayout)

// 测试相关
testImplementation(libs.junit)
androidTestImplementation(libs.androidx.junit)
androidTestImplementation(libs.androidx.espresso.core)
````

📌 **下一步添加：**

```kotlin
// 添加 MaterialCalendarView
implementation("com.prolificinteractive:material-calendarview:1.7.0")
```

---

## 🔧 快速开始

1. 克隆本仓库：

   ```bash
   git clone https://github.com/ppshuX/kotline_calendar.git
   ```

2. 在 Android Studio 中打开项目。

3. 确保你已添加所需依赖（如 `MaterialCalendarView`）。

4. 运行项目，即可看到基础日历界面。

---

## 🧱 开发计划（可选）

* [ ] 日历自定义主题样式
* [ ] 点击日期弹出详细事项
* [ ] 增加事件提醒功能
* [ ] 数据持久化（Room）

---

## ✍️ 作者

* 🎓 项目开发者：J.Grigg（2023届南昌大学软件工程专业）


---

## 📜 License

本项目仅用于学习交流，暂未添加开源协议，如需使用请注明来源。

