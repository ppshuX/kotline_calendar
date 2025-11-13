# 🚀 Ralendar 服务器迁移指南

## 📋 迁移概述

**迁移原因**: Roamio团队需要将Ralendar和Roamio进行服务器对调，以满足工信部备案要求。

**迁移时间**: 2025年11月14日（周四）或 11月16日（周六）凌晨 02:00 - 04:00

**目标服务器**: 阿里云 `47.121.137.60`（当前运行Roamio）

**当前服务器**: 腾讯云 `81.71.138.122`

---

## ⚠️ 重要说明

**当前Ralendar部署方式**: ✅ **已Docker化**（使用现有Dockerfile和docker-compose.yml）

**迁移方式**: 直接使用现有Docker配置生成镜像并迁移

---

## 🎯 迁移方案：使用现有Docker配置

Ralendar项目已经在Docker中开发，直接使用现有的Dockerfile和docker-compose.yml即可。

### 迁移步骤
1. 在腾讯云服务器上导出Docker镜像
2. 传输镜像到阿里云服务器
3. 在阿里云服务器上加载镜像并启动

---

## 📦 迁移步骤（Docker方案）

### Phase 1: 准备阶段（迁移前1天）

#### 1.1 在腾讯云服务器上备份

```bash
# SSH登录到腾讯云服务器
ssh acs@app7626.acapp.acwing.com.cn

# 备份数据库（从Docker容器中）
docker exec ralendar-db mysqldump -u root -p ralendar_db > /tmp/ralendar_db_$(date +%Y%m%d).sql

# 或者使用Django dumpdata
docker exec ralendar-web python manage.py dumpdata > /tmp/ralendar_backup_$(date +%Y%m%d).json

# 备份配置文件
tar -czf /tmp/ralendar_config_$(date +%Y%m%d).tar.gz \
    ~/kotlin_calendar/backend/.env \
    ~/kotlin_calendar/docker-compose.yml \
    /etc/nginx/sites-available/ralendar

# 备份静态文件
tar -czf /tmp/ralendar_static_$(date +%Y%m%d).tar.gz \
    ~/kotlin_calendar/web \
    ~/kotlin_calendar/acapp/dist
```

#### 1.2 导出Docker镜像

```bash
# 在腾讯云服务器上
cd ~/kotlin_calendar

# 查看当前运行的容器
docker ps

# 导出镜像（使用现有镜像名称）
docker save ralendar:latest -o /tmp/ralendar_image.tar

# 或者从运行的容器创建镜像
docker commit ralendar-web ralendar:migration
docker save ralendar:migration -o /tmp/ralendar_image.tar

# 压缩镜像（可选，减少传输时间）
gzip /tmp/ralendar_image.tar
```

#### 1.3 准备迁移脚本

创建`scripts/migrate_to_aliyun.sh`:

```bash
#!/bin/bash
# Ralendar迁移到阿里云脚本

set -e

TARGET_SERVER="root@47.121.137.60"
BACKUP_DIR="/tmp/ralendar_migration_$(date +%Y%m%d)"

echo "=== Ralendar迁移到阿里云 ==="
echo "目标服务器: $TARGET_SERVER"
echo "备份目录: $BACKUP_DIR"

# 1. 创建备份目录
mkdir -p $BACKUP_DIR

# 2. 备份数据库
echo "备份数据库..."
cd ~/kotlin_calendar/backend
python manage.py dumpdata > $BACKUP_DIR/db_backup.json

# 3. 备份配置文件
echo "备份配置文件..."
cp .env $BACKUP_DIR/
cp uwsgi.ini $BACKUP_DIR/
cp /etc/nginx/sites-available/ralendar $BACKUP_DIR/nginx.conf 2>/dev/null || true

# 4. 打包项目文件
echo "打包项目文件..."
cd ~
tar -czf $BACKUP_DIR/ralendar_project.tar.gz kotlin_calendar/

# 5. 传输到阿里云
echo "传输文件到阿里云..."
scp -r $BACKUP_DIR $TARGET_SERVER:/tmp/

# 6. 传输Docker镜像（如果已构建）
if [ -f /tmp/ralendar_image.tar.gz ]; then
    echo "传输Docker镜像..."
    scp /tmp/ralendar_image.tar.gz $TARGET_SERVER:/tmp/
fi

echo "=== 备份完成 ==="
echo "文件已传输到: $TARGET_SERVER:/tmp/ralendar_migration_$(date +%Y%m%d)"
```

---

### Phase 2: 迁移执行（迁移当天）

#### 2.1 在阿里云服务器上准备环境

```bash
# SSH登录到阿里云服务器
ssh root@47.121.137.60

# 安装Docker和Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
pip3 install docker-compose

# 创建项目目录
mkdir -p ~/ralendar
cd ~/ralendar
```

#### 2.2 传输文件

```bash
# 在腾讯云服务器上执行（或从本地）
# 传输项目文件
scp -r ~/kotlin_calendar root@47.121.137.60:~/ralendar/

# 传输备份文件
scp /tmp/ralendar_migration_*/ralendar_project.tar.gz root@47.121.137.60:/tmp/
```

#### 2.3 在阿里云服务器上部署

