# AcWing App (acapp)

**纯 Vue3 CDN 方案** - 无构建工具，极简开发

---

## 🎯 技术特色

- ❌ 无 Vue CLI
- ❌ 无 Vite
- ❌ 无 npm/node_modules
- ❌ 无 Bootstrap
- ✅ **纯 Vue3 CDN**
- ✅ **纯手写 CSS**（BEM 命名）
- ✅ **直接写 HTML/JS/CSS**

---

## 📁 文件结构

```
acapp/
├── index.html       # 本地测试入口
├── src/
│   ├── app.js       # 业务逻辑（~300 行）
│   └── app.css      # 样式（~350 行）
├── PLAN.md          # 详细开发计划
└── README.md        # 本文档
```

**总代码量**：< 700 行（不含注释）  
**文件体积**：< 50KB（压缩前）

---

## 🚀 本地开发

### 方式 1：直接打开（推荐）

```bash
# 双击打开 index.html
# 或者右键 → 打开方式 → 浏览器
```

### 方式 2：简单服务器

```bash
# Python 3
cd acapp
python -m http.server 8080

# 访问 http://localhost:8080
```

### 方式 3：VS Code Live Server

```
1. 安装 Live Server 扩展
2. 右键 index.html → Open with Live Server
```

---

## 🌐 部署到服务器

### 1. 上传文件

```bash
# 上传 JS 和 CSS
scp src/app.js src/app.css acs@app7626.acapp.acwing.com.cn:~/acapp/
```

### 2. AcWing 平台配置

- **CSS 地址**: `https://app7626.acapp.acwing.com.cn/acapp/app.css`
- **JS 地址**: `https://app7626.acapp.acwing.com.cn/acapp/app.js`
- **主类名**: `Calendar`

---

## 📝 代码说明

### `index.html`

```html
<!-- Vue 3 CDN -->
<script src="https://cdn.jsdelivr.net/npm/vue@3/dist/vue.global.prod.js"></script>

<!-- 业务代码 -->
<link rel="stylesheet" href="src/app.css">
<script src="src/app.js"></script>

<!-- 容器 -->
<div id="calendar-container"></div>

<!-- 初始化 -->
<script>
  new Calendar(document.getElementById('calendar-container'));
</script>
```

### `src/app.js`

```javascript
// 解构 Vue3 API（从 CDN 加载的全局变量）
const { createApp, ref, computed, onMounted } = Vue;

// 导出 Calendar 类
class Calendar {
  constructor(parent) {
    this.app = createApp({
      setup() {
        // Vue3 Composition API
        const events = ref([]);
        
        const fetchEvents = async () => {
          const res = await fetch('API_URL');
          events.value = await res.json();
        };
        
        onMounted(fetchEvents);
        
        return { events, fetchEvents };
      },
      
      template: `<div class="kc-calendar">...</div>`
    });
    
    this.app.mount(parent);
  }
}

window.Calendar = Calendar;
```

### `src/app.css`

```css
/* BEM 命名，kc- 前缀防止冲突 */
.kc-calendar { /* 容器 */ }
.kc-header { /* 头部 */ }
.kc-btn { /* 按钮 */ }
.kc-grid { /* 日历网格 */ }
.kc-event-item { /* 日程项 */ }
```

---

## 🎨 样式隔离

所有 CSS 类名都使用 **`.kc-`** 前缀（KotlinCalendar）：

- ✅ `.kc-calendar` - 不会冲突
- ✅ `.kc-btn` - 不会影响其他应用
- ❌ `.btn` - 可能和 Bootstrap 冲突

---

## 🔧 修改代码

### 修改样式

直接编辑 `src/app.css`：

```css
.kc-btn {
  background: #409eff; /* 修改颜色 */
  padding: 10px 20px;  /* 修改大小 */
}
```

### 修改逻辑

直接编辑 `src/app.js`：

```javascript
const fetchEvents = async () => {
  // 修改 API 地址
  const response = await fetch('YOUR_API_URL');
  // ...
};
```

### 修改模板

在 `app.js` 中修改 `template` 字符串：

```javascript
template: `
  <div class="kc-calendar">
    <h1>我的日历</h1>  <!-- 修改标题 -->
    <!-- ... -->
  </div>
`
```

---

## 📦 可选：压缩代码

如果需要减小文件体积：

```bash
# 使用在线工具
# https://jscompress.com/
# https://cssminifier.com/

# 或使用命令行工具
npx terser src/app.js -o src/app.min.js -c -m
npx cssnano src/app.css src/app.min.css
```

---

## 🆚 与 Web 端的区别

| 特性 | Web 端 | AcWing 端 |
|------|--------|----------|
| Vue3 引入 | npm install | **CDN** |
| 构建工具 | Vite | **无** |
| UI 库 | Bootstrap + Element Plus | **纯手写** |
| 文件数量 | ~30 个 | **3 个** |
| 代码体积 | 1.34MB | **<50KB** |
| 开发方式 | `npm run dev` | **直接打开HTML** |
| 部署方式 | `npm run build` + git | **scp 直接上传** |

---

## ❓ 常见问题

### Q: 为什么不用 Vue CLI？
**A**: 为了展示技术多样性，acapp 采用最原始的方式开发，不依赖构建工具。

### Q: 为什么不用 Bootstrap？
**A**: AcWing 平台是沙箱环境，多个应用共存。Bootstrap 的全局 CSS 会影响其他应用。

### Q: 如何调试？
**A**: 在浏览器中打开 `index.html`，按 F12 打开开发者工具。

### Q: 可以用 TypeScript 吗？
**A**: 不建议。使用 TS 就需要构建工具，违背了"无构建"的初衷。

### Q: 性能如何？
**A**: 
- Vue3 从 CDN 加载（不计入文件体积）
- 业务代码 <50KB（非常小）
- 性能优秀

---

## 🔗 相关文档

- [PLAN.md](PLAN.md) - 详细开发计划
- [ARCHITECTURE.md](../ARCHITECTURE.md) - 三客户端架构
- [Vue 3 文档](https://cn.vuejs.org/)

---

**极简、轻量、原生！这就是 acapp 的魅力！** ✨

