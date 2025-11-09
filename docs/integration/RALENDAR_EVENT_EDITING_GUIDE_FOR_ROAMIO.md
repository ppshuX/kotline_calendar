# 📝 Ralendar 事件编辑功能说明文档

> **目标读者**: Roamio 团队  
> **用途**: 参考 Ralendar 的编辑功能来优化 Roamio 的事件编辑界面  
> **日期**: 2025-11-09

---

## 🎯 **文档目的**

本文档详细说明 Ralendar 的事件编辑功能和选项，供 Roamio 团队参考：
- 了解 Ralendar 支持哪些编辑字段
- 参考编辑界面的设计
- 了解邮件提醒和地图功能
- 优化 Roamio 的编辑体验

---

## 📋 **Ralendar 事件的完整字段**

### **基础字段**

| 字段 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| `title` | String | ✅ 是 | 事件标题 | "北京五日游 - Day 1" |
| `description` | Text | ❌ 否 | 事件描述 | "14:00 抵达首都机场..." |
| `start_time` | DateTime | ✅ 是 | 开始时间 | "2025-11-15T14:00:00+08:00" |
| `end_time` | DateTime | ❌ 否 | 结束时间 | "2025-11-15T18:00:00+08:00" |

### **地点字段**

| 字段 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| `location` | String | ❌ 否 | 地点名称 | "北京首都国际机场" |
| `latitude` | Float | ❌ 否 | 纬度 | 40.0799 |
| `longitude` | Float | ❌ 否 | 经度 | 116.6031 |
| `map_provider` | String | ❌ 否 | 地图提供商 | "baidu"（默认） |

**注意**：
- 如果提供地理坐标，latitude 和 longitude 必须同时存在
- Ralendar 使用百度地图
- 用户可以通过地图选择器选择位置

### **提醒字段**

| 字段 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| `reminder_minutes` | Integer | ❌ 否 | 提前多少分钟提醒 | 60（提前1小时） |
| `email_reminder` | Boolean | ❌ 否 | 是否发送邮件提醒 | true |

**提醒时间选项**：
- 15 分钟
- 30 分钟
- 1 小时（60 分钟）
- 2 小时（120 分钟）
- 1 天（1440 分钟）
- 自定义

### **来源追踪字段**（由 Ralendar 自动设置）

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `source_app` | String | 来源应用 | "roamio" |
| `source_id` | String | 来源 ID | "trip_123" |
| `related_trip_slug` | String | 关联旅行 slug | "beijing-trip-2025" |

### **系统字段**（只读）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | Integer | 事件 ID |
| `user` | ForeignKey | 所属用户 |
| `created_at` | DateTime | 创建时间 |
| `updated_at` | DateTime | 更新时间 |
| `notification_sent` | Boolean | 提醒是否已发送 |

---

## 🎨 **Ralendar 编辑界面设计**

### **界面布局**

```
┌────────────────────────────────────────┐
│  创建/编辑事件               [X 关闭]  │
├────────────────────────────────────────┤
│                                        │
│  标题   [________________输入框______] │
│                                        │
│  时间   [2025-11-15 14:00] 至          │
│         [2025-11-15 18:00]             │
│                                        │
│  位置   [________________输入框______] │
│         [📍 在地图上选择]              │
│         ┌──────────────────────────┐  │
│         │   [地图预览]             │  │
│         │   北京首都国际机场       │  │
│         └──────────────────────────┘  │
│                                        │
│  描述   ┌────────────────────────┐    │
│         │ 多行文本框             │    │
│         │                        │    │
│         └────────────────────────┘    │
│                                        │
│  提醒   [▼ 提前 1 小时]                │
│         [✓] 邮件提醒                   │
│                                        │
│  ──────────────────────────────────   │
│         [取消]         [保存]         │
└────────────────────────────────────────┘
```

---

## 🔧 **编辑功能详解**

### **1. 标题编辑** 📝

**UI 组件**：单行输入框（el-input）

**特点**：
- 必填项
- 最大长度：200 字符
- 自动 trim 空格

