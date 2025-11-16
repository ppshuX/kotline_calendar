# 📝 Ralendar 项目说明（给小白看的版本）

> 不用懂太多技术，也能看懂 Ralendar 是什么、能做什么、怎么跑起来。

---

## 1. 这个项目是干嘛的？

**Ralendar = 智能日历 + 节假日 + 第三方授权**

你可以把它想成一个「更聪明的日历」：

- 能像手机日历一样 **新增 / 编辑 / 删除日程**；
- 会自动显示 **中国节假日、传统节日**；
- 支持用 **QQ / AcWing 登录**，不用记密码；
- 还能让别的应用（比如 **Roamio 旅行规划**）通过授权的方式访问你的日历。

目前项目已经上线，网页地址是：

- `https://app7626.acapp.acwing.com.cn`

---

## 2. 整个项目长什么样？

从结构上看，可以简单分成三部分：

- `backend/`：后端（Django），处理接口、数据库、登录、OAuth 授权等；
- `web_frontend/`：前端源码（Vue3），开发时用；
- `web/`：前端打包后的静态文件，线上就是用这一份；

再加上一些辅助的目录：

- `docs/`：文档（你现在看的这个文件就在这里）；
- `adapp/`、`acapp/`：Android 和 AcWing 平台相关（课程作业的延伸，暂时可以先不管）。

你只要关心：**前端 = web_frontend + web，后端 = backend**。

---

## 3. 主要功能一览（用人话讲）

### 3.1 日历界面

打开 Web 页面，你能看到：

- 左边是一块大日历：
  - 支持「月视图 / 日视图 / 自定义周视图」；
  - 日期格子里会有：
    - 一个小圆点，表示这一天有多少个事件（颜色越深事情越多）；
    - 一条小条文字，表示这一天是什么节日（比如「🎉 元旦」）。
- 右边是一个侧边栏：
  - 显示「今天 / 选中日期」的日程列表；
  - 显示该日期的节日详情（包括传统节日、国际节日）。

### 3.2 节日和农历

后端内置了一个节假日同步脚本，会把一年里的节假日数据导入到数据库。前端通过接口：

- `/api/v1/holidays/?year=2025` 获取全年节日；
- `/api/v1/holidays/today/` 获取今天的节日；
- `/api/v1/holidays/check/?date=YYYY-MM-DD` 检查某一天是不是节日。

前端会根据这些数据：

- 在日历格子里加上节日小标签；
- 在右侧节日面板里展示详细说明。

### 3.3 登录和账号

目前主要的登录方式是：

- QQ 登录（通过 QQ 互联）；
- AcWing 登录（通过 AcWing 平台）。

登录之后你就有了一个属于自己的账号，可以：

- 管理自己的日程；
- 以后可以绑定多种登录方式（例如 QQ + 邮箱）。

### 3.4 和 Roamio 的授权连接

这是本项目比较大的亮点：**自建了一个 OAuth2 授权服务器**。

当你在 Roamio 中点击「连接 Ralendar」时，会发生：

1. Roamio 打开 `https://app7626.acapp.acwing.com.cn/oauth/authorize?...`；
2. Ralendar 显示一个授权页面：
   - 顶部展示「Roamio 请求访问你的 Ralendar」；
   - 中间列出 Roamio 想要的权限（读取日历、写入日历、读取基本信息等）；
   - 底部有「取消」和「授权」按钮；
3. 你点击「授权」后，Ralendar 会：
   - 生成一个授权码 `code`；
   - 把你重定向回 Roamio 的回调地址 `redirect_uri`；
4. Roamio 再用这个 `code` 调用 Ralendar 的 `/oauth/token` 换取 `access_token`；
5. 之后 Roamio 就可以通过 `/oauth/userinfo`、`/api/v1/fusion/...` 等接口访问你的日历。

整个过程和「微信授权登录第三方应用」的流程类似，只是这里是「Roamio 授权访问 Ralendar」。

---

