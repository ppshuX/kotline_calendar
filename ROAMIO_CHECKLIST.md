# ✅ Roamio QQ UnionID 集成检查清单

**日期**: 2025-11-08  
**状态**: 待 Roamio 团队确认

---

## 🔑 关键问题修正

### ❌ **问题 1: QQ OAuth 配置错误**

**原配置**:
```bash
QQ_APP_ID=your_qq_app_id       # ❌ 占位符
QQ_APP_KEY=your_qq_app_key     # ❌ 占位符
```

**正确配置**:
```bash
QQ_APP_ID=102813859            # ✅ Roamio 实际 APP ID
QQ_APP_KEY=OddPvLYXHo69wTYO    # ✅ Roamio 实际 APP KEY
```

---

### ⚠️ **问题 2: 回调 URI 需要确认**

**当前配置**:
```bash
QQ_REDIRECT_URI=https://your-domain.com/settings/qq/receive_code
```

**建议配置**（根据 Roamio 实际路由）:
```bash
QQ_REDIRECT_URI=https://app7508.acapp.acwing.com.cn/api/v1/auth/qq/callback/
```

⚠️ **请 Roamio 团队确认实际的回调地址！**

---

## 🎯 Roamio 团队需要确认的事项

### 1️⃣ **代码是否已添加 unionid=1 参数？**

需要在以下位置添加：

#### OAuth 授权 URL
```python
# 示例代码
def get_qq_login_url():
    return (
        f"https://graph.qq.com/oauth2.0/authorize?"
        f"response_type=code"
        f"&client_id={QQ_APP_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&state=qq"
        f"&unionid=1"  # ← 添加这个参数
    )
```

#### 获取 access_token
```python
token_params = {
    'grant_type': 'authorization_code',
    'client_id': QQ_APP_ID,
    'client_secret': QQ_APP_KEY,
    'code': code,
    'redirect_uri': REDIRECT_URI,
    'unionid': 1  # ← 添加这个参数
}
```

#### 获取 openid
```python
openid_url = f"https://graph.qq.com/oauth2.0/me?access_token={token}&unionid=1"
#                                                                    ^^^^^^^^^^^^ 添加这个
```

#### 获取用户信息
```python
userinfo_params = {
    'access_token': token,
    'oauth_consumer_key': QQ_APP_ID,
    'openid': openid,
    'unionid': 1  # ← 添加这个参数
}
```

---

### 2️⃣ **数据库是否有 unionid 字段？**

**检查方法**（在 Django shell 或数据库中）:
```sql
DESCRIBE social_account;
```

**应该看到**:
```
Field      | Type         | Null | Key | Default | Extra
-----------+--------------+------+-----+---------+-------
id         | int          | NO   | PRI | NULL    | auto_increment
user_id    | int          | NO   | MUL | NULL    |
provider   | varchar(20)  | NO   |     | NULL    |
uid        | varchar(100) | NO   |     | NULL    |
unionid    | varchar(100) | YES  | MUL | NULL    |  ← 应该有这个字段
nickname   | varchar(100) | YES  |     | NULL    |
avatar_url | varchar(200) | YES  |     | NULL    |
...
```

**如果没有 unionid 字段**，需要创建迁移：
```python
# 在 Roamio 项目创建迁移
python manage.py makemigrations
python manage.py migrate
```

---

### 3️⃣ **登录逻辑是否保存 UnionID？**

**检查代码**（QQ 登录视图）:
```python
def qq_callback(request):
    # ... 获取 access_token, openid ...
    
    # 获取用户信息
    user_info = get_qq_user_info(token, openid)
    
    # ⚠️ 关键：提取 unionid
    unionid = user_info.get('unionid', '')  # ← 确认有这行代码
    
    # ⚠️ 关键：保存 unionid
    social_account, created = SocialAccount.objects.get_or_create(
        provider='qq',
        uid=openid,
        defaults={
            'unionid': unionid,  # ← 确认保存了 unionid
            'nickname': user_info.get('nickname'),
            'avatar_url': user_info.get('figureurl_qq_2')
        }
    )
    
    # 如果是老用户，更新 unionid
    if not created and not social_account.unionid:
        social_account.unionid = unionid
        social_account.save()
```

---

### 4️⃣ **用户匹配逻辑是否优先使用 UnionID？**

**推荐实现**:
```python
def qq_callback(request):
    # ... 获取 unionid ...
    
    if unionid:
        # 优先通过 UnionID 查找（跨应用识别）
        social_account = SocialAccount.objects.filter(
            provider='qq',
            unionid=unionid
        ).first()
        
        if social_account:
            # 找到了！更新 uid（因为不同应用的 openid 不同）
            social_account.uid = openid
            social_account.save()
        else:
            # 没找到，通过 uid 查找
            social_account = SocialAccount.objects.filter(
                provider='qq',
                uid=openid
            ).first()
            
            if social_account:
                # 补充 unionid
                social_account.unionid = unionid
                social_account.save()
    else:
        # 没有 unionid，回退到 uid 查找
        social_account = SocialAccount.objects.filter(
            provider='qq',
            uid=openid
        ).first()
    
    if not social_account:
        # 创建新用户...
        pass
```

---

## 🧪 测试步骤

### 步骤 1: 检查配置
```bash
# 1. 查看 .env 文件
cat ~/roamio/.env | grep QQ

# 应该看到：
# QQ_APP_ID=102813859
# QQ_APP_KEY=OddPvLYXHo69wTYO
```

### 步骤 2: 检查数据库
```bash
# 2. 进入 Django shell
python manage.py shell

# 3. 检查 unionid 字段
from backend.models import SocialAccount
from django.db import connection
cursor = connection.cursor()
cursor.execute("DESCRIBE social_account")
for row in cursor.fetchall():
    print(row)

# 应该看到 unionid 字段
```

### 步骤 3: 测试 QQ 登录
```bash
# 1. 用 QQ 登录 Roamio
# 2. 检查数据库是否保存了 unionid

python manage.py shell
>>> from backend.models import SocialAccount
>>> accounts = SocialAccount.objects.filter(provider='qq')
>>> for acc in accounts[:5]:
...     print(f"User: {acc.user.username}, UnionID: {acc.unionid}")

# 应该看到 UnionID 值（不是 None）
```

### 步骤 4: 测试跨应用识别
```bash
# 1. 用户在 Roamio 用 QQ 登录
#    → 记录 unionid

# 2. 同一用户在 Ralendar 用 QQ 登录
#    → 查询数据库，unionid 应该相同

# 3. （如果共享数据库）user_id 应该相同
```

---

## ✅ 验收标准

- [ ] ✅ `.env` 文件配置正确（QQ_APP_ID, QQ_APP_KEY, QQ_REDIRECT_URI）
- [ ] ✅ 代码中所有 OAuth 请求添加了 `unionid=1` 参数
- [ ] ✅ 数据库 `social_account` 表有 `unionid` 字段
- [ ] ✅ 登录逻辑保存了 `unionid`
- [ ] ✅ 用户匹配逻辑优先使用 `unionid`
- [ ] ✅ 测试 QQ 登录，能成功获取 `unionid`
- [ ] ✅ 同一 QQ 用户在 Ralendar 和 Roamio 的 `unionid` 相同
- [ ] ✅ （可选）共享数据库后，`user_id` 相同

---

## 📞 联系支持

如有问题，联系 Ralendar 团队：
- QQ/邮箱: 2064747320@qq.com
- 参考文档: `docs/integration/QQ_UNIONID_INTEGRATION.md`

---

**最后更新**: 2025-11-08 23:50