```bash
# SSH登录到阿里云服务器
ssh root@47.121.137.60

cd ~/ralendar

# 解压项目文件（如果传输的是压缩包）
tar -xzf /tmp/ralendar_migration_*/ralendar_project.tar.gz

# 加载Docker镜像
docker load -i /tmp/ralendar_image.tar.gz

# 配置环境变量
cd backend
cp .env.example .env
# 编辑.env文件，填入正确的配置（数据库地址等）
nano .env

# 恢复配置文件
cd ..
tar -xzf /tmp/ralendar_migration_*/ralendar_config_*.tar.gz

# 启动Docker容器（使用现有的docker-compose.yml）
docker-compose up -d

# 等待服务启动
sleep 10

# 恢复数据库
docker exec ralendar-db mysql -u root -p ralendar_db < /tmp/ralendar_db_*.sql
# 或者使用Django loaddata
docker exec ralendar-web python manage.py migrate
docker exec ralendar-web python manage.py loaddata /tmp/ralendar_backup_*.json

# 收集静态文件
docker exec ralendar-web python manage.py collectstatic --noinput

# 重启服务
docker-compose restart
```

#### 2.4 配置Nginx

```bash
# 在阿里云服务器上
# 创建Nginx配置
cat > /etc/nginx/sites-available/ralendar << 'EOF'
server {
    listen 80;
    server_name app7626.acapp.acwing.com.cn;

    # 前端静态文件
    location / {
        root /root/ralendar/web;
        try_files $uri $uri/ /index.html;
    }

    # AcApp静态文件
    location /acapp/ {
        alias /root/ralendar/acapp/dist/;
        try_files $uri $uri/ /acapp/index.html;
    }

    # API代理
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态文件
    location /static {
        alias /root/ralendar/backend/static;
    }
}
EOF

# 启用配置
ln -s /etc/nginx/sites-available/ralendar /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

---

### Phase 3: DNS更新

```bash
# 联系域名管理员或AcWing平台管理员
# 更新DNS记录：
# app7626.acapp.acwing.com.cn → 47.121.137.60
```

---

### Phase 4: 验证

```bash
# 1. 检查服务状态
docker-compose ps

# 2. 检查日志
docker-compose logs web
docker-compose logs celery

# 3. 测试API
curl http://localhost:8000/api/v1/health/

# 4. 测试前端
curl http://localhost/

# 5. 检查数据库连接
docker exec ralendar-web python manage.py dbshell
```

---

## 🔄 回滚方案

如果迁移出现问题，可以快速回滚：

```bash
# 1. 恢复DNS到原IP（联系域名管理员）
# app7626.acapp.acwing.com.cn → 81.71.138.122

# 2. 在腾讯云服务器上重启服务
ssh acs@app7626.acapp.acwing.com.cn
cd ~/kotlin_calendar/backend
./deploy.sh

# 3. 验证服务恢复
curl https://app7626.acapp.acwing.com.cn/api/v1/health/
```

---

## 📝 迁移检查清单

### 迁移前
- [ ] 备份数据库
- [ ] 备份配置文件
- [ ] 备份静态文件
- [ ] 构建Docker镜像
- [ ] 准备迁移脚本
- [ ] 确认阿里云服务器可用
- [ ] 确认迁移时间

### 迁移中
- [ ] 停止腾讯云服务（可选，减少数据不一致）
- [ ] 传输文件到阿里云
- [ ] 部署Docker容器
- [ ] 恢复数据库
- [ ] 配置Nginx
- [ ] 更新DNS
- [ ] 验证服务

### 迁移后
- [ ] 功能测试
- [ ] 性能测试
- [ ] 监控日志
- [ ] 通知用户（如需要）
- [ ] 清理腾讯云资源（确认迁移成功后）

---

## 🆘 故障排查

### 问题1: Docker容器无法启动

```bash
# 查看日志
docker-compose logs web

# 检查环境变量
docker exec ralendar-web env | grep DB

# 检查数据库连接
docker exec ralendar-web python manage.py dbshell
```

### 问题2: 数据库连接失败

```bash
# 检查MySQL容器状态
docker-compose ps db

# 检查MySQL日志
docker-compose logs db

# 测试连接
docker exec ralendar-web python manage.py check --database default
```

### 问题3: 静态文件404

```bash
# 重新收集静态文件
docker exec ralendar-web python manage.py collectstatic --noinput

# 检查Nginx配置
nginx -t

# 检查文件权限
ls -la ~/ralendar/web/
```

### 问题4: API返回502

```bash
# 检查uWSGI进程
docker exec ralendar-web ps aux | grep uwsgi

# 检查端口占用
netstat -tlnp | grep 8000

# 重启容器
docker-compose restart web
```

---

## 📞 联系方式

**Ralendar团队**
- 技术负责人：[待填写]
- 联系方式：[待填写]

**Roamio团队**
- 负责人：吕文潇
- 目标服务器：腾讯云 81.71.138.122

---

## 📚 相关文档

- [部署指南](./DEPLOYMENT_GUIDE.md)
- [Docker部署最佳实践](https://docs.docker.com/compose/production/)
- [Nginx配置指南](https://nginx.org/en/docs/)

---

**最后更新**: 2025年11月13日  
**文档版本**: v1.0

