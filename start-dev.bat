@echo off
chcp 65001 >nul
cd /d "%~dp0"
title ZhichengBlog Dev Server

echo.
echo ================================================
echo    ZhichengBlog Local Dev Server
echo ================================================
echo.
echo Project path: %cd%
echo.
echo Starting dev server, please wait...
echo After startup, open in browser: http://localhost:4321
echo.
echo Press Ctrl+C to stop the server
echo ================================================
echo.

call npm run dev

echo.
echo Server stopped
pause
