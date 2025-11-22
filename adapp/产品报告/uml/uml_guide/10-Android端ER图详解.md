# 10. Android端ER图详解

## 📖 这个图讲的是什么？

这个图展示了**Android端数据库的实体关系**，就像手机上的数据库结构图，告诉我们有哪些表，表里有哪些字段，以及表与表之间的关系。

## 🔍 两个主要实体（表）

### 1️⃣ Event 实体（日程表）

**作用**：存储用户的所有日程事件

**实体结构**：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | Long | 主键，自动生成，唯一标识每条日程 |
| title | String | 日程标题，必填（如"团队会议"） |
| description | String | 日程描述，可选（如"讨论项目进度"） |
| dateTime | Long | 日期时间，必填（Unix时间戳，毫秒） |
| reminderMinutes | Int | 提前提醒分钟数（0=不提醒，30=提前30分钟） |
| subscriptionId | Long? | 订阅ID，可空（null=用户创建的，有值=订阅的） |
| locationName | String | 地点名称（如"会议室A"） |
| latitude | Double | 纬度（0表示无地点） |
| longitude | Double | 经度（0表示无地点） |
| createdAt | Long | 创建时间戳 |

**简单理解**：这是"日程本"，记录着每个日程的详细信息。

**字段详解**：

- **id**：日程的唯一编号，就像身份证号，每条日程都有唯一ID
- **title**：日程的标题，就像日程的名字（如"春节"、"团队会议"）
- **description**：日程的详细说明，可选填写
- **dateTime**：日程的时间，用时间戳存储（毫秒），方便排序和查询
- **reminderMinutes**：提前多久提醒，0表示不提醒，30表示提前30分钟提醒
- **subscriptionId**：如果这个日程是从订阅源同步来的，这里记录订阅源的ID；如果是用户自己创建的，这里就是null
- **locationName/latitude/longitude**：地点的名称和坐标，用于地图定位
- **createdAt**：什么时候创建的这条日程

**数据示例**：

```kotlin
// 用户创建的日程
Event(
    id = 1,
    title = "团队会议",
    dateTime = 1702274400000L,  // 2024-01-10 14:00:00
    subscriptionId = null  // 用户创建的
)

// 从订阅源同步的日程
Event(
    id = 2,
    title = "春节",
    dateTime = 1704067200000L,  // 2024-01-01 00:00:00
    subscriptionId = 1  // 来自订阅ID=1的订阅源
)
```

### 2️⃣ Subscription 实体（订阅表）

**作用**：存储用户订阅的日历源信息

**实体结构**：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | Long | 主键，自动生成，唯一标识每个订阅 |
| name | String | 订阅名称（如"中国法定节假日"） |
| slug | String | 后端标识（如"china-holidays"） |
| description | String | 描述信息 |
| color | String | 显示颜色（如"#FF6B6B"） |
| icon | String | 图标emoji（如"🎉"） |
| isEnabled | Boolean | 是否启用显示 |
| eventCount | Int | 事件数量（统计用） |
| lastSyncTime | Long | 最后同步时间戳 |
| createdAt | Long | 创建时间戳 |

**简单理解**：这是"订阅源列表"，记录着你订阅了哪些日历（如"节假日"、"纪念日"等）。

**字段详解**：

- **id**：订阅的唯一编号
- **name**：订阅的名称，用于界面显示（如"中国法定节假日"）
- **slug**：后端标识，用于API查询（如"china-holidays"），对应后端的订阅源slug
- **description**：订阅的描述，说明这个订阅包含什么内容
- **color**：显示颜色，用于在日历上区分不同的订阅源
- **icon**：图标emoji，用于界面显示（如"🎉"、"🌍"）
- **isEnabled**：是否启用，用户可以临时禁用某个订阅，但不会删除
- **eventCount**：这个订阅源有多少个日程事件（统计用）
- **lastSyncTime**：最后同步的时间，用于判断是否需要重新同步
- **createdAt**：什么时候订阅的

**数据示例**：

```kotlin
Subscription(
    id = 1,
    name = "中国法定节假日",
    slug = "china-holidays",
    eventCount = 11  // 2024年有11个法定节假日
)
```

## 🔗 实体关系（箭头表示关联）

### Subscription 与 Event 的关系

```
Subscription (1) ──────── (N) Event
订阅源                    多个日程
```

**关系说明**：

