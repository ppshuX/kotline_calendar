# Android 客户端 (adapp)

**Android Development App** - 移动端日历应用

---

## 📱 说明

这是 KotlinCalendar 的 **Android 移动端客户端**。

- **类型**：Android 原生应用（Kotlin）
- **运行环境**：Android 手机/平板
- **开发方式**：本地 Android Studio 开发
- **部署方式**：编译成 APK 安装到手机

---

## ⚠️ 注意

**Android 应用源码不在服务器上**

- ✅ 完整源码在本地开发环境
- ✅ 使用 Android Studio 开发
- ✅ 编译成 APK 后安装到手机
- ❌ 不需要部署到云服务器

---

## 🎯 技术栈

- **语言**：Kotlin
- **UI**：Material Design 3
- **数据库**：Room
- **网络**：Retrofit 2
- **架构**：MVVM
- **异步**：Kotlin Coroutines

---

## 🔗 API 对接

Android 客户端通过 Retrofit 调用后端 API：

```kotlin
// API 地址
private const val BASE_URL = "https://app7626.acapp.acwing.com.cn/api/"
```

---

## 📦 功能特性

- 📅 日历视图（月视图）
- ✏️ 日程管理（增删改查）
- 🔔 提醒通知（AlarmManager）
- 💾 本地存储（Room 数据库）
- 🌐 网络同步（Retrofit API）
- 🏮 农历显示
- 📡 日历订阅

---

## 🚀 安装使用

### 方式 1：USB 调试
1. 手机开启开发者选项
2. USB 连接电脑
3. Android Studio → Run

### 方式 2：APK 安装
1. 本地编译生成 APK
2. 发送到手机安装

---

## 📂 本地开发目录

```
本地 D:\KotlinProjects\KotlinCalendar\adapp\
├── app/
│   ├── src/main/
│   │   ├── java/             # Kotlin 源码
│   │   ├── res/              # 资源文件
│   │   └── AndroidManifest.xml
│   └── build.gradle.kts
├── gradle/
├── build.gradle.kts
└── settings.gradle.kts
```

---

## 🔗 相关链接

- [项目总览](../README.md)
- [后端部署](../DEPLOYMENT_GUIDE.md)
- [架构说明](../ARCHITECTURE.md)

---

**adapp = Android Development App（移动端）**  
**未来计划：acapp = AcWing App（平台集成端）**
