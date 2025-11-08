# ✅ Roamio × Ralendar 集成状态总结

**更新时间**: 2025-11-08 23:55  
**状态**: 配置正确 ✅，待确认代码实现 ⏳

---

## ✅ **已确认正确的配置**

### 1️⃣ **Roamio .env 配置**
```bash
✅ SECRET_KEY: django-insecure-#6avwo7=$9vse4txxj!phdfx5-ql(bc5otpoiw@x)u0i+^1-5h
   （与 Ralendar 相同，JWT Token 可互认）

✅ QQ_APP_ID: 102813859
✅ QQ_APP_KEY: OddPvLYXHo69wTYO
✅ QQ_REDIRECT_URI: https://app7508.acapp.acwing.com.cn/settings/qq/receive_code

✅ EMAIL: 2064747320@qq.com (与 Ralendar 相同)
✅ RALENDAR_API_URL: https://app7626.acapp.acwing.com.cn/api/v1
```

### 2️⃣ **Ralendar .env 配置**
```bash
✅ SECRET_KEY: django-insecure-#6avwo7=$9vse4txxj!phdfx5-ql(bc5otpoiw@x)u0i+^1-5h
   （与 Roamio 相同）

✅ QQ_APPID: 102818448
✅ QQ_APPKEY: sZ0B7nDQP8Bzb1JP

✅ EMAIL: 2064747320@qq.com (与 Roamio 相同)
```

### 3️⃣ **QQ UnionID 权限**
```
✅ Roamio (APP: 102813859): UnionID 已获取
✅ Ralendar (APP: 102818448): UnionID 已获取
```

---

## ⏳ **Roamio 团队需要确认的 3 件事**

### 1️⃣ **代码是否添加了 `unionid=1` 参数？**

**需要检查的文件**: `settings/qq/views.py` 或类似的 QQ 登录视图

**检查位置 A: OAuth 授权 URL**
```python
# 查找类似这样的代码
def get_qq_login_url(request):
    url = (
        f"https://graph.qq.com/oauth2.0/authorize?"
        f"response_type=code"
        f"&client_id={settings.QQ_APP_ID}"
        f"&redirect_uri={settings.QQ_REDIRECT_URI}"
        f"&state=STATE_STRING"
        # f"&unionid=1"  # ← 检查是否有这一行？
    )
    return url
```

**如果没有，添加**:
```python
# ✅ 修改为
def get_qq_login_url(request):
    url = (
        f"https://graph.qq.com/oauth2.0/authorize?"
        f"response_type=code"
        f"&client_id={settings.QQ_APP_ID}"
        f"&redirect_uri={settings.QQ_REDIRECT_URI}"
        f"&state=STATE_STRING"
        f"&unionid=1"  # ✅ 添加这一行
    )
    return url
```

**检查位置 B: 获取 access_token**
```python
# 查找类似这样的代码
def qq_receive_code(request):
    code = request.GET.get('code')
    
    # 获取 access_token
    token_params = {
        'grant_type': 'authorization_code',
        'client_id': settings.QQ_APP_ID,
        'client_secret': settings.QQ_APP_KEY,
        'code': code,
        'redirect_uri': settings.QQ_REDIRECT_URI,
        # 'unionid': 1,  # ← 检查是否有这一行？
    }
```

**如果没有，添加**:
```python
# ✅ 修改为
token_params = {
    'grant_type': 'authorization_code',
    'client_id': settings.QQ_APP_ID,
    'client_secret': settings.QQ_APP_KEY,
    'code': code,
    'redirect_uri': settings.QQ_REDIRECT_URI,
    'unionid': 1,  # ✅ 添加这一行
}
```

**检查位置 C: 获取 openid**
```python
# 获取 openid
openid_url = f"https://graph.qq.com/oauth2.0/me?access_token={token}"
# ← 检查是否添加了 &unionid=1 ？
```

**如果没有，修改为**:
```python
# ✅ 修改为
openid_url = f"https://graph.qq.com/oauth2.0/me?access_token={token}&unionid=1"
```

**检查位置 D: 获取用户信息**
```python
# 获取用户信息
userinfo_params = {
    'access_token': token,
    'oauth_consumer_key': settings.QQ_APP_ID,
    'openid': openid,
    # 'unionid': 1,  # ← 检查是否有这一行？
}
```

**如果没有，添加**:
```python
# ✅ 修改为
userinfo_params = {
    'access_token': token,
    'oauth_consumer_key': settings.QQ_APP_ID,
    'openid': openid,
    'unionid': 1,  # ✅ 添加这一行
}
```

---

### 2️⃣ **数据库是否有 `unionid` 字段？**

**检查方法**:
```bash
# SSH 到 Roamio 服务器
ssh acs@app7508.acapp.acwing.com.cn

# 进入项目目录
cd ~/roamio  # 或实际项目路径

# 进入 Django shell
python manage.py shell

# 检查数据库表结构
from django.db import connection
cursor = connection.cursor()
cursor.execute("DESCRIBE social_account")  # 或实际的表名
for row in cursor.fetchall():
    print(row)
```

**应该看到**:
```
('id', 'int', 'NO', 'PRI', None, 'auto_increment')
('user_id', 'int', 'NO', 'MUL', None, '')
('provider', 'varchar(20)', 'NO', '', None, '')
('uid', 'varchar(100)', 'NO', '', None, '')
('unionid', 'varchar(100)', 'YES', 'MUL', None, '')  ← 应该有这个字段
('nickname', 'varchar(100)', 'YES', '', None, '')
...
```

