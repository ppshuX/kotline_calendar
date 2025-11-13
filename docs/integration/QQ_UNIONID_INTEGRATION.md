# 🔗 Ralendar × Roamio QQ UnionID 集成指南

**目标**: 通过 QQ UnionID 实现两个应用的用户账号互通  
**前提**: 两个应用都已获取 QQ UnionID 接口权限  
**最后更新**: 2025-11-08

---

## 📊 当前配置

### Roamio QQ 应用
```
APP ID:  102813859
APP Key: OddPvLYXHo69wTYO
状态:    ✅ UnionID 已获取
网站地址: https://roamio.cn
回调:    https://roamio.cn/settings/qq/receive_code
备案号:  滇ICP备2025073012号-1
```

### Ralendar QQ 应用
```
APP ID:  102818448
APP Key: sZ0B7nDQP8Bzb1JP
状态:    ✅ UnionID 已获取
回调:    https://app7626.acapp.acwing.com.cn/api/v1/auth/qq/callback/
```

---

## 🎯 UnionID 工作原理

### 1. 什么是 UnionID？

**UnionID** 是 QQ 互联提供的**跨应用统一用户标识**：
- 同一个 QQ 用户在不同应用中有不同的 `openid`（应用内唯一）
- 但在**同一开发者账号**下的所有应用，该用户有**相同的 `unionid`**（全局唯一）

```
用户: 张三（QQ: 123456789）

在 Roamio 中:
  openid:  ABC123DEF  （仅在 Roamio 有效）
  unionid: UNION-XYZ-999  ✅（跨应用统一标识）

在 Ralendar 中:
  openid:  XYZ789GHI  （仅在 Ralendar 有效）
  unionid: UNION-XYZ-999  ✅（与 Roamio 相同！）
```

**关键**: 通过 `unionid` 字段，两个应用可以识别为同一用户！

---

## 🔧 技术实现步骤

### 步骤 1: 确认 UnionID 权限（两边都要）

**Roamio**: ✅ 已完成（截图显示已获取）

**Ralendar**: ✅ 已完成（截图显示已获取）

---

### 步骤 2: 修改 QQ OAuth 请求（添加 unionid=1 参数）

**当前 OAuth URL**:
```
https://graph.qq.com/oauth2.0/authorize?
  response_type=code
  &client_id={APP_ID}
  &redirect_uri={CALLBACK_URL}
  &state={STATE}
```

**修改后（添加 unionid=1）**:
```
https://graph.qq.com/oauth2.0/authorize?
  response_type=code
  &client_id={APP_ID}
  &redirect_uri={CALLBACK_URL}
  &state={STATE}
  &unionid=1  ← 添加这个参数！
```

---

### 步骤 3: 获取 UnionID（API 调用）

在获取用户信息时，QQ 会额外返回 `unionid` 字段：

**API 请求**:
```
GET https://graph.qq.com/user/get_user_info?
  access_token={ACCESS_TOKEN}
  &oauth_consumer_key={APP_ID}
  &openid={OPENID}
  &unionid=1  ← 添加这个参数
```

**响应示例**:
```json
{
  "ret": 0,
  "msg": "success",
  "nickname": "张三",
  "figureurl_qq_2": "http://...",
  "unionid": "UID_A1B2C3D4E5F6G7H8"  ← 这个是关键！
}
```

---

### 步骤 4: 数据库存储 UnionID

#### Roamio 数据库（已有）:
```python
# models.py
class SocialAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.CharField(max_length=20)  # 'qq'
    openid = models.CharField(max_length=100)   # QQ openid
    unionid = models.CharField(max_length=100, blank=True, null=True)  # ✅ UnionID
    nickname = models.CharField(max_length=100)
    avatar_url = models.URLField(blank=True)
```

#### Ralendar 数据库（需要添加 unionid 字段）:
```python
# backend/api/models/user.py
class QQUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='qq_profile')
    openid = models.CharField(max_length=100, unique=True)
    unionid = models.CharField(max_length=100, blank=True, null=True)  # ← 添加这个字段
    access_token = models.CharField(max_length=200, blank=True)
    refresh_token = models.CharField(max_length=200, blank=True)
    photo_url = models.URLField(blank=True)
    nickname = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'api_qquser'
        indexes = [
            models.Index(fields=['unionid']),  # ← 添加索引
        ]
```

