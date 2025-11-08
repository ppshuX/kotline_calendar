# 🎯 下一步行动清单

**更新时间**: 2025-11-08 23:58  
**状态**: 代码完成，等待部署和测试

---

## 📦 **今晚已完成**

- ✅ 项目结构整理（删除 3000 行冗余）
- ✅ 文档重组（40+ 文件分类）
- ✅ QQ UnionID 代码实现（后端完成）
- ✅ 集成资料准备（8 个文档/工具）
- ✅ 代码推送到 GitHub

---

## 🚀 **明天需要做的事**

### ⭐ **优先级 1: Ralendar 部署到服务器**（30-45 分钟）

#### 步骤：
```bash
# 1. SSH 登录
ssh acs@app7626.acapp.acwing.com.cn

# 2. 拉取代码
cd ~/kotlin_calendar
git pull

# 3. 更新 .env（使用 TEMP_ENV_FOR_SERVER.txt 的内容）
nano backend/.env
# 粘贴内容，保存

# 4. 执行迁移
cd backend
python manage.py migrate

# 5. 重启服务
pkill -f uwsgi
uwsgi --ini uwsgi.ini &

# 6. 测试
python ../QQ_UNIONID_TEST.py
```

**预期结果**:
- ✅ 迁移成功（看到 0008_add_qq_unionid applied）
- ✅ unionid 字段已创建
- ✅ 测试脚本通过

---

### ⭐ **优先级 2: 测试 QQ 登录**（15 分钟）

```bash
# 1. 打开 Ralendar
https://app7626.acapp.acwing.com.cn/login

# 2. 用你的 QQ 登录

# 3. 查看服务器日志
ssh acs@app7626.acapp.acwing.com.cn
tail -f ~/kotlin_calendar/backend/logs/django.log

# 应该看到：
# [QQ Login] OpenID: xxx..., UnionID: yyy...
# [QQ Login] Creating new user with UnionID: yyy...
```

**验证**:
```bash
# 进入 Django shell
python manage.py shell

# 查看 UnionID
from api.models import QQUser
qq_user = QQUser.objects.latest('id')
print(f"最新用户: {qq_user.user.username}")
print(f"UnionID: {qq_user.unionid}")
# UnionID 应该不为空
```

---

### ⭐ **优先级 3: 联系 Roamio 团队**（沟通）

#### 发送资料：
1. `ROAMIO_INTEGRATION_STATUS.md` ⭐
2. `ROAMIO_CHECKLIST.md` ⭐
3. GitHub 链接：`docs/integration/` 目录

#### 需要他们确认：
- [ ] QQ OAuth 代码是否添加了 `unionid=1` 参数？（4 个位置）
- [ ] 数据库是否有 `unionid` 字段？
- [ ] 登录逻辑是否保存 UnionID？

**方式**:
- QQ: 2064747320
- 或发邮件，附带文档链接

---

### ⭐ **优先级 4: 联调测试**（等 Roamio 确认后）

#### 测试流程：
1. **清空测试数据**（可选）
   ```bash
   # Ralendar
   python manage.py shell
   >>> from api.models import QQUser
   >>> QQUser.objects.filter(user__username='测试用户').delete()
   ```

2. **用同一个 QQ 账号测试**
   - 先在 Ralendar 登录
   - 记录 UnionID
   - 再在 Roamio 登录
   - 检查 UnionID 是否相同

3. **测试 API 互通**
   ```bash
   # 用 Roamio 的 Token 调用 Ralendar API
   curl -H "Authorization: Bearer ROAMIO_TOKEN" \
     https://app7626.acapp.acwing.com.cn/api/v1/events/
   ```

---

## 📋 **Roamio 团队检查清单**（精简版）

### ✅ 必须确认的 3 点：

#### 1️⃣ 代码添加 `unionid=1`
```python
# 检查这 4 个位置：
1. OAuth URL:      ?...&unionid=1
2. 获取 token:     'unionid': 1
3. 获取 openid:    ?...&unionid=1
4. 获取用户信息:   'unionid': 1
```

#### 2️⃣ 数据库有 `unionid` 字段
```sql
DESCRIBE social_account;
-- 应该有 unionid varchar(100)
```

#### 3️⃣ 登录保存 UnionID
```python
unionid = user_info.get('unionid', '')
social_account.unionid = unionid
social_account.save()
```

---

## 🎉 **预期效果**

完成后：
```
用户在 Roamio 用 QQ 登录
  → UnionID: ABC-XYZ-123 ✅

同一用户在 Ralendar 用 QQ 登录
  → UnionID: ABC-XYZ-123 ✅（相同！）

→ 系统识别为同一用户 🎯
→ 可以无缝"添加到日历" 🎊
```

---

## ⏰ **时间安排建议**

### 今晚（可选）:
- 如果有时间，可以先部署 Ralendar

### 明天上午:
- Ralendar 部署 + 测试（你）
- 代码检查（Roamio 团队）

### 明天下午:
- 联调测试
- 实现"添加到日历"按钮

---

**所有准备工作已完成！明天就是验证和集成了！** 🚀💪

