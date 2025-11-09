# 🔍 UnionID 匹配问题排查步骤

## 问题描述
- Roamio 用户: user_id = 11
- Ralendar 用户: user_id = 2
- 同一个 QQ 账号，但创建了两个不同的用户

---

## 步骤 1: SSH 到服务器

```bash
ssh -p 20220 ppshuX@app7626.acapp.acwing.com.cn
cd ~/Ralendar
```

---

## 步骤 2: 检查数据库迁移

```bash
cd backend
source venv/bin/activate  # 激活虚拟环境
python manage.py showmigrations api
```

**期望输出**:
```
api
 [X] 0001_initial
 [X] 0002_event_reminder_minutes_alter_event_end_time_and_more
 ...
 [X] 0007_add_fusion_fields
 [X] 0008_add_qq_unionid  ← 必须有这个！
```

**如果没有 [X]**:
```bash
python manage.py migrate
```

---

## 步骤 3: 进入 Django Shell 检查数据

```bash
python manage.py shell
```

```python
from api.models import QQUser
from django.contrib.auth.models import User

# 查看所有 QQ 用户
print("\n=== 所有 QQ 用户 ===")
for qu in QQUser.objects.all():
    print(f"User ID: {qu.user_id}, Username: {qu.user.username}")
    print(f"  OpenID: {qu.openid[:20]}...")
    print(f"  UnionID: {qu.unionid[:20] if qu.unionid else 'NULL'}...")
    print()

# 查询 user_id = 2 的用户
print("\n=== User ID = 2 的 QQ 信息 ===")
qu = QQUser.objects.filter(user_id=2).first()
if qu:
    print(f"OpenID: {qu.openid}")
    print(f"UnionID: {qu.unionid if qu.unionid else 'NULL'}")
    print(f"Nickname: {qu.nickname}")
    print(f"Created: {qu.created_at}")
else:
    print("没有找到!")

# 退出
exit()
```

---

## 步骤 4: 直接查询数据库

```bash
# 进入 MySQL
mysql -u ralendar -p

# 输入密码后
use ralendar_db;

# 查询所有 QQ 用户
SELECT 
    id,
    user_id,
    LEFT(openid, 20) as openid_prefix,
    LEFT(unionid, 20) as unionid_prefix,
    nickname,
    created_at
FROM api_qquser
ORDER BY id;

# 查询 user_id = 2
SELECT 
    id,
    user_id,
    openid,
    unionid,
    nickname
FROM api_qquser 
WHERE user_id = 2;

# 退出
exit;
```

---

## 步骤 5: 对比 UnionID

**Roamio 的 UnionID** (请 Roamio 团队提供):
```sql
-- Roamio 数据库
SELECT unionid FROM backend_socialaccount 
WHERE user_id = 11 AND provider='qq';
```

**Ralendar 的 UnionID**:
```sql
-- Ralendar 数据库
SELECT unionid FROM api_qquser WHERE user_id = 2;
```

**如果两者相同**: UnionID 获取正常，匹配逻辑可能有时序问题  
**如果两者不同**: UnionID 获取有问题，需要检查 QQ 应用配置

---

## 步骤 6: 测试 UnionID 匹配

```bash
python manage.py shell
```

```python
from api.models import QQUser

# 使用 Roamio 提供的 UnionID 测试
test_unionid = "PASTE_ROAMIO_UNIONID_HERE"

# 查找
qu = QQUser.objects.filter(unionid=test_unionid).first()

if qu:
    print(f"✅ 找到匹配用户!")
    print(f"User ID: {qu.user_id}")
    print(f"Username: {qu.user.username}")
else:
    print("❌ 没有找到匹配的用户")
    print("\n可能原因:")
    print("1. UnionID 不匹配（两边获取的不一样）")
    print("2. Ralendar 用户的 unionid 字段是 NULL")
    print("3. 两边用的不是同一个 QQ 账号")

exit()
```

---

## 步骤 7: 查看最近的登录日志