**验证**：
```javascript
rules: {
  title: [
    { required: true, message: '请输入事件标题' },
    { max: 200, message: '标题不能超过 200 字符' }
  ]
}
```

---

### **2. 时间编辑** ⏰

**UI 组件**：日期时间选择器（el-date-picker）

**特点**：
- 开始时间必填
- 结束时间可选（默认为开始时间 + 1小时）
- 时间格式：`YYYY-MM-DD HH:mm:ss`
- 时区：自动使用本地时区（Asia/Shanghai）

**选择器配置**：
```javascript
{
  type: 'datetime',
  format: 'YYYY-MM-DD HH:mm',
  valueFormat: 'YYYY-MM-DDTHH:mm:ss',
  placeholder: '选择时间'
}
```

**时间范围验证**：
```javascript
// 结束时间必须晚于开始时间
if (end_time && end_time <= start_time) {
  return '结束时间必须晚于开始时间'
}
```

---

### **3. 地点编辑** 📍

**UI 组件**：输入框 + 地图选择器

**方式 A：直接输入**
```html
<el-input 
  v-model="form.location" 
  placeholder="输入地点名称"
/>
```

**方式 B：地图选择**（更推荐）
```html
<MapPicker 
  v-model:location="form.location"
  v-model:latitude="form.latitude"
  v-model:longitude="form.longitude"
/>
```

**地图选择器功能**：
1. 搜索地点（百度地图 API）
2. 点击地图选择位置
3. 自动获取地址和坐标
4. 显示已选位置卡片

**数据格式**：
```json
{
  "location": "北京首都国际机场",
  "latitude": 40.0799,
  "longitude": 116.6031,
  "map_provider": "baidu"
}
```

**地图 API 密钥**：
```javascript
// 百度地图 AK
const BAIDU_MAP_AK = 'YOUR_BAIDU_MAP_KEY'
```

---

### **4. 描述编辑** 📄

**UI 组件**：多行文本框（el-input type="textarea"）

**特点**：
- 可选字段
- 支持多行输入
- 最大长度：2000 字符
- 自动高度调整（autosize）

**配置**：
```javascript
{
  type: 'textarea',
  rows: 4,
  autosize: { minRows: 4, maxRows: 10 },
  placeholder: '添加事件描述...',
  maxlength: 2000,
  showWordLimit: true
}
```

---

### **5. 提醒设置** ⏰📧

#### **A. 提醒时间**

**UI 组件**：下拉选择器（el-select）

**选项**：
```javascript
[
  { label: '不提醒', value: 0 },
  { label: '准时', value: 0 },
  { label: '提前 15 分钟', value: 15 },
  { label: '提前 30 分钟', value: 30 },
  { label: '提前 1 小时', value: 60 },
  { label: '提前 2 小时', value: 120 },
  { label: '提前 1 天', value: 1440 }
]
```

**默认值**：15 分钟

#### **B. 邮件提醒**

**UI 组件**：复选框（el-checkbox）

**特点**：
- 需要用户设置了邮箱
- 需要配置邮件服务器
- 通过 Celery 异步发送

**邮件内容**：
```
主题：📅 Ralendar Logo [日程提醒] 标题
内容：
  - 日程标题
  - 开始时间
  - 地点（如果有）
  - 描述（如果有）
  - Ralendar Logo
```

**发送时机**：
```
事件开始时间 - reminder_minutes = 发送时间
```

---

## 📊 **完整事件数据示例**

### **最小示例（只有必填字段）**：
```json
{
  "title": "测试事件",
  "start_time": "2025-11-20T10:00:00+08:00"
}
```

### **完整示例（所有字段）**：
```json
{
  "title": "北京五日游 - Day 1: 抵达北京",
  "description": "搭乘 CA1234 航班抵达首都机场，预计 14:00 到达。\n入住酒店：北京希尔顿酒店\n晚餐：全聚德烤鸭",
  "start_time": "2025-11-15T14:00:00+08:00",
  "end_time": "2025-11-15T18:00:00+08:00",
  "location": "北京首都国际机场",
  "latitude": 40.0799,
  "longitude": 116.6031,
  "map_provider": "baidu",
  "reminder_minutes": 120,
  "email_reminder": true,
  "source_app": "roamio",
  "related_trip_slug": "beijing-trip-2025"
}
```