**创建迁移文件**:
```bash
cd backend
python manage.py makemigrations api
python manage.py migrate
```

---

### 步骤 5: 修改登录逻辑（保存 UnionID）

#### Roamio 登录逻辑（示例）:
```python
# views/auth.py
def qq_callback(request):
    # 1. 获取 access_token
    access_token = get_access_token(code)
    
    # 2. 获取 openid
    openid = get_openid(access_token)
    
    # 3. 获取用户信息（带 unionid）
    user_info = requests.get(
        'https://graph.qq.com/user/get_user_info',
        params={
            'access_token': access_token,
            'oauth_consumer_key': settings.QQ_APP_ID,
            'openid': openid,
            'unionid': 1  # ← 关键参数
        }
    ).json()
    
    unionid = user_info.get('unionid', '')  # ← 获取 UnionID
    
    # 4. 查找或创建用户
    social_account, created = SocialAccount.objects.get_or_create(
        provider='qq',
        openid=openid,
        defaults={
            'unionid': unionid,  # ← 保存 UnionID
            'nickname': user_info.get('nickname'),
            'avatar_url': user_info.get('figureurl_qq_2')
        }
    )
    
    # 5. 如果是老用户，更新 unionid
    if not created and not social_account.unionid:
        social_account.unionid = unionid
        social_account.save()
    
    # 6. 关联 Django User
    user = social_account.user
    if not user:
        # 首次登录，创建用户
        user = User.objects.create_user(
            username=f'qq_{openid[:8]}',
            email=f'{openid}@qq.user'
        )
        social_account.user = user
        social_account.save()
    
    # 7. 生成 JWT Token
    tokens = get_tokens_for_user(user)
    return Response(tokens)
```

#### Ralendar 登录逻辑（需要修改）:
```python
# backend/api/views/auth.py
@api_view(['POST'])
def qq_login(request):
    code = request.data.get('code')
    
    # 1. 获取 access_token（带 unionid=1）
    token_url = 'https://graph.qq.com/oauth2.0/token'
    token_params = {
        'grant_type': 'authorization_code',
        'client_id': settings.QQ_APPID,
        'client_secret': settings.QQ_APPKEY,
        'code': code,
        'redirect_uri': settings.QQ_REDIRECT_URI,
        'unionid': 1  # ← 添加这个
    }
    
    # 2. 获取 openid（带 unionid=1）
    openid_url = 'https://graph.qq.com/oauth2.0/me'
    openid_params = {
        'access_token': access_token,
        'unionid': 1  # ← 添加这个
    }
    
    # 3. 获取用户信息（带 unionid）
    user_info_url = 'https://graph.qq.com/user/get_user_info'
    user_info_params = {
        'access_token': access_token,
        'oauth_consumer_key': settings.QQ_APPID,
        'openid': openid,
        'unionid': 1  # ← 添加这个
    }
    
    user_info = requests.get(user_info_url, params=user_info_params).json()
    unionid = user_info.get('unionid', '')  # ← 获取 UnionID
    
    # 4. 查找用户（优先通过 unionid 查找）
    if unionid:
        try:
            # 先通过 unionid 查找（跨应用识别）
            qq_user = QQUser.objects.get(unionid=unionid)
            user = qq_user.user
            
            # 更新 openid（因为不同应用的 openid 不同）
            qq_user.openid = openid
            qq_user.access_token = access_token
            qq_user.save()
            
        except QQUser.DoesNotExist:
            # 通过 openid 查找（同应用内）
            try:
                qq_user = QQUser.objects.get(openid=openid)
                user = qq_user.user
                
                # 补充 unionid
                qq_user.unionid = unionid
                qq_user.save()
                
            except QQUser.DoesNotExist:
                # 首次登录，创建新用户
                user = User.objects.create_user(
                    username=f'qq_{openid[:8]}',
                    email=f'{openid}@ralendar.user'
                )
                
                qq_user = QQUser.objects.create(
                    user=user,
                    openid=openid,
                    unionid=unionid,  # ← 保存 UnionID
                    access_token=access_token,
                    nickname=user_info.get('nickname', ''),
                    photo_url=user_info.get('figureurl_qq_2', '')
                )
    
    # 5. 生成 JWT Token
    tokens = get_tokens_for_user(user)
    return Response(tokens)
```

---

## 🔄 用户匹配流程

### 场景 1: 用户先在 Roamio 登录，再在 Ralendar 登录

