@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo =========================================
echo    ✏️  纸橙的动画小屋 · 页面内容编辑器
echo =========================================
echo.

:: ---------- 菜单 ----------
echo  可编辑的页面：
echo.
echo  ┌──────────────────────────────────────────┐
echo  │  1️⃣  首页 Hero 文案                      │
echo  │  2️⃣  关于页 · 个人介绍                    │
echo  │  3️⃣  关于页 · 联系方式（GitHub/Email）    │
echo  │  4️⃣  关于页 · 正在做的事（Now）           │
echo  │  5️⃣  关于页 · 技术栈（Stack）             │
echo  │  6️⃣  页脚 · 版权/签名                     │
echo  │  0️⃣  退出                                │
echo  └──────────────────────────────────────────┘
echo.
set "choice="
set /p "choice=👉 请选择操作 (0-6): "

if "!choice!"=="1" goto :edit_hero
if "!choice!"=="2" goto :edit_about_intro
if "!choice!"=="3" goto :edit_about_contact
if "!choice!"=="4" goto :edit_about_now
if "!choice!"=="5" goto :edit_about_stack
if "!choice!"=="6" goto :edit_footer
if "!choice!"=="0" goto :eof
echo.
echo [x] 无效选择。
pause
exit /b 1


:: ==================== 1. 首页 Hero 文案 ====================
:edit_hero
echo.
echo 📋 首页 Hero 文案在 src/pages/index.astro 里：
echo.
echo    大标题："A quiet, warm notebook for slow thoughts."
echo    副标题："欢迎来到 纸橙的动画小屋。这里记录动画、技术，以及一些值得慢下来想一想的事。"
echo.
echo  ┌──────────────────────────────────────────┐
echo  │  a) 修改大标题                          │
echo  │  b) 修改副标题（lede）                   │
echo  │  0) 返回                                │
echo  └──────────────────────────────────────────┘
echo.
set "hero_choice="
set /p "hero_choice=👉 请选择 (a/b/0): "

if /i "!hero_choice!"=="a" goto :edit_hero_title
if /i "!hero_choice!"=="b" goto :edit_hero_lede
if /i "!hero_choice!"=="0" goto :eof
echo [x] 无效选择。
pause
exit /b 1

:edit_hero_title
echo.
echo 📝 当前大标题："A quiet, warm notebook for slow thoughts."
echo.
set "new_title="
set /p "new_title=输入新标题（英文，直接回车取消）: "
if "!new_title!"=="" ( echo 已取消。 & pause & exit /b 0 )

powershell -NoProfile -Command "(Get-Content 'src\pages\index.astro' -Raw) -replace 'A quiet, warm\s+notebook for slow thoughts\.', '!new_title!.' | Set-Content 'src\pages\index.astro' -NoNewline"
echo.
echo ✅ 大标题已更新为：!new_title!.
echo.
echo ⚠️  别忘了：
echo     1. 双击 start-dev.bat 本地预览确认
echo     2. 双击 publish.bat 发布到线上
echo.
pause
exit /b 0

:edit_hero_lede
echo.
echo 📝 当前副标题：
echo    "欢迎来到 纸橙的动画小屋。这里记录动画、技术，以及一些值得慢下来想一想的事。"
echo.
set "new_lede="
set /p "new_lede=输入新副标题（中文，直接回车取消）: "
if "!new_lede!"=="" ( echo 已取消。 & pause & exit /b 0 )

powershell -NoProfile -Command "(Get-Content 'src\pages\index.astro' -Raw) -replace '欢迎来到 <span[^>]*>纸橙的动画小屋</span>。这里记录动画、技术，以及一些值得慢下来想一想的事。', '!new_lede!' | Set-Content 'src\pages\index.astro' -NoNewline"
echo.
echo ✅ 副标题已更新。
echo.
echo ⚠️  别忘了本地预览 + 发布。
echo.
pause
exit /b 0


:: ==================== 2. 关于页个人介绍 ====================
:edit_about_intro
echo.
echo 📋 关于页个人介绍在 src/pages/about.astro 里：
echo.
echo    "一名技术动画实习生。对我来说，动画不只是让角色动起来——
echo     每一帧里藏着物理、曲线、情绪和意图。"
echo.
echo    "最近在学 Transformer 和 Motion Matching 的底层原理，
echo     也在看 AI 和动画怎么结合。这里是我慢慢记下这些想法的地方。"
echo.
echo  ┌──────────────────────────────────────────┐
echo  │  a) 修改第一段介绍                      │
echo  │  b) 修改第二段介绍                      │
echo  │  0) 返回                                │
echo  └──────────────────────────────────────────┘
echo.
set "intro_choice="
set /p "intro_choice=👉 请选择 (a/b/0): "