---

## 🔄 **事件 CRUD 操作**

### **1. 创建事件（CREATE）**

**端点**：
```
POST /api/v1/fusion/events/batch/
```

**请求体**：
```json
{
  "source_app": "roamio",
  "unionid": "xxx",  // 推荐添加
  "related_trip_slug": "trip-slug",
  "events": [
    {
      "title": "事件标题",
      "start_time": "2025-11-20T10:00:00+08:00",
      "description": "...",
      "location": "...",
      ...
    }
  ]
}
```

**响应**：
```json
{
  "success": true,
  "created_count": 1,
  "events": [
    {
      "id": 123,
      "title": "事件标题",
      ...所有字段...
    }
  ]
}
```

---

### **2. 更新事件（UPDATE）**

**端点**：
```
PUT /api/v1/events/{event_id}/
PATCH /api/v1/events/{event_id}/  (部分更新)
```

**请求体**：
```json
{
  "title": "修改后的标题",
  "start_time": "2025-11-20T11:00:00+08:00",
  "reminder_minutes": 30
}
```

**响应**：
```json
{
  "id": 123,
  "title": "修改后的标题",
  ...更新后的所有字段...
}
```

**注意**：
- PUT：需要所有字段
- PATCH：只需要要修改的字段

---

### **3. 查询事件（READ）**

#### **查询所有事件**：
```
GET /api/v1/events/
```

#### **查询单个事件**：
```
GET /api/v1/events/{event_id}/
```

#### **查询旅行相关事件**：
```
GET /api/v1/fusion/events/by-trip/{trip_slug}/
```

**响应**：
```json
{
  "trip_slug": "beijing-trip",
  "events_count": 5,
  "events": [...]
}
```

---

### **4. 删除事件（DELETE）**

#### **删除单个事件**：
```
DELETE /api/v1/events/{event_id}/
```

#### **删除旅行的所有事件**：
```
DELETE /api/v1/fusion/events/by-trip/{trip_slug}/delete/
```

**响应**：
```json
{
  "success": true,
  "deleted_count": 5
}
```

---

## 🎨 **Ralendar 编辑界面特点**

### **1. 表单布局**

```
┌─────────────────────────────────────┐
│  [字段标签]  [输入控件............] │  ← 左右布局
│                                     │
│  标题       [________________]      │  ← 单行输入
│  时间       [日期选择器] 至         │  ← 双日期选择
│             [日期选择器]            │
│  位置       [________________]      │  ← 输入 + 地图
│             [📍 在地图上选择]       │
│  描述       ┌─────────────────┐     │  ← 多行输入
│             │                 │     │
│             └─────────────────┘     │
│  提醒       [下拉选择 ▼]            │  ← 选择器
│             [✓] 邮件提醒            │  ← 复选框
└─────────────────────────────────────┘
```

### **2. 实时验证**

- ✅ 标题为空 → 显示错误提示
- ✅ 时间冲突 → 显示警告
- ✅ 结束时间早于开始时间 → 阻止提交
- ✅ 只有 latitude 或只有 longitude → 提示需要同时填写

### **3. 用户体验优化**

#### **智能默认值**：
```javascript
// 创建时
{
  start_time: 当前选中的日期 + 当前时间,
  end_time: start_time + 1小时,
  reminder_minutes: 15,
  email_reminder: false
}

// 编辑时
{
  // 保留所有原始值
}
```

#### **快捷操作**：
- 🗺️ 点击"在地图上选择" → 弹出地图选择器
- ⏰ 点击时间 → 日期时间选择器
- 📧 悬停邮件图标 → 显示提示"需要设置邮箱"

#### **视觉反馈**：
- ✅ 保存成功 → 绿色提示："✅ 添加成功"
- ❌ 保存失败 → 红色提示："❌ 保存失败：xxx"
- ⏳ 保存中 → 按钮显示 loading 动画

---

## 🗺️ **地图选择功能详解**

### **百度地图集成**

