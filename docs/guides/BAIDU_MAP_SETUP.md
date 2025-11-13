# 🗺️ 百度地图集成指南

> **创建日期**: 2025-11-08  
> **版本**: v1.0  
> **状态**: ✅ 已完成开发

---

## 📋 功能概览

### ✨ 已实现功能

- ✅ **地图选择器**：在创建/编辑事件时选择地点
- ✅ **POI 搜索**：搜索地点名称，快速定位
- ✅ **地图预览**：事件详情中显示迷你地图
- ✅ **导航链接**：一键打开百度地图导航
- ✅ **地理编码**：点击地图自动获取地址
- ✅ **响应式设计**：PC 和移动端完美适配

---

## 🔑 获取百度地图 AK（API Key）

### 步骤 1：注册百度地图开放平台

1. 访问：https://lbsyun.baidu.com/
2. 点击右上角"控制台"
3. 使用百度账号登录（或注册新账号）

### 步骤 2：创建应用

1. 进入控制台后，点击"应用管理" → "我的应用"
2. 点击"创建应用"
3. 填写应用信息：
   - **应用名称**：Ralendar（或你喜欢的名称）
   - **应用类型**：选择"浏览器端"
   - **启用服务**：勾选以下服务：
     - ✅ 地图 JS API
     - ✅ 地点搜索服务
     - ✅ 地理编码服务
4. 点击"提交"

### 步骤 3：获取 AK

创建成功后，会显示：
```
应用AK: 你的32位AK密钥
```

复制这个 AK（类似：`abcdefghijklmnopqrstuvwxyz123456`）

### 步骤 4：配置白名单（重要）

1. 在应用列表中找到刚创建的应用
2. 点击"设置" → "IP白名单配置"
3. 选择"IP校验"：
   - **开发环境**：添加 `localhost` 和 `127.0.0.1`
   - **生产环境**：添加服务器 IP（如：`47.121.137.60`）
   - **或者选择"无"**（不推荐，有配额限制风险）

---

## ⚙️ 配置步骤

### 1. 更新前端 index.html

编辑：`web_frontend/index.html`

找到这一行：
```html
<script type="text/javascript" src="https://api.map.baidu.com/api?v=3.0&ak=YOUR_BAIDU_MAP_AK"></script>
```

替换 `YOUR_BAIDU_MAP_AK` 为你的实际 AK：
```html
<script type="text/javascript" src="https://api.map.baidu.com/api?v=3.0&ak=你的32位AK"></script>
```

### 2. 更新后端配置（可选）

编辑：`backend/.env`

添加：
```bash
# 百度地图配置
BAIDU_MAP_AK=你的32位AK
```

这样后端也可以调用百度地图 API（如服务端地理编码）。

### 3. 重新构建前端

```bash
cd web_frontend
npm run build
```

### 4. 部署到服务器

```bash
git add -A
git commit -m "feat: integrate Baidu Maps with your AK"
git push

# 在服务器上
cd ~/kotlin_calendar
git pull
sudo /etc/init.d/nginx restart
```

---

## 🎯 使用指南

### 创建带地点的事件

1. 点击日历上的日期或"添加日程"按钮
2. 填写事件标题
3. **勾选"在地图上选择位置"**
4. 在地图中：
   - **方法1**：在搜索框输入地点名称（如"北京天安门"），点击搜索结果
   - **方法2**：直接在地图上点击位置
5. 地点和经纬度会自动填充
6. 可选：勾选"邮件提醒"，在事件前收到邮件
7. 点击"保存"

### 查看事件地图

1. 点击事件卡片查看详情
2. 如果事件有地理位置，会显示迷你地图
3. 点击"📍 导航"按钮，打开百度地图导航

---

## 📊 免费配额说明

百度地图开放平台提供免费额度：

| 服务 | 免费额度 | 说明 |
|------|---------|------|
| 地图 JS API | 每日 100,000 次 | 显示地图 |
| 地点搜索 | 每日 30,000 次 | POI 搜索 |
| 地理编码 | 每日 30,000 次 | 地址 ↔ 坐标 |

对于个人项目，完全够用！

---

## 🐛 常见问题

### Q1: 地图显示空白？

**原因**：AK 未配置或配置错误

**解决**：
1. 检查 `index.html` 中的 AK 是否正确
2. 打开浏览器开发者工具（F12）
3. 查看 Console 是否有错误信息
4. 确认 AK 的白名单配置

### Q2: 提示"服务未授权"？

**原因**：AK 未启用相应服务

**解决**：
1. 登录百度地图开放平台
2. 进入"应用管理"
3. 编辑应用，勾选所需服务
4. 等待几分钟生效

### Q3: 地图可以显示但搜索不工作？

**原因**：未启用"地点搜索服务"

**解决**：
在百度地图开放平台的应用设置中，启用"地点搜索服务"

---

## 🎨 界面展示

### 地图选择器
- 🔍 搜索框：输入地点名称快速定位
- 🗺️ 地图：点击选择精确位置
- 📍 标记：显示选中的位置
- ✅ 确认：自动填充地点和经纬度

### 事件详情
- 📍 地点显示：文字描述
- 🗺️ 迷你地图：可视化位置预览
- 🧭 导航按钮：一键打开百度地图

---

## 📱 移动端体验

- ✅ 地图高度自适应（PC: 400px, 移动: 300px）
- ✅ 搜索结果滚动列表
- ✅ 触摸友好的交互设计
- ✅ 导航按钮自动打开地图 App

---

## 🚀 技术实现

### 前端组件
```
components/
├── map/
│   └── MapPicker.vue        # 地图选择器（340行）
└── calendar/
    ├── EventDialog.vue      # 集成地图选择器
    └── EventDetail.vue      # 地图预览
```

### 后端支持
```python
class Event(models.Model):
    latitude = models.FloatField()        # 纬度
    longitude = models.FloatField()       # 经度
    map_provider = models.CharField()     # 地图服务商
    
    @property
    def map_url(self):
        # 自动生成百度地图导航链接
        return f"https://api.map.baidu.com/marker?..."
```

---

## 📖 参考文档

- [百度地图开放平台](https://lbsyun.baidu.com/)
- [JavaScript API 文档](https://lbsyun.baidu.com/index.php?title=jspopular3.0)
- [POI 搜索文档](https://lbsyun.baidu.com/index.php?title=jspopular3.0/guide/search)

---

**祝你使用愉快！** 🗺️✨

