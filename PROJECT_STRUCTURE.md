# 📁 Ralendar 项目结构说明

**项目名称**: Ralendar - 智能日历应用  
**版本**: v1.0  
**最后更新**: 2025-11-08

---

## 🎯 项目概述

Ralendar 是一个全栈智能日历应用，支持多端（Web、Android、AcWing 平台），具备事件管理、邮件提醒、地图定位、第三方登录等功能。

---

## 📂 目录结构详解

```
Ralendar/
│
├── 📱 acapp/                          # AcWing 平台前端（构建产物）
│   └── dist/
│       ├── app.css                    # 单文件 CSS（657 KB）
│       ├── app.js                     # 单文件 JS（1.35 MB）
│       ├── favicon.ico
│       └── index.html
│
├── 📱 acapp_frontend/                  # AcWing 平台前端源码（Vue 3）
│   ├── src/                           # 源代码
│   │   ├── components/                # 组件
│   │   ├── views/                     # 视图页面
│   │   ├── store/                     # Vuex 状态管理
│   │   ├── assets/                    # 静态资源
│   │   ├── App.vue                    # 根组件
│   │   └── main.js                    # 入口文件
│   ├── public/                        # 公共资源
│   ├── package.json                   # 依赖配置
│   ├── babel.config.js                # Babel 配置
│   └── vue.config.js                  # Vue CLI 配置
│   │
│   └── 📝 说明：AcWing 平台版本的前端源码
│       构建后输出到 acapp/dist/
│       特点：单文件构建，适配 AcWing 平台
│
├── 📱 adapp/                           # Android 应用（Kotlin）
│   ├── app/
│   │   ├── src/
│   │   │   ├── main/
│   │   │   │   ├── java/              # Kotlin 源码
│   │   │   │   ├── res/               # 资源文件
│   │   │   │   └── AndroidManifest.xml
│   │   │   └── test/                  # 测试代码
│   │   └── build.gradle.kts           # 应用级构建配置
│   ├── gradle/                        # Gradle 配置
│   ├── build.gradle.kts               # 项目级构建配置
│   ├── settings.gradle.kts
│   └── PHASE_RECORD/                  # 开发记录
│       └── Day01~Day11.md             # 每日开发日志
│   │
│   └── 📝 说明：Android Development App
│       原生 Android 应用，使用 Kotlin 开发
│       包含日历 UI、事件管理、网络集成等功能
│
├── 🌐 web/                             # Web 前端（构建产物，生产环境）
│   ├── assets/
│   │   ├── index-*.js                 # 打包后的 JS（带哈希）
│   │   ├── index-*.css                # 打包后的 CSS（带哈希）
│   │   └── *.woff                     # 字体文件
│   ├── favicon.ico
│   ├── logo.png
│   └── index.html
│   │
│   └── 📝 说明：Web 版生产构建产物
│       由 web_frontend 构建生成
│       部署到服务器供用户访问
│
├── 🌐 web_frontend/                    # Web 前端源码（Vue 3 + Vite）⭐
│   ├── src/
│   │   ├── api/                       # API 请求封装
│   │   │   ├── auth.js                # 认证相关 API
│   │   │   ├── axios.js               # Axios 配置（拦截器）
│   │   │   └── index.js               # API 统一导出
│   │   │
│   │   ├── components/                # 可复用组件
│   │   │   ├── calendar/              # 日历相关组件
│   │   │   │   ├── CalendarGrid.vue   # 日历网格
│   │   │   │   ├── EventDialog.vue    # 事件编辑对话框
│   │   │   │   └── EventDetail.vue    # 事件详情
│   │   │   ├── map/                   # 地图组件
│   │   │   │   └── MapPicker.vue      # 地图选点
│   │   │   └── NavBar.vue             # 导航栏
│   │   │
│   │   ├── composables/               # 组合式 API（可复用逻辑）
│   │   │   └── useCalendar.js         # 日历逻辑
│   │   │
│   │   ├── views/                     # 页面视图
│   │   │   ├── account/               # 账号相关页面
│   │   │   │   ├── LoginView.vue      # 登录页面
│   │   │   │   ├── ProfileView.vue    # 个人中心
│   │   │   │   ├── AcWingCallback.vue # AcWing OAuth 回调
│   │   │   │   └── QQCallback.vue     # QQ OAuth 回调
│   │   │   └── CalendarView.vue       # 日历主页
│   │   │
│   │   ├── router/                    # Vue Router 路由配置
│   │   │   └── index.js
│   │   │
│   │   ├── stores/                    # Pinia 状态管理
│   │   │   └── user.js                # 用户状态
│   │   │
│   │   ├── styles/                    # 全局样式
│   │   │   └── main.css
│   │   │
│   │   ├── App.vue                    # 根组件
│   │   └── main.js                    # 入口文件
│   │
│   ├── public/                        # 公共资源
│   │   ├── favicon.ico
│   │   └── logo.png
│   │
│   ├── package.json                   # 依赖配置
│   ├── vite.config.js                 # Vite 构建配置
│   ├── jsconfig.json                  # JavaScript 配置
│   └── eslint.config.js               # ESLint 配置
│   │
│   └── 📝 说明：Web 版前端源码（主力开发）
│       使用 Vue 3 Composition API + Vite
│       构建后输出到 web/ 目录
│       特点：现代化、响应式、移动端优化
│
├── 🔧 backend/                         # Django 后端（核心）⭐
│   ├── api/                           # 主应用
│   │   ├── models/                    # 数据模型（模块化）
│   │   │   ├── __init__.py            # 统一导入
│   │   │   ├── user.py                # 用户模型（AcWingUser, QQUser）
│   │   │   ├── event.py               # 事件模型（Event）
│   │   │   └── calendar.py            # 日历模型（PublicCalendar）
│   │   │
│   │   ├── views/                     # API 视图（模块化）
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                # 认证相关（登录、注册、OAuth）
│   │   │   ├── user.py                # 用户信息（个人中心、统计）
│   │   │   ├── events.py              # 事件管理（CRUD）
│   │   │   ├── calendars.py           # 公共日历
│   │   │   ├── holidays.py            # 节假日查询
│   │   │   ├── lunar.py               # 农历转换
│   │   │   ├── fusion.py              # Roamio 集成（批量创建）
│   │   │   └── oauth_callback.py      # OAuth 回调处理
│   │   │
│   │   ├── url_patterns/              # URL 路由（模块化）
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                # 认证路由
│   │   │   ├── user.py                # 用户路由
│   │   │   ├── fusion.py              # 融合路由
│   │   │   └── utils.py               # 工具路由
│   │   │
│   │   ├── migrations/                # 数据库迁移文件
│   │   │   ├── 0001_initial.py
│   │   │   ├── 0002_event_reminder_minutes_...py
│   │   │   ├── 0005_acwinguser.py
│   │   │   ├── 0006_qquser.py
│   │   │   └── 0007_add_fusion_fields.py
│   │   │
│   │   ├── data/                      # 静态数据
│   │   │   └── holidays_2025.json     # 2025 年节假日
│   │   │
│   │   ├── serializers.py             # DRF 序列化器
│   │   ├── tasks.py                   # Celery 异步任务（邮件提醒）
│   │   ├── urls.py                    # 主 URL 配置
│   │   ├── admin.py                   # Django Admin 配置
│   │   ├── apps.py                    # 应用配置
│   │   └── __init__.py
│   │
│   ├── calendar_backend/              # Django 项目配置
│   │   ├── settings.py                # 核心设置（数据库、JWT、CORS）
│   │   ├── urls.py                    # 根 URL 路由
│   │   ├── celery.py                  # Celery 配置
│   │   ├── wsgi.py                    # WSGI 入口
│   │   ├── asgi.py                    # ASGI 入口
│   │   └── __init__.py
│   │
│   ├── static/                        # 静态文件
│   │   └── images/
│   │       ├── AcWing_logo.png
│   │       └── qq_login.png
│   │
│   ├── db.sqlite3                     # SQLite 数据库（开发环境）
│   ├── manage.py                      # Django 管理脚本
│   ├── requirements.txt               # Python 依赖
│   │
│   ├── 🚀 部署脚本
│   ├── deploy.sh                      # 一键部署脚本
│   ├── start_celery.sh                # 启动 Celery Worker + Beat
│   ├── migrate_to_shared_db.sh        # 迁移到共享数据库
│   ├── install_celery_only.sh         # 仅安装 Celery
│   ├── setup_email_step_by_step.sh    # 邮件提醒配置
│   │
│   ├── 🔧 服务器配置
│   ├── uwsgi.ini                      # uWSGI 配置
│   └── nginx.conf                     # Nginx 配置
│   │
│   └── 📝 说明：Django REST Framework 后端
│       提供所有 API 接口
│       使用 JWT 认证、Celery 异步任务
│       支持 SQLite（开发）和 MySQL（生产）
│
├── 📚 docs/                            # 项目文档（重组后）⭐
│   │
│   ├── 📖 guides/                     # 操作指南
│   │   ├── ACWING_LOGIN_GUIDE.md      # AcWing 登录集成指南
│   │   ├── ACWING_PLATFORM_CONFIG.md  # AcWing 平台配置
│   │   ├── DEPLOYMENT_GUIDE.md        # 部署指南
│   │   ├── MIGRATION_GUIDE.md         # 数据库迁移指南
│   │   ├── WEB_AUTH_GUIDE.md          # Web 认证指南
│   │   ├── BAIDU_MAP_SETUP.md         # 百度地图配置
│   │   └── EMAIL_REMINDER_GUIDE.md    # 邮件提醒配置
│   │
│   ├── 🏗️ architecture/               # 架构文档
│   │   ├── ARCHITECTURE.md            # 项目整体架构
│   │   ├── Component_Structure.md     # 组件结构设计
│   │   └── UNIFIED_REMINDER_ARCHITECTURE.md # 统一提醒架构
│   │
│   ├── 🔗 integration/                # 集成文档
│   │   ├── ROAMIO_INTEGRATION_GUIDE.md    # Roamio 集成指南（详细）
│   │   ├── ROAMIO_INTEGRATION_STATUS.md   # 集成状态
│   │   ├── ROAMIO_QUICKSTART.md           # 快速开始（5 分钟）
│   │   └── FUSION_PROGRESS.md             # 融合进度
│   │
│   ├── 📝 summaries/                  # 重构总结
│   │   ├── CODE_CLEANUP_SUMMARY.md    # 代码清理总结
│   │   ├── Component_Refactoring.md   # 组件重构
│   │   ├── CSS_REFACTORING_SUMMARY.md # CSS 重构
│   │   ├── URL_REFACTORING_SUMMARY.md # URL 重构
│   │   └── UX_OPTIMIZATION_SUMMARY.md # UX 优化总结
│   │
│   ├── 📅 daily_logs/                 # 开发日志
│   │   ├── DAY10_SUMMARY.md
│   │   ├── Day12_ACWING_LOGIN.md
│   │   ├── Day13_WEB_ACWING_LOGIN.md
│   │   ├── Day14_COMPLETE_SUMMARY.md
│   │   ├── Day14_QQ_LOGIN_AND_CLEANUP.md
│   │   ├── Day15_CODE_REFACTORING.md
│   │   ├── Day15_SUMMARY.md
│   │   ├── Day16_FINAL_SUMMARY.md
│   │   └── Day16_MAJOR_FEATURES_AND_INTEGRATION.md
│   │
│   ├── 🚀 plans/                      # 未来计划
│   │   ├── AI_ASSISTANT_PLAN.md       # AI 助手计划
│   │   ├── CALENDAR_SHARING_PLAN.md   # 日历分享计划
│   │   ├── Day15_PLAN.md              # Day15 计划
│   │   ├── FUTURE_PLAN.md             # 未来计划
│   │   ├── MAP_INTEGRATION_PLAN.md    # 地图集成计划
│   │   ├── PRODUCT_ROADMAP.md         # 产品路线图
│   │   └── RALENDAR_ROAMIO_FUSION_PLAN.md # 融合计划
│   │
│   ├── 📦 archive/                    # 归档（已过时或已完成）
│   │   ├── DAY12_PLAN.md
│   │   ├── Day13_PLAN.md
│   │   ├── Day14_PLAN.md
│   │   ├── FEATURES_SUMMARY.md
│   │   ├── FINAL_ARCHITECTURE.md
│   │   ├── PROJECT_STRUCTURE.md
│   │   └── REFACTORING_SUMMARY.md
│   │
│   ├── 🔌 api/                        # API 文档
│   │   └── ROAMIO_ECOSYSTEM_API_DOCUMENTATION.md
│   │
│   ├── README.md                      # 文档说明
│   └── INDEX.md                       # 文档索引
│
├── README.md                          # 项目主 README
└── PROJECT_STRUCTURE.md               # 本文件（项目结构说明）⭐

```