**功能**：
1. **地点搜索**
   ```javascript
   // 搜索 API
   const localSearch = new BMap.LocalSearch(map, {
     onSearchComplete: (results) => {
       // 显示搜索结果
     }
   })
   localSearch.search('北京首都机场')
   ```

2. **地图点击选择**
   ```javascript
   map.addEventListener('click', (e) => {
     const point = e.point  // {lng, lat}
     // 反向地理编码获取地址
   })
   ```

3. **自动定位**
   ```javascript
   const geolocation = new BMap.Geolocation()
   geolocation.getCurrentPosition((position) => {
     // 显示当前位置
   })
   ```

**MapPicker 组件数据流**：
```
用户输入地点名称 → 搜索建议
    ↓
用户点击建议 → 地图定位
    ↓
用户在地图上点击 → 获取坐标
    ↓
反向地理编码 → 获取详细地址
    ↓
✅ 返回：location, latitude, longitude
```

---

## 📧 **邮件提醒功能详解**

### **发送条件**

```python
# Celery Beat 每分钟检查
if event.email_reminder and not event.notification_sent:
    reminder_time = event.start_time - timedelta(minutes=event.reminder_minutes)
    
    if now >= reminder_time and now < reminder_time + timedelta(minutes=2):
        # 发送邮件
        send_event_reminder_email.delay(event.id)
```

### **邮件模板**

**主题**：
```
[Ralendar Logo] 日程提醒 | 事件标题
```

**内容**（HTML）：
```html
<!DOCTYPE html>
<html>
<head>
    <style>
        .container { max-width: 600px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #667eea, #764ba2); }
        .logo-section img { width: 80px; }
        .event-info { padding: 20px; }
        .event-title { font-size: 24px; font-weight: bold; }
        .event-time { color: #667eea; font-size: 18px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo-section">
            <img src="https://app7626.acapp.acwing.com.cn/logo.png" alt="Ralendar">
        </div>
        <div class="header">
            <h2>日程提醒</h2>
        </div>
        <div class="event-info">
            <div class="event-title">🎯 事件标题</div>
            <div class="event-time">📅 2025年11月15日 14:00</div>
            <div class="event-location">📍 北京首都国际机场</div>
            <div class="event-description">描述内容...</div>
        </div>
        <div class="footer">
            <a href="https://app7626.acapp.acwing.com.cn/calendar">查看日历</a>
        </div>
    </div>
</body>
</html>
```

---

## 💡 **Roamio 可以参考的优化**

### **1. 快速填充功能** ⚡

```javascript
// 根据旅行计划自动填充
function autoFillFromTrip(trip) {
  return {
    title: `${trip.title} - Day ${dayNumber}`,
    start_time: trip.dates[dayNumber].morning,
    end_time: trip.dates[dayNumber].evening,
    location: trip.destinations[dayNumber],
    description: `行程安排：\n${trip.itinerary[dayNumber]}`
  }
}
```

### **2. 批量编辑** 📦

```javascript
// 选中多个事件，批量修改提醒时间
function batchUpdateReminder(eventIds, reminderMinutes) {
  eventIds.forEach(id => {
    updateEvent(id, { reminder_minutes: reminderMinutes })
  })
}
```

### **3. 模板功能** 📋

```javascript
// 保存常用设置为模板
const templates = [
  {
    name: '会议模板',
    reminder_minutes: 30,
    email_reminder: true,
    duration_hours: 1
  },
  {
    name: '旅行模板',
    reminder_minutes: 120,
    email_reminder: true,
    duration_hours: 8
  }
]
```

### **4. 智能建议** 🤖

```javascript
// 根据标题智能建议
function suggestSettings(title) {
  if (title.includes('会议')) {
    return { reminder_minutes: 30, duration: 1 }
  }
  if (title.includes('飞机') || title.includes('航班')) {
    return { reminder_minutes: 120, duration: 4 }
  }
  if (title.includes('火车')) {
    return { reminder_minutes: 60, duration: 2 }
  }
  return { reminder_minutes: 15, duration: 1 }
}
```

---

## 🎯 **推荐的 Roamio 编辑功能**

