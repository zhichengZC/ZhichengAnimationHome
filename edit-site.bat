@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo =========================================
echo    🏠 纸橙的动画小屋 · 网站设置编辑器
echo =========================================
echo.

:: ---------- 读取当前设置 ----------
set "current_title="
set "current_desc="
set "current_author="
for /f "usebackq delims=" %%a in (`powershell -NoProfile -Command "(Get-Content 'src\consts.ts' -Raw) -replace '(?s).*SITE_TITLE\s*=\s*''([^'']*)''.*', '$1'"`) do set "current_title=%%a"
for /f "usebackq delims=" %%a in (`powershell -NoProfile -Command "(Get-Content 'src\consts.ts' -Raw) -replace '(?s).*SITE_DESCRIPTION\s*=\s*''([^'']*)''.*', '$1'"`) do set "current_desc=%%a"
for /f "usebackq delims=" %%a in (`powershell -NoProfile -Command "(Get-Content 'src\consts.ts' -Raw) -replace '(?s).*SITE_AUTHOR\s*=\s*''([^'']*)''.*', '$1'"`) do set "current_author=%%a"

echo  📋 当前设置：
echo.
echo     站点标题：!current_title!
echo     站点描述：!current_desc!
echo     作者名称：!current_author!
echo.

:: ---------- 菜单 ----------
echo  ┌──────────────────────────────────┐
echo  │  1️⃣  修改站点标题                │
echo  │  2️⃣  修改站点描述                │
echo  │  3️⃣  修改作者名称                │
echo  │  4️⃣  修改导航链接                │
echo  │  5️⃣  修改关于页联系方式          │
echo  │  0️⃣  退出                        │
echo  └──────────────────────────────────┘
echo.

set "choice="
set /p "choice=👉 请选择操作 (0-5): "

if "!choice!"=="1" goto :edit_title
if "!choice!"=="2" goto :edit_desc
if "!choice!"=="3" goto :edit_author
if "!choice!"=="4" goto :edit_nav
if "!choice!"=="5" goto :edit_about
if "!choice!"=="0" goto :eof
echo.
echo [x] 无效选择。
pause
exit /b 1

:: ==================== 1. 修改标题 ====================
:edit_title
echo.
echo 📝 当前标题：!current_title!
echo.
set "new_title="
set /p "new_title=输入新标题（直接回车取消）: "
if "!new_title!"=="" (
    echo 已取消。
    pause
    exit /b 0
)

powershell -NoProfile -Command "(Get-Content 'src\consts.ts' -Raw) -replace '(SITE_TITLE\s*=\s*'')[^'']*', (''' + '!new_title!' + '''') | Set-Content 'src\consts.ts' -NoNewline"
echo.
echo ✅ 标题已更新为：!new_title!
echo.
echo ⚠️  别忘了发布才能线上生效（双击 publish.bat）
pause
exit /b 0

:: ==================== 2. 修改描述 ====================
:edit_desc
echo.
echo 📝 当前描述：!current_desc!
echo.
set "new_desc="
set /p "new_desc=输入新描述（直接回车取消）: "
if "!new_desc!"=="" (
    echo 已取消。
    pause
    exit /b 0
)

powershell -NoProfile -Command "(Get-Content 'src\consts.ts' -Raw) -replace '(SITE_DESCRIPTION\s*=\s*'')[^'']*', (''' + '!new_desc!' + '''') | Set-Content 'src\consts.ts' -NoNewline"
echo.
echo ✅ 描述已更新为：!new_desc!
echo.
echo ⚠️  别忘了发布才能线上生效（双击 publish.bat）
pause
exit /b 0

:: ==================== 3. 修改作者 ====================
:edit_author
echo.
echo 📝 当前作者：!current_author!
echo.
set "new_author="
set /p "new_author=输入新作者名（直接回车取消）: "
if "!new_author!"=="" (
    echo 已取消。
    pause
    exit /b 0
)

