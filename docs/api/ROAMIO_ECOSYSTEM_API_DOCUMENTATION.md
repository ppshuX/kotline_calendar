# 🌏 Roamio 生态系统 API 文档

> **版本**: v1.0.0  
> **更新日期**: 2025-11-07  
> **适用项目**: Roamio + Ralendar  
> **维护**: Roamio Team

---

## 📖 文档说明

本文档是 **Roamio 生态系统**的统一 API 文档，涵盖：
- **Roamio**：旅行规划与内容分享平台
- **Ralendar**：智能日历与时间管理工具

两个项目共享用户认证体系，未来将深度融合，实现数据互通和功能联动。

---

## 🏗️ 生态架构

```
┌─────────────────────────────────────────────────────────────┐
│                  Roamio Ecosystem Architecture               │
└─────────────────────────────────────────────────────────────┘

                    统一用户认证系统
                    (JWT + OAuth2)
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
    Roamio API       Ralendar API      未来产品
   (旅行规划)         (日历管理)      (Rote, Rapture...)
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                    共享数据层（可选）
                   User, OAuth绑定
```

### 核心设计理念

1. **独立开发，统一部署** - 各项目独立开发，共享认证体系
2. **API 优先** - RESTful 设计，便于跨端调用
3. **数据互通** - 预留接口，支持未来数据联动
4. **可扩展性** - 模块化设计，易于添加新产品

---

## 🔐 认证体系（通用）

### JWT Token 认证

**认证方式**：Bearer Token

**Header 格式**：
```
Authorization: Bearer <access_token>
```

**Token 生命周期**：
- Access Token：5 分钟（短期，安全）
- Refresh Token：15 天（长期，便利）

### 获取 Token

**端点**: `POST /api/v1/token/` (Roamio) 或 `POST /api/auth/login/` (Ralendar)

**请求**：
```json
{
  "username": "string",
  "password": "string"
}
```

**响应**：
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "张三",
    "email": "user@example.com"
  }
}
```

### 刷新 Token

**端点**: `POST /api/v1/token/refresh/` (Roamio) 或 `POST /api/auth/refresh/` (Ralendar)

**请求**：
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**响应**：
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## 🌏 Roamio API

**Base URL**: `https://roamio.cn/api/v1/`

### 1. 认证接口 (Auth)

#### 1.1 用户注册

**端点**: `POST /api/v1/auth/register/`

**权限**: 匿名

**请求**：
```json
{
  "username": "string",
  "email": "email@example.com",
  "password": "string",
  "password_confirm": "string"
}
```

**响应** (201 Created):
```json
{
  "user": {
    "id": 1,
    "username": "张三",
    "email": "user@example.com",
    "profile": {
      "avatar": "https://...",
      "bio": "",
      "level": "novice"
    }
  },
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### 1.2 用户登录

**端点**: `POST /api/v1/auth/login/`

**权限**: 匿名

**请求**：
```json
{
  "username": "string",  // 或 email
  "password": "string"
}
```

**响应** (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "张三",
    "email": "user@example.com"
  }
}
```

#### 1.3 获取当前用户

**端点**: `GET /api/v1/auth/me/`

**权限**: 已认证

**响应** (200 OK):
```json
{
  "id": 1,
  "username": "张三",
  "email": "user@example.com",
  "profile": {
    "avatar": "https://...",
    "bio": "旅行爱好者",
    "birthday": "1990-01-01",
    "tags": "摄影,美食",
    "level": "explorer",
    "email_verified": true
  },
  "social_accounts": [
    {
      "provider": "qq",
      "nickname": "QQ昵称",
      "avatar_url": "https://..."
    }
  ],
  "trips_count": 5,
  "comments_count": 23
}
```

#### 1.4 发送邮箱验证码

**端点**: `POST /api/v1/auth/send_verification_code/`

**权限**: 匿名

**请求**：
```json
{
  "email": "user@example.com",
  "type": "register"  // register | reset_password | verify_email
}
```

**频率限制**：
- 同一邮箱：5分钟内最多3次
- 同一IP：1小时内最多10次

**响应** (200 OK):
```json
{
  "success": true,
  "message": "验证码已发送到您的邮箱",
  "expires_in": 600  // 10分钟
}
```

**响应** (429 Too Many Requests):
```json
{
  "error": "发送过于频繁，请稍后再试",
  "remaining_seconds": 180
}
```

#### 1.5 验证邮箱验证码

**端点**: `POST /api/v1/auth/verify_code/`

**权限**: 匿名

**请求**：
```json
{
  "email": "user@example.com",
  "code": "123456",
  "type": "register"
}
```

**响应** (200 OK):
```json
{
  "success": true,
  "verified": true,
  "message": "验证成功",
  "email": "user@example.com",
  "verification_token": "abcd1234...",  // 临时token，5分钟有效
  "expires_in": 300
}
```

#### 1.6 QQ 登录 - 获取授权 URL

**端点**: `GET /api/v1/auth/qq_login_url/`

**权限**: 匿名

**响应** (200 OK):
```json
{
  "authorize_url": "https://graph.qq.com/oauth2.0/authorize?...",
  "state": "random_state_string"
}
```

#### 1.7 QQ 登录 - 回调处理

**端点**: `POST /api/v1/auth/qq_callback/`

**权限**: 匿名

**请求**：
```json
{
  "code": "authorization_code",
  "state": "state_string"
}
```

**响应** (200 OK):
```json
{
  "success": true,
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "QQ用户",
    "email": ""
  },
  "message": "QQ登录成功",
  "email_optional": true,
  "tip": "建议在个人中心绑定邮箱"
}
```

#### 1.8 绑定 QQ（已有账号）

**端点**: `POST /api/v1/auth/qq_bind_existing/`

**权限**: 已认证

**请求**：
```json
{
  "code": "authorization_code",
  "state": "state_string"
}
```

**响应** (200 OK):
```json
{
  "success": true,
  "message": "QQ绑定成功"
}
```