---

## 🔑 关键目录说明

### 1. **前端开发（3 套代码）**

| 目录 | 用途 | 技术栈 | 构建产物 |
|------|------|--------|---------|
| `acapp_frontend/` | AcWing 平台版 | Vue 3 + Webpack | `acapp/dist/` |
| `web_frontend/` | Web 版（主力）| Vue 3 + Vite | `web/` |
| `adapp/` | Android 版 | Kotlin | APK |

**为什么有 3 套前端？**
- **acapp_frontend**: AcWing 平台有特殊要求（单文件构建）
- **web_frontend**: 现代化的 Web 应用，支持代码分割
- **adapp**: 原生 Android 应用

### 2. **后端架构（Django）**

```
backend/
├── api/                    # 主应用（业务逻辑）
│   ├── models/             # 数据模型（按模块拆分）
│   ├── views/              # API 视图（按功能拆分）
│   ├── url_patterns/       # URL 路由（按模块拆分）
│   ├── serializers.py      # 序列化器
│   └── tasks.py            # 异步任务（Celery）
│
└── calendar_backend/       # 项目配置
    ├── settings.py         # 核心设置
    ├── urls.py             # 根路由
    └── celery.py           # Celery 配置
```

**设计原则**:
- ✅ 模块化（models、views、urls 分文件）
- ✅ 单一职责（每个文件负责一个功能模块）
- ✅ 易于维护和扩展

