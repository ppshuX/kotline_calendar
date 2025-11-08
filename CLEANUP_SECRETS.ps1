# 🚨 清理 Git 历史中的敏感信息（Windows PowerShell 版本）
# 警告：此脚本会重写 Git 历史，执行前请备份！

Write-Host "==========================================" -ForegroundColor Yellow
Write-Host "🚨 Git 历史敏感信息清理工具" -ForegroundColor Red
Write-Host "==========================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "⚠️  警告：此操作将重写 Git 历史！" -ForegroundColor Red
Write-Host "⚠️  建议先备份 .git 文件夹" -ForegroundColor Red
Write-Host ""

$confirm = Read-Host "是否继续？(输入 YES 继续)"

if ($confirm -ne "YES") {
    Write-Host "❌ 操作已取消" -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "📋 步骤 1: 检查当前分支..." -ForegroundColor Cyan
$currentBranch = git branch --show-current
Write-Host "当前分支: $currentBranch" -ForegroundColor Green

Write-Host ""
Write-Host "📋 步骤 2: 查找可能包含敏感信息的提交..." -ForegroundColor Cyan
Write-Host ""
Write-Host "检查 .env 文件历史..." -ForegroundColor Yellow
git log --all --full-history -- "**/.env" --pretty=format:"%h %ad %s" --date=short 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "未找到 .env 文件历史记录" -ForegroundColor Green
}

Write-Host ""
Write-Host ""
Write-Host "📋 步骤 3: 清理 Git 历史..." -ForegroundColor Cyan
Write-Host ""

# 需要清理的文件列表
$filesToRemove = @(
    "backend/.env",
    "backend/.env.local",
    "backend/.env.production",
    ".env",
    ".env.local"
)

foreach ($file in $filesToRemove) {
    Write-Host "正在清理: $file" -ForegroundColor Yellow
    git filter-branch --force --index-filter "git rm --cached --ignore-unmatch $file" --prune-empty --tag-name-filter cat -- --all 2>$null
}

Write-Host ""
Write-Host "📋 步骤 4: 清理 reflog 和垃圾回收..." -ForegroundColor Cyan
git reflog expire --expire=now --all
git gc --prune=now --aggressive

Write-Host ""
Write-Host "📋 步骤 5: 验证清理结果..." -ForegroundColor Cyan
Write-Host ""
$envCheck = git log --all --full-history -- "**/.env" --pretty=format:"%h" 2>$null | Select-Object -First 1
if ($envCheck) {
    Write-Host "⚠️  警告：.env 文件可能仍在历史中！" -ForegroundColor Red
} else {
    Write-Host "✅ .env 文件已从历史中移除" -ForegroundColor Green
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Yellow
Write-Host "✅ 清理完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "📝 接下来的步骤：" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. 撤销并重新生成 QQ 邮箱授权码" -ForegroundColor White
Write-Host "   https://mail.qq.com → 设置 → 账户 → 生成授权码" -ForegroundColor Gray
Write-Host ""
Write-Host "2. 更新服务器 backend/.env 文件（使用新的授权码）" -ForegroundColor White
Write-Host ""
Write-Host "3. 强制推送到 GitHub（会重写远程历史）：" -ForegroundColor White
Write-Host "   git push --force --all" -ForegroundColor Yellow
Write-Host "   git push --force --tags" -ForegroundColor Yellow
Write-Host ""
Write-Host "4. 如有协作者，通知他们重新克隆仓库" -ForegroundColor White
Write-Host ""
Write-Host "5. 在 GitGuardian 标记问题为已解决" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  警告：强制推送会重写远程历史！" -ForegroundColor Red
Write-Host "==========================================" -ForegroundColor Yellow