**如果没有 `unionid` 字段**，需要创建迁移:
```bash
# 1. 修改模型（假设在 backend/models.py）
class SocialAccount(models.Model):
    # ... 其他字段 ...
    unionid = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_index=True,  # 添加索引
        verbose_name='UnionID'
    )

# 2. 创建并执行迁移
python manage.py makemigrations
python manage.py migrate
```

---

### 3️⃣ **登录逻辑是否保存 UnionID？**

**需要检查的代码**: QQ 登录回调处理

```python
def qq_receive_code(request):
    # ... 获取 code, token, openid ...
    
    # 获取用户信息
    userinfo_url = "https://graph.qq.com/user/get_user_info"
    userinfo_params = {
        'access_token': token,
        'oauth_consumer_key': settings.QQ_APP_ID,
        'openid': openid,
        'unionid': 1
    }
    response = requests.get(userinfo_url, params=userinfo_params)
    user_info = response.json()
    
    # ⚠️ 关键：提取 unionid
    unionid = user_info.get('unionid', '')  # ← 检查是否有这行？
    
    # ⚠️ 关键：保存到数据库
    social_account, created = SocialAccount.objects.get_or_create(
        provider='qq',
        uid=openid,
        defaults={
            'user': user,
            'unionid': unionid,  # ← 检查是否保存了 unionid？
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

## 🧪 **快速测试方法**

### 方法 1: 检查现有用户
```bash
# 进入 Django shell
python manage.py shell

# 查看现有 QQ 用户
from backend.models import SocialAccount  # 根据实际路径调整
qq_accounts = SocialAccount.objects.filter(provider='qq')

print(f"共有 {qq_accounts.count()} 个 QQ 用户")

for acc in qq_accounts[:5]:
    print(f"用户: {acc.user.username}")
    print(f"  OpenID: {acc.uid[:15]}...")
    print(f"  UnionID: {acc.unionid[:15] if acc.unionid else '(未设置)'}")
    print()
```

**预期结果**:
- ✅ 如果已经实现，应该看到 UnionID 值
- ❌ 如果未实现，UnionID 应该是 `(未设置)` 或 `None`

### 方法 2: 实际登录测试
```bash
# 1. 打开 Roamio
https://app7508.acapp.acwing.com.cn

# 2. 用 QQ 登录

# 3. 查看服务器日志
tail -f ~/roamio/logs/django.log  # 或实际日志路径

# 应该看到类似的日志：
# [QQ Login] OpenID: xxx..., UnionID: yyy...
```

---

## 📊 **集成状态总览**

| 项目 | 状态 | 说明 |
|------|------|------|
| **Ralendar 配置** | ✅ 完成 | .env 配置正确 |
| **Ralendar 代码** | ✅ 完成 | UnionID 已实现 |
| **Ralendar 数据库** | ✅ 完成 | unionid 字段已添加 |
| **Roamio 配置** | ✅ 完成 | .env 配置正确 |
| **Roamio 代码** | ⏳ 待确认 | 需要检查是否添加 unionid=1 |
| **Roamio 数据库** | ⏳ 待确认 | 需要检查是否有 unionid 字段 |
| **跨应用测试** | ⏳ 待测试 | 需要实际登录验证 |

---

## 📝 **简化版检查清单**

**给 Roamio 团队**（只需确认 3 点）:

- [ ] 代码中所有 QQ OAuth 请求是否添加了 `unionid=1` 参数？
  - OAuth 授权 URL: `&unionid=1`
  - 获取 token: `'unionid': 1`
  - 获取 openid: `&unionid=1`
  - 获取用户信息: `'unionid': 1`

- [ ] 数据库 `social_account` 表是否有 `unionid` 字段？
  ```sql
  DESCRIBE social_account;
  ```

- [ ] 登录逻辑是否提取并保存了 `unionid`？
  ```python
  unionid = user_info.get('unionid', '')
  social_account.unionid = unionid
  ```

---

## 🎯 **下一步行动**

### Ralendar（你）:
1. ✅ 代码已完成
2. ⏳ 部署到服务器（还没做）
3. ⏳ 执行数据库迁移
4. ⏳ 测试 QQ 登录

### Roamio 团队:
1. ⏳ 检查代码（上述 3 点）
2. ⏳ 如果缺少，按照示例添加
3. ⏳ 部署到服务器
4. ⏳ 测试 QQ 登录

### 双方:
1. ⏳ 同时测试：同一 QQ 用户在两边登录
2. ⏳ 验证 UnionID 是否相同
3. ⏳ （可选）配置共享数据库

---

## 📞 **协调建议**

建议你们：
1. **今晚/明天**: 各自完成服务器部署
2. **明天测试**: 用同一个 QQ 账号在两边登录
3. **验证**: 检查数据库中的 UnionID 是否相同

**如果 UnionID 相同** ✅:
- 恭喜！集成成功！
- 可以开始开发"添加到日历"功能

**如果 UnionID 不同** ❌:
- Roamio 代码可能缺少 `unionid=1` 参数
- 按照上面的示例补充

---

**总结**: Roamio 的配置是正确的！重点是确认代码实现的 3 个要点。建议明天双方同时部署测试！🚀

