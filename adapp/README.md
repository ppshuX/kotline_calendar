# Android Calendar App (adapp)

**Android Development App** - KotlinCalendar 移动端

---

## 📱 应用说明

这是一个独立的 Android 客户端应用，**不需要部署到服务器**。

### 运行环境
- **客户端**：Android 手机/平板/模拟器
- **后端 API**：`https://app7626.acapp.acwing.com.cn/api`

---

## 🚀 开发 & 使用

### 1. 本地开发

```bash
# 打开 Android Studio
# File → Open → 选择 adapp 目录

# 或者使用命令行编译
cd adapp
./gradlew assembleDebug
```

### 2. 安装到手机

#### **方式一：USB 调试（推荐）**

1. 手机开启开发者选项 + USB 调试
2. USB 连接电脑
3. Android Studio → Run (Shift + F10)
4. 选择你的设备

#### **方式二：生成 APK 手动安装**

```bash
# 1. 生成 Debug APK
./gradlew assembleDebug

# APK 位置：
# adapp/app/build/outputs/apk/debug/app-debug.apk

# 2. 安装到手机
# 方式 A: ADB 命令
adb install app/build/outputs/apk/debug/app-debug.apk

# 方式 B: 直接传输
# 把 app-debug.apk 发送到手机 → 点击安装
```

#### **方式三：发布版 APK**

```bash
# 生成 Release APK（需要签名）
./gradlew assembleRelease

# 配置签名：app/build.gradle.kts
# signingConfigs { ... }
```

---

## ⚙️ 功能特性

### ✅ 已实现功能

- 📅 **日历视图**：月视图展示
- ✏️ **日程管理**：增删改查
- 🔔 **提醒通知**：AlarmManager + Notification
- 💾 **本地存储**：Room 数据库
- 🌐 **网络同步**：Retrofit 调用云端 API
- 🏮 **农历显示**：查看农历日期
- 📡 **日历订阅**：订阅网络日历

### 技术栈

- **语言**：Kotlin
- **UI**：Material Design 3
- **数据库**：Room
- **网络**：Retrofit 2 + OkHttp
- **异步**：Kotlin Coroutines
- **架构**：MVVM

---

## 🔧 配置说明

### API 配置

后端 API 地址在 `RetrofitClient.kt` 中配置：

```kotlin
// adapp/app/src/main/java/com/ncu/kotlincalendar/api/RetrofitClient.kt
private const val BASE_URL = "https://app7626.acapp.acwing.com.cn/api/"
```

如果需要切换到本地测试：
```kotlin
// 本地测试
private const val BASE_URL = "http://10.0.2.2:8000/api/"  // Android 模拟器
// 或
private const val BASE_URL = "http://192.168.x.x:8000/api/"  // 真机（局域网 IP）
```

### 权限配置

`AndroidManifest.xml` 已包含必要权限：
```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
<uses-permission android:name="android.permission.SCHEDULE_EXACT_ALARM" />
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
```

---

## 📦 项目结构

```
adapp/
├── app/
│   └── src/main/
│       ├── java/com/ncu/kotlincalendar/
│       │   ├── MainActivity.kt          # 主界面
│       │   ├── Event.kt                 # 日程实体
│       │   ├── EventDao.kt              # 数据访问
│       │   ├── AppDatabase.kt           # Room 数据库
│       │   ├── EventAdapter.kt          # RecyclerView 适配器
│       │   ├── ReminderManager.kt       # 提醒管理
│       │   ├── AlarmReceiver.kt         # 闹钟接收器
│       │   └── api/
│       │       ├── RetrofitClient.kt    # 网络客户端
│       │       ├── CalendarApi.kt       # API 接口定义
│       │       └── ApiModels.kt         # API 数据模型
│       └── res/
│           └── layout/
│               ├── activity_main.xml    # 主布局
│               ├── dialog_add_event.xml # 添加日程对话框
│               └── item_event.xml       # 日程列表项
└── build.gradle.kts                     # Gradle 配置
```

---

## 🐛 调试技巧

### 查看日志

```bash
# 查看应用日志
adb logcat -s KotlinCalendar

# 或在 Android Studio 的 Logcat 窗口中过滤
```

### 清除应用数据

```bash
# 清除数据库和缓存
adb shell pm clear com.ncu.kotlincalendar
```

### 网络调试

1. 确保手机和服务器网络互通
2. 检查 API URL 配置
3. 查看 OkHttp 日志（已启用 HttpLoggingInterceptor）

---

## 📤 发布流程（可选）

如果要公开发布应用：

### 1. 生成签名密钥

```bash
keytool -genkey -v -keystore my-release-key.jks \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias my-key-alias
```

### 2. 配置 build.gradle.kts

```kotlin
android {
    signingConfigs {
        create("release") {
            storeFile = file("my-release-key.jks")
            storePassword = "your-password"
            keyAlias = "my-key-alias"
            keyPassword = "your-password"
        }
    }
    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
            isMinifyEnabled = true
            proguardFiles(...)
        }
    }
}
```

### 3. 生成发布版 APK

```bash
./gradlew assembleRelease
# 输出: app/build/outputs/apk/release/app-release.apk
```

### 4. 发布到应用商店

- **Google Play**: https://play.google.com/console
- **华为应用市场**: https://developer.huawei.com/
- **小米应用商店**: https://dev.mi.com/
- **其他国内应用市场**

---

## ❓ 常见问题

### Q1: 为什么 adapp 不部署到服务器？
**A**: Android 应用是客户端软件，运行在用户手机上，不需要部署到服务器。服务器上只需要部署后端 API（backend）。

### Q2: 如何更新应用？
**A**: 
- 开发阶段：重新编译 → 覆盖安装
- 发布后：上传新版本到应用商店 → 用户更新

### Q3: API 连接失败？
**A**: 检查：
1. 手机网络是否正常
2. API 地址是否正确（`RetrofitClient.kt`）
3. 服务器防火墙是否开放（HTTPS 443 端口）
4. 模拟器使用 `10.0.2.2` 代替 `localhost`

### Q4: 本地测试如何配置？
**A**: 
```kotlin
// 修改 RetrofitClient.kt
// 生产环境
private const val BASE_URL = "https://app7626.acapp.acwing.com.cn/api/"
// 本地测试
private const val BASE_URL = "http://10.0.2.2:8000/api/"  // 模拟器
```

---

## 🔗 相关文档

- [项目总览](../README.md)
- [后端部署](../DEPLOYMENT_GUIDE.md)
- [API 文档](../backend/README.md)
- [开发日志](./PHASE_RECORD/)

---

## 📞 支持

**学校**: 南昌大学  
**课程**: Android 开发  
**技术栈**: Kotlin + Room + Retrofit + Material Design  

---

**注意**：此应用仅用于学习和演示，不建议直接用于生产环境。