- **一个订阅源**可以有**多个日程**（一对多关系）
- **一个日程**只能属于**一个订阅源**（多对一关系）
- 使用 `subscriptionId` 字段关联

**简单理解**：

- 就像"节假日"这个订阅源，包含多个日程：元旦、春节、清明节等
- 每个日程通过 `subscriptionId` 字段知道它来自哪个订阅源
- 如果 `subscriptionId` 是 null，说明这是用户自己创建的日程

**关系示例**：

```
订阅源（ID=1）：中国法定节假日
  ├── 日程1：元旦（subscriptionId = 1）
  ├── 日程2：春节（subscriptionId = 1）
  ├── 日程3：清明节（subscriptionId = 1）
  └── ...（共11个日程）

订阅源（ID=2）：世界纪念日
  ├── 日程1：世界和平日（subscriptionId = 2）
  ├── 日程2：世界环境日（subscriptionId = 2）
  └── ...（共365个日程）

用户创建的日程（subscriptionId = null）
  ├── 日程1：团队会议（subscriptionId = null）
  ├── 日程2：约会（subscriptionId = null）
  └── ...
```

## 💡 举个例子理解ER图

**场景一**：用户订阅"中国法定节假日"

1. 用户在订阅界面点击"订阅中国法定节假日"
2. 系统创建一个**Subscription**记录：
   - id = 1
   - name = "中国法定节假日"
   - slug = "china-holidays"
   - eventCount = 0（还没同步日程）
3. 系统通过网络API获取这个订阅源的所有日程（元旦、春节等）
4. 为每个日程创建一个**Event**记录：
   - 日程1：title = "元旦", subscriptionId = 1
   - 日程2：title = "春节", subscriptionId = 1
   - ...（共11个）
5. 更新Subscription的eventCount = 11

**简单理解**：就像订阅报纸，你先订阅（Subscription），然后接收所有文章（Event），每篇文章都知道它来自哪个订阅源。

**场景二**：用户添加自己的日程

1. 用户点击"添加日程"
2. 创建一个**Event**记录：
   - title = "团队会议"
   - dateTime = 2024-01-10 14:00:00
   - subscriptionId = null（用户创建的）
3. 不需要创建Subscription记录，因为这是用户自己的日程

**简单理解**：就像自己写日记，这是你自己的内容（subscriptionId = null），不需要订阅源。

**场景三**：取消订阅

1. 用户点击"取消订阅"
2. 删除**Subscription**记录（id = 1）
3. 删除所有关联的**Event**记录（subscriptionId = 1的所有日程）
4. 用户自己创建的日程（subscriptionId = null）不受影响

**简单理解**：就像取消订阅报纸，订阅源取消了，相关的文章也删除了，但你自己写的日记还在。

## 🎯 为什么要设计这两个实体？

1. **Subscription（订阅源）**：
   - 管理订阅的日历源
   - 可以订阅多个源（节假日、纪念日等）
   - 可以临时禁用某个订阅

2. **Event（日程）**：
   - 存储具体的日程数据
   - 可以是订阅的，也可以是用户创建的
   - 通过 subscriptionId 区分来源

3. **关系设计**：
   - 一个订阅源包含多个日程（一对多）
   - 便于管理订阅和日程的关系
   - 取消订阅时可以批量删除相关日程

## 📊 实体关系的特点

### 优点

- **结构清晰**：两个表职责明确，易于理解
- **易于管理**：可以通过订阅源批量管理日程
- **灵活扩展**：可以轻松添加新的订阅源

### 注意事项

- **外键约束**：subscriptionId 必须对应一个存在的 Subscription
- **删除策略**：删除订阅源时，需要同时删除相关的日程（级联删除）
- **空值处理**：subscriptionId 可以为 null（用户创建的日程）

## 📝 总结

这个图展示了Android端数据库的结构：

- **Event 实体**：日程表，存储所有日程数据
- **Subscription 实体**：订阅表，存储订阅的日历源
- **关系**：一个订阅源包含多个日程（一对多）

就像图书馆系统：
- **Subscription** = 图书馆的藏书分类（如"文学类"、"科技类"）
- **Event** = 具体的书籍（每本书都属于一个分类）
- **subscriptionId** = 书籍上的分类标签（标记它属于哪个分类）

它们共同构建了Android端的数据库结构，既支持订阅的日历，也支持用户自己创建的日程！