#### 1.9 解绑 QQ

**端点**: `DELETE /api/v1/auth/qq_unbind/`

**权限**: 已认证

**响应** (200 OK):
```json
{
  "success": true,
  "message": "QQ解绑成功"
}
```

#### 1.10 重置密码

**端点**: `POST /api/v1/auth/reset_password/`

**权限**: 匿名

**请求**：
```json
{
  "email": "user@example.com",
  "verification_token": "token_from_verify_code",
  "new_password": "new_password",
  "password_confirm": "new_password"
}
```

**响应** (200 OK):
```json
{
  "success": true,
  "message": "密码重置成功，请使用新密码登录"
}
```

---

### 2. 用户接口 (Users)

#### 2.1 获取用户列表

**端点**: `GET /api/v1/users/`

**权限**: 匿名（只读）

**查询参数**：
- `page`: 页码（默认 1）
- `page_size`: 每页数量（默认 20）

**响应** (200 OK):
```json
{
  "count": 100,
  "next": "https://roamio.com/api/v1/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "张三",
      "profile": {
        "avatar": "https://...",
        "bio": "旅行爱好者",
        "level": "explorer"
      },
      "trips_count": 5,
      "public_trips_count": 3
    }
  ]
}
```

#### 2.2 获取用户详情

**端点**: `GET /api/v1/users/{id}/`

**权限**: 匿名

**响应** (200 OK):
```json
{
  "id": 1,
  "username": "张三",
  "profile": {
    "avatar": "https://...",
    "bio": "旅行爱好者，走过30个国家",
    "birthday": "1990-01-01",
    "tags": "摄影,美食,徒步",
    "level": "wanderer",
    "visited_countries": "中国,日本,泰国"
  },
  "trips": [
    {
      "id": 1,
      "slug": "abc123def456",
      "title": "云南之旅",
      "icon": "🏔️",
      "start_date": "2025-11-15",
      "end_date": "2025-11-20"
    }
  ],
  "trips_count": 5,
  "public_trips_count": 3,
  "comments_count": 45,
  "joined_at": "2025-01-01T00:00:00Z"
}
```

#### 2.3 更新个人资料

**端点**: `PATCH /api/v1/users/{id}/profile/`

**权限**: 本人或管理员

**请求**：
```json
{
  "bio": "string",
  "birthday": "1990-01-01",
  "tags": "摄影,美食"
}
```

**响应** (200 OK):
```json
{
  "success": true,
  "message": "资料更新成功",
  "profile": {
    "bio": "...",
    "birthday": "1990-01-01",
    "tags": "摄影,美食"
  }
}
```

#### 2.4 上传头像

**端点**: `POST /api/v1/users/{id}/avatar/`

**权限**: 本人或管理员

**请求**：
```
Content-Type: multipart/form-data

avatar: <file>
```

**响应** (200 OK):
```json
{
  "success": true,
  "message": "头像上传成功",
  "avatar_url": "https://cos.ap-beijing.myqcloud.com/..."
}
```

---

### 3. 旅行计划接口 (Trips)

#### 3.1 获取旅行列表

**端点**: `GET /api/v1/trips/`

**权限**: 匿名

**查询参数**：
- `visibility`: 可见性筛选（public | private）
- `author`: 作者ID
- `status`: 状态筛选（draft | published）
- `page`: 页码
- `page_size`: 每页数量

**响应** (200 OK):
```json
{
  "count": 50,
  "next": "https://roamio.com/api/v1/trips/?page=2",
  "previous": null,
  "results": [
    {
      "slug": "abc123def456",
      "title": "云南秘境探索",
      "description": "一场说走就走的旅行",
      "icon": "🏔️",
      "author": {
        "id": 1,
        "username": "张三",
        "avatar": "https://..."
      },
      "start_date": "2025-11-15",
      "end_date": "2025-11-20",
      "days_count": 6,
      "status": "published",
      "visibility": "public",
      "views": 1234,
      "likes": 56,
      "checked_in": true,
      "comments_count": 23,
      "created_at": "2025-11-01T10:00:00Z"
    }
  ]
}
```

#### 3.2 获取旅行详情

**端点**: `GET /api/v1/trips/{slug}/`

**权限**: 匿名（公开），本人或管理员（私有）

**响应** (200 OK):
```json
{
  "slug": "abc123def456",
  "title": "云南秘境探索",
  "description": "一场说走就走的旅行...",
  "icon": "🏔️",
  "author": {
    "id": 1,
    "username": "张三",
    "avatar": "https://..."
  },
  "start_date": "2025-11-15",
  "end_date": "2025-11-20",
  "days_count": 6,
  "status": "published",
  "visibility": "public",
  "config": {
    "enabledModules": ["basicInfo", "highlights", "itinerary", "budget", "tips"]
  },
  "overview": {
    "basicInfo": {
      "destination": "云南",
      "duration": "6天5晚",
      "budget": 5000
    },
    "highlights": [
      "香格里拉",
      "丽江古城",
      "泸沽湖"
    ],
    "itinerary": [
      {
        "day": 1,
        "title": "抵达昆明",
        "activities": ["机场接机", "酒店入住"]
      }
    ]
  },
  "theme_color": "#f0e68c",
  "background_music": "https://...",
  "views": 1235,  // 自动+1
  "likes": 56,
  "checked_in": true,
  "comments_count": 23,
  "created_at": "2025-11-01T10:00:00Z",
  "updated_at": "2025-11-06T15:30:00Z"
}
```

#### 3.3 创建旅行计划

**端点**: `POST /api/v1/trip-plans/`

**权限**: 已认证

**请求**：
```json
{
  "title": "string",
  "description": "string (可选)",
  "icon": "🗺️ (可选)",
  "start_date": "2025-11-15 (可选)",
  "end_date": "2025-11-20 (可选)",
  "visibility": "private",  // private | public
  "status": "draft",  // draft | published
  "config": {
    "enabledModules": ["basicInfo", "highlights"]
  },
  "overview": {}
}
```