```bash
# 查看应用日志
sudo supervisorctl tail -f ralendar stderr

# 或者查看 Django 日志
tail -f ~/Ralendar/backend/logs/django.log

# 搜索 QQ Login 相关日志
grep "QQ Login" ~/Ralendar/backend/logs/django.log | tail -20
```

**期望看到**:
```
[QQ Login] OpenID: xxx..., UnionID: yyy...
[QQ Login] Found existing user by UnionID: username
```

**如果看到**:
```
[QQ Login] OpenID: xxx..., UnionID: None...
```
说明 QQ 没有返回 UnionID！

---

## 常见问题和解决方案

### 问题 1: UnionID 字段是 NULL

**原因**: 迁移没执行或登录时间早于 UnionID 功能

**解决**:
```bash
# 执行迁移
python manage.py migrate

# 用户重新登录一次
```

### 问题 2: QQ 应用没启用 UnionID

**原因**: QQ 互联管理中心没有开启

**解决**:
1. 登录 https://connect.qq.com/
2. 进入应用管理
3. 找到你的应用
4. 申请开通 UnionID 功能

### 问题 3: 两边 UnionID 不同

**原因**: 可能用的不是同一个 QQ 账号

**解决**:
1. 确认两边都用同一个 QQ 登录
2. 清除浏览器缓存后重新登录
3. 对比登录的 QQ 号码

### 问题 4: UnionID 匹配逻辑有时序问题

**原因**: Ralendar 先登录（没有 UnionID），Roamio 后登录

**解决**:
```python
# Django shell
from api.models import QQUser

# 手动更新 Ralendar 用户的 unionid
qu = QQUser.objects.get(user_id=2)
qu.unionid = "ROAMIO_PROVIDED_UNIONID"
qu.save()

print(f"✅ 已更新 user_id={qu.user_id} 的 UnionID")
```

---

## 完整测试流程

1. **Ralendar 用户重新登录**
   - 访问 https://app7626.acapp.acwing.com.cn/
   - 退出登录
   - 用 QQ 重新登录
   - 检查 api_qquser 表的 unionid 字段

2. **Roamio 用户尝试同步**
   - 用同一个 QQ 账号登录 Roamio
   - 创建一个测试事件并同步到 Ralendar
   - 检查是否匹配到正确的用户

3. **查看 Fusion API 日志**
   ```bash
   grep "Fusion API" ~/Ralendar/backend/logs/django.log | tail -50
   ```
   
   期望看到:
   ```
   [Fusion API] 查找 UnionID: xxx...
   [Fusion API] ✅ 通过 UnionID 匹配到用户: username (ID: 2)
   ```

---

## 提供给 Roamio 团队的信息

请提供以下信息以便我们对比：

1. **Roamio 的 UnionID**（前 20 位即可）:
   ```sql
   SELECT LEFT(unionid, 20) FROM backend_socialaccount 
   WHERE user_id = 11 AND provider='qq';
   ```

2. **用的是哪个 QQ 账号**: (QQ号码或昵称)

3. **登录时间**:
   - Ralendar 第一次用 QQ 登录的时间
   - Roamio 第一次用 QQ 登录的时间

---

## 快速修复方案（如果确认是同一个 QQ）

如果确认两边用的是同一个 QQ 账号，但 UnionID 就是不匹配：

```python
# Django shell
from api.models import QQUser

# 获取 Roamio 提供的 UnionID
roamio_unionid = "PASTE_HERE"

# 更新 Ralendar 用户
ralendar_qq = QQUser.objects.get(user_id=2)
ralendar_qq.unionid = roamio_unionid
ralendar_qq.save()

print("✅ UnionID 已同步!")
print(f"User ID: {ralendar_qq.user_id}")
print(f"Username: {ralendar_qq.user.username}")
print(f"UnionID: {ralendar_qq.unionid}")
```

---

## 联系方式

如果遇到问题，随时联系：
- QQ: 2064747320
- 邮箱: 2064747320@qq.com

执行完这些步骤后，请把结果发给我们！

