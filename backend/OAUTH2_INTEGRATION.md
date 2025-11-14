# OAuth 2.0 集成文档

## 📖 概述

Ralendar 实现了标准的 OAuth 2.0 Authorization Code Flow，允许第三方应用（如 Roamio）安全地访问用户的日历数据。

---

## 🎯 核心特性

- ✅ **标准 OAuth 2.0**：遵循 RFC 6749 规范
- ✅ **细粒度权限控制**：支持多种 scope
- ✅ **Token 刷新机制**：支持 refresh_token
- ✅ **Token 撤销**：用户可随时撤销授权
- ✅ **安全可靠**：JWT + 数据库双重验证

---

## 🔧 实现的接口

### 1. 授权端点

**URL**: `GET /oauth/authorize`

**用途**: 用户授权页面

**参数**:
- `client_id` (必需): 客户端ID
- `redirect_uri` (必需): 回调地址
- `response_type` (必需): 固定为 `code`
- `state` (必需): 防CSRF的随机字符串
- `scope` (可选): 权限范围，默认 `calendar:read`

**示例**:
```
https://ralendar.com/oauth/authorize?
    client_id=roamio_client_xxx&
    redirect_uri=https://roamio.cn/auth/callback&
    response_type=code&
    state=random_string_12345&
    scope=calendar:read calendar:write user:read
```

**响应**:
- 用户同意: 重定向到 `redirect_uri?code=xxx&state=xxx`
- 用户拒绝: 重定向到 `redirect_uri?error=access_denied&state=xxx`

---

### 2. Token 端点

**URL**: `POST /api/oauth/token`

**用途**: 用授权码换取访问令牌

**请求头**:
```
Content-Type: application/json
```

**请求体**:
```json
{
  "grant_type": "authorization_code",
  "code": "AUTHORIZATION_CODE_xxx",
  "client_id": "roamio_client_xxx",
  "client_secret": "CLIENT_SECRET_xxx",
  "redirect_uri": "https://roamio.cn/auth/callback"
}
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 7200,
  "refresh_token": "REFRESH_TOKEN_xxx",
  "scope": "calendar:read calendar:write user:read"
}
```

---

### 3. 刷新Token

**URL**: `POST /api/oauth/token`

**请求体**:
```json
{
  "grant_type": "refresh_token",
  "refresh_token": "REFRESH_TOKEN_xxx",
  "client_id": "roamio_client_xxx",
  "client_secret": "CLIENT_SECRET_xxx"
}
```

**响应**: 同上（返回新的 access_token 和 refresh_token）

---

### 4. UserInfo 端点

**URL**: `GET /api/oauth/userinfo`

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应**:
```json
{
  "user_id": 12345,
  "username": "张三",
  "email": "zhangsan@example.com",
  "avatar": "https://ralendar.com/media/avatars/user_12345.jpg",
  "provider": "qq",
  "openid": "xxx",
  "unionid": "ABC123",
  "created_at": "2025-01-01T12:00:00Z"
}
```

---

### 5. Token 撤销端点

**URL**: `POST /api/oauth/revoke`

**请求头**:
```
Authorization: Bearer {access_token}
```

**请求体**:
```json
{
  "client_id": "roamio_client_xxx",
  "revoke_all": true
}
```

**响应**:
```json
{
  "success": true,
  "message": "已撤销 3 个访问令牌",
  "revoked_count": 3
}
```

---

### 6. 已授权应用列表

**URL**: `GET /api/oauth/authorized-apps`

**请求头**:
```
Authorization: Bearer {ralendar_jwt_token}
```

**响应**:
```json
{
  "apps": [
    {
      "client_id": "roamio_client_xxx",
      "client_name": "Roamio",
      "client_description": "Roamio 旅行规划应用",
      "logo_url": "https://roamio.cn/logo.png",
      "scope": "calendar:read calendar:write",
      "authorized_at": "2025-11-14T10:00:00Z",
      "last_used_at": "2025-11-14T15:30:00Z",
      "token_count": 2
    }
  ],
  "total": 1
}
```

---

## 🔐 权限范围（Scope）

| Scope | 描述 |
|-------|------|
| `calendar:read` | 查看日历事件 |
| `calendar:write` | 创建和编辑日历事件 |
| `calendar:delete` | 删除日历事件 |
| `user:read` | 读取用户基本信息 |

---

## 🚀 快速开始

### 步骤 1：注册 OAuth 客户端

运行管理命令初始化客户端：

```bash
cd backend
python manage.py init_oauth_client \
    --client-name "Roamio" \
    --redirect-uris "https://roamio.cn/auth/callback,http://localhost:8080/auth/callback"
```

命令会输出：
```
=== 客户端配置信息 ===
Client ID:     ralendar_client_xxx
Client Secret: yyy
Client Name:   Roamio
Redirect URIs:
  - https://roamio.cn/auth/callback
  - http://localhost:8080/auth/callback
Allowed Scopes:
  - calendar:read
  - calendar:write
  - user:read

⚠️  请妥善保管 Client Secret，不要泄露！
```

### 步骤 2：Roamio 后端配置

在 Roamio 的环境变量中设置：