**响应** (201 Created):
```json
{
  "slug": "abc123def456",  // 自动生成
  "title": "云南之旅",
  "author": 1,
  "created_at": "2025-11-07T10:00:00Z"
}
```

#### 3.4 更新旅行计划

**端点**: `PATCH /api/v1/trip-plans/{slug}/`

**权限**: 作者或管理员

**请求**：
```json
{
  "title": "新标题 (可选)",
  "description": "新描述 (可选)",
  "overview": {  // 部分更新
    "basicInfo": {
      "destination": "云南",
      "duration": "6天5晚"
    }
  }
}
```

**响应** (200 OK):
```json
{
  "slug": "abc123def456",
  "title": "新标题",
  "updated_at": "2025-11-07T11:00:00Z"
}
```

#### 3.5 删除旅行计划

**端点**: `DELETE /api/v1/trip-plans/{slug}/`

**权限**: 作者或管理员

**响应** (204 No Content)

#### 3.6 点赞旅行

**端点**: `POST /api/v1/trips/{slug}/like/`

**权限**: 匿名

**响应** (200 OK):
```json
{
  "likes": 57
}
```

#### 3.7 打卡旅行

**端点**: `POST /api/v1/trips/{slug}/checkin/`

**权限**: 匿名

**响应** (200 OK):
```json
{
  "checked_in": true
}
```

#### 3.8 获取旅行统计

**端点**: `GET /api/v1/trips/{slug}/stats/`

**权限**: 匿名

**响应** (200 OK):
```json
{
  "page": "trip_abc123",
  "views": 1234,
  "likes": 56,
  "checked_in": true,
  "comments_count": 23
}
```

---

### 4. 评论接口 (Comments)

#### 4.1 获取评论列表

**端点**: `GET /api/v1/comments/`

**权限**: 匿名

**查询参数**：
- `page_filter`: 筛选页面（如 "trip_abc123"）
- `parent_id`: 筛选回复（父评论ID）
- `page`: 页码
- `page_size`: 每页数量

**响应** (200 OK):
```json
{
  "count": 50,
  "results": [
    {
      "id": 1,
      "user": {
        "id": 2,
        "username": "李四",
        "avatar": "https://..."
      },
      "content": "写得真好！",
      "image": "https://...",
      "video": null,
      "page": "trip_abc123",
      "parent": null,
      "replies_count": 3,
      "likes": 12,
      "liked_by_me": false,
      "is_pinned": false,
      "timestamp": "2025-11-06T10:00:00Z"
    }
  ]
}
```

#### 4.2 发表评论

**端点**: `POST /api/v1/comments/`

**权限**: 已认证

**请求**：
```json
{
  "content": "评论内容",
  "page": "trip_abc123",
  "parent": null,  // 父评论ID（回复时填写）
  "image": "https://... (可选)",
  "video": "https://... (可选)"
}
```

**响应** (201 Created):
```json
{
  "id": 1,
  "user": {
    "id": 1,
    "username": "张三"
  },
  "content": "评论内容",
  "timestamp": "2025-11-07T12:00:00Z"
}
```

#### 4.3 点赞评论

**端点**: `POST /api/v1/comments/{id}/like/`

**权限**: 已认证

**响应** (200 OK):
```json
{
  "success": true,
  "likes": 13,
  "liked_by_me": true
}
```

#### 4.4 删除评论

**端点**: `DELETE /api/v1/comments/{id}/`

**权限**: 作者或管理员

**响应** (204 No Content)

---

## 📅 Ralendar API

**Base URL**: `https://app7626.acapp.acwing.com.cn/api/`

### 1. 认证接口 (Auth)

#### 1.1 用户注册

**端点**: `POST /api/auth/register/`

**权限**: 匿名

**请求**：
```json
{
  "username": "string",
  "password": "string",
  "email": "email@example.com (可选)"
}
```

**响应** (201 Created):
```json
{
  "id": 1,
  "username": "张三",
  "email": "user@example.com"
}
```

#### 1.2 用户登录

**端点**: `POST /api/auth/login/`

**权限**: 匿名

**请求**：
```json
{
  "username": "string",
  "password": "string"
}
```

**响应** (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "张三",
    "email": "user@example.com",
    "photo": "https://..."  // AcWing/QQ头像
  }
}
```

#### 1.3 获取当前用户

**端点**: `GET /api/auth/me/`

**权限**: 已认证

**响应** (200 OK):
```json
{
  "id": 1,
  "username": "张三",
  "email": "user@example.com",
  "photo": "https://..."
}
```

#### 1.4 AcWing 一键登录

**端点**: `POST /api/auth/acwing/login/`

**权限**: 匿名

**请求**：
```json
{
  "code": "authorization_code",
  "state": "state_string (可选)"
}
```

**响应** (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "AcWing用户",
    "email": "",
    "photo": "https://cdn.acwing.com/..."
  }
}
```

#### 1.5 AcWing 回调端点

**端点**: `GET /api/oauth2/receive_code/`

**权限**: 匿名

**查询参数**：
- `code`: 授权码
- `state`: 状态码

**响应** (200 OK):
```json
{
  "code": "authorization_code",
  "state": "state_string"
}
```

**说明**：此端点专为 AcWingOS API 设计，返回纯 JSON（不是 HTML）

#### 1.6 QQ 一键登录

**端点**: `POST /api/auth/qq/login/`

**权限**: 匿名

**请求**：
```json
{
  "code": "authorization_code",
  "state": "state_string (可选)"
}
```

