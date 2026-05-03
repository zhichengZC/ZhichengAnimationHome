@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo =========================================
echo    🚀 纸橙的动画小屋 · 一键发布
echo =========================================
echo.

:: ---------- 0. 检查是不是 git 仓库 ----------
if not exist ".git" (
    echo [x] 当前目录不是 Git 仓库，无法发布。
    echo     请确认你在 ZhichengBlog 项目根目录下。
    pause
    exit /b 1
)

:: ---------- 1. 看看有没有改动 ----------
echo [1/5] 🔍 正在检查本地改动...
echo.

git status --short

:: 用 git status 的输出判断有没有变化
for /f %%i in ('git status --porcelain ^| find /c /v ""') do set "changes=%%i"

if "!changes!"=="0" (
    echo.
    echo [!] 没有检测到任何改动，无需发布。
    echo.
    pause
    exit /b 0
)

echo.
echo     共检测到 !changes! 处改动。
echo.

:: ---------- 2. 取提交信息 ----------
:: 优先用调用方传进来的参数（new-post.bat 会传文章标题）
set "msg=%~1"

if "!msg!"=="" (
    echo [2/5] ✍️  请输入本次更新说明
    echo      例如：新增文章 / 修复样式 / 更新关于页
    echo.
    set /p "msg=   说明（直接回车使用默认值）: "
)

:: 如果还是空的，用日期做默认值
if "!msg!"=="" (
    for /f "usebackq delims=" %%a in (`powershell -NoProfile -Command "Get-Date -Format 'yyyy-MM-dd HH:mm'"`) do set "today=%%a"
    set "msg=日常更新 !today!"
)

echo.
echo     提交信息：!msg!
echo.

:: ---------- 3. 确认 ----------
set "confirm="
set /p "confirm=⚠️  确认要发布到 GitHub 吗？(y/回车=取消): "
if /i not "!confirm!"=="y" (
    echo.
    echo 已取消发布。
    pause
    exit /b 0
)

:: ---------- 4. add + commit + push ----------
echo.
echo [3/5] 📦 正在打包改动 (git add)...
git add .
if !errorlevel! neq 0 (
    echo [x] git add 失败。
    pause
    exit /b 1
)

echo.
echo [4/5] � 正在提交 (git commit)...
git commit -m "!msg!"
if !errorlevel! neq 0 (
    echo [x] git commit 失败，可能是没有改动或配置问题。
    pause
    exit /b 1
)

echo.
echo [5/5] ☁️  正在推送到 GitHub (git push)...
echo     如果是第一次推送，可能会弹出登录窗口，请完成登录。
echo.
git push
if !errorlevel! neq 0 (
    echo.
    echo [x] 推送失败。常见原因：
    echo     1. 网络问题，稍后再试。
    echo     2. 远端有新提交，试试先执行：git pull --rebase
    echo     3. GitHub 要求 Token 登录，请到 GitHub Settings 生成 Personal Access Token。
    pause
    exit /b 1
)

echo.
echo =========================================
echo    ✅ 推送成功！
echo =========================================
echo.
echo  🌐 GitHub Actions 会自动执行构建和部署，
echo     大约 1-3 分钟后网站会更新完成。
echo.
echo  📊 查看部署进度（Actions 标签页）：
echo     打开你的 GitHub 仓库页面 → 点顶部的 "Actions" 标签
echo     看到绿色对勾 ✓ 就说明部署完成啦。
echo.
echo  🔗 你的网站地址：
echo     https://（你的GitHub用户名）.github.io/（仓库名）/
echo.
pause