powershell -NoProfile -Command "(Get-Content 'src\consts.ts' -Raw) -replace '(SITE_AUTHOR\s*=\s*'')[^'']*', (''' + '!new_author!' + '''') | Set-Content 'src\consts.ts' -NoNewline"
echo.
echo ✅ 作者名已更新为：!new_author!
echo.
echo ⚠️  别忘了发布才能线上生效（双击 publish.bat）
pause
exit /b 0

:: ==================== 4. 修改导航链接 ====================
:edit_nav
echo.
echo 📋 当前导航链接（来自 src/consts.ts 的 NAV_LINKS）：
echo.
echo   / → 首页
echo   /blog → 文章
echo   /about → 关于
echo.
echo  ┌──────────────────────────────────┐
echo  │  a) 添加新导航项                 │
echo  │  b) 删除导航项                   │
echo  │  c) 修改导航项标签               │
echo  │  0) 返回                        │
echo  └──────────────────────────────────┘
echo.
set "nav_choice="
set /p "nav_choice=👉 请选择 (a/b/c/0): "

if /i "!nav_choice!"=="a" goto :nav_add
if /i "!nav_choice!"=="b" goto :nav_del
if /i "!nav_choice!"=="c" goto :nav_edit
if /i "!nav_choice!"=="0" goto :eof
echo [x] 无效选择。
pause
exit /b 1

:nav_add
echo.
set "nav_href="
set "nav_label="
set /p "nav_href=输入链接路径（例如 /portfolio）: "
if "!nav_href!"=="" ( echo 已取消。 & pause & exit /b 0 )
set /p "nav_label=输入显示名称（例如 作品集）: "
if "!nav_label!"=="" ( echo 已取消。 & pause & exit /b 0 )

:: 用 PowerShell 在 NAV_LINKS 数组末尾插入新项
powershell -NoProfile -Command ^
"$c = Get-Content 'src\consts.ts' -Raw; " ^
"$newItem = \"`n  { href: '!nav_href!', label: '!nav_label!' }\"; " ^
"$c = $c -replace '(NAV_LINKS\s*=\s*\[[^\]]*)\]', (\"`$1,\" + $newItem + '`n]'); " ^
"Set-Content 'src\consts.ts' -Value $c -NoNewline"

echo.
echo ✅ 已添加导航：!nav_label! → !nav_href!
echo.
echo ⚠️  别忘了：
echo     1. 创建对应的页面文件（如 src/pages/portfolio.astro）
echo     2. 发布才能线上生效（双击 publish.bat）
pause
exit /b 0

:nav_del
echo.
echo 当前导航项：
echo   1. / → 首页
echo   2. /blog → 文章
echo   3. /about → 关于
echo.
set "del_idx="
set /p "del_idx=输入要删除的编号（1/2/3，直接回车取消）: "
if "!del_idx!"=="1" ( echo [!] 不建议删除首页导航。 & pause & exit /b 0 )
if "!del_idx!"=="2" (
    powershell -NoProfile -Command "(Get-Content 'src\consts.ts' -Raw) -replace ',?\s*\{\s*href:\s*''/blog''[^}]*\}', '' | Set-Content 'src\consts.ts' -NoNewline"
    echo ✅ 已删除 /blog 导航项。
) 
if "!del_idx!"=="3" (
    powershell -NoProfile -Command "(Get-Content 'src\consts.ts' -Raw) -replace ',?\s*\{\s*href:\s*''/about''[^}]*\}', '' | Set-Content 'src\consts.ts' -NoNewline"
    echo ✅ 已删除 /about 导航项。
)
echo.
echo ⚠️  别忘了发布才能线上生效（双击 publish.bat）
pause
exit /b 0

