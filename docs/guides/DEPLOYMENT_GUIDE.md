# KotlinCalendar 完整部署指南

本文档说明如何管理和部署整个项目（后端 + 前端 + Android）

## 🌐 生产环境信息

- **域名**: https://app7626.acapp.acwing.com.cn
- **服务器 IP**: 47.121.137.60（已迁移到阿里云）
- **SSH 登录**: `ssh acs@app7626.acapp.acwing.com.cn`
- **API 地址**: https://app7626.acapp.acwing.com.cn/api
- **前端地址**: https://app7626.acapp.acwing.com.cn

---

## 📂 项目结构

```
KotlinCalendar/
├── adapp/                # Android App（Android Development App）
├── backend/              # Django 后端 API
├── web/                  # Vue3 Build 产物（提交到 Git，服务器部署）
└── web_frontend/         # Vue3 源码（不提交 Git，仅本地开发）
```

---

## 🎯 部署策略

### **后端（Backend）**
- ✅ Git 管理（提交到仓库）
- ✅ 服务器上用 `git pull` 更新
- ✅ 不包含敏感信息（db.sqlite3、logs、*.pid）

### **前端（Web）**
- ✅ **源码**（`web_frontend/`）：Git 管理，仅本地开发
- ✅ **Build 产物**（`web/`）：**提交到 Git**，服务器 `git pull` 部署
- ✅ 本地 build 后提交，服务器不需要 Node.js

### **Android（adapp）**
- ✅ Git 管理（版本控制）
- ❌ **不部署到服务器**（Android 应用在手机上运行）
- ✅ 本地编译成 APK 后安装到手机
- ✅ 使用方式：
  - USB 调试 → Android Studio 直接运行
  - 生成 APK → 手动安装到手机
  - 发布到应用商店（可选）
- 📱 adapp = Android Development App（移动端）
- ⏳ acapp = AcWing App（未来计划，Web 端集成）

---

## 🚀 完整部署流程

### **一、初次部署**

#### 1. 本地准备

```bash
# 克隆项目
git clone <your-repo-url>
cd KotlinCalendar

# 安装前端依赖
cd web/calendar_web
npm install
cd ../..
```

#### 2. 服务器部署后端

```bash
# 服务器上
cd ~
git clone <your-repo-url> kotlin_calendar
cd kotlin_calendar/backend

# 安装依赖
pip3 install -r requirements.txt

# 修改配置
nano calendar_backend/settings.py
# 修改：DEBUG = False, ALLOWED_HOSTS = ['app7626.acapp.acwing.com.cn']

# 数据库迁移
python3 manage.py migrate

# 启动服务
./deploy.sh
```

#### 3. 本地 Build 并上传前端

```bash
# 本地
cd web/calendar_web

# 修改 API 地址
# src/api/index.js: baseURL = 'https://app7626.acapp.acwing.com.cn/api'

# Build
npm run build

# 上传到服务器
scp -r dist/* acs@app7626.acapp.acwing.com.cn:~/kotlin_calendar/web/
```

#### 4. 配置 Nginx

```bash
# 服务器上
sudo cp ~/kotlin_calendar/backend/nginx.conf /etc/nginx/nginx.conf
sudo nginx -t
sudo systemctl reload nginx
```

---

### **二、日常更新流程**

#### **更新后端（使用 Git）**

```bash
# 本地修改后
git add backend/
git commit -m "feat: 新功能描述"
git push

# 服务器上更新
cd ~/kotlin_calendar
git pull
cd backend
uwsgi --reload uwsgi.pid  # 或 ./deploy.sh
```

#### **更新前端（使用 SCP）**

**方法1：手动**

```bash
# 本地 build
cd web/calendar_web
npm run build

# 上传
scp -r dist/* acs@app7626.acapp.acwing.com.cn:~/kotlin_calendar/web/
```

**方法2：使用部署脚本（推荐）**

```bash
# 本地
cd web
chmod +x deploy_web.sh
./deploy_web.sh
```

#### **更新 Android App**

```bash
# 本地修改后
git add acapp/
git commit -m "feat: Android 新功能"
git push

# Build APK（Android Studio）
# Build → Generate Signed Bundle/APK
```

---

## 📋 Git 工作流

### **提交规范**

```bash
# 只提交后端
git add backend/
git commit -m "feat: 新增农历 API"

# 只提交前端源码
git add web/calendar_web/
git commit -m "feat: 优化日历 UI"

# 只提交 Android
git add acapp/
git commit -m "fix: 修复通知 Bug"

# 提交所有（小心不要提交 build 产物）
git status  # 检查一下
git add .
git commit -m "feat: 全栈更新"
```

