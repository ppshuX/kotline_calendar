#!/bin/bash

# 🚨 清理 Git 历史中的敏感信息
# 警告：此脚本会重写 Git 历史，执行前请备份！

set -e

echo "=========================================="
echo "🚨 Git 历史敏感信息清理工具"
echo "=========================================="
echo ""
echo "⚠️  警告：此操作将重写 Git 历史！"
echo "⚠️  建议先备份仓库：cp -r .git .git.backup"
echo ""
read -p "是否继续？(输入 YES 继续): " confirm

if [ "$confirm" != "YES" ]; then
    echo "❌ 操作已取消"
    exit 1
fi

echo ""
echo "📋 步骤 1: 检查当前分支..."
CURRENT_BRANCH=$(git branch --show-current)
echo "当前分支: $CURRENT_BRANCH"

echo ""
echo "📋 步骤 2: 查找可能包含敏感信息的文件..."
echo ""
echo "检查 .env 文件历史..."
git log --all --full-history -- "**/.env" --pretty=format:"%h %ad %s" --date=short || echo "未找到 .env 文件历史"

echo ""
echo "检查包含 'password' 的文件..."
git log --all --full-history -- "**/*password*" --pretty=format:"%h %ad %s" --date=short || echo "未找到"

echo ""
echo ""
echo "📋 步骤 3: 使用 git filter-branch 清理敏感文件..."
echo ""

# 清理可能包含敏感信息的文件
FILES_TO_REMOVE=(
    "backend/.env"
    "backend/.env.local"
    "backend/.env.production"
    ".env"
    ".env.local"
)

for file in "${FILES_TO_REMOVE[@]}"; do
    echo "正在清理: $file"
    git filter-branch --force --index-filter \
        "git rm --cached --ignore-unmatch $file" \
        --prune-empty --tag-name-filter cat -- --all 2>/dev/null || true
done

echo ""
echo "📋 步骤 4: 清理 reflog 和垃圾回收..."
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo ""
echo "📋 步骤 5: 验证清理结果..."
echo ""
echo "检查 .env 是否还在历史中..."
if git log --all --full-history -- "**/.env" --pretty=format:"%h" | head -1; then
    echo "⚠️  警告：.env 文件仍在历史中！"
else
    echo "✅ .env 文件已从历史中移除"
fi

echo ""
echo "=========================================="
echo "✅ 清理完成！"
echo "=========================================="
echo ""
echo "📝 接下来的步骤："
echo ""
echo "1. 撤销并重新生成 QQ 邮箱授权码"
echo "   https://mail.qq.com → 设置 → 账户 → 生成授权码"
echo ""
echo "2. 更新服务器 .env 文件（使用新的授权码）"
echo ""
echo "3. 强制推送到 GitHub（会重写远程历史）："
echo "   git push --force --all"
echo "   git push --force --tags"
echo ""
echo "4. 通知所有协作者重新克隆仓库："
echo "   git clone <repo-url>"
echo ""
echo "5. 在 GitGuardian 标记问题为已解决"
echo ""
echo "⚠️  注意：所有协作者需要删除本地仓库并重新克隆！"
echo "=========================================="

