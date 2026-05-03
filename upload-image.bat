@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo =========================================
echo    🖼️  纸橙的动画小屋 · 图片上传器
echo =========================================
echo.

:: ---------- 检查目标目录 ----------
if not exist "public\images" (
    echo [!] public\images 目录不存在，正在创建...
    mkdir "public\images"
)

echo  📂 图片将保存到：public\images\
echo.

:: ---------- 让用户选择图片 ----------
echo  ┌──────────────────────────────────────────┐
echo  │  拖拽图片文件到此窗口，然后按回车，        │
echo  │  或者手动输入完整路径（支持 .jpg/.png/.gif/.svg/.webp）│
echo  └──────────────────────────────────────────┘
echo.
set "src_path="
set /p "src_path=👉 图片源路径: "

:: 去掉可能的首尾引号
set "src_path=!src_path:"=!"

if "!src_path!"=="" (
    echo [x] 路径不能为空。
    pause
    exit /b 1
)

:: 检查源文件是否存在
if not exist "!src_path!" (
    echo [x] 找不到文件：!src_path!
    pause
    exit /b 1
)

:: ---------- 输入目标文件名 ----------
echo.
set "img_name="
for %%f in ("!src_path!") do set "img_name=%%~nxf"

echo  📝 当前文件名：!img_name!
echo.
set "custom_name="
set /p "custom_name=✏️  输入新文件名（直接回车保留原名，不用加扩展名）: "

if not "!custom_name!"=="" (
    for %%f in ("!src_path!") do set "img_ext=%%~xf"
    set "img_name=!custom_name!!img_ext!"
)

:: 小写化文件名（URL里大写字母有时会出问题）
call :toLower img_name

:: 检查是否已存在
if exist "public\images\!img_name!" (
    echo.
    echo [x] public\images\!img_name! 已存在！
    set "ow="
    set /p "ow=   覆盖？(y/回车=取消): "
    if /i not "!ow!"=="y" (
        echo 已取消。
        pause
        exit /b 0
    )
)

:: ---------- 复制文件 ----------
copy /Y "!src_path!" "public\images\!img_name!" >nul 2>nul
if !errorlevel! neq 0 (
    echo [x] 复制失败，请检查权限或磁盘空间。
    pause
    exit /b 1
)

echo.
echo =========================================
echo    ✅ 图片上传成功！
echo =========================================
echo.
echo  📂 保存位置：public\images\!img_name!
echo.
echo  📋 在 Markdown 里这样引用：
echo     ![图片说明](/images/!img_name!)
echo.
echo  💡 提示：
echo     - 路径以 /images/ 开头（不需要写 public）
echo     - 发布后图片会一起部署到线上
echo.
pause
exit /b 0


:: ========== 小写化函数 ==========
:toLower
for %%a in (A B C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    set "!%1=!!%1:%%a=%%a!"
)
goto :eof

endlocal