### **基础编辑**（必须有）：
- ✅ 标题
- ✅ 时间（开始/结束）
- ✅ 描述

### **进阶功能**（推荐添加）：
- ✅ 地点（文本输入）
- ✅ 地图选择（如果有地图 API）
- ✅ 提醒时间选择
- ✅ 邮件提醒开关

### **高级功能**（可选）：
- 重复事件（每天/每周/每月）
- 事件分类/标签
- 优先级设置
- 参与人员
- 附件上传

---

## 📱 **移动端适配建议**

### **布局调整**：
```css
@media (max-width: 768px) {
  /* 全宽显示 */
  .el-dialog {
    width: 90vw !important;
  }
  
  /* 标签和输入框上下排列 */
  .el-form-item {
    display: flex;
    flex-direction: column;
  }
  
  /* 地图选择器简化 */
  .map-picker {
    height: 200px;  /* 桌面端 400px */
  }
}
```

---

## 🔧 **前端组件代码示例**

### **Vue 3 事件表单**：

```vue
<template>
  <el-dialog v-model="visible" title="编辑事件" width="600px">
    <el-form :model="form" :rules="rules" ref="formRef">
      <!-- 标题 -->
      <el-form-item label="标题" prop="title">
        <el-input v-model="form.title" placeholder="请输入事件标题" />
      </el-form-item>
      
      <!-- 时间 -->
      <el-form-item label="开始时间" prop="start_time">
        <el-date-picker 
          v-model="form.start_time" 
          type="datetime"
          placeholder="选择开始时间"
        />
      </el-form-item>
      
      <el-form-item label="结束时间">
        <el-date-picker 
          v-model="form.end_time" 
          type="datetime"
          placeholder="选择结束时间"
        />
      </el-form-item>
      
      <!-- 地点 -->
      <el-form-item label="地点">
        <el-input v-model="form.location" placeholder="请输入地点" />
        <el-button @click="showMapPicker = true">
          📍 在地图上选择
        </el-button>
      </el-form-item>
      
      <!-- 描述 -->
      <el-form-item label="描述">
        <el-input 
          v-model="form.description" 
          type="textarea" 
          :rows="4"
          placeholder="添加事件描述..."
        />
      </el-form-item>
      
      <!-- 提醒 -->
      <el-form-item label="提醒">
        <el-select v-model="form.reminder_minutes">
          <el-option label="不提醒" :value="0" />
          <el-option label="提前 15 分钟" :value="15" />
          <el-option label="提前 30 分钟" :value="30" />
          <el-option label="提前 1 小时" :value="60" />
          <el-option label="提前 2 小时" :value="120" />
        </el-select>
      </el-form-item>
      
      <!-- 邮件提醒 -->
      <el-form-item>
        <el-checkbox v-model="form.email_reminder">
          发送邮件提醒
        </el-checkbox>
      </el-form-item>
    </el-form>
    
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="handleSave">保存</el-button>
    </template>
  </el-dialog>
  
  <!-- 地图选择器 -->
  <MapPicker 
    v-model:visible="showMapPicker"
    @select="handleMapSelect"
  />
</template>

<script setup>
import { ref } from 'vue'

const form = ref({
  title: '',
  description: '',
  start_time: null,
  end_time: null,
  location: '',
  latitude: null,
  longitude: null,
  reminder_minutes: 15,
  email_reminder: false
})

const rules = {
  title: [
    { required: true, message: '请输入标题' }
  ],
  start_time: [
    { required: true, message: '请选择开始时间' }
  ]
}

const handleSave = async () => {
  // 验证表单
  await formRef.value.validate()
  
  // 调用 API
  const response = await createEvent(form.value)
  
  // 显示结果
  if (response.success) {
    ElMessage.success('保存成功！')
    visible.value = false
  }
}
</script>
```

---

## 🎁 **额外功能建议**

### **1. 时间冲突检测**

```javascript
function checkConflict(newEvent, existingEvents) {
  return existingEvents.filter(e => {
    const newStart = new Date(newEvent.start_time)
    const newEnd = new Date(newEvent.end_time || newEvent.start_time)
    const existStart = new Date(e.start_time)
    const existEnd = new Date(e.end_time || e.start_time)
    
    // 检查时间重叠
    return newStart < existEnd && newEnd > existStart
  })
}
```

