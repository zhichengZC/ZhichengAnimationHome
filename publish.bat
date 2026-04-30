@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo =========================================
echo    🍊 纸橙的动画小屋 · 一键发布
echo =========================================
echo.

cd /d "%~dp0"

:: Check git repo
if not exist ".git" (
    echo [!] 当前目录还没初始化 Git 仓库。
    echo     正在初始化...
    git init
    git branch -M main
    echo.
    echo [!] 请先在 GitHub 创建仓库 zhichengZC.github.io ，然后运行：
    echo     git remote add origin https://github.com/zhichengZC/zhichengZC.github.io.git
    echo.
    pause
    exit /b 1
)

:: Get commit message
set "msg=%~1"
if "%msg%"=="" (
    set /p "msg=📝 请输入本次更新说明 (直接回车使用默认): "
)
if "%msg%"=="" (
    for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value ^| find "="') do set "dt=%%a"
    set "msg=update: !dt:~0,4!-!dt:~4,2!-!dt:~6,2! !dt:~8,2!:!dt:~10,2!"
)

echo.
echo [1/3] 📦 添加变更...
git add -A

echo [2/3] 💬 提交："%msg%"
git commit -m "%msg%"
if errorlevel 1 (
    echo [i] 没有新变更需要提交，直接推送。
)

echo [3/3] 🚀 推送到 GitHub...
git push origin main
if errorlevel 1 (
    echo.
    echo [x] 推送失败，请检查网络或远程仓库配置。
    pause
    exit /b 1
)

echo.
echo =========================================
echo  ✅ 推送成功！
echo  🌐 GitHub Actions 正在自动部署中...
echo  📡 1-2 分钟后访问: https://zhichengzc.github.io
echo  📊 查看部署进度: https://github.com/zhichengZC/zhichengZC.github.io/actions
echo =========================================
echo.
pause