### **分支管理（可选）**

```bash
# 开发新功能
git checkout -b feature/new-api
# ... 开发 ...
git commit -m "feat: 新功能"
git push origin feature/new-api

# 合并到主分支
git checkout main
git merge feature/new-api
git push
```

---

## 🔧 服务器端 Git 管理

### **方案1：完整克隆（推荐）**

```bash
# 服务器上克隆整个仓库
cd ~
git clone <your-repo-url> kotlin_calendar

# 更新时只 pull backend
cd ~/kotlin_calendar
git pull  # 会拉取所有更新，但只用 backend
```

**优点**：简单，和本地一致  
**缺点**：服务器上有不需要的前端源码（但不影响使用）

### **方案2：Sparse Checkout（只要 backend）**

```bash
# 服务器上只克隆 backend
cd ~
git clone --no-checkout <your-repo-url> kotlin_calendar
cd kotlin_calendar
git sparse-checkout init --cone
git sparse-checkout set backend
git checkout main

# 更新
git pull
```

**优点**：服务器上只有 backend，干净  
**缺点**：配置稍复杂

---

## 📝 .gitignore 说明

已配置的忽略规则：

```gitignore
# 前端 build 产物（不提交）
web/js/
web/css/
web/images/

# 前端依赖
web/calendar_web/node_modules/
web/calendar_web/dist/

# 后端敏感文件
backend/db.sqlite3
backend/logs/
backend/*.pid

# Android build
acapp/build/
acapp/.gradle/
```

**原则**：
- ✅ 提交：源代码、配置文件、依赖列表（requirements.txt, package.json）
- ❌ 不提交：Build 产物、依赖包、日志、数据库、临时文件

---

## 🎯 最佳实践

### **1. 环境变量管理**

**生产环境配置**（服务器）：
```bash
# backend/calendar_backend/settings.py
DEBUG = False
ALLOWED_HOSTS = ['app7626.acapp.acwing.com.cn']
```

**开发环境配置**（本地）：
```bash
DEBUG = True
ALLOWED_HOSTS = ['*']
```

**建议**：使用环境变量或单独的 `settings_prod.py`

### **2. 数据库备份**

```bash
# 服务器上定期备份
cd ~/kotlin_calendar/backend
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d)
```

### **3. 前端 API 地址管理**

**本地开发**：
```javascript
// src/api/index.js
baseURL: 'http://127.0.0.1:8000/api'
```

**生产环境**：
```javascript
// src/api/index.js
baseURL: 'https://app7626.acapp.acwing.com.cn/api'
```

**建议**：使用环境变量（`.env.development` 和 `.env.production`）

---

## ✅ 部署检查清单

### **后端部署**
- [ ] 代码已推送到 Git
- [ ] 服务器上 `git pull` 成功
- [ ] `settings.py` 已配置（DEBUG=False, ALLOWED_HOSTS）
- [ ] 数据库已迁移（`python3 manage.py migrate`）
- [ ] uWSGI 已启动（`ps aux | grep uwsgi`）
- [ ] API 可访问（`curl https://app7626.acapp.acwing.com.cn/api/`）

### **前端部署**
- [ ] API 地址已修改为生产环境
- [ ] `npm run build` 成功
- [ ] 文件已上传到服务器 `~/kotlin_calendar/web/`
- [ ] Nginx 配置正确
- [ ] 网站可访问（`https://app7626.acapp.acwing.com.cn/`）

### **Android 部署**
- [ ] `BASE_URL` 已改为生产环境 API
- [ ] APK 已签名
- [ ] 测试连接成功

---

## 🐛 常见问题

### **Q1：git pull 后前端也变了？**

**A**：没关系！服务器上的前端是从 `web/js/css/` 读取的，不是从 `web/calendar_web/src/` 读取。前端源码在服务器上不会被使用。

### **Q2：每次都要手动 scp 上传前端？**

**A**：使用 `web/deploy_web.sh` 脚本一键部署！或者考虑使用 CI/CD（GitHub Actions、Jenkins）。

### **Q3：数据库如何迁移到生产环境？**

**A**：
```bash
# 本地导出
python manage.py dumpdata > data.json

# 上传到服务器
scp data.json acs@server:~/kotlin_calendar/backend/

# 服务器导入
python3 manage.py loaddata data.json
```

---

**部署策略已明确！后端用 Git，前端用 SCP！** ✅