if /i "!intro_choice!"=="a" goto :edit_intro_p1
if /i "!intro_choice!"=="b" goto :edit_intro_p2
if /i "!intro_choice!"=="0" goto :eof
echo [x] 无效选择。
pause
exit /b 1

:edit_intro_p1
echo.
set "new_p1="
set /p "new_p1=输入新第一段（中文，直接回车取消）: "
if "!new_p1!"=="" ( echo 已取消。 & pause & exit /b 0 )

powershell -NoProfile -Command ^
"$c = Get-Content 'src\pages\about.astro' -Raw; " ^
"$c = $c -replace '一名技术动画实习生[^。]*。', '!new_p1!'; " ^
"Set-Content 'src\pages\about.astro' -Value $c -NoNewline"

echo.
echo ✅ 第一段已更新。
echo.
echo ⚠️  别忘了本地预览 + 发布。
echo.
pause
exit /b 0

:edit_intro_p2
echo.
set "new_p2="
set /p "new_p2=输入新第二段（中文，直接回车取消）: "
if "!new_p2!"=="" ( echo 已取消。 & pause & exit /b 0 )

powershell -NoProfile -Command ^
"$c = Get-Content 'src\pages\about.astro' -Raw; " ^
"$c = $c -replace '最近在学 Transformer[^。]*。', '!new_p2!'; " ^
"Set-Content 'src\pages\about.astro' -Value $c -NoNewline"

echo.
echo ✅ 第二段已更新。
echo.
echo ⚠️  别忘了本地预览 + 发布。
echo.
pause
exit /b 0


:: ==================== 3. 关于页联系方式 ====================
:edit_about_contact
echo.
echo 📋 当前联系方式（来自 src/pages/about.astro）：
echo.
echo    GitHub: https://github.com/zhichengZC
echo    Email:  hello@example.com
echo.
echo  ┌──────────────────────────────────────────┐
echo  │  a) 修改 GitHub 链接                    │
echo  │  b) 修改 Email 地址                     │
echo  │  c) 修改个人签名（a quiet notebook...） │
echo  │  0) 返回                                │
echo  └──────────────────────────────────────────┘
echo.
set "contact_choice="
set /p "contact_choice=👉 请选择 (a/b/c/0): "

if /i "!contact_choice!"=="a" goto :contact_github
if /i "!contact_choice!"=="b" goto :contact_email
if /i "!contact_choice!"=="c" goto :contact_tagline
if /i "!contact_choice!"=="0" goto :eof
echo [x] 无效选择。
pause
exit /b 1

:contact_github
echo.
set "new_gh="
set /p "new_gh=输入新 GitHub 链接（直接回车取消）: "
if "!new_gh!"=="" ( echo 已取消。 & pause & exit /b 0 )

powershell -NoProfile -Command "(Get-Content 'src\pages\about.astro' -Raw) -replace 'https://github\.com/[^\"''<\s]+', '!new_gh!' | Set-Content 'src\pages\about.astro' -NoNewline"
echo ✅ GitHub 链接已更新为：!new_gh!
echo ⚠️  别忘了本地预览 + 发布。
pause
exit /b 0

:contact_email
echo.
set "new_em="
set /p "new_em=输入新 Email 地址（直接回车取消）: "
if "!new_em!"=="" ( echo 已取消。 & pause & exit /b 0 )

powershell -NoProfile -Command "(Get-Content 'src\pages\about.astro' -Raw) -replace 'mailto:[^\"''<\s]+', ('mailto:' + '!new_em!') | Set-Content 'src\pages\about.astro' -NoNewline"
echo ✅ Email 已更新为：!new_em!
echo ⚠️  别忘了本地预览 + 发布。
pause
exit /b 0

:contact_tagline
echo.
echo 📝 当前签名："a quiet notebook for slow thoughts."
echo.
set "new_tag="
set /p "new_tag=输入新签名（英文，直接回车取消）: "
if "!new_tag!"=="" ( echo 已取消。 & pause & exit /b 0 )

powershell -NoProfile -Command "(Get-Content 'src\pages\about.astro' -Raw) -replace 'a quiet notebook for slow thoughts\.', '!new_tag!.' | Set-Content 'src\pages\about.astro' -NoNewline"
echo ✅ 签名已更新为：!new_tag!.
echo ⚠️  别忘了本地预览 + 发布。
pause
exit /b 0


:: ==================== 4. 正在做的事（Now） ====================
:edit_about_now
echo.
echo 📋 当前 "Now" 项目（来自 src/pages/about.astro）：
echo.
echo   Learning:  Transformer / Attention 底层机制
echo   Building:  技术动画管线与 AI 生成 demo
echo   Playing:   ARC Raiders · Elden Ring
echo   Reading:   Character Animation with Direct3D
echo.
echo  ┌──────────────────────────────────────────┐
echo  │  a) 修改 Learning 项                    │
echo  │  b) 修改 Building 项                    │
echo  │  c) 修改 Playing 项                     │
echo  │  d) 修改 Reading 项                     │
echo  │  0) 返回                                │
echo  └──────────────────────────────────────────┘
echo.
set "now_choice="
set /p "now_choice=👉 请选择 (a/b/c/d/0): "

