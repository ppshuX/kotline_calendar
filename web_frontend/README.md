# KotlinCalendar Web 管理端 🌐

Vue 3 + FullCalendar + Element Plus

---

## 🚀 快速开始

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

访问：http://localhost:5173/

---

## ✨ 功能特性

- 📅 **日历视图**
  - 月视图/周视图/日视图切换
  - FullCalendar 5 强大的日历组件
  
- ✏️ **日程管理**
  - 添加日程（点击日期）
  - 编辑日程（点击事件）
  - 删除日程
  - 设置提醒
  
- 🏮 **农历显示**
  - 查看任意日期的农历
  - 显示生肖
  
- 🔄 **实时同步**
  - 与 Django 后端 API 对接
  - 数据实时加载和保存

---

## 🎨 技术栈

- **Vue 3** - 渐进式 JavaScript 框架
- **Vue Router** - 官方路由
- **Pinia** - 状态管理
- **Element Plus** - Vue 3 UI 组件库
- **FullCalendar** - 强大的日历组件
- **Axios** - HTTP 客户端
- **Vite** - 现代化构建工具

---

## 📡 API 对接

### 配置后端地址

`src/api/index.js`:

```javascript
const api = axios.create({
  baseURL: 'http://localhost:8000/api',  // Django 后端地址
  timeout: 10000
})
```

### 可用 API

- `eventAPI.getAll()` - 获取所有日程
- `eventAPI.create(data)` - 创建日程
- `eventAPI.update(id, data)` - 更新日程
- `eventAPI.delete(id)` - 删除日程
- `lunarAPI.getLunarDate(date)` - 获取农历

---

## 📁 项目结构

```
web/calendar_web/
├── src/
│   ├── api/
│   │   └── index.js           # API 配置和封装
│   ├── views/
│   │   └── CalendarView.vue   # 日历主视图
│   ├── router/
│   │   └── index.js           # 路由配置
│   ├── App.vue                # 根组件
│   └── main.js                # 入口文件
├── public/
├── index.html
└── package.json
```

---

## 🎯 使用说明

### 1. 确保后端运行

```bash
# 在 backend/ 目录
python manage.py runserver
```

后端地址：http://localhost:8000/api/

---

### 2. 启动前端

```bash
# 在 web/calendar_web/ 目录
npm run dev
```

前端地址：http://localhost:5173/

---

### 3. 开始使用

1. **查看日历**：打开浏览器访问 http://localhost:5173/
2. **添加日程**：点击任意日期，填写表单
3. **查看详情**：点击日历上的事件
4. **测试农历**：点击"测试农历"按钮
5. **刷新数据**：点击"刷新"按钮

---

## 🐛 调试技巧

### 打开浏览器开发者工具

- **Chrome/Edge**: F12 或 Ctrl+Shift+I
- **Firefox**: F12 或 Ctrl+Shift+K

### 查看网络请求

1. 打开 Network（网络）标签
2. 操作日程
3. 查看 API 请求和响应

### 常见问题

**1. CORS 错误**

确保 Django 后端已配置 CORS：

```python
# backend/calendar_backend/settings.py
CORS_ALLOW_ALL_ORIGINS = True
```

**2. API 连接失败**

检查后端是否运行：

```bash
curl http://localhost:8000/api/events/
```

**3. FullCalendar 中文显示**

已配置 `locale: 'zh-cn'`

---

## 📸 界面截图

（待添加）

---

## 🚢 构建部署

### 构建生产版本

```bash
npm run build
```

生成的文件在 `dist/` 目录

### 部署到 Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    root /path/to/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api/ {
        proxy_pass http://localhost:8000;
    }
}
```

---

## 📝 开发记录

- ✅ 项目初始化
- ✅ Element Plus 集成
- ✅ FullCalendar 集成
- ✅ Axios API 配置
- ✅ 日程增删改查
- ✅ 农历功能
- ✅ 响应式设计

---

## 💡 未来计划

- [ ] 用户认证
- [ ] 数据统计图表
- [ ] 导出 PDF
- [ ] 拖拽修改日程
- [ ] 暗色模式
- [ ] 移动端适配

---

**开发者**: KotlinCalendar Team  
**License**: MIT