### **2. 自动完成**

```javascript
// 地点输入自动完成
const locationSuggestions = [
  '北京首都国际机场',
  '故宫博物院',
  '长城',
  // 常用地点
]
```

### **3. 时间段快捷选择**

```javascript
const quickTimeOptions = [
  { label: '上午（9:00-12:00）', start: '09:00', end: '12:00' },
  { label: '下午（14:00-17:00）', start: '14:00', end: '17:00' },
  { label: '晚上（19:00-21:00）', start: '19:00', end: '21:00' },
  { label: '全天（8:00-18:00）', start: '08:00', end: '18:00' }
]
```

---

## 📊 **字段优先级建议**

### **第一优先级（必须）**：
1. ✅ 标题
2. ✅ 开始时间

### **第二优先级（重要）**：
3. ✅ 结束时间
4. ✅ 地点
5. ✅ 描述

### **第三优先级（增强）**：
6. ✅ 提醒时间
7. ✅ 邮件提醒
8. ✅ 地理坐标

### **第四优先级（高级）**：
9. 重复规则
10. 分类标签
11. 优先级
12. 附件

---

## 🎯 **与 Ralendar 同步时的建议**

### **创建事件时**：

```javascript
// Roamio 编辑界面
const eventData = {
  title: form.title,
  description: form.description,
  start_time: form.start_time,
  end_time: form.end_time || null,  // 可选
  location: form.location || '',
  latitude: form.latitude || null,
  longitude: form.longitude || null,
  reminder_minutes: form.reminder_minutes || 15,
  email_reminder: form.email_reminder || false
}

// 同步到 Ralendar
await syncToRalendar({
  unionid: getCurrentUserUnionId(),  // 重要！
  events: [eventData]
})
```

### **同步选项**：

- **即时同步**：创建/修改时立即同步
- **批量同步**：保存整个旅行计划时一次性同步
- **手动同步**：用户点击"同步到 Ralendar"按钮

---

## 📝 **验证规则参考**

```javascript
const validationRules = {
  title: {
    required: true,
    minLength: 1,
    maxLength: 200
  },
  start_time: {
    required: true,
    format: 'ISO 8601'
  },
  end_time: {
    required: false,
    mustAfterStart: true
  },
  location: {
    required: false,
    maxLength: 200
  },
  latitude: {
    required: false,
    range: [-90, 90],
    requiresWith: 'longitude'
  },
  longitude: {
    required: false,
    range: [-180, 180],
    requiresWith: 'latitude'
  },
  reminder_minutes: {
    required: false,
    type: 'integer',
    min: 0,
    max: 10080  // 最多提前 7 天
  },
  description: {
    required: false,
    maxLength: 2000
  }
}
```

---

## 🎨 **UI 组件库推荐**

Ralendar 使用的是 **Element Plus**：

```bash
npm install element-plus
```

**核心组件**：
- `el-dialog`：对话框
- `el-form`：表单容器
- `el-input`：输入框
- `el-date-picker`：日期时间选择器
- `el-select`：下拉选择器
- `el-checkbox`：复选框
- `el-button`：按钮
- `el-message`：消息提示

---

## 📞 **联系我们**

如果有任何问题或需要更多技术细节：

- **QQ**: 2064747320
- **邮箱**: 2064747320@qq.com
- **GitHub**: https://github.com/ppshuX/Ralendar

我们随时准备协助！🤝

---

## 🎉 **总结**

**Ralendar 提供了完整的事件编辑功能**：
- ✅ 基础字段（标题、时间、地点、描述）
- ✅ 邮件提醒系统
- ✅ 地图定位功能
- ✅ 灵活的 API 设计
- ✅ 良好的用户体验

**Roamio 可以参考并增强**：
- 更智能的自动填充
- 批量编辑功能
- 模板系统
- 冲突检测
- 更多快捷操作

---

**期待 Roamio 的优化版本！** 🚀

---

**Ralendar 团队**  
**2025-11-09**