**响应** (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "QQ用户",
    "email": "",
    "photo": "http://qzapp.qlogo.cn/..."
  }
}
```

---

### 2. 用户中心接口 (User)

#### 2.1 获取用户统计

**端点**: `GET /api/user/stats/`

**权限**: 已认证

**响应** (200 OK):
```json
{
  "total_events": 45,
  "today_events": 3,
  "upcoming_events": 12  // 未来7天
}
```

#### 2.2 获取绑定状态

**端点**: `GET /api/user/bindings/`

**权限**: 已认证

**响应** (200 OK):
```json
{
  "has_acwing": true,
  "has_qq": true,
  "has_password": true,
  "acwing_username": "AcWing用户",
  "qq_nickname": "QQ昵称"
}
```

#### 2.3 更新个人信息

**端点**: `PATCH /api/user/profile/`

**权限**: 已认证

**请求**：
```json
{
  "username": "新用户名 (可选)",
  "email": "new@example.com (可选)"
}
```

**响应** (200 OK):
```json
{
  "id": 1,
  "username": "新用户名",
  "email": "new@example.com"
}
```

#### 2.4 修改密码

**端点**: `POST /api/user/change-password/`

**权限**: 已认证

**请求**：
```json
{
  "old_password": "string",
  "new_password": "string"
}
```

**响应** (200 OK):
```json
{
  "message": "密码修改成功，请重新登录"
}
```

**说明**：OAuth 账号（无密码）无法调用此接口

#### 2.5 解绑 AcWing

**端点**: `DELETE /api/user/unbind/acwing/`

**权限**: 已认证

**响应** (200 OK):
```json
{
  "message": "AcWing 账号已解绑"
}
```

**错误** (400 Bad Request):
```json
{
  "error": "至少保留一种登录方式"
}
```

#### 2.6 解绑 QQ

**端点**: `DELETE /api/user/unbind/qq/`

**权限**: 已认证

**响应** (200 OK):
```json
{
  "message": "QQ 账号已解绑"
}
```

---

### 3. 日程接口 (Events)

#### 3.1 获取日程列表

**端点**: `GET /api/events/`

**权限**: 已认证（自己的日程），匿名只读（公开日程）

**查询参数**：
- `start_date`: 开始日期（YYYY-MM-DD）
- `end_date`: 结束日期（YYYY-MM-DD）
- `page`: 页码
- `page_size`: 每页数量

**响应** (200 OK):
```json
[
  {
    "id": 1,
    "user": 1,
    "title": "团队会议",
    "description": "讨论Q4计划",
    "start_time": "2025-11-07T14:00:00Z",
    "end_time": "2025-11-07T15:30:00Z",
    "location": "公司会议室",
    "reminder_minutes": 15,
    "created_at": "2025-11-01T10:00:00Z",
    "updated_at": "2025-11-06T15:30:00Z"
  }
]
```

#### 3.2 获取单个日程

**端点**: `GET /api/events/{id}/`

**权限**: 本人

**响应** (200 OK):
```json
{
  "id": 1,
  "user": 1,
  "title": "团队会议",
  "description": "讨论Q4计划",
  "start_time": "2025-11-07T14:00:00Z",
  "end_time": "2025-11-07T15:30:00Z",
  "location": "公司会议室",
  "reminder_minutes": 15,
  "created_at": "2025-11-01T10:00:00Z",
  "updated_at": "2025-11-06T15:30:00Z"
}
```

#### 3.3 创建日程

**端点**: `POST /api/events/`

**权限**: 已认证

**请求**：
```json
{
  "title": "string",
  "description": "string (可选)",
  "start_time": "2025-11-07T14:00:00Z",
  "end_time": "2025-11-07T15:30:00Z (可选)",
  "location": "string (可选)",
  "reminder_minutes": 15  // 0, 5, 15, 30, 60, 1440, 10080
}
```

**响应** (201 Created):
```json
{
  "id": 1,
  "title": "团队会议",
  "start_time": "2025-11-07T14:00:00Z",
  "created_at": "2025-11-07T10:00:00Z"
}
```

#### 3.4 更新日程

**端点**: `PUT /api/events/{id}/` 或 `PATCH /api/events/{id}/`

**权限**: 本人

**请求**：
```json
{
  "title": "新标题 (可选)",
  "start_time": "2025-11-07T15:00:00Z (可选)"
}
```

**响应** (200 OK):
```json
{
  "id": 1,
  "title": "新标题",
  "updated_at": "2025-11-07T12:00:00Z"
}
```

#### 3.5 删除日程

**端点**: `DELETE /api/events/{id}/`

**权限**: 本人

**响应** (204 No Content)

---

### 4. 公开日历接口 (Calendars)

#### 4.1 获取公开日历列表

**端点**: `GET /api/calendars/`

**权限**: 匿名

**响应** (200 OK):
```json
[
  {
    "id": 1,
    "name": "中国法定假日",
    "url_slug": "china-holidays",
    "description": "2025年中国法定假日日历",
    "is_public": true,
    "created_by": 1,
    "events_count": 11,
    "created_at": "2025-01-01T00:00:00Z"
  }
]
```

#### 4.2 创建公开日历

**端点**: `POST /api/calendars/`

**权限**: 已认证

**请求**：
```json
{
  "name": "string",
  "url_slug": "unique-slug",
  "description": "string (可选)",
  "is_public": true
}
```

**响应** (201 Created):
```json
{
  "id": 1,
  "name": "我的课程表",
  "url_slug": "my-schedule",
  "created_at": "2025-11-07T10:00:00Z"
}
```

#### 4.3 订阅公开日历

**端点**: `POST /api/calendars/{id}/subscribe/`

**权限**: 已认证

**响应** (200 OK):
```json
{
  "success": true,
  "message": "订阅成功",
  "synced_events_count": 11
}
```

---

### 5. 农历接口 (Lunar)

#### 5.1 阳历转农历

**端点**: `GET /api/lunar/`

**权限**: 匿名

**查询参数**：
- `year`: 年份（如 2025）
- `month`: 月份（1-12）
- `day`: 日期（1-31）

**响应** (200 OK):
```json
{
  "year": 2025,
  "month": 9,
  "day": 16,
  "isleap": false,
  "lunarDate": "2025年九月十六"
}
```

---

## 🔗 生态融合接口（未来）

### 1. 旅行 → 日程同步

**端点**: `POST /api/v1/trips/{slug}/sync-to-calendar/`

**权限**: 作者

**请求**：
```json
{
  "create_events": true,  // 是否创建日程
  "calendar_api_base": "https://ralendar.com/api/"  // Ralendar API 地址
}
```

**响应** (200 OK):
```json
{
  "success": true,
  "synced_events": [
    {
      "id": 1,
      "title": "飞机起飞",
      "start_time": "2025-11-15T10:00:00Z"
    }
  ],
  "synced_count": 3
}
```

**实现逻辑**：
```python
def sync_to_calendar(trip):
    events = []
    
    # 从旅行计划提取日程
    if trip.overview.get('itinerary'):
        for item in trip.overview['itinerary']:
            event = {
                'title': item['title'],
                'start_time': item['time'],
                'location': item.get('location', ''),
                'description': f"来自旅行：{trip.title}"
            }
            events.append(event)
    
    # 调用 Ralendar API 批量创建
    # POST /api/events/batch/
    return events
