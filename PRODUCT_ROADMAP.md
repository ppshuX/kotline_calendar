# KotlinCalendar 产品规划

## 🎯 产品定位

**智能日历助手** - 集日程管理、节日提醒、运势分析于一体的多端日历应用

---

## 📊 功能分层设计

### 🆓 免费版（未登录）

```
✅ 完整日历视图
├── 月份切换
├── 今天高亮
├── 周末标识
└── 日期选择

✅ 节日提醒
├── 法定节假日（元旦、春节、国庆等）
├── 传统节日（端午、中秋等）
└── 工作日/休息日标识

✅ 农历显示
├── 农历日期
├── 生肖年
└── 传统节气

✅ 简单运势
├── 每日宜忌
├── 幸运颜色
└── 星座运势
```

---

### 🔓 基础会员（登录后）

```
✅ 免费版所有功能

✅ 个性化事项管理
├── 添加日程
├── 编辑日程
├── 删除日程
├── 日程提醒
└── 日程分类（工作/生活/学习）

✅ 云端同步
├── 三端同步（Android/Web/AcWing）
├── 数据备份
└── 跨设备访问

✅ 基础统计
├── 本月日程数量
├── 完成率统计
└── 时间分布图
```

---

### 💎 VIP 会员（付费）

```
✅ 基础会员所有功能

✅ 详细运势分析
├── 八字运势
├── 五行分析
├── 每日吉时
├── 黄历宜忌
└── 生辰八字查询

✅ AI 智能助手
├── 智能日程建议
├── 时间冲突检测
├── 重要事项提醒
└── 习惯分析

✅ 高级功能
├── 订阅网络日历
├── 数据导出（iCal/Excel）
├── 团队共享日历
├── 自定义主题
└── 去广告

✅ 专属服务
├── 专属客服
├── 数据优先同步
└── 更大存储空间
```

---

## 🛠️ 技术实现方案

### 1. 节假日数据

```javascript
// 可以使用第三方 API
// 或维护本地数据库

const holidays2025 = {
  '2025-01-01': { name: '元旦', type: 'holiday', work: false },
  '2025-02-10': { name: '春节', type: 'holiday', work: false },
  '2025-04-05': { name: '清明节', type: 'holiday', work: false },
  '2025-05-01': { name: '劳动节', type: 'holiday', work: false },
  '2025-10-01': { name: '国庆节', type: 'holiday', work: false },
  // 调休工作日
  '2025-02-08': { name: '春节调休', type: 'workday', work: true },
}
```

---

### 2. 农历 API（已有）

```javascript
// 已实现的 Django API
GET /api/lunar/?date=2025-11-06

Response:
{
  "lunar_date": "农历十月初七",
  "zodiac": "蛇"
}
```

---

### 3. 运势系统

#### 简单版（免费）
```javascript
// 固定的运势文案
const fortunes = [
  { luck: '吉', suitable: '开会、出行', avoid: '熬夜' },
  { luck: '中吉', suitable: '学习、创作', avoid: '争吵' },
]
```

#### VIP 版（付费）
```python
# Django 新增 API
GET /api/fortune/?date=2025-11-06&user_id=123

# 根据用户生辰八字计算详细运势
Response:
{
  "bazi": "乙巳年 丁亥月 甲寅日",
  "wuxing": { "jin": 1, "mu": 3, "shui": 2, "huo": 1, "tu": 1 },
  "luck_score": 85,
  "suitable": ["签约", "开业", "出行"],
  "avoid": ["装修", "搬家"],
  "lucky_time": ["9:00-11:00", "13:00-15:00"],
  "lucky_color": "绿色",
  "lucky_number": 8,
}
```

---

### 4. 用户认证系统

```python
# Django 用户模型
class User(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField()
    
    # AcWing 登录
    acwing_openid = models.CharField(max_length=100, unique=True, null=True)
    
    # QQ 登录
    qq_openid = models.CharField(max_length=100, unique=True, null=True)
    
    # VIP 信息
    is_vip = models.BooleanField(default=False)
    vip_expire_date = models.DateTimeField(null=True)
    
    # 个人信息（用于运势计算）
    birthday = models.DateField(null=True)  # 公历生日
    birth_time = models.TimeField(null=True)  # 出生时辰
    gender = models.CharField(max_length=10, null=True)
```

---

## 📅 开发计划

### Phase 1: 基础功能完善（当前）✅
- [x] 三客户端架构搭建
- [x] 基础日程管理
- [x] Vuex 模拟路由
- [x] 部署上线

### Phase 2: 日历增强（1-2天）
- [ ] 完整日历 UI ✅ 刚完成
- [ ] 节假日数据集成
- [ ] 农历显示优化
- [ ] 简单运势展示

### Phase 3: 用户系统（2-3天）
- [ ] AcWing 一键登录
- [ ] 用户注册/登录
- [ ] 个人信息管理
- [ ] 权限控制

### Phase 4: VIP 系统（2-3天）
- [ ] VIP 会员购买
- [ ] 支付接口集成
- [ ] 详细运势 API
- [ ] VIP 专属功能

### Phase 5: 高级功能（可选）
- [ ] AI 日程建议
- [ ] 团队协作
- [ ] 数据分析
- [ ] 小程序端

---

## 💰 变现模式

### 1. VIP 会员
- **月卡**: ¥9.9/月
- **季卡**: ¥25/季
- **年卡**: ¥88/年

### 2. 增值服务
- 详细运势报告: ¥6.8/次
- 生辰八字分析: ¥19.9/次
- 团队版: ¥299/年

### 3. 广告收入
- 免费用户展示广告
- VIP 用户无广告

---

## 🎨 UI/UX 优化

### 视觉层次

```
【未登录】
顶部：简单导航 + 登录按钮
主体：完整日历 + 节日标识
底部：今日运势（简单）

【登录后】
顶部：用户信息 + 退出
主体：日历 + 我的日程
底部：今日运势 + VIP 升级入口

【VIP】
顶部：VIP 标识 + 到期时间
主体：日历 + 高级功能
底部：详细运势分析
```

---

## 📱 三端功能对比

| 功能 | Android | Web | AcWing |
|------|---------|-----|--------|
| 日历视图 | ✅ | ✅ | ✅ |
| 事项管理 | ✅ | ✅ | ✅ |
| 登录系统 | ✅ | ✅ | ✅ AcWing登录 |
| 运势查询 | ✅ | ✅ | ✅ |
| VIP 功能 | ✅ | ✅ | ✅ |
| 本地提醒 | ✅ 推送通知 | ⚠️ 浏览器通知 | ❌ |
| 离线使用 | ✅ Room | ❌ | ❌ |

---

## 🎯 立即可做的事

### 1. 完善日历 UI（今天可完成）
- [x] 日历网格 ✅ 刚完成
- [ ] 美化样式
- [ ] 添加动画效果

### 2. 集成节假日（1小时）
- [ ] 导入 2025 年节假日数据
- [ ] 在日历上标注
- [ ] 工作日/休息日区分

### 3. 运势展示（30分钟）
- [ ] 每日宜忌
- [ ] 随机运势文案
- [ ] 运势卡片样式

---

**你的产品思路非常好！** 这是一个有商业价值的完整产品！

**现在要不要先把日历 UI 构建并部署，让用户能看到完整的日历？** 🚀