if /i "!now_choice!"=="a" goto :now_learning
if /i "!now_choice!"=="b" goto :now_building
if /i "!now_choice!"=="c" goto :now_playing
if /i "!now_choice!"=="d" goto :now_reading
if /i "!now_choice!"=="0" goto :eof
echo [x] 无效选择。
pause
exit /b 1

:now_learning
echo.
set "new_val="
set /p "new_val=输入新 Learning 内容（直接回车取消）: "
if "!new_val!"=="" ( echo 已取消。 & pause & exit /b 0 )

powershell -NoProfile -Command "(Get-Content 'src\pages\about.astro' -Raw) -replace '(?<=''Learning'',?\s*value:\s*'')[^'']*', '!new_val!' | Set-Content 'src\pages\about.astro' -NoNewline"
echo ✅ Learning 已更新。
echo ⚠️  别忘了本地预览 + 发布。
pause
exit /b 0

:now_building
echo.
set "new_val="
set /p "new_val=输入新 Building 内容（直接回车取消）: "
if "!new_val!"=="" ( echo 已取消。 & pause & exit /b 0 )

powershell -NoProfile -Command "(Get-Content 'src\pages\about.astro' -Raw) -replace '(?<=''Building'',?\s*value:\s*'')[^'']*', '!new_val!' | Set-Content 'src\pages\about.astro' -NoNewline"
echo ✅ Building 已更新。
echo ⚠️  别忘了本地预览 + 发布。
pause
exit /b 0

:now_playing
echo.
set "new_val="
set /p "new_val=输入新 Playing 内容（直接回车取消）: "
if "!new_val!"=="" ( echo 已取消。 & pause & exit /b 0 )

powershell -NoProfile -Command "(Get-Content 'src\pages\about.astro' -Raw) -replace '(?<=''Playing'',?\s*value:\s*'')[^'']*', '!new_val!' | Set-Content 'src\pages\about.astro' -NoNewline"
echo ✅ Playing 已更新。
echo ⚠️  别忘了本地预览 + 发布。
pause
exit /b 0

:now_reading
echo.
set "new_val="
set /p "new_val=输入新 Reading 内容（直接回车取消）: "
if "!new_val!"=="" ( echo 已取消。 & pause & exit /b 0 )

powershell -NoProfile -Command "(Get-Content 'src\pages\about.astro' -Raw) -replace '(?<=''Reading'',?\s*value:\s*'')[^'']*', '!new_val!' | Set-Content 'src\pages\about.astro' -NoNewline"
echo ✅ Reading 已更新。
echo ⚠️  别忘了本地预览 + 发布。
pause
exit /b 0


:: ==================== 5. 技术栈（Stack） ====================
:edit_about_stack
echo.
echo 📋 当前技术栈（来自 src/pages/about.astro）：
echo.
echo   Tools:    Unreal, Unity, Blender, Maya
echo   Code:     Python · PyTorch, C++ · C#, TypeScript
echo   Research: Transformer, Motion Matching, PFNN, Diffusion
echo   Writing:  Astro, Tailwind, Markdown, Obsidian
echo.
echo  ┌──────────────────────────────────────────┐
echo  │  a) 修改 Tools 列表                     │
echo  │  b) 修改 Code 列表                      │
echo  │  c) 修改 Research 列表                   │
echo  │  d) 修改 Writing 列表                    │
echo  │  0) 返回                                │
echo  └──────────────────────────────────────────┘
echo.
set "stack_choice="
set /p "stack_choice=👉 请选择 (a/b/c/d/0): "

if /i "!stack_choice!"=="a" goto :stack_tools
if /i "!stack_choice!"=="b" goto :stack_code
if /i "!stack_choice!"=="c" goto :stack_research
if /i "!stack_choice!"=="d" goto :stack_writing
if /i "!stack_choice!"=="0" goto :eof
echo [x] 无效选择。
pause
exit /b 1

:stack_tools
echo.
set "new_val="
set /p "new_val=输入新 Tools 列表（逗号分隔，直接回车取消）: "
if "!new_val!"=="" ( echo 已取消。 & pause & exit /b 0 )

powershell -NoProfile -Command ^
"$c = Get-Content 'src\pages\about.astro' -Raw; " ^
"$items = '!new_val!' -split ',' | ForEach-Object { $_.Trim() }; " ^
"$newItems = ($items | ForEach-Object { \"'$_'\" }) -join ', '; " ^
"$c = $c -replace '(?<=''Tools'',?\s*items:\s*\[)[^\]]*', $newItems; " ^
"Set-Content 'src\pages\about.astro' -Value $c -NoNewline"