```

### 2. 日程 → 旅行关联

**端点**: `PATCH /api/events/{id}/link-trip/`

**权限**: 本人

**请求**：
```json
{
  "trip_slug": "abc123def456",
  "roamio_api_base": "https://roamio.com/api/v1/"
}
```

**响应** (200 OK):
```json
{
  "success": true,
  "event_id": 1,
  "trip_slug": "abc123def456",
  "linked": true
}
```

### 3. 用户信息同步

**端点**: `POST /api/sync/user-info/`

**权限**: 系统级（需要 API Key）

**请求**：
```json
{
  "user_id": 1,
  "source": "roamio",  // roamio | ralendar
  "data": {
    "username": "张三",
    "email": "user@example.com",
    "avatar": "https://..."
  }
}
```

**响应** (200 OK):
```json
{
  "success": true,
  "synced_fields": ["username", "email", "avatar"]
}
```

---

## 📊 数据模型关系

### Roamio 核心模型

```python
User (Django 内置)
├── UserProfile (一对一)
│   ├── avatar
│   ├── bio
│   ├── level
│   └── email_verified
├── SocialAccount (一对多)
│   ├── provider (qq/wechat/github)
│   ├── uid
│   └── avatar_url
├── Trip (一对多)
│   ├── slug
│   ├── title
│   ├── overview (JSON)
│   └── config (JSON)
└── Comment (一对多)
    ├── content
    ├── page
    └── parent (自关联)
```

### Ralendar 核心模型

```python
User (Django 内置) - 与 Roamio 共享
├── AcWingUser (一对一)
│   ├── openid
│   └── photo_url
├── QQUser (一对一)
│   ├── openid
│   └── nickname
├── Event (一对多)
│   ├── title
│   ├── start_time
│   ├── end_time (可选)
│   ├── location
│   └── reminder_minutes
└── PublicCalendar (一对多)
    ├── name
    ├── url_slug
    └── events (多对多)
```

### 融合后的扩展模型

```python
# Ralendar Event 扩展
class Event(models.Model):
    # 原有字段
    user = ForeignKey(User)
    title = CharField()
    start_time = DateTimeField()
    
    # 新增：关联旅行
    related_trip_slug = CharField(null=True, blank=True)  # Roamio Trip slug
    sync_from = CharField(choices=['manual', 'roamio'])  # 来源
    
# Roamio Trip 扩展
class Trip(models.Model):
    # 原有字段
    slug = SlugField()
    title = CharField()
    
    # 新增：关联日程
    synced_to_calendar = BooleanField(default=False)
    calendar_events_ids = JSONField(default=list)  # Ralendar Event IDs
```

---

## 🌟 API 设计原则

### 1. RESTful 规范

- **资源名词化**：`/api/events/` 而不是 `/api/get-events/`
- **HTTP 方法语义化**：GET 查询，POST 创建，PATCH 部分更新，PUT 完整更新，DELETE 删除
- **状态码标准化**：200 成功，201 创建，400 客户端错误，401 未认证，403 无权限，404 未找到，500 服务器错误

### 2. 统一响应格式

**成功响应**：
```json
{
  "data": {...},
  "message": "操作成功 (可选)"
}
```

**错误响应**：
```json
{
  "error": "错误描述",
  "error_code": "ERROR_CODE (可选)",
  "details": {...} (可选)
}
```

### 3. 分页规范

**查询参数**：
- `page`: 页码（从 1 开始）
- `page_size`: 每页数量（默认 20，最大 100）

**响应格式**：
```json
{
  "count": 100,
  "next": "https://.../api/resource/?page=2",
  "previous": null,
  "results": [...]
}
```

### 4. 过滤和排序

**过滤参数**：
- 字段名直接作为查询参数：`?status=published&visibility=public`
- 时间范围：`?start_date=2025-11-01&end_date=2025-11-30`

**排序参数**：
- `ordering`: 排序字段，加 `-` 表示降序
- 示例：`?ordering=-created_at` （最新的在前）

### 5. 时间格式

**标准格式**: ISO 8601
- 日期时间：`2025-11-07T14:30:00Z` (UTC)
- 日期：`2025-11-07`
- 时间：`14:30:00`

---

## 🔧 技术实现指南

### 1. 跨项目 API 调用

#### 场景：Roamio 调用 Ralendar API

```python
# roamio/backend/utils/ralendar_client.py

import requests
from django.conf import settings

