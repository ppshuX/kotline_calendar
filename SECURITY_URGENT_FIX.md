# 🚨 安全紧急修复指南

## ⚠️ SMTP 凭据泄露 - 立即执行

### 第一步：撤销 QQ 邮箱授权码（最优先！）

1. 登录 QQ 邮箱：https://mail.qq.com
2. 进入【设置】→【账户】
3. 找到 **POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务**
4. 点击【生成授权码】旁边的【管理】
5. **删除所有现有授权码**
6. 重新生成一个新的授权码
7. **只保存在服务器的 .env 文件中，不要提交到 Git！**

### 第二步：清理 Git 历史中的敏感信息

```bash
# 1. 查找包含敏感信息的提交
cd D:\KotlinProjects\Ralendar
git log --all --full-history -- "*env*" --pretty=format:"%h %s"

# 2. 使用 BFG Repo-Cleaner 或 git filter-branch 清理
# 注意：这会重写 Git 历史，需要强制推送！

# 方法 A: 使用 BFG (推荐)
# 下载: https://rtyley.github.io/bfg-repo-cleaner/
# java -jar bfg.jar --delete-files .env
# git reflog expire --expire=now --all && git gc --prune=now --aggressive
# git push --force

# 方法 B: 使用 git filter-branch (复杂但内置)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch backend/.env" \
  --prune-empty --tag-name-filter cat -- --all
```

### 第三步：检查并清理所有包含敏感信息的文件

已知泄露的文件：
- `backend/.env` (如果被提交)
- 可能的文档文件中的示例

### 第四步：更新 .gitignore

确保 `.gitignore` 包含：
```
# Environment variables
.env
.env.local
.env.production
*.env

# Credentials
*password*
*secret*
*credentials*
```

### 第五步：通知团队

如果这是团队项目，立即通知所有成员：
1. 旧的 SMTP 密码已失效
2. 需要在服务器更新新的授权码
3. 不要在任何文档中硬编码凭据

---

## ✅ 安全最佳实践

### 1. 永远不要提交敏感信息到 Git

❌ **错误做法**:
```bash
# .env 文件
EMAIL_HOST_PASSWORD=zwcqgzukwkfyeaja  # 危险！
```

✅ **正确做法**:
```bash
# .env.example (提交到 Git)
EMAIL_HOST_PASSWORD=your_password_here

# .env (不提交，只在服务器配置)
EMAIL_HOST_PASSWORD=zwcqgzukwkfyeaja
```

### 2. 使用环境变量

```python
# settings.py
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
# 永远不要写成: EMAIL_HOST_PASSWORD = 'zwcqgzukwkfyeaja'
```

### 3. 使用密钥管理服务

生产环境考虑使用：
- AWS Secrets Manager
- Azure Key Vault
- HashiCorp Vault
- Aliyun KMS

### 4. 定期轮换密钥

每 30-90 天更换一次：
- 数据库密码
- API 密钥
- SMTP 授权码
- Django SECRET_KEY

---

## 📞 GitGuardian 处理

1. 登录 GitGuardian Dashboard
2. 确认这是真实的泄露（不是误报）
3. 点击 "Fix this secret leak"
4. 按照他们的指导清理仓库
5. 标记为 "Resolved"

---

## ⏱️ 执行检查清单

- [ ] 撤销泄露的 QQ 邮箱授权码
- [ ] 生成新的授权码
- [ ] 更新服务器 .env 文件
- [ ] 清理 Git 历史
- [ ] 强制推送到 GitHub
- [ ] 更新 .gitignore
- [ ] 在 GitGuardian 标记为已解决
- [ ] 通知团队成员（如果是团队项目）
- [ ] 检查其他可能泄露的凭据（数据库密码、API 密钥等）

---

## 🔒 后续监控

1. 启用 GitHub Secret Scanning
2. 启用 GitGuardian 持续监控
3. 使用 pre-commit hooks 防止提交敏感信息
4. 定期审计 Git 历史

---

**⚠️ 重要提醒：在完成所有步骤之前，不要进行任何新的 git push！**