```
1. 用户在 Roamio 用 QQ 登录
   → Roamio 保存: openid_R, unionid=U123, user_id=1

2. 用户在 Ralendar 用同一个 QQ 登录
   → Ralendar 获取: openid_L, unionid=U123
   → 查询: QQUser.objects.filter(unionid='U123') → 未找到
   → 创建: 新用户 user_id=5, unionid=U123

3. 结果: Roamio 和 Ralendar 各有一个用户账号（未关联）
```

**解决方案**: 共享数据库（推荐）

---

### 场景 2: 共享数据库（推荐方案）✅

```
1. Ralendar 和 Roamio 使用同一个 MySQL 数据库
2. 共享 auth_user 表
3. 共享 social_account / api_qquser 表

结果:
- 用户在 Roamio 登录 → 创建 user_id=1, unionid=U123
- 用户在 Ralendar 登录 → 查询 unionid=U123 → 找到 user_id=1
- ✅ 自动识别为同一用户！
```

**配置**:
```python
# Ralendar settings.py
USE_SHARED_DB = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'roamio_production',
        'USER': 'ralendar_user',
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': '3306',
    }
}

# 重要：使用相同的 SECRET_KEY
SECRET_KEY = 'django-insecure-#6avwo7=$9vse4txxj!phdfx5-ql(bc5otpoiw@x)u0i+^1-5h'
```

---

## 📝 给 Roamio 团队的配置清单

### ✅ Roamio 需要确认的：

1. **QQ UnionID 接口已获取** ✅（截图已确认）
   
2. **数据库表有 `unionid` 字段** ✅（根据之前文档）
   ```sql
   SELECT * FROM social_account LIMIT 1;
   -- 确认有 unionid 字段
   ```

3. **QQ 登录代码已添加 `unionid=1` 参数**
   ```python
   # 检查代码中是否有这些参数
   # 1. OAuth 授权 URL
   url = f'...&unionid=1'
   
   # 2. 获取 openid
   params = {'access_token': token, 'unionid': 1}
   
   # 3. 获取用户信息
   params = {..., 'unionid': 1}
   ```

4. **登录逻辑保存 UnionID**
   ```python
   # 检查保存逻辑
   social_account.unionid = user_info.get('unionid', '')
   social_account.save()
   ```

---

## 🧪 测试步骤

### 1. 测试 UnionID 获取

```python
# 在 Roamio 和 Ralendar 各自的 shell 中测试

# Roamio
python manage.py shell
>>> from backend.models import SocialAccount
>>> accounts = SocialAccount.objects.filter(provider='qq')
>>> for acc in accounts[:5]:
...     print(f"User: {acc.user.username}, OpenID: {acc.openid[:10]}, UnionID: {acc.unionid[:15] if acc.unionid else 'None'}")

# Ralendar
python manage.py shell
>>> from api.models import QQUser
>>> users = QQUser.objects.all()
>>> for u in users[:5]:
...     print(f"User: {u.user.username}, OpenID: {u.openid[:10]}, UnionID: {u.unionid[:15] if u.unionid else 'None'}")
```

**期望结果**: 
- 同一个 QQ 用户在两边的 `unionid` 相同 ✅
- 但 `openid` 不同（这是正常的）

---

### 2. 测试用户匹配

**测试流程**:
1. 用户 A 用 QQ 登录 Roamio
2. 检查数据库：记录 unionid
3. 用户 A 用同一个 QQ 登录 Ralendar
4. 检查数据库：unionid 应该相同
5. （如果共享数据库）检查 user_id 是否相同

---

## 📞 联系支持

如有问题，联系 Ralendar 团队：
- **QQ/邮箱**: 2064747320@qq.com
- **技术支持**: GitHub Issues

---

## ✅ 集成检查清单

- [x] Roamio 已获取 QQ UnionID 接口权限 ✅
- [x] Ralendar 已获取 QQ UnionID 接口权限 ✅
- [ ] Ralendar 数据库添加 `unionid` 字段
- [ ] 两边 QQ OAuth URL 添加 `unionid=1` 参数
- [ ] 两边登录逻辑保存 UnionID
- [ ] 测试 UnionID 获取成功
- [ ] 测试用户匹配逻辑
- [ ] （推荐）配置共享数据库
- [ ] 生产环境验证

---

**关键**: UnionID 是跨应用识别用户的唯一标识！✨

