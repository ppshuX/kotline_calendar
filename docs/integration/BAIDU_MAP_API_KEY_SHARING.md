# 🗺️ 百度地图 API Key 共享说明

> **发送方**: Ralendar 团队  
> **接收方**: Roamio 团队  
> **日期**: 2025-11-09  
> **主题**: 百度地图 API Key 共享

---

## 📍 **Ralendar 的百度地图配置**

### **API Key (AK)**：
```
i8UmOotWSekjTJlPbydOk1xQZuUeGeE1
```

### **API 版本**：
```
v3.0
```

### **引入方式**：
```html
<script 
  type="text/javascript" 
  src="https://api.map.baidu.com/api?v=3.0&ak=i8UmOotWSekjTJlPbydOk1xQZuUeGeE1"
></script>
```

---

## ✅ **可以共享！**

**答案**：可以使用我们的 API Key！✅

**理由**：
1. 我们是同一个开发者账号的两个项目
2. 百度地图的配额通常比较充裕
3. 当前 Ralendar 使用量很小
4. 数据格式统一更方便

---

## 📊 **使用限制和配额**

### **百度地图 API 配额（免费版）**：

| 服务 | 每日配额 | 当前使用 |
|------|---------|---------|
| 地图显示 | 无限制 | 很少 |
| 定位服务 | 6,000 次/天 | < 100 |
| 地点搜索 | 6,000 次/天 | < 50 |
| 地理编码 | 6,000 次/天 | < 50 |

**Ralendar 当前使用**：
- 每天约 50-100 次地图加载
- 远低于配额限制

**Roamio 预估使用**：
- 每天约 100-200 次
- 合计：200-300 次/天
- **占配额：< 5%** ✅

**结论**：完全够用！不需要担心配额！

---

## ⚠️ **使用注意事项**

### **1. 域名白名单**

需要在百度地图控制台添加 Roamio 的域名：

**当前已配置**：
- `app7626.acapp.acwing.com.cn` (Ralendar)

**需要添加**：
- `roamio.cn` (Roamio)

**操作步骤**：
```
1. 登录：https://lbsyun.baidu.com/apiconsole/key
2. 找到对应的 AK
3. 设置 → 白名单 → 添加域名
4. 添加：roamio.cn
5. 保存
```

---

### **2. Referer 检查**

百度地图会检查请求来源，确保：
```javascript
// 在 Roamio 的 HTML 中引入
<script 
  type="text/javascript" 
  src="https://api.map.baidu.com/api?v=3.0&ak=i8UmOotWSekjTJlPbydOk1xQZuUeGeE1"
></script>
```

---

### **3. 使用建议**

#### **推荐做法** ✅：
- 只在前端使用（浏览器直接加载）
- 不要在后端使用（会暴露 IP）
- 遵守百度地图使用协议
- 不要滥用 API

#### **不推荐** ❌：
- 不要用于非地图场景
- 不要频繁调用（添加防抖）
- 不要在循环中调用

---

## 🗺️ **集成示例**

### **在 Roamio 中引入百度地图**

#### **步骤 1：在 HTML 中引入**

```html
<!-- Roamio 的 index.html -->
<!DOCTYPE html>
<html>
<head>
  <title>Roamio</title>
  
  <!-- 百度地图 API -->
  <script 
    type="text/javascript" 
    src="https://api.map.baidu.com/api?v=3.0&ak=i8UmOotWSekjTJlPbydOk1xQZuUeGeE1"
  ></script>
</head>
<body>
  <div id="app"></div>
</body>
</html>
```

#### **步骤 2：创建地图选择组件**

```vue
<template>
  <div class="map-picker">
    <div id="roamio-map" style="height: 400px;"></div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'

const selectedLocation = ref({
  name: '',
  lat: null,
  lng: null
})

onMounted(() => {
  // 初始化地图
  const map = new BMap.Map('roamio-map')
  const point = new BMap.Point(116.404, 39.915)
  map.centerAndZoom(point, 15)
  
  // 添加控件
  map.addControl(new BMap.NavigationControl())
  
  // 点击地图选择位置
  map.addEventListener('click', (e) => {
    const point = e.point
    
    // 反向地理编码
    const geocoder = new BMap.Geocoder()
    geocoder.getLocation(point, (result) => {
      selectedLocation.value = {
        name: result.address,
        lat: point.lat,
        lng: point.lng
      }
    })
  })
})
</script>
```