class RalendarClient:
    """Ralendar API 客户端"""
    
    def __init__(self, user_token=None):
        self.base_url = settings.RALENDAR_API_BASE
        self.token = user_token
    
    def get_headers(self):
        """获取请求头"""
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers
    
    def create_event(self, event_data):
        """创建日程"""
        url = f'{self.base_url}/events/'
        response = requests.post(
            url,
            json=event_data,
            headers=self.get_headers(),
            timeout=10
        )
        return response.json()
    
    def sync_trip_events(self, trip, user_token):
        """同步旅行计划到日历"""
        events = []
        
        # 从旅行计划提取日程
        if trip.overview.get('itinerary'):
            for item in trip.overview['itinerary']:
                event_data = {
                    'title': item['title'],
                    'start_time': item['time'],
                    'location': item.get('location', ''),
                    'description': f"来自旅行：{trip.title}",
                    'related_trip_slug': trip.slug
                }
                
                result = self.create_event(event_data)
                events.append(result)
        
        return events

# 使用示例
client = RalendarClient(user_token=request.user.get_jwt_token())
synced_events = client.sync_trip_events(trip, user_token)
```

### 2. 共享认证实现

#### 方案 A：共享 Django User 表（推荐）

```python
# settings.py（两个项目配置相同数据库）

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'roamio_ecosystem',  # 共享数据库
        'USER': 'roamio_user',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# JWT 配置（两个项目使用相同的 SECRET_KEY）
SECRET_KEY = 'same-secret-key-for-both-projects'

# 这样生成的 JWT Token 可以在两个项目中互通
```

**优势**：
- ✅ 一个账号，两个产品
- ✅ Token 互通
- ✅ 用户信息同步

#### 方案 B：API 互调验证

```python
# ralendar/backend/api/middleware/roamio_auth.py

