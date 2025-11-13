# 🔧 修复根路径500错误

## 问题描述

访问 `https://app7626.acapp.acwing.com.cn/` 返回500错误。

## 原因分析

1. **Nginx配置路径错误**: `nginx.conf` 中仍使用旧路径 `kotlin_calendar`，实际项目已迁移到 `ralendar`
2. **根路径应该由Nginx直接服务静态文件**，而不是转发给Django

## 修复步骤

### 1. 更新Nginx配置

修改 `backend/nginx.conf` 中的路径：

```nginx
# 静态文件
location /static/ {
    alias /home/acs/ralendar/backend/static/;  # 已更新
    expires 30d;
    add_header Cache-Control "public, immutable";
}

# AcWing 平台应用
location /acapp/ {
    alias /home/acs/ralendar/acapp/dist/;  # 已更新
    try_files $uri $uri/ /acapp/index.html;
    add_header Access-Control-Allow-Origin *;
}

# Web 前端（最后匹配）
location / {
    root /home/acs/ralendar/web;  # 已更新
    index index.html;
    try_files $uri $uri/ /index.html;
}
```

### 2. 检查前端文件是否存在

```bash
# SSH到服务器
ls -la /home/acs/ralendar/web/
# 应该看到 index.html 和 assets/ 目录
```

### 3. 重新加载Nginx配置

```bash
# 测试配置
sudo nginx -t

# 重新加载配置
sudo nginx -s reload
# 或
sudo systemctl reload nginx
```

### 4. 验证修复

访问 `https://app7626.acapp.acwing.com.cn/` 应该正常显示前端页面。

## 如果仍然500错误

### 检查1: 文件权限

```bash
# 确保Nginx可以读取文件
sudo chown -R www-data:www-data /home/acs/ralendar/web
sudo chmod -R 755 /home/acs/ralendar/web
```

### 检查2: Nginx错误日志

```bash
sudo tail -f /var/log/nginx/error.log
```

### 检查3: 确认前端文件已构建

```bash
# 如果web目录为空或不存在，需要重新构建
cd ~/ralendar/web_frontend
npm run build
```

## 完整Nginx配置检查清单

- [ ] 路径已更新为 `ralendar`
- [ ] 前端文件存在于 `/home/acs/ralendar/web/`
- [ ] Nginx配置测试通过 (`nginx -t`)
- [ ] Nginx已重新加载 (`nginx -s reload`)
- [ ] 文件权限正确 (`www-data` 可读)
- [ ] 错误日志无异常

