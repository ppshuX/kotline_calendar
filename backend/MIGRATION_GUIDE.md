# 数据库迁移指南

## ⚠️ 重要提示
由于修改了 Event 模型字段（date_time → start_time/end_time），需要执行数据库迁移。

## 🔧 本地执行步骤

### 1. 创建迁移文件
```bash
cd backend
python manage.py makemigrations
```

### 2. 执行迁移
```bash
python manage.py migrate
```

### 3. 创建超级用户（可选）
```bash
python manage.py createsuperuser
```

## 🚀 服务器部署步骤

### 1. 推送到 Git
```bash
git add -A
git commit -m "feat: implement JWT authentication and update Event model"
git push
```

### 2. 服务器端操作
```bash
# SSH 登录服务器
ssh acs@app7626.acapp.acwing.com.cn

# 进入项目目录
cd ~/kotlin_calendar

# 拉取最新代码
git pull

# 进入 backend 目录
cd backend

# 安装新依赖
pip3 install --user -r requirements.txt

# 执行迁移
python3 manage.py makemigrations
python3 manage.py migrate

# 重启 uWSGI
pkill -9 uwsgi
uwsgi --ini uwsgi.ini &
```

## 📝 迁移内容

### Event 模型变更
- ❌ 删除: `date_time`, `reminder_minutes`
- ✅ 新增: `start_time`, `end_time`, `location`

### 新功能
- ✅ JWT 认证系统
- ✅ 用户注册/登录 API
- ✅ 自动关联用户到事件

## 🔗 新的 API 端点

### 用户认证
- `POST /api/auth/register/` - 注册
  ```json
  {
    "username": "test",
    "email": "test@example.com",
    "password": "123456",
    "password_confirm": "123456"
  }
  ```

- `POST /api/auth/login/` - 登录
  ```json
  {
    "username": "test",
    "password": "123456"
  }
  ```
  返回: `{ "access": "token...", "refresh": "token..." }`

- `POST /api/auth/refresh/` - 刷新 token
  ```json
  {
    "refresh": "refresh_token..."
  }
  ```

- `GET /api/auth/me/` - 获取当前用户
  请求头: `Authorization: Bearer <access_token>`

### 事件 API（需认证）
- `GET /api/events/` - 获取当前用户的事件
- `POST /api/events/` - 创建事件（自动关联当前用户）
- `PUT /api/events/{id}/` - 更新事件
- `DELETE /api/events/{id}/` - 删除事件

请求头必须携带: `Authorization: Bearer <access_token>`

## ⚠️ 注意事项
1. 旧数据库中的事件将被清空（因为字段结构变化较大）
2. 如需保留旧数据，请先备份 `db.sqlite3`
3. 首次部署后需要创建一个用户账号用于测试