```bash
RALENDAR_CLIENT_ID=ralendar_client_xxx
RALENDAR_CLIENT_SECRET=yyy
RALENDAR_OAUTH_URL=https://ralendar.com/oauth/authorize
RALENDAR_TOKEN_URL=https://ralendar.com/api/oauth/token
```

### 步骤 3：实现授权流程

参考 Roamio 团队提供的文档实现 OAuth 客户端。

---

## 📊 数据库模型

### OAuthClient（OAuth客户端）

```python
class OAuthClient(models.Model):
    client_id = models.CharField(max_length=100, unique=True)
    client_secret_hash = models.CharField(max_length=255)  # 加密存储
    client_name = models.CharField(max_length=100)
    redirect_uris = models.JSONField(default=list)
    allowed_scopes = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### AuthorizationCode（授权码）

```python
class AuthorizationCode(models.Model):
    code = models.CharField(max_length=100, unique=True)
    client = models.ForeignKey(OAuthClient, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    redirect_uri = models.CharField(max_length=500)
    scope = models.CharField(max_length=200)
    expires_at = models.DateTimeField()  # 10分钟过期
    used = models.BooleanField(default=False)
```

### OAuthAccessToken（访问令牌）

```python
class OAuthAccessToken(models.Model):
    token = models.CharField(max_length=500, unique=True)  # JWT
    client = models.ForeignKey(OAuthClient, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    scope = models.CharField(max_length=200)
    expires_at = models.DateTimeField()  # 2小时过期
    refresh_token = models.CharField(max_length=100, blank=True, null=True)
    is_revoked = models.BooleanField(default=False)
    last_used_at = models.DateTimeField(null=True, blank=True)
```

---

## 🛡️ 安全机制

1. **Client Secret 加密存储**: 使用 Django 的 `make_password` 加密
2. **State 参数**: 防止 CSRF 攻击
3. **授权码一次性**: 使用后立即标记为 `used=True`
4. **Token 时效性**: 
   - 授权码: 10分钟
   - Access Token: 2小时
   - Refresh Token: 可长期有效
5. **Redirect URI 白名单**: 严格校验回调地址
6. **JWT 签名**: 防止 Token 伪造

---

## 🧪 测试场景

### 场景 1：完整授权流程

```python
# 1. 构造授权URL
auth_url = f"https://ralendar.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&state={state}&scope=calendar:read%20calendar:write"

# 2. 用户访问授权页面，点击"授权"
# 3. 重定向回 Roamio，提取 code
code = request.GET.get('code')

# 4. 后端用 code 换取 token
response = requests.post('https://ralendar.com/api/oauth/token', json={
    'grant_type': 'authorization_code',
    'code': code,
    'client_id': client_id,
    'client_secret': client_secret,
    'redirect_uri': redirect_uri
})

access_token = response.json()['access_token']

# 5. 使用 token 调用 API
headers = {'Authorization': f'Bearer {access_token}'}
events = requests.get('https://ralendar.com/api/events', headers=headers).json()
```

### 场景 2：Token 刷新

```python
response = requests.post('https://ralendar.com/api/oauth/token', json={
    'grant_type': 'refresh_token',
    'refresh_token': refresh_token,
    'client_id': client_id,
    'client_secret': client_secret
})

new_access_token = response.json()['access_token']
```

### 场景 3：撤销授权

```python
response = requests.post('https://ralendar.com/api/oauth/revoke', 
    headers={'Authorization': f'Bearer {access_token}'},
    json={'client_id': client_id, 'revoke_all': True}
)
```

---

## 📝 错误码

| 错误码 | HTTP状态 | 说明 |
|--------|---------|------|
| `invalid_request` | 400 | 请求参数错误 |
| `invalid_client` | 401 | client_id/secret 错误 |
| `invalid_grant` | 400 | 授权码无效 |
| `unauthorized_client` | 401 | 客户端未授权 |
| `unsupported_grant_type` | 400 | 不支持的授权类型 |
| `invalid_scope` | 400 | 权限范围无效 |
| `invalid_token` | 401 | Token 无效或已过期 |
| `insufficient_scope` | 403 | 权限不足 |

---

## 🔄 维护任务

### 定期清理过期数据

```python
# 清理过期的授权码
AuthorizationCode.cleanup_expired()

# 清理过期的访问令牌
OAuthAccessToken.cleanup_expired()
```

建议设置定时任务（Celery）每天执行一次。

---

## 📞 技术支持

- **Ralendar 开发团队**: dev@ralendar.example.com
- **文档更新**: 2025-11-14
- **版本**: v1.0

---

## 🎉 完成状态

✅ OAuth 2.0 服务器已完整实现！

**已实现的功能**:
- ✅ 授权端点 (`/oauth/authorize`)
- ✅ Token 端点 (`/api/oauth/token`)
- ✅ UserInfo 端点 (`/api/oauth/userinfo`)
- ✅ Token 撤销 (`/api/oauth/revoke`)
- ✅ 授权管理 (`/api/oauth/authorized-apps`)
- ✅ 权限验证中间件 (`@require_oauth_scope`)
- ✅ Token 刷新机制
- ✅ 管理命令 (`init_oauth_client`)
- ✅ 前端授权页面

**可供 Roamio 使用的功能**:
1. 用户授权流程
2. 日历事件CRUD API（需要 OAuth Token）
3. 用户信息API
4. Token管理

