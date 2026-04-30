@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo =========================================
echo    🍊 纸橙的动画小屋 · 一键写文章
echo =========================================
echo.

:: ---------- 1. 输入标题 ----------
set "title="
set /p "title=📝 文章标题（中文随意写）: "
if "!title!"=="" (
    echo [x] 标题不能为空，已取消。
    pause
    exit /b 1
)

:: ---------- 2. 输入英文文件名 ----------
set "slug="
set /p "slug=🔗 文件名（英文小写+连字符，例如 my-first-day，不用加 .md）: "
if "!slug!"=="" (
    echo [x] 文件名不能为空，已取消。
    pause
    exit /b 1
)

:: 如果用户手滑加了 .md 后缀，自动去掉，防止生成 xxx.md.md
if /i "!slug:~-3!"==".md" set "slug=!slug:~0,-3!"

:: 校验文件是否已存在
set "target=src\content\posts\!slug!.md"
if exist "!target!" (
    echo.
    echo [x] 文件已存在：!target!
    echo     请换一个文件名再试。
    pause
    exit /b 1
)

:: ---------- 3. 输入描述（可选） ----------
set "desc="
set /p "desc=💬 一句话描述（可选，直接回车跳过）: "
if "!desc!"=="" set "desc=!title!"

:: ---------- 4. 输入标签（可选） ----------
set "tags="
set /p "tags=🏷️  标签（用英文逗号分隔，例如 随笔,生活。可选）: "

:: 把输入的 tag 拼成 [a, b, c] 格式
set "tagList=[]"
if not "!tags!"=="" (
    set "tagList=["
    set "first=1"
    for %%t in ("!tags:,=" "!") do (
        set "t=%%~t"
        :: 去掉首尾空格
        for /f "tokens=* delims= " %%s in ("!t!") do set "t=%%s"
        if "!first!"=="1" (
            set "tagList=!tagList!!t!"
            set "first=0"
        ) else (
            set "tagList=!tagList!, !t!"
        )
    )
    set "tagList=!tagList!]"
)

:: ---------- 5. 取当前日期 ----------
:: 用 PowerShell 拿日期（wmic 在新版 Win11 已被移除，必须用 PS 才稳）
for /f "usebackq delims=" %%a in (`powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd"`) do set "today=%%a"

if "!today!"=="" (
    echo [x] 获取系统日期失败，请手动在文件里修改 pubDate。
    set "today=2026-01-01"
)

:: ---------- 6. 写 front-matter ----------
echo.
echo [1/3] 📄 正在创建文件：!target!

(
    echo ---
    echo title: !title!
    echo description: !desc!
    echo pubDate: !today!
    echo tags: !tagList!
    echo ---
    echo.
    echo ## 在这里开始写正文吧 ✍️
    echo.
    echo 删掉这段说明，把你想说的写进来 ——
    echo.
    echo - **加粗** 用两个星号包住
    echo - *斜体* 用一个星号包住
    echo - [链接文字]^(https://example.com^) 就是一个超链接
    echo - `行内代码` 用反引号
    echo.
    echo ### 二级小标题用三个井号
    echo.
    echo ^> 引用段落用大于号开头
    echo.
    echo 图片放进 public/images/ 里，然后这样写：
    echo.
    echo ![图片说明]^(/images/your-image.jpg^)
    echo.
    echo ---
    echo.
    echo 🍊
) > "!target!"

if not exist "!target!" (
    echo [x] 文件创建失败，请检查权限。
    pause
    exit /b 1
)

echo     ✅ 创建成功！

:: ---------- 7. 打开编辑器 ----------
echo.
echo [2/3] ✍️  正在打开编辑器...
echo     写完内容后 **保存并关闭编辑器**，脚本会继续询问是否发布。
echo.

:: 优先用 VSCode（如果装了），其次用记事本
where code >nul 2>nul
if !errorlevel! equ 0 (
    :: VSCode 用 --wait 让它阻塞到窗口关闭
    code --wait "!target!"
) else (
    notepad "!target!"
)

:: ---------- 8. 询问是否立即发布 ----------
echo.
echo [3/3] 🚀 文章已保存。是否立即发布到 GitHub？
echo.
set "confirm="
set /p "confirm=   输入 y 发布 / 直接回车先不发布: "

if /i "!confirm!"=="y" (
    echo.
    call publish.bat "新增文章：!title!"
) else (
    echo.
    echo [i] 已保存到本地，稍后想发布就双击 publish.bat
    echo     文件位置: !target!
    echo.
    pause
)

endlocal