:nav_edit
echo.
echo 当前导航项：
echo   1. / → 首页
echo   2. /blog → 文章
echo   3. /about → 关于
echo.
set "edit_idx="
set /p "edit_idx=输入要修改的编号（1/2/3，直接回车取消）: "
set "new_label="
if "!edit_idx!"=="1" (
    set /p "new_label=输入新标签名（当前：首页）: "
    if not "!new_label!"=="" (
        powershell -NoProfile -Command "(Get-Content 'src\consts.ts' -Raw) -replace '(href:\s*''/''[^}]*label:\s*'')[^'']*', ('''' + '!new_label!' + '''') | Set-Content 'src\consts.ts' -NoNewline"
        echo ✅ 首页标签已改为：!new_label!
    )
)
if "!edit_idx!"=="2" (
    set /p "new_label=输入新标签名（当前：文章）: "
    if not "!new_label!"=="" (
        powershell -NoProfile -Command "(Get-Content 'src\consts.ts' -Raw) -replace '(href:\s*''/blog''[^}]*label:\s*'')[^'']*', ('''' + '!new_label!' + '''') | Set-Content 'src\consts.ts' -NoNewline"
        echo ✅ 文章标签已改为：!new_label!
    )
)
if "!edit_idx!"=="3" (
    set /p "new_label=输入新标签名（当前：关于）: "
    if not "!new_label!"=="" (
        powershell -NoProfile -Command "(Get-Content 'src\consts.ts' -Raw) -replace '(href:\s*''/about''[^}]*label:\s*'')[^'']*', ('''' + '!new_label!' + '''') | Set-Content 'src\consts.ts' -NoNewline"
        echo ✅ 关于标签已改为：!new_label!
    )
)
echo.
echo ⚠️  别忘了发布才能线上生效（双击 publish.bat）
pause
exit /b 0

:: ==================== 5. 修改关于页联系方式 ====================
:edit_about
echo.
echo 📋 关于页的联系方式写在 src/pages/about.astro 里：
echo.
echo   当前联系方式：
echo     GitHub: https://github.com/zhichengZC
echo     Email:  hello@example.com
echo     RSS:    /rss.xml
echo.
echo  ┌──────────────────────────────────┐
echo  │  a) 修改 GitHub 链接             │
echo  │  b) 修改 Email 地址              │
echo  │  c) 修改个人签名 / 副标题        │
echo  │  0) 返回                        │
echo  └──────────────────────────────────┘
echo.
set "about_choice="
set /p "about_choice=👉 请选择 (a/b/c/0): "

if /i "!about_choice!"=="a" goto :about_github
if /i "!about_choice!"=="b" goto :about_email
if /i "!about_choice!"=="c" goto :about_tagline
if /i "!about_choice!"=="0" goto :eof
echo [x] 无效选择。
pause
exit /b 1

:about_github
echo.
set "new_github="
set /p "new_github=输入新 GitHub 链接（直接回车取消）: "
if "!new_github!"=="" ( echo 已取消。 & pause & exit /b 0 )
powershell -NoProfile -Command "(Get-Content 'src\pages\about.astro' -Raw) -replace 'https://github\.com/[^\"'']*', '!new_github!' | Set-Content 'src\pages\about.astro' -NoNewline"
echo ✅ GitHub 链接已更新为：!new_github!
echo ⚠️  别忘了发布才能线上生效（双击 publish.bat）
pause
exit /b 0

:about_email
echo.
set "new_email="
set /p "new_email=输入新 Email 地址（直接回车取消）: "
if "!new_email!"=="" ( echo 已取消。 & pause & exit /b 0 )
powershell -NoProfile -Command "(Get-Content 'src\pages\about.astro' -Raw) -replace 'mailto:[^\"'']*', ('mailto:' + '!new_email!') | Set-Content 'src\pages\about.astro' -NoNewline"
echo ✅ Email 已更新为：!new_email!
echo ⚠️  别忘了发布才能线上生效（双击 publish.bat）
pause
exit /b 0

:about_tagline
echo.
echo 📝 当前签名："a quiet notebook for slow thoughts."
echo.
set "new_tagline="
set /p "new_tagline=输入新签名（英文，直接回车取消）: "
if "!new_tagline!"=="" ( echo 已取消。 & pause & exit /b 0 )
powershell -NoProfile -Command "(Get-Content 'src\pages\about.astro' -Raw) -replace 'a quiet notebook for slow thoughts\.', '!new_tagline!.' | Set-Content 'src\pages\about.astro' -NoNewline"
echo ✅ 签名已更新为：!new_tagline!.
echo ⚠️  别忘了发布才能线上生效（双击 publish.bat）
pause
exit /b 0

endlocal