echo ✅ Tools 已更新。
echo ⚠️  别忘了本地预览 + 发布。
pause
exit /b 0

:stack_code
echo.
set "new_val="
set /p "new_val=输入新 Code 列表（逗号分隔，直接回车取消）: "
if "!new_val!"=="" ( echo 已取消。 & pause & exit /b 0 )

powershell -NoProfile -Command ^
"$c = Get-Content 'src\pages\about.astro' -Raw; " ^
"$items = '!new_val!' -split ',' | ForEach-Object { $_.Trim() }; " ^
"$newItems = ($items | ForEach-Object { \"'$_'\" }) -join ', '; " ^
"$c = $c -replace '(?<=''Code'',?\s*items:\s*\[)[^\]]*', $newItems; " ^
"Set-Content 'src\pages\about.astro' -Value $c -NoNewline"

echo ✅ Code 已更新。
echo ⚠️  别忘了本地预览 + 发布。
pause
exit /b 0

:stack_research
echo.
set "new_val="
set /p "new_val=输入新 Research 列表（逗号分隔，直接回车取消）: "
if "!new_val!"=="" ( echo 已取消。 & pause & exit /b 0 )

powershell -NoProfile -Command ^
"$c = Get-Content 'src\pages\about.astro' -Raw; " ^
"$items = '!new_val!' -split ',' | ForEach-Object { $_.Trim() }; " ^
"$newItems = ($items | ForEach-Object { \"'$_'\" }) -join ', '; " ^
"$c = $c -replace '(?<=''Research'',?\s*items:\s*\[)[^\]]*', $newItems; " ^
"Set-Content 'src\pages\about.astro' -Value $c -NoNewline"

echo ✅ Research 已更新。
echo ⚠️  别忘了本地预览 + 发布。
pause
exit /b 0

:stack_writing
echo.
set "new_val="
set /p "new_val=输入新 Writing 列表（逗号分隔，直接回车取消）: "
if "!new_val!"=="" ( echo 已取消。 & pause & exit /b 0 )

powershell -NoProfile -Command ^
"$c = Get-Content 'src\pages\about.astro' -Raw; " ^
"$items = '!new_val!' -split ',' | ForEach-Object { $_.Trim() }; " ^
"$newItems = ($items | ForEach-Object { \"'$_'\" }) -join ', '; " ^
"$c = $c -replace '(?<=''Writing'',?\s*items:\s*\[)[^\]]*', $newItems; " ^
"Set-Content 'src\pages\about.astro' -Value $c -NoNewline"

echo ✅ Writing 已更新。
echo ⚠️  别忘了本地预览 + 发布。
pause
exit /b 0


:: ==================== 6. 页脚版权/签名 ====================
:edit_footer
echo.
echo 📋 当前页脚（来自 src/components/Footer.astro）：
echo.
echo    作者名：纸橙（来自 src/consts.ts 的 SITE_AUTHOR）
echo    签名：  "a quiet notebook for slow thoughts."
echo    引擎：  "Built with Astro · Read slowly"
echo.
echo  ┌──────────────────────────────────────────┐
echo  │  a) 修改页脚签名（a quiet notebook...） │
echo  │  b) 修改 "Built with Astro" 后面的标语  │
echo  │  0) 返回                                │
echo  └──────────────────────────────────────────┘
echo.
set "foot_choice="
set /p "foot_choice=👉 请选择 (a/b/0): "

if /i "!foot_choice!"=="a" goto :foot_tagline
if /i "!foot_choice!"=="b" goto :foot_slogan
if /i "!foot_choice!"=="0" goto :eof
echo [x] 无效选择。
pause
exit /b 1

:foot_tagline
echo.
set "new_tag="
set /p "new_tag=输入新签名（英文，直接回车取消）: "
if "!new_tag!"=="" ( echo 已取消。 & pause & exit /b 0 )

powershell -NoProfile -Command "(Get-Content 'src\components\Footer.astro' -Raw) -replace 'a quiet notebook for slow thoughts\.', '!new_tag!.' | Set-Content 'src\components\Footer.astro' -NoNewline"
echo ✅ 页脚签名已更新。
echo ⚠️  别忘了本地预览 + 发布。
pause
exit /b 0

:foot_slogan
echo.
set "new_slg="
set /p "new_slg=输入新标语（英文，直接回车取消）: "
if "!new_slg!"=="" ( echo 已取消。 & pause & exit /b 0 )

powershell -NoProfile -Command "(Get-Content 'src\components\Footer.astro' -Raw) -replace 'Read slowly', '!new_slg!' | Set-Content 'src\components\Footer.astro' -NoNewline"
echo ✅ 页脚标语已更新。
echo ⚠️  别忘了本地预览 + 发布。
pause
exit /b 0


endlocal
