# AcWing 平台配置指南

## 📋 项目架构说明

### 端命名约定

- **adapp** = **Android Development App**（Android 移动端）
- **acapp** = **AcWing App**（AcWing 平台集成端，未来计划）

### 当前项目结构

```
Ralendar/
├── adapp/          # Android App（移动端开发版本）
├── backend/        # Django 后端 API
├── web/            # Vue3 Build 产物（单文件）
└── web_frontend/   # Vue3 源码（开发用）
```

---

## 🎯 AcWing 平台配置

### 应用信息

- **域名**: `https://app7626.acapp.acwing.com.cn`
- **服务器 IP**: `47.121.137.60`（已迁移到阿里云）
- **AppID**: `7626`

### 文件配置（已优化为单文件）

| 配置项 | 值 | 说明 |
|--------|-----|------|
| **CSS 地址** | `https://app7626.acapp.acwing.com.cn/assets/app.css` | ✅ 单个 CSS 文件（657 KB） |
| **JS 地址** | `https://app7626.acapp.acwing.com.cn/assets/app.js` | ✅ 单个 JS 文件（1.35 MB） |
| **主类名** | `Calendar` | ✅ 单个主类 |

### 构建配置

在 `web_frontend/vite.config.js` 中已配置：

```javascript
build: {
  outDir: '../web',
  emptyOutDir: true,
  chunkSizeWarningLimit: 2000,
  rollupOptions: {
    output: {
      // 禁用代码分割，只生成单个 JS 和 CSS
      manualChunks: undefined,
      entryFileNames: 'assets/app.js',
      chunkFileNames: 'assets/app.js',
      assetFileNames: (assetInfo) => {
        if (assetInfo.name.endsWith('.css')) {
          return 'assets/app.css';
        }
        return 'assets/[name][extname]';
      },
    },
  },
}
```

---

## 🚀 部署流程

### 1. 本地构建

```bash
cd web_frontend
npm run build
```

**输出结果**：
```
../web/index.html         0.56 kB
../web/assets/app.css     657 KB   ← 单个 CSS
../web/assets/app.js      1.35 MB  ← 单个 JS
```

### 2. 提交到 Git

```bash
git add -A
git commit -m "build: update web bundle"
git push
```

### 3. 服务器部署

```bash
# SSH 登录服务器
ssh acs@app7626.acapp.acwing.com.cn

# 更新代码
cd ~/kotlin_calendar
git pull

# 重启后端（如需要）
cd backend
./deploy.sh
```

### 4. 验证部署

访问以下 URL 确认文件可访问：
- CSS: https://app7626.acapp.acwing.com.cn/assets/app.css
- JS: https://app7626.acapp.acwing.com.cn/assets/app.js
- 前端: https://app7626.acapp.acwing.com.cn/

---

## ✅ 配置检查清单

- [x] 只生成一个 `app.js` 文件
- [x] 只生成一个 `app.css` 文件
- [x] 主类名为 `Calendar`
- [x] 项目重命名：`acapp` → `adapp`（Android Development App）
- [x] 为未来预留 `acapp`（AcWing App 集成）

---

## 📝 AcWing 平台配置步骤

1. **登录 AcWing 平台**: https://www.acwing.com/
2. **进入应用管理**: 应用 → kotlin_calendar
3. **配置文件地址**:
   - CSS 地址: `https://app7626.acapp.acwing.com.cn/assets/app.css`
   - JS 地址: `https://app7626.acapp.acwing.com.cn/assets/app.js`
   - 主类名: `Calendar`
4. **保存配置**

---

## 🔄 后续更新流程

每次修改前端后：

```bash
# 1. 本地构建
cd web_frontend
npm run build

# 2. 提交代码
git add web/
git commit -m "build: update web bundle"
git push

# 3. 服务器更新
ssh acs@app7626.acapp.acwing.com.cn
cd ~/kotlin_calendar
git pull
```

---

## 💡 技术说明

### 为什么使用单文件构建？

1. **AcWing 平台要求**: 只能配置一个 CSS 和一个 JS 文件
2. **简化部署**: 无需配置多个文件路径
3. **减少 HTTP 请求**: 单文件加载更快

### 代码分割 vs 单文件

| 方式 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **代码分割** | 按需加载、首屏快 | 多个 HTTP 请求 | 普通 Web 应用 |
| **单文件** | 部署简单、平台兼容 | 文件较大（1.35 MB） | AcWing 等平台 |

### 性能优化

虽然是单文件，但已启用 gzip 压缩：
- `app.js`: 1.35 MB → 438 KB (gzip)
- `app.css`: 657 KB → 92 KB (gzip)

---

## 📞 相关链接

- **GitHub**: https://github.com/ppshuX/kotline_calendar
- **生产域名**: https://app7626.acapp.acwing.com.cn
- **API 文档**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

**最后更新**: 2025-11-06

