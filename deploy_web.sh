#!/bin/bash

# Vue3 前端部署脚本

SERVER="acs@app7626.acapp.acwing.com.cn"
REMOTE_PATH="~/kotlin_calendar/web"

echo "🚀 开始部署前端..."

# 1. Build Vue3
echo "📦 正在 Build Vue3 项目..."
cd web_frontend
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Build 失败！"
    exit 1
fi

# 2. 上传到服务器
echo "📤 正在上传到服务器..."
scp -r dist/* ${SERVER}:${REMOTE_PATH}/

if [ $? -ne 0 ]; then
    echo "❌ 上传失败！"
    exit 1
fi

echo "✅ 前端部署完成！"
echo "🌐 访问地址：https://app7626.acapp.acwing.com.cn/"