class RoamioTokenMiddleware:
    """验证来自 Roamio 的 Token"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 检查是否来自 Roamio
        if request.META.get('HTTP_X_SOURCE') == 'roamio':
            token = request.META.get('HTTP_X_ROAMIO_TOKEN')
            
            # 调用 Roamio API 验证 Token
            user = self.verify_roamio_token(token)
            if user:
                request.user = user
        
        return self.get_response(request)
    
    def verify_roamio_token(self, token):
        """调用 Roamio API 验证 Token"""
        response = requests.get(
            'https://roamio.com/api/v1/auth/verify-token/',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if response.status_code == 200:
            user_data = response.json()
            # 在本地创建/更新用户
            return self.get_or_create_user(user_data)
        
        return None
```

### 3. Webhook 实现（事件驱动）

```python
# roamio/backend/utils/webhooks.py

class WebhookService:
    """Webhook 服务"""
    
    @staticmethod
    def trigger_event(event_type, data):
        """触发 Webhook 事件"""
        webhooks = [
            {
                'name': 'ralendar',
                'url': 'https://ralendar.com/api/webhooks/roamio/',
                'events': ['trip.created', 'trip.updated', 'trip.deleted']
            }
        ]
        
        for webhook in webhooks:
            if event_type in webhook['events']:
                try:
                    requests.post(
                        webhook['url'],
                        json={
                            'event': event_type,
                            'data': data,
                            'timestamp': timezone.now().isoformat()
                        },
                        headers={
                            'X-Webhook-Signature': generate_signature(data)
                        },
                        timeout=5
                    )
                except:
                    pass  # 失败不影响主流程

# 使用示例
def create_trip(request):
    trip = Trip.objects.create(...)
    
    # 触发 Webhook
    WebhookService.trigger_event('trip.created', {
        'trip_id': trip.id,
        'slug': trip.slug,
        'title': trip.title,
        'start_date': trip.start_date,
        'end_date': trip.end_date
    })
    
    return Response(...)
```

---

## 🚀 部署配置

### Nginx 配置（统一入口）

```nginx
server {
    listen 443 ssl;
    server_name roamio.cn;
    
    # SSL 证书
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # Roamio 前端
    location / {
        root /var/www/roamio/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # Roamio API
    location /api/v1/ {
        proxy_pass http://127.0.0.1:8000/api/v1/;
        proxy_set_header Host $host;
        proxy_set_header Authorization $http_authorization;
    }
    
    # Ralendar 前端（子路径）
    location /calendar/ {
        root /var/www/ralendar/dist;
        try_files $uri $uri/ /calendar/index.html;
    }
    
    # Ralendar API（代理到另一个端口）
    location /api/calendar/ {
        proxy_pass http://127.0.0.1:8001/api/;
        proxy_set_header Host $host;
        proxy_set_header Authorization $http_authorization;
    }
    
    # 静态文件
    location /static/ {
        alias /var/www/static/;
        expires 30d;
    }
}
```

### 环境变量配置

#### Roamio

```bash
# roamio/.env

# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=roamio.cn,*.roamio.cn

# Database
DB_ENGINE=postgresql
DB_NAME=roamio_ecosystem
DB_USER=roamio_user
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# QQ OAuth
QQ_APPID=102814915
QQ_APPKEY=your-qq-appkey

# 腾讯云 COS
TENCENT_COS_SECRET_ID=your-secret-id
TENCENT_COS_SECRET_KEY=your-secret-key
TENCENT_COS_BUCKET=roamio-1234567
TENCENT_COS_REGION=ap-beijing

# 邮件服务
EMAIL_HOST=smtp.qq.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@qq.com
EMAIL_HOST_PASSWORD=your-smtp-password

# Ralendar API（用于跨项目调用）
RALENDAR_API_BASE=https://roamio.cn/api/calendar/
```

#### Ralendar

```bash
# ralendar/.env

# Django
SECRET_KEY=same-as-roamio  # 如果共享JWT，必须相同
DEBUG=False
ALLOWED_HOSTS=roamio.cn,app7626.acapp.acwing.com.cn

# Database（可以共享 Roamio 的数据库）
DB_ENGINE=postgresql
DB_NAME=roamio_ecosystem  # 与 Roamio 共享
DB_USER=roamio_user
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# AcWing OAuth
ACWING_APPID=7626
ACWING_SECRET=your-acwing-secret

# QQ OAuth
QQ_APPID=102818448
QQ_APPKEY=your-qq-appkey

# Roamio API（用于跨项目调用）
ROAMIO_API_BASE=https://roamio.cn/api/v1/
```

---

## 🔄 跨项目调用示例

### 示例 1：Roamio 创建旅行时同步到 Ralendar

```python
# roamio/backend/views/trip_views.py

from ..utils.ralendar_client import RalendarClient

class TripViewSet(viewsets.ModelViewSet):
    
    @action(detail=True, methods=['post'])
    def sync_to_calendar(self, request, slug=None):
        """同步旅行计划到日历"""
        trip = self.get_object()
        
        # 获取用户的 JWT Token
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        user_token = auth_header.replace('Bearer ', '')
        
        # 初始化 Ralendar 客户端
        ralendar = RalendarClient(user_token=user_token)
        
        # 提取行程中的事件
        events_to_create = []
        
        if trip.overview.get('itinerary'):
            for day_item in trip.overview['itinerary']:
                for activity in day_item.get('activities', []):
                    event = {
                        'title': f"{trip.title} - {activity['name']}",
                        'start_time': f"{trip.start_date}T{activity.get('time', '09:00')}:00Z",
                        'location': activity.get('location', ''),
                        'description': f"来自旅行计划：{trip.title}",
                        'reminder_minutes': 60  # 提前1小时提醒
                    }
                    events_to_create.append(event)
        
        # 批量创建日程
        synced_events = []
        for event_data in events_to_create:
            try:
                result = ralendar.create_event(event_data)
                synced_events.append(result)
            except Exception as e:
                print(f"Failed to sync event: {e}")
        
        # 记录同步状态
        trip.synced_to_calendar = True
        trip.calendar_events_ids = [e['id'] for e in synced_events]
        trip.save()
        
        return Response({
            'success': True,
            'synced_events_count': len(synced_events),
            'events': synced_events
        })
```

### 示例 2：Ralendar 显示关联的旅行信息

```python
# ralendar/backend/api/views/events.py

from ..utils.roamio_client import RoamioClient

class EventViewSet(viewsets.ModelViewSet):
    
    @action(detail=True, methods=['get'])
    def related_trip(self, request, pk=None):
        """获取关联的旅行信息"""
        event = self.get_object()
        
        if not event.related_trip_slug:
            return Response({
                'has_related_trip': False
            })
        
        # 调用 Roamio API 获取旅行信息
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        user_token = auth_header.replace('Bearer ', '')
        
        roamio = RoamioClient(user_token=user_token)
        trip_info = roamio.get_trip(event.related_trip_slug)
        
        if trip_info:
            return Response({
                'has_related_trip': True,
                'trip': {
                    'slug': trip_info['slug'],
                    'title': trip_info['title'],
                    'start_date': trip_info['start_date'],
                    'end_date': trip_info['end_date'],
                    'url': f'https://roamio.cn/trips/{trip_info["slug"]}/'
                }
            })
        
        return Response({
            'has_related_trip': False,
            'error': '关联的旅行不存在或无权访问'
        })
```

---

## 📋 API 端点总览

### Roamio API 端点汇总

| 端点 | 方法 | 功能 | 权限 |
|-----|------|------|------|
| `/api/v1/auth/register/` | POST | 用户注册 | 匿名 |
| `/api/v1/auth/login/` | POST | 用户登录 | 匿名 |
| `/api/v1/auth/me/` | GET | 获取当前用户 | 已认证 |
| `/api/v1/auth/logout/` | POST | 用户登出 | 已认证 |
| `/api/v1/auth/send_verification_code/` | POST | 发送验证码 | 匿名 |
| `/api/v1/auth/verify_code/` | POST | 验证验证码 | 匿名 |
| `/api/v1/auth/qq_login_url/` | GET | 获取QQ登录URL | 匿名 |
| `/api/v1/auth/qq_callback/` | POST | QQ登录回调 | 匿名 |
| `/api/v1/auth/qq_bind_existing/` | POST | 绑定QQ（已有账号）| 已认证 |
| `/api/v1/auth/qq_unbind/` | DELETE | 解绑QQ | 已认证 |
| `/api/v1/auth/reset_password/` | POST | 重置密码 | 匿名 |
| `/api/v1/users/` | GET | 获取用户列表 | 匿名 |
| `/api/v1/users/{id}/` | GET | 获取用户详情 | 匿名 |
| `/api/v1/users/{id}/profile/` | PATCH | 更新个人资料 | 本人 |
| `/api/v1/users/{id}/avatar/` | POST | 上传头像 | 本人 |
| `/api/v1/trips/` | GET | 获取旅行列表 | 匿名 |
| `/api/v1/trips/{slug}/` | GET | 获取旅行详情 | 条件 |
| `/api/v1/trips/{slug}/like/` | POST | 点赞 | 匿名 |
| `/api/v1/trips/{slug}/checkin/` | POST | 打卡 | 匿名 |
| `/api/v1/trips/{slug}/stats/` | GET | 获取统计 | 匿名 |
| `/api/v1/trips/{slug}/comments/` | GET | 获取评论 | 匿名 |
| `/api/v1/trip-plans/` | GET, POST | 旅行计划CRUD | 条件 |
| `/api/v1/trip-plans/{slug}/` | GET, PATCH, DELETE | 旅行计划操作 | 作者 |
| `/api/v1/comments/` | GET, POST | 评论CRUD | 条件 |
| `/api/v1/comments/{id}/` | GET, DELETE | 评论操作 | 条件 |
| `/api/v1/comments/{id}/like/` | POST | 点赞评论 | 已认证 |
| `/api/v1/token/` | POST | 获取Token | 匿名 |
| `/api/v1/token/refresh/` | POST | 刷新Token | 匿名 |

**总计**: 30+ 个端点

### Ralendar API 端点汇总

| 端点 | 方法 | 功能 | 权限 |
|-----|------|------|------|
| `/api/auth/register/` | POST | 用户注册 | 匿名 |
| `/api/auth/login/` | POST | 用户登录 | 匿名 |
| `/api/auth/refresh/` | POST | 刷新Token | 匿名 |
| `/api/auth/me/` | GET | 获取当前用户 | 已认证 |
| `/api/auth/acwing/login/` | POST | AcWing登录 | 匿名 |
| `/api/oauth2/receive_code/` | GET | AcWing回调 | 匿名 |
| `/api/auth/qq/login/` | POST | QQ登录 | 匿名 |
| `/api/user/stats/` | GET | 用户统计 | 已认证 |
| `/api/user/bindings/` | GET | 绑定状态 | 已认证 |
| `/api/user/profile/` | PATCH | 更新资料 | 已认证 |
| `/api/user/change-password/` | POST | 修改密码 | 已认证 |
| `/api/user/unbind/acwing/` | DELETE | 解绑AcWing | 已认证 |
| `/api/user/unbind/qq/` | DELETE | 解绑QQ | 已认证 |
| `/api/events/` | GET, POST | 日程CRUD | 条件 |
| `/api/events/{id}/` | GET, PUT, PATCH, DELETE | 日程操作 | 本人 |
| `/api/calendars/` | GET, POST | 公开日历CRUD | 条件 |
| `/api/calendars/{id}/` | GET, PUT, PATCH, DELETE | 日历操作 | 条件 |
| `/api/lunar/` | GET | 农历转换 | 匿名 |

**总计**: 20+ 个端点

---

## 📝 最佳实践

### 1. 错误处理

**统一错误格式**：
```json
{
  "error": "错误描述",
  "error_code": "INVALID_INPUT",
  "details": {
    "field": "具体字段错误"
  }
}
```

**常见错误码**：
- `INVALID_INPUT` - 输入无效
- `UNAUTHORIZED` - 未认证
- `FORBIDDEN` - 无权限
- `NOT_FOUND` - 资源不存在
- `RATE_LIMIT_EXCEEDED` - 超过频率限制
- `INTERNAL_ERROR` - 服务器内部错误

### 2. 版本控制

**URL 版本化**：
- Roamio: `/api/v1/...`
- Ralendar: `/api/...` (当前版本)
- 未来: `/api/v2/...` (向后兼容)

**废弃策略**：
- 提前3个月通知
- 返回 `Deprecated` 头
- 提供迁移指南

### 3. 性能优化

**分页**：
- 所有列表接口必须分页
- 默认 20 条/页
- 最大 100 条/页

**缓存**：
- 使用 Redis 缓存热点数据
- 旅行详情缓存 5 分钟
- 评论列表缓存 1 分钟

**查询优化**：
- 使用 `select_related` 预加载外键
- 使用 `prefetch_related` 预加载多对多
- 添加数据库索引

### 4. 安全考虑

**CORS 配置**：
```python
CORS_ALLOWED_ORIGINS = [
    'https://roamio.cn',
    'https://www.roamio.cn',
    'https://app7626.acapp.acwing.com.cn',
    'https://www.acwing.com',
]
```

**频率限制**：
- 匿名用户：100 请求/小时
- 已认证用户：1000 请求/小时
- 敏感操作（发送验证码）：特殊限制

**SQL 注入防护**：
- 使用 Django ORM（自动转义）
- 避免原始 SQL 查询

**XSS 防护**：
- 用户输入内容转义
- 使用 DRF Serializer 验证

---

## 🧪 API 测试

### 使用 Postman/Insomnia

#### 环境变量

```
ROAMIO_BASE_URL = https://roamio.cn
RALENDAR_BASE_URL = https://app7626.acapp.acwing.com.cn
ACCESS_TOKEN = (登录后获取)
```

#### 测试流程

**1. 注册/登录**
```
POST {{ROAMIO_BASE_URL}}/api/v1/auth/register/
→ 获取 access_token
```

**2. 创建旅行**
```
POST {{ROAMIO_BASE_URL}}/api/v1/trip-plans/
Headers: Authorization: Bearer {{ACCESS_TOKEN}}
```

**3. 同步到日历**
```
POST {{ROAMIO_BASE_URL}}/api/v1/trips/{slug}/sync-to-calendar/
```

**4. 查看日程**
```
GET {{RALENDAR_BASE_URL}}/api/events/
Headers: Authorization: Bearer {{ACCESS_TOKEN}}
```

### 使用 Swagger UI

**Roamio**: https://roamio.cn/api/docs/  
**Ralendar**: (待集成 drf-yasg)

---

## 🌟 未来扩展接口（预留）

### 1. 智能推荐

**端点**: `GET /api/v1/recommendations/trips/`

**功能**: 基于用户历史推荐旅行

### 2. 地图集成

**端点**: `POST /api/events/{id}/geocode/`

**功能**: 地址 → 坐标转换

### 3. AI 助手

**端点**: `POST /api/ai/create-event/`

**功能**: 语音转文字 → 创建日程

### 4. 数据分析

**端点**: `GET /api/analytics/user-insights/`

**功能**: 用户行为分析

---

## 📚 相关文档

- [Roamio 项目文档](./roamio/docs/README.md)
- [Ralendar 项目文档](./tc_camp_projects/kotlin_calendar/README.md)
- [生态融合计划](./ROAMIO_RALENDAR_INTEGRATION_PLAN.md)
- [部署指南](./DEPLOYMENT_GUIDE.md)

---

## 🔗 快速链接

- **Roamio 项目**: https://github.com/yourusername/roamio
- **Ralendar 项目**: https://github.com/yourusername/kotlin-calendar
- **API 在线文档**: https://roamio.cn/api/docs/
- **问题反馈**: https://github.com/yourusername/roamio/issues

---

## 📞 联系方式

**技术支持**: tech@roamio.cn  
**商务合作**: business@roamio.cn  
**API 文档维护**: Roamio Team

---

**最后更新**: 2025-11-07  
**文档版本**: v1.0.0  
**作者**: Roamio Team

**© 2025 Roamio. 用心打造有温度的数字生活系统。** 🌏✨

