@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

cd /d "%~dp0"

:menu
cls
echo.
echo ╔══════════════════════════════════════════════════╗
echo ║                                                  ║
echo ║       🧰  纸橙的动画小屋 · 工具箱                ║
echo ║                                                  ║
echo ╚══════════════════════════════════════════════════╝
echo.
echo   ┌────────────────────────────────────────────────┐
echo   │                                                │
echo   │   📝 1. 新建文章                               │
echo   │   🖼️  2. 上传图片                              │
echo   │                                                │
echo   │   ✏️  3. 修改网站信息（标题/描述/导航/联系方式）│
echo   │   📄 4. 修改页面内容（首页/关于页/页脚）        │
echo   │                                                │
echo   │   🚀 5. 本地预览                               │
echo   │   ☁️  6. 一键发布到线上                         │
echo   │                                                │
echo   │   ❌ 0. 退出                                    │
echo   │                                                │
echo   └────────────────────────────────────────────────┘
echo.
set "choice="
set /p "choice=👉 请选择操作 (0-6): "

if "!choice!"=="1" goto :do_new_post
if "!choice!"=="2" goto :do_upload_image
if "!choice!"=="3" goto :do_edit_site
if "!choice!"=="4" goto :do_edit_page
if "!choice!"=="5" goto :do_dev
if "!choice!"=="6" goto :do_publish
if "!choice!"=="0" goto :eof

echo.
echo [x] 无效选择，请重新输入。
timeout /t 2 >nul
goto :menu


:do_new_post
cls
call new-post.bat
echo.
echo 按任意键返回主菜单...
pause >nul
goto :menu

:do_upload_image
cls
call upload-image.bat
echo.
echo 按任意键返回主菜单...
pause >nul
goto :menu

:do_edit_site
cls
call edit-site.bat
echo.
echo 按任意键返回主菜单...
pause >nul
goto :menu

:do_edit_page
cls
call edit-page.bat
echo.
echo 按任意键返回主菜单...
pause >nul
goto :menu

:do_dev
cls
call start-dev.bat
echo.
echo 按任意键返回主菜单...
pause >nul
goto :menu

:do_publish
cls
call publish.bat
echo.
echo 按任意键返回主菜单...
pause >nul
goto :menu


endlocal