## 4. 小白如何在本地跑起来？

> 前提：你只想在自己的电脑上跑「后端 + Web 前端」，不必搭建整套生产环境。

### 4.1 准备环境

- 安装好 **Python 3.8+**；
- 安装好 **Node.js 18+**；
- 安装好 **Git**。

### 4.2 克隆代码

```bash
git clone https://github.com/ppshuX/kotline_calendar.git
cd kotline_calendar
```

### 4.3 启动后端（开发模式）

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 初始化数据库（使用自带的 SQLite）
python manage.py migrate

# 启动开发服务器
python manage.py runserver
```

看到类似 `Starting development server at http://127.0.0.1:8000/` 就说明后端起好了。

### 4.4 启动前端（开发模式）

```bash
cd web_frontend

# 安装依赖
npm install

# 启动前端
npm run dev
```

终端会提示一个本地地址，例如：`http://localhost:5173`。  
用浏览器打开，就能看到本地开发版的 Ralendar 界面。

> 注意：本地开发环境会调用本地的后端（你可以在 `web_frontend/src/api/index.js` 中查看和修改接口基础地址）。

---

## 5. 线上部署的关键点（只看个大概就行）

线上部署和本地最大的区别是：

- 有一个 **Nginx** 在前面做入口：
  - `/api/`、`/oauth/`、`/admin/` 等接口转发到 uWSGI（Django）；
  - `/` 默认返回 `web/` 目录里的静态前端；
  - `/terms` 和 `/privacy` 单独转发到 Django，由模板渲染用户协议和隐私政策。
- Django 不是用 `runserver` 跑，而是用 **uWSGI** 常驻在后台。

你暂时不需要完全掌握 Nginx 和 uWSGI 的细节，只要知道：

- 开发环境：`npm run dev` + `python manage.py runserver`；
- 生产环境：`web/` 静态文件 + Nginx + uWSGI。

---

## 6. 代码结构（非常简化版）

只列出和「日历 + 授权」强相关的部分：

- 后端 `backend/api/`
  - `models/event.py`：日程事件模型；
  - `models/calendar_data.py`：节假日、黄历等模型；
  - `models/oauth.py`：OAuth 客户端、授权码、访问令牌模型；
  - `views/calendar/events.py`：事件相关 API；
  - `views/external/holidays.py`：节假日相关 API；
  - `views/oauth/authorize.py`：授权页面和授权逻辑；
  - `views/oauth/token.py`：用 code 换 token；
  - `views/oauth/userinfo.py`：向 Roamio 等外部应用提供用户信息。

- 前端 `web_frontend/src/`
  - `views/CalendarView.vue`：主界面（日历 + 侧边栏）；
  - `components/calendar/HolidayPanel.vue`：节日列表与详情；
  - `composables/useHolidayData.js`：节假日数据获取与处理；
  - `composables/useCalendarEvents.js`：日程数据获取与 FullCalendar 配置。

---

## 7. 现在项目大概做到什么程度？

已经完成：

- ✅ Web 端日历界面（桌面端 + 移动端）；
  - 自定义圆点、节日标签、侧边栏。
- ✅ 节假日数据同步与展示；
- ✅ QQ / AcWing 登录；
- ✅ 自建 OAuth2 服务端 + Roamio 集成；
- ✅ 用户协议、隐私政策页面；
- ✅ 线上部署（Nginx + uWSGI）。

后续可以继续做的：

- 邮件提醒 / 手机推送；
- 更细致的个人中心（绑定/解绑多种登录方式）；
- AI 辅助创建日程；
- 更多统计分析（这周/这月忙不忙，习惯养成等）。

---

如果你是老师、评审或者第一次接触这个项目，希望这个文档能帮你快速弄清楚：

- 这是一个什么样的系统；
- 大概有哪些功能；
- 技术上是怎么分层的；
- 怎么在本地跑起来体验。

更深入的技术细节，可以参考根目录的 `README.md` 和 `docs/` 里的各种指南。 👍