#### **步骤 3：使用组件**

```vue
<template>
  <el-form-item label="地点">
    <el-input v-model="form.location" />
    <el-button @click="showMap = true">📍 选择位置</el-button>
  </el-form-item>
  
  <el-dialog v-model="showMap" title="选择地点">
    <MapPicker @select="handleLocationSelect" />
  </el-dialog>
</template>

<script setup>
const handleLocationSelect = (location) => {
  form.location = location.name
  form.latitude = location.lat
  form.longitude = location.lng
  showMap.value = false
}
</script>
```

---

## 📦 **可以直接复用 Ralendar 的组件！**

我们可以把 `MapPicker.vue` 组件打包提供给你们！

**组件功能**：
- ✅ 地点搜索
- ✅ 地图点击选择
- ✅ 自动定位
- ✅ 反向地理编码
- ✅ 已选位置显示

**使用方式**：
```vue
<MapPicker 
  v-model:location="form.location"
  v-model:latitude="form.latitude"
  v-model:longitude="form.longitude"
  :initial-lat="39.915"
  :initial-lng="116.404"
/>
```

---

## ⚖️ **配额监控**

### **如果未来配额不够**

可以考虑：

#### **方案 A：升级为付费版**
- 每月约 50 元
- 配额增加到 100,000 次/天
- 两个项目共享成本

#### **方案 B：Roamio 申请独立 AK**
- 免费申请
- 独立配额
- 互不影响

#### **方案 C：使用不同地图服务**
- 高德地图（类似配额）
- 腾讯地图（我们用 QQ 登录，可能有优惠）

---

## 🎯 **推荐方案**

### **当前阶段（测试和开发）** ⭐

**使用 Ralendar 的 AK**：
```
AK: i8UmOotWSekjTJlPbydOk1xQZuUeGeE1
```

**优点**：
- ✅ 快速开始，无需申请
- ✅ 数据格式统一
- ✅ 配额充足

**需要做**：
- ⏳ 我在百度地图控制台添加 Roamio 域名白名单

---

### **未来（正式上线后）**

**可选择**：
- 继续共享（如果配额够用）
- 或申请独立 AK（完全独立）

---

## 🔧 **我现在需要做什么**

### **添加 Roamio 域名到白名单**

```
1. 登录百度地图开放平台
2. 找到 AK: i8UmOotWSekjTJlPbydOk1xQZuUeGeE1
3. 设置 → 白名单
4. 添加：roamio.cn
5. 保存
```

**完成后通知你们！** ✅

---

## 📝 **给 Roamio 团队的完整信息**

### **百度地图 AK**：
```
i8UmOotWSekjTJlPbydOk1xQZuUeGeE1
```

### **API 引入**：
```html
<script 
  type="text/javascript" 
  src="https://api.map.baidu.com/api?v=3.0&ak=i8UmOotWSekjTJlPbydOk1xQZuUeGeE1"
></script>
```

### **使用限制**：
- 每日地点搜索：6,000 次
- 每日地理编码：6,000 次
- 地图显示：无限制
- **当前使用：< 5%** ✅

### **注意事项**：
1. 等我添加域名白名单（5 分钟）
2. 只在前端使用，不要在后端
3. 搜索功能添加防抖（debounce 300ms）
4. 遵守百度地图使用协议

### **参考代码**：
- `web_frontend/src/components/map/MapPicker.vue`
- 可以直接复用或参考

---

## 🎁 **额外提供**

### **MapPicker 组件源码**

如果你们需要，我可以：
1. 提供完整的 MapPicker.vue 源码
2. 或打包成 npm 包
3. 或提供使用示例

---

## ✅ **总结**

**可以使用！** ✅

- **AK**: `i8UmOotWSekjTJlPbydOk1xQZuUeGeE1`
- **配额**: 充足（< 5% 使用率）
- **限制**: 等我添加域名白名单
- **建议**: 参考 Ralendar 的 MapPicker 组件

**我现在去添加 Roamio 域名白名单，5 分钟后通知你们！** 🚀

---

**有其他问题随时问！** 🤝

---

**Ralendar 团队**  
**ppshuX**  
**2025-11-09 12:00**

