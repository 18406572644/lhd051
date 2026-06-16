@echo off
chcp 65001 >nul
echo ============================================
echo    花语集 - 重启 Docker 服务
echo ============================================
echo.

cd /d "%~dp0"
echo 正在重启服务...
docker-compose down
echo.
echo 重新构建并启动...
docker-compose up -d --build
echo.
timeout /t 5 /nobreak >nul
echo.
echo ============================================
echo   服务重启完成！
echo   前端: http://localhost:2051
echo   后端: http://localhost:6051
echo ============================================
pause
