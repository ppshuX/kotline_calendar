# KotlinCalendar 后端部署指南

部署到云服务器（app7626.acapp.acwing.com.cn）

---

## 📋 部署步骤

### 1. 上传代码到服务器

```bash
# 服务器上
cd ~
mkdir -p kotlin_calendar
cd kotlin_calendar

# 克隆代码（或直接上传）
git clone <your-repo-url> .

# 或者本地上传
# scp -r backend web acs@app7626.acapp.acwing.com.cn:~/kotlin_calendar/
```

---

### 2. 修改 Django 配置

```bash
cd ~/kotlin_calendar/backend
nano calendar_backend/settings.py
```

修改以下内容：

```python
# 生产环境
DEBUG = False

# 允许的域名
ALLOWED_HOSTS = ['app7626.acapp.acwing.com.cn', '127.0.0.1']

# 数据库（可选：改为 PostgreSQL）
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'calendar_db',
#         'USER': 'your_user',
#         'PASSWORD': 'your_password',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }
```

---

### 3. 运行部署脚本

```bash
chmod +x deploy.sh
./deploy.sh
```

或者手动执行：

```bash
# 安装依赖
pip3 install -r requirements.txt

# 数据库迁移
python3 manage.py migrate

# 启动 uWSGI
uwsgi --ini uwsgi.ini
```

---

### 4. 配置 Nginx

```bash
# 备份原配置
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bak

# 使用新配置
sudo cp nginx.conf /etc/nginx/nginx.conf

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl reload nginx
```

---

### 5. 测试 API

```bash
# 测试农历 API
curl "https://app7626.acapp.acwing.com.cn/api/lunar/?date=2025-11-06"

# 测试日程 API
curl "https://app7626.acapp.acwing.com.cn/api/events/"
```

---

## 🔧 常用命令

### 查看后端日志

```bash
cd ~/kotlin_calendar/backend
tail -f logs/uwsgi.log
```

### 重启后端

```bash
uwsgi --stop uwsgi.pid
./deploy.sh
```

### 查看进程

```bash
ps aux | grep uwsgi
```

### 停止后端

```bash
uwsgi --stop uwsgi.pid
# 或
pkill -f "uwsgi.*calendar_backend"
```

---

## 🌐 部署后的访问地址

- **前端**: https://app7626.acapp.acwing.com.cn/
- **API**: https://app7626.acapp.acwing.com.cn/api/
- **API 文档**: https://app7626.acapp.acwing.com.cn/api/ （DRF 自带界面）

---

## 📱 Android App 配置

修改 `RetrofitClient.kt`：

```kotlin
private const val BASE_URL = "https://app7626.acapp.acwing.com.cn/api/"
```

重新 Build APK！

---

## ✅ 部署检查清单

- [ ] 代码已上传
- [ ] Django settings.py 已修改（DEBUG=False, ALLOWED_HOSTS）
- [ ] 依赖已安装（pip3 install -r requirements.txt）
- [ ] 数据库已迁移（python3 manage.py migrate）
- [ ] uWSGI 已启动（ps aux | grep uwsgi）
- [ ] Nginx 配置已更新
- [ ] Nginx 已重启（sudo systemctl reload nginx）
- [ ] API 测试通过（curl）
- [ ] 前端可访问
- [ ] Android App 可连接

---

## 🐛 常见问题

### 1. 502 Bad Gateway

**原因**：uWSGI 没启动或端口不对

**解决**：
```bash
ps aux | grep uwsgi
./deploy.sh
```

### 2. uWSGI 未安装

**解决**：
```bash
pip3 install uwsgi
# 或
sudo apt-get install uwsgi uwsgi-plugin-python3
```

### 3. CORS 错误

**解决**：检查 Django settings.py 中的 CORS 配置

### 4. 静态文件 404

**解决**：检查 web 目录下的文件路径

---

**部署文档已生成！** 📝

