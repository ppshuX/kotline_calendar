# 📅 Ralendar 日历数据模型设计

> **目标**: 实现"离线也能查，联网查更多"的智能数据架构

---

## 📋 目录

1. [设计原则](#设计原则)
2. [数据模型](#数据模型)
3. [数据来源](#数据来源)
4. [更新策略](#更新策略)
5. [API 设计](#api-设计)

---

## 🎯 设计原则

### **离线优先（Offline-First）**

```
┌─────────────────────────────────────────────────────┐
│                    数据加载策略                      │
└─────────────────────────────────────────────────────┘

1. 优先从本地数据库读取 (秒级响应)
   ↓
2. 如果数据过期或不存在，从服务器更新
   ↓
3. 服务器更新失败，仍使用本地数据（降级策略）
```

### **分层缓存**

- **L1**: 内存缓存（当前月份数据）
- **L2**: 本地数据库（近 3 年数据）
- **L3**: 服务器 API（所有历史和未来数据）

### **按需加载**

- **核心数据**（节假日、农历）：预装到 App
- **扩展数据**（黄历、运势）：首次使用时下载
- **个性化数据**（星座运势）：实时查询

---

## 📚 数据模型

### **1. 节假日表 (Holiday)**

```python
class Holiday(models.Model):
    """
    法定节假日和传统节日
    
    数据范围：往前 1 年，往后 3 年（共 4 年）
    更新频率：每年 1 月自动更新
    """
    date = models.DateField(db_index=True, help_text="日期")
    name = models.CharField(max_length=50, help_text="节日名称，如'春节'")
    type = models.CharField(max_length=20, choices=[
        ('major', '主要节日'),           # 节日当天
        ('vacation', '假期'),            # 假期中的其他天
        ('traditional', '传统节日'),      # 农历节日
        ('international', '国际节日'),    # 情人节、圣诞节等
    ], help_text="节日类型")
    
    is_legal_holiday = models.BooleanField(default=False, help_text="是否法定假日")
    is_rest_day = models.BooleanField(default=False, help_text="是否休息日")
    is_workday = models.BooleanField(default=False, help_text="是否调休工作日")
    
    # 关联信息
    holiday_group = models.CharField(max_length=50, null=True, blank=True, 
                                     help_text="假期组名，如'春节假期'")
    lunar_date = models.CharField(max_length=20, null=True, blank=True,
                                  help_text="农历日期，如'正月初一'")
    
    # 元数据
    description = models.TextField(null=True, blank=True, help_text="节日介绍")
    emoji = models.CharField(max_length=10, default='🎉', help_text="Emoji 图标")
    
    # 数据版本
    data_version = models.CharField(max_length=20, default='1.0', help_text="数据版本")
    last_updated = models.DateTimeField(auto_now=True, help_text="最后更新时间")
    
    class Meta:
        db_table = 'calendar_holidays'
        unique_together = ('date', 'name', 'type')
        ordering = ['date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['type']),
            models.Index(fields=['is_legal_holiday']),
        ]
    
    def __str__(self):
        return f"{self.date} - {self.name}"


class HolidayCalendar(models.Model):
    """
    年度节假日日历（用于批量查询优化）
    
    一条记录 = 一年的所有节假日数据（JSON）
    """
    year = models.IntegerField(unique=True, db_index=True, help_text="年份")
    data = models.JSONField(help_text="节假日数据（JSON 格式）")
    
    # 数据版本控制
    data_version = models.CharField(max_length=20, default='1.0')
    is_official = models.BooleanField(default=False, help_text="是否官方发布数据")
    source_url = models.URLField(null=True, blank=True, help_text="数据来源 URL")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'calendar_holiday_calendars'
        ordering = ['-year']
```

**数据示例：**

```json
{
  "2025": {
    "holidays": [
      {
        "date": "2025-01-01",
        "name": "元旦",
        "type": "major",
        "is_legal_holiday": true,
        "is_rest_day": true,
        "emoji": "🎉"
      },
      {
        "date": "2025-01-28",
        "name": "春节",
        "type": "major",
        "lunar_date": "正月初一",
        "is_legal_holiday": true,
        "is_rest_day": true,
        "holiday_group": "春节假期",
        "emoji": "🧧"
      }
    ]
  }
}
```

---

### **2. 黄历表 (LunarCalendar)**

```python
class LunarCalendar(models.Model):
    """
    黄历数据（宜忌、冲煞、吉神凶煞等）
    
    数据范围：当前年 + 未来 1 年（共 2 年，约 730 条）
    更新频率：每年 12 月自动更新下一年数据
    """
    date = models.DateField(unique=True, db_index=True, help_text="公历日期")
    
    # 农历信息
    lunar_year = models.IntegerField(help_text="农历年份")
    lunar_month = models.CharField(max_length=10, help_text="农历月份，如'正月'")
    lunar_day = models.CharField(max_length=10, help_text="农历日期，如'初一'")
    lunar_date_cn = models.CharField(max_length=50, help_text="农历日期中文，如'甲辰年正月初一'")
    
    # 生肖和天干地支
    zodiac = models.CharField(max_length=2, help_text="生肖，如'龙'")
    ganzhi_year = models.CharField(max_length=4, help_text="年干支，如'甲辰'")
    ganzhi_month = models.CharField(max_length=4, help_text="月干支")
    ganzhi_day = models.CharField(max_length=4, help_text="日干支")
    
    # 节气
    solar_term = models.CharField(max_length=10, null=True, blank=True, 
                                  help_text="节气，如'立春'")
    
    # 宜忌
    yi = models.JSONField(default=list, help_text="宜（适合做的事）")
    ji = models.JSONField(default=list, help_text="忌（不宜做的事）")
    
    # 冲煞
    chong = models.CharField(max_length=20, null=True, blank=True, 
                            help_text="相冲生肖，如'冲鼠'")
    sha = models.CharField(max_length=20, null=True, blank=True,
                          help_text="煞方位，如'煞北'")
    
    # 神煞
    ji_shen = models.JSONField(default=list, help_text="吉神")
    xiong_shen = models.JSONField(default=list, help_text="凶神")
    
    # 五行
    wu_xing = models.CharField(max_length=20, null=True, blank=True,
                               help_text="五行，如'金'")
    
    # 吉凶等级（1-5 星）
    auspicious_level = models.IntegerField(default=3, 
                                          help_text="吉凶等级：1=大凶, 3=平, 5=大吉")
    
    # 数据版本
    data_version = models.CharField(max_length=20, default='1.0')
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'calendar_lunar_calendars'
        ordering = ['date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['lunar_year', 'lunar_month']),
            models.Index(fields=['auspicious_level']),
        ]
    
    def __str__(self):
        return f"{self.date} - {self.lunar_date_cn}"
    
    @property
    def yi_display(self):
        """宜的事项（中文）"""
        return '、'.join(self.yi) if self.yi else '无'
    
    @property
    def ji_display(self):
        """忌的事项（中文）"""
        return '、'.join(self.ji) if self.ji else '无'
```

**数据示例：**

```json
{
  "date": "2025-11-10",
  "lunar_date_cn": "乙巳年十月初十",
  "zodiac": "蛇",
  "ganzhi_day": "丙子",
  "yi": ["祭祀", "祈福", "出行", "嫁娶", "移徙"],
  "ji": ["开市", "动土", "破土", "安葬"],
  "chong": "冲马",
  "sha": "煞南",
  "ji_shen": ["天德", "月德", "天恩"],
  "xiong_shen": ["五离", "天牢"],
  "wu_xing": "涧下水",
  "auspicious_level": 4
}
```

---

### **3. 运势表 (Fortune)**

```python
class DailyFortune(models.Model):
    """
    每日运势（星座 + 生肖）
    
    数据范围：当天 + 未来 7 天
    更新频率：每天凌晨自动更新
    """
    date = models.DateField(db_index=True, help_text="日期")
    fortune_type = models.CharField(max_length=20, choices=[
        ('zodiac', '生肖运势'),
        ('constellation', '星座运势'),
    ], help_text="运势类型")
    
    # 生肖 or 星座
    zodiac = models.CharField(max_length=2, null=True, blank=True,
                             help_text="生肖，如'龙'")
    constellation = models.CharField(max_length=20, null=True, blank=True,
                                    help_text="星座，如'天蝎座'")
    
    # 综合运势
    overall_score = models.IntegerField(default=50, help_text="综合运势评分（0-100）")
    summary = models.TextField(help_text="运势总结")
    
    # 分项运势
    love_score = models.IntegerField(default=50, help_text="爱情运势（0-100）")
    career_score = models.IntegerField(default=50, help_text="事业运势（0-100）")
    wealth_score = models.IntegerField(default=50, help_text="财运（0-100）")
    health_score = models.IntegerField(default=50, help_text="健康运势（0-100）")
    
    # 幸运元素
    lucky_color = models.CharField(max_length=20, null=True, blank=True,
                                   help_text="幸运颜色")
    lucky_number = models.CharField(max_length=20, null=True, blank=True,
                                    help_text="幸运数字")
    lucky_direction = models.CharField(max_length=20, null=True, blank=True,
                                       help_text="幸运方位")
    
    # 建议
    advice = models.TextField(null=True, blank=True, help_text="今日建议")
    
    # 数据来源
    data_source = models.CharField(max_length=50, default='auto', 
                                   help_text="数据来源：auto/api/user_input")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'calendar_fortunes'
        unique_together = ('date', 'fortune_type', 'zodiac', 'constellation')
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date', 'fortune_type']),
            models.Index(fields=['zodiac']),
            models.Index(fields=['constellation']),
        ]
    
    def __str__(self):
        if self.zodiac:
            return f"{self.date} - {self.zodiac}运势"
        else:
            return f"{self.date} - {self.constellation}运势"


class UserFortune(models.Model):
    """
    用户个性化运势订阅
    
    用户可以订阅自己的生肖/星座运势
    """
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, 
                            related_name='fortunes')
    
    # 个人信息
    birth_date = models.DateField(help_text="出生日期")
    zodiac = models.CharField(max_length=2, help_text="生肖")
    constellation = models.CharField(max_length=20, help_text="星座")
    
    # 订阅设置
    subscribe_zodiac = models.BooleanField(default=True, help_text="订阅生肖运势")
    subscribe_constellation = models.BooleanField(default=True, help_text="订阅星座运势")
    notify_daily = models.BooleanField(default=False, help_text="每日推送运势")
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'calendar_user_fortunes'
        unique_together = ('user',)
    
    def __str__(self):
        return f"{self.user.username} - {self.zodiac}/{self.constellation}"
```

---

### **4. 数据更新记录表 (DataSyncLog)**

```python
class DataSyncLog(models.Model):
    """
    数据同步日志
    
    记录每次数据更新的状态
    """
    data_type = models.CharField(max_length=20, choices=[
        ('holiday', '节假日'),
        ('lunar', '黄历'),
        ('fortune', '运势'),
    ], help_text="数据类型")
    
    sync_date = models.DateField(help_text="同步日期范围开始")
    sync_date_end = models.DateField(null=True, blank=True, help_text="同步日期范围结束")
    
    status = models.CharField(max_length=20, choices=[
        ('pending', '待同步'),
        ('syncing', '同步中'),
        ('success', '成功'),
        ('failed', '失败'),
    ], default='pending', help_text="同步状态")
    
    records_count = models.IntegerField(default=0, help_text="同步记录数")
    error_message = models.TextField(null=True, blank=True, help_text="错误信息")
    
    # 时间戳
    started_at = models.DateTimeField(null=True, blank=True, help_text="开始时间")
    completed_at = models.DateTimeField(null=True, blank=True, help_text="完成时间")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'calendar_data_sync_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['data_type', 'status']),
            models.Index(fields=['sync_date']),
        ]
    
    def __str__(self):
        return f"{self.data_type} - {self.sync_date} - {self.status}"
```

---

## 🔄 数据来源

### **1. 节假日数据**

**来源优先级：**

1. **国务院官网**（最权威）
   - URL: http://www.gov.cn/zhengce/content/
   - 每年 12 月发布下一年节假日安排
   - 需要爬虫解析

2. **第三方 API**（实时更新）
   - 天行数据: https://www.tianapi.com/
   - 聚合数据: https://www.juhe.cn/
   - 免费额度：100-500 次/天

3. **手动维护**（兜底方案）
   - 每年手动更新 JSON 文件
   - 适合小项目

### **2. 黄历数据**

**来源优先级：**

1. **万年历 API**
   - 天行数据 - 黄历接口
   - 价格：¥0.01/次
   - 一年数据约 ¥3.65

2. **开源黄历库**
   - GitHub: `chinese-calendar`
   - Python: `lunarcalendar`（已在用）
   - 扩展：添加宜忌数据

3. **自建数据库**
   - 从传统黄历书籍整理
   - 一次性工作量较大

### **3. 运势数据**

**来源优先级：**

1. **运势 API**
   - 星座运势 API
   - 生肖运势 API
   - 价格：¥0.005-0.01/次

2. **AI 生成**（未来可能）
   - 使用 LLM 生成每日运势
   - 更个性化

3. **用户自定义**
   - 用户可以记录自己的感受
   - 形成个人运势日记

---

## 🔄 更新策略

### **数据更新优先级**

| 数据类型 | 更新频率 | 数据量 | 优先级 | 存储位置 |
|---------|---------|--------|--------|---------|
| 节假日 | 每年 1 次 | ~100 条/年 | 🔴 P0 | 数据库 + App 预装 |
| 农历 | 实时计算 | 无需存储 | 🔴 P0 | 库计算 |
| 黄历 | 每年 1 次 | ~365 条/年 | 🟡 P1 | 数据库（按需下载） |
| 运势 | 每天 1 次 | ~20 条/天 | 🟢 P2 | 数据库（实时查询） |

### **自动更新流程**

```python
# backend/api/tasks.py

from celery import shared_task
from datetime import date, timedelta
from .models import Holiday, LunarCalendar, DataSyncLog

@shared_task
def sync_holiday_data(year=None):
    """
    同步节假日数据
    
    触发时机：
    1. 每年 12 月 1 日自动执行（同步下一年数据）
    2. 手动触发
    """
    if year is None:
        year = date.today().year + 1  # 同步下一年
    
    log = DataSyncLog.objects.create(
        data_type='holiday',
        sync_date=date(year, 1, 1),
        sync_date_end=date(year, 12, 31),
        status='syncing'
    )
    
    try:
        # 1. 从 API 获取数据
        holidays_data = fetch_holidays_from_api(year)
        
        # 2. 保存到数据库
        count = 0
        for holiday_item in holidays_data:
            Holiday.objects.update_or_create(
                date=holiday_item['date'],
                name=holiday_item['name'],
                defaults={
                    'type': holiday_item['type'],
                    'is_legal_holiday': holiday_item['is_legal_holiday'],
                    # ... 其他字段
                }
            )
            count += 1
        
        # 3. 更新日志
        log.status = 'success'
        log.records_count = count
        log.completed_at = timezone.now()
        log.save()
        
        return f"✅ 同步成功：{count} 条节假日数据"
    
    except Exception as e:
        log.status = 'failed'
        log.error_message = str(e)
        log.save()
        return f"❌ 同步失败：{str(e)}"


@shared_task
def sync_lunar_calendar_data(year=None):
    """
    同步黄历数据
    
    触发时机：
    1. 每年 11 月 1 日自动执行（同步下一年数据）
    2. 首次使用时按需同步
    """
    # 实现类似 sync_holiday_data
    pass


@shared_task
def sync_daily_fortune():
    """
    同步每日运势
    
    触发时机：每天凌晨 6:00
    """
    # 实现类似 sync_holiday_data
    pass
```

**Celery Beat 配置：**

```python
# backend/calendar_backend/celery.py

app.conf.beat_schedule = {
    # 节假日数据同步（每年 12 月 1 日）
    'sync-holiday-data': {
        'task': 'api.tasks.sync_holiday_data',
        'schedule': crontab(day_of_month='1', month_of_year='12', hour='1', minute='0'),
    },
    
    # 黄历数据同步（每年 11 月 1 日）
    'sync-lunar-calendar-data': {
        'task': 'api.tasks.sync_lunar_calendar_data',
        'schedule': crontab(day_of_month='1', month_of_year='11', hour='2', minute='0'),
    },
    
    # 每日运势同步（每天凌晨 6:00）
    'sync-daily-fortune': {
        'task': 'api.tasks.sync_daily_fortune',
        'schedule': crontab(hour='6', minute='0'),
    },
}
```

---

## 🌐 API 设计

### **RESTful API 端点**

```
# 节假日
GET  /api/v1/holidays/                 # 获取节假日列表
GET  /api/v1/holidays/check/?date=YYYY-MM-DD  # 检查是否节假日
GET  /api/v1/holidays/today/            # 今日节假日
GET  /api/v1/holidays/month/?month=YYYY-MM  # 某月节假日

# 黄历
GET  /api/v1/lunar/?date=YYYY-MM-DD     # 获取某日黄历
GET  /api/v1/lunar/today/               # 今日黄历
GET  /api/v1/lunar/month/?month=YYYY-MM # 某月黄历（批量）

# 运势
GET  /api/v1/fortune/zodiac/{zodiac}/   # 生肖运势
GET  /api/v1/fortune/constellation/{name}/  # 星座运势
GET  /api/v1/fortune/my/                # 我的运势（需登录）
POST /api/v1/fortune/subscribe/         # 订阅运势
```

### **响应格式示例**

**节假日 API：**

```json
{
  "date": "2025-11-10",
  "is_holiday": false,
  "is_workday": true,
  "holiday_name": null,
  "traditional_festivals": [],
  "international_festivals": []
}
```

**黄历 API：**

```json
{
  "date": "2025-11-10",
  "lunar": {
    "date_cn": "乙巳年十月初十",
    "zodiac": "蛇",
    "ganzhi": "丙子"
  },
  "yi": ["祭祀", "祈福", "出行", "嫁娶", "移徙"],
  "ji": ["开市", "动土", "破土", "安葬"],
  "auspicious_level": 4,
  "lucky_color": "红色",
  "lucky_direction": "东南"
}
```

**运势 API：**

```json
{
  "date": "2025-11-10",
  "zodiac": "龙",
  "overall_score": 85,
  "summary": "今日运势极佳，诸事顺利",
  "scores": {
    "love": 90,
    "career": 85,
    "wealth": 80,
    "health": 75
  },
  "lucky": {
    "color": "红色",
    "number": "8",
    "direction": "东南"
  },
  "advice": "适合签约、开业、搬家"
}
```

---

## 📱 Android 端数据策略

### **预装数据（App 安装包）**

```
ralendar.apk
│
├── assets/
│   ├── holidays_2024.json  (5KB)
│   ├── holidays_2025.json  (5KB)
│   ├── holidays_2026.json  (5KB)
│   └── holidays_2027.json  (5KB)
│       总计：~20KB
```

### **Room 数据库结构**

```kotlin
// Android 端数据库
@Database(
    entities = [
        HolidayEntity::class,
        LunarCalendarEntity::class,
        FortuneEntity::class
    ],
    version = 1
)
abstract class CalendarDatabase : RoomDatabase() {
    abstract fun holidayDao(): HolidayDao
    abstract fun lunarDao(): LunarDao
    abstract fun fortuneDao(): FortuneDao
}
```

### **数据同步策略**

```kotlin
class DataSyncManager(
    private val api: CalendarApi,
    private val database: CalendarDatabase
) {
    suspend fun syncIfNeeded() {
        // 1. 检查本地数据版本
        val localVersion = getLocalDataVersion()
        
        // 2. 查询服务器最新版本
        val remoteVersion = api.getDataVersion()
        
        // 3. 如果版本不一致，同步数据
        if (localVersion < remoteVersion) {
            val holidays = api.getHolidays()
            database.holidayDao().insertAll(holidays)
        }
    }
}
```

---

## ✅ 实施步骤

### **阶段 1：数据模型（1 天）**

- [ ] 创建数据库模型（Holiday, LunarCalendar, Fortune）
- [ ] 运行数据库迁移
- [ ] 编写基础 CRUD API

### **阶段 2：节假日功能（2 天）**

- [ ] 导入现有 holidays_2025.json 到数据库
- [ ] 添加 2024, 2026, 2027 年数据
- [ ] 实现节假日查询 API
- [ ] 前端展示优化

### **阶段 3：黄历功能（3 天）**

- [ ] 集成黄历数据 API 或自建数据
- [ ] 实现黄历查询 API
- [ ] 前端 UI 设计和开发
- [ ] 测试验证

### **阶段 4：运势功能（3 天）**

- [ ] 集成运势 API
- [ ] 实现用户运势订阅
- [ ] 前端 UI 设计和开发
- [ ] 测试验证

### **阶段 5：数据同步（2 天）**

- [ ] 实现 Celery 定时任务
- [ ] Android 端数据同步逻辑
- [ ] 离线模式测试
- [ ] 性能优化

---

## 📊 数据量估算

| 数据类型 | 单条大小 | 数量/年 | 年数 | 总大小 |
|---------|---------|--------|-----|--------|
| 节假日 | ~200 bytes | ~100 | 4 | ~80 KB |
| 黄历 | ~1 KB | ~365 | 2 | ~730 KB |
| 运势 | ~500 bytes | ~7300 | - | ~3.5 MB |
| **总计** | - | - | - | **~4.3 MB** |

**结论：数据量很小，完全可以本地存储！**

---

## 💡 最佳实践

### **1. 分层缓存**

```python
def get_holiday(date):
    # L1: 内存缓存
    if date in memory_cache:
        return memory_cache[date]
    
    # L2: 数据库
    holiday = Holiday.objects.filter(date=date).first()
    if holiday:
        memory_cache[date] = holiday
        return holiday
    
    # L3: 服务器 API
    holiday = fetch_from_api(date)
    if holiday:
        Holiday.objects.create(**holiday)
        memory_cache[date] = holiday
        return holiday
    
    return None
```

### **2. 智能预加载**

```python
# 用户打开日历时，预加载前后 2 个月的数据
def preload_data(current_month):
    start_month = current_month - 1
    end_month = current_month + 2
    
    # 异步预加载
    async_load_holidays(start_month, end_month)
    async_load_lunar_calendars(start_month, end_month)
```

### **3. 降级策略**

```python
# API 失败时使用本地数据
def get_fortune_with_fallback(date, zodiac):
    try:
        # 尝试从 API 获取
        return api.get_fortune(date, zodiac)
    except APIError:
        # 降级：使用本地数据
        return get_local_fortune(date, zodiac)
    except:
        # 兜底：返回默认值
        return get_default_fortune()
```

---

## 📞 联系方式

**文档维护者**: Ralendar 核心团队  
**问题反馈**: 在项目根目录创建 Issue

---

## 📝 更新日志

### v1.0 (2025-11-10)
- 初始版本
- 完整的数据模型设计
- 数据来源和更新策略

