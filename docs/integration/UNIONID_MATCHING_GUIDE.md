# 🔗 UnionID 用户匹配实现指南

> **日期**: 2025-11-09  
> **状态**: ✅ 已实现

---

## 🎯 **功能说明**

UnionID 用户匹配是实现跨应用用户识别的关键功能。

**目标**：
- Roamio 用户在 Ralendar 创建的事件应该归属于正确的 Ralendar 用户
- 不是所有事件都归属于 anonymous

---

## 🔄 **三层匹配策略**

### **策略 1：UnionID 匹配（首选）** ⭐

```python
# 1. 从请求中获取 unionid
unionid = request.data.get('unionid', '')

# 2. 在 Ralendar 中查找
qq_user = QQUser.objects.filter(unionid=unionid).first()

# 3. 获取关联的用户
if qq_user:
    ralendar_user = qq_user.user
    # ✅ 找到了正确的用户！
```

**优点**：
- ✅ 准确识别同一个 QQ 用户
- ✅ 跨应用用户一致性
- ✅ 符合设计初衷

**前提**：
- Roamio 需要在请求中包含 `unionid` 字段

---

### **策略 2：user_id 匹配（备选）**

```python
# 尝试用相同的 user_id 查找
try:
    ralendar_user = User.objects.get(id=roamio_user_id)
    # ✅ 碰巧 ID 相同
except User.DoesNotExist:
    # ❌ ID 不同，继续下一个策略
    pass
```

**优点**：
- ✅ 不需要额外数据
- ✅ 如果 ID 碰巧相同就能用

**缺点**：
- ❌ 不可靠（ID 通常不同）
- ❌ 只是碰运气

---

### **策略 3：默认用户（兜底）**

```python
# 使用第一个用户（anonymous）
ralendar_user = User.objects.first()
```

**优点**：
- ✅ 总能创建事件（不会失败）
- ✅ 用于测试和演示

**缺点**：
- ❌ 不准确
- ❌ 所有事件都归属于同一用户

---

## 📊 **匹配流程图**

```
Roamio 发送请求（带 unionid）
    ↓
策略 1: 查找 QQUser.unionid
    ↓
找到了？
    ├─ 是 → ✅ 使用该用户
    └─ 否 → 继续
         ↓
策略 2: 查找 User.id = roamio_user_id
    ↓
找到了？
    ├─ 是 → ✅ 使用该用户
    └─ 否 → 继续
         ↓
策略 3: User.objects.first()
    ↓
✅ 使用默认用户（anonymous）
```

---

## 🔧 **Roamio 需要做的修改**

### **方法 1：在请求数据中包含 unionid（推荐）** ⭐

**文件**: `backend/utils/ralendar_client.py`

```python
def batch_create_events(self, user_token, events_list, trip_slug, unionid):
    url = f"{self.base_url}/fusion/events/batch/"
    
    data = {
        "source_app": "roamio",
        "unionid": unionid,  # ← 添加这个！
        "related_trip_slug": trip_slug,
        "events": events_list
    }
    
    headers = {
        "Authorization": f"Bearer {user_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=data, headers=headers)
    return response.json()
```

**获取 unionid**：
```python
# 从 Roamio 的数据库中获取
from backend.models import SocialAccount

social = SocialAccount.objects.filter(
    user=request.user,
    provider='qq'
).first()

unionid = social.unionid if social else ''
```

---

### **方法 2：在 JWT Token 中包含 unionid**

**文件**: Roamio 的 Token 生成逻辑

```python
from rest_framework_simplejwt.tokens import AccessToken

def get_tokens_for_user(user):
    token = AccessToken.for_user(user)
    
    # 添加 unionid 到 payload
    social = user.socialaccount_set.filter(provider='qq').first()
    if social and social.unionid:
        token['unionid'] = social.unionid
    
    return str(token)
```

---

## 📝 **Ralendar 已实现的逻辑**

```python
# 1. 从请求或 Token 获取 unionid
unionid = data.get('unionid', '') or token.payload.get('unionid', '')

# 2. 通过 UnionID 查找用户
if unionid:
    qq_user = QQUser.objects.filter(unionid=unionid).first()
    if qq_user:
        ralendar_user = qq_user.user  # ✅ 匹配成功！

# 3. 备选：通过 user_id 匹配
if not ralendar_user:
    try:
        ralendar_user = User.objects.get(id=roamio_user_id)
    except User.DoesNotExist:
        pass

# 4. 兜底：默认用户
if not ralendar_user:
    ralendar_user = User.objects.first()
```

---

## 🧪 **测试场景**

### **测试 1：有 UnionID**

**Roamio 发送**：
```json
{
  "unionid": "AE123456789",
  "events": [...]
}
```

**Ralendar 查找**：
```sql
SELECT * FROM api_qquser WHERE unionid = 'AE123456789'
```

**结果**：
- ✅ 找到 → 使用该用户
- ❌ 没找到 → 降级到策略 2

---

### **测试 2：无 UnionID，user_id 碰巧相同**

**Token 中**：
```json
{
  "user_id": 2
}
```

**Ralendar 查找**：
```sql
SELECT * FROM auth_user WHERE id = 2
```

**结果**：
- ✅ ID=2 存在 → 使用该用户（W ૧ H）
- ❌ ID=2 不存在 → 降级到策略 3

---

### **测试 3：无 UnionID，user_id 不同**

**降级到默认用户**（anonymous）

---

## 📊 **用户匹配优先级**

| 优先级 | 方法 | 准确性 | 要求 |
|--------|------|--------|------|
| 🥇 第1 | UnionID 匹配 | 100% | Roamio 提供 unionid |
| 🥈 第2 | user_id 匹配 | 碰运气 | 两边 ID 相同 |
| 🥉 第3 | 默认用户 | 不准确 | 无 |

---

## 🎯 **日志输出**

部署后，日志会显示完整的匹配过程：

```
[Fusion API] 收到请求
[Fusion API] Roamio user_id: 5
[Fusion API] 查找 UnionID: AE123456789
[Fusion API] ✅ 通过 UnionID 匹配到用户: W ૧ H (ID: 2)
[Fusion API] Events count: 1
[Fusion API] ✅ 创建成功: Hi Ralendar! (ID: 3)
```

或者：

```
[Fusion API] ⚠️ 请求中没有 UnionID
[Fusion API] ⚠️ user_id 5 在 Ralendar 中不存在
[Fusion API] ⚠️ 使用默认用户: anonymous
```

---

## 🚀 **部署和测试**

### **1. 部署 Ralendar**：
```bash
cd ~/kotlin_calendar
git pull
cd backend
pkill -9 -f uwsgi
sleep 3
uwsgi --ini uwsgi.ini &
```

### **2. Roamio 修改代码**：
添加 `unionid` 到请求数据

### **3. 重新测试**：
检查事件是否创建到正确的用户下

---

## 📞 **给 Roamio 团队的说明**

```
UnionID 用户匹配已实现！

请在请求中添加 unionid 字段：
{
  "unionid": "xxx",  ← 从你们的 SocialAccount 表获取
  "events": [...]
}

或者在 JWT Token 中包含：
{
  "user_id": 5,
  "unionid": "xxx"  ← 添加到 Token payload
}

这样事件就会创建到正确的 Ralendar 用户下！

详细说明：docs/integration/UNIONID_MATCHING_GUIDE.md
```

---

**代码已完成！准备部署！** 🚀