### 3. **文档结构（docs/）**

重组后的文档按功能分类：
- **guides/** - 如何做（How-to）
- **architecture/** - 架构设计（Design）
- **integration/** - 集成指南（Integration）
- **summaries/** - 总结回顾（Summary）
- **daily_logs/** - 开发日志（Logs）
- **plans/** - 未来计划（Plans）
- **archive/** - 已过时文档（Archive）

---

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/ppshuX/kotlin_calendar.git
cd Ralendar
```

### 2. 启动后端
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### 3. 启动前端（Web 版）
```bash
cd web_frontend
npm install
npm run dev
```

### 4. 构建 Web 生产版本
```bash
cd web_frontend
npm run build  # 输出到 ../web/
```

### 5. 构建 AcWing 版本
```bash
cd acapp_frontend
npm install
npm run build  # 输出到 ../acapp/dist/
```

---

## 📦 部署

### 生产环境（Linux 服务器）

```bash
# 1. 更新代码
cd ~/kotlin_calendar
git pull

# 2. 部署后端
cd backend
./deploy.sh

# 3. 启动 Celery（邮件提醒）
./start_celery.sh

# 4. 前端已构建好，Nginx 直接服务静态文件
```

**访问地址**:
- Web 版: https://app7626.acapp.acwing.com.cn/
- API: https://app7626.acapp.acwing.com.cn/api/v1/

---

## 🧩 核心技术栈

### 前端
- **Vue 3** (Composition API)
- **Vue Router** (路由)
- **Pinia** (状态管理)
- **Element Plus** (UI 组件库)
- **Axios** (HTTP 客户端)
- **Vite** (构建工具)

### 后端
- **Django 4.2**
- **Django REST Framework** (API)
- **Simple JWT** (JWT 认证)
- **Celery** (异步任务)
- **Redis** (消息队列)
- **MySQL / SQLite** (数据库)

### 移动端
- **Kotlin** (Android)
- **Jetpack Compose** (UI)
- **Room** (本地数据库)
- **Retrofit** (网络请求)

---

## 🔐 环境变量配置

在 `backend/` 目录创建 `.env` 文件：

```bash
# Django
DEBUG=False
SECRET_KEY=your-secret-key-here

# OAuth
ACWING_APPID=your-acwing-appid
ACWING_SECRET=your-acwing-secret
QQ_APPID=your-qq-appid
QQ_APPKEY=your-qq-appkey

# 邮件
EMAIL_HOST=smtp.qq.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@qq.com
EMAIL_HOST_PASSWORD=your-qq-authorization-code
DEFAULT_FROM_EMAIL=Ralendar <your-email@qq.com>

# Celery/Redis
CELERY_BROKER_URL=redis://localhost:6379/0

# 百度地图
BAIDU_MAP_AK=your-baidu-map-ak

# 数据库（可选，共享 Roamio 数据库）
USE_SHARED_DB=False
DB_HOST=your-mysql-host
DB_NAME=roamio_production
DB_USER=ralendar_user
DB_PASSWORD=your-db-password
```

---

## 📝 命名规范

### 项目名称演变
- **KotlinCalendar** → **Ralendar**
- **acapp** = AcWing App（平台版）
- **adapp** = Android Development App（移动端）

### 文件命名
- **组件**: PascalCase（如 `EventDialog.vue`）
- **视图**: PascalCase + View（如 `CalendarView.vue`）
- **工具**: camelCase（如 `useCalendar.js`）
- **配置**: kebab-case（如 `vite.config.js`）

---

## 🔗 相关链接

- **GitHub**: https://github.com/ppshuX/kotlin_calendar
- **生产环境**: https://app7626.acapp.acwing.com.cn
- **文档索引**: [docs/INDEX.md](docs/INDEX.md)
- **API 文档**: [docs/api/](docs/api/)

---

## 📞 联系方式

- **开发者**: ppshuX
- **QQ/邮箱**: 2064747320@qq.com
- **相关项目**: Roamio（旅行规划应用）

---

## ⚖️ 许可证

MIT License

---

**最后更新**: 2025-11-08  
**文档版本**: v1.0

