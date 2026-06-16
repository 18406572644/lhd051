@echo off
chcp 65001 >nul
echo ============================================
echo    花语集 - 干花标本管理系统 Docker 启动脚本
echo ============================================
echo.

echo [1/3] 检查 Docker 是否运行...
docker version >nul 2>&1
if errorlevel 1 (
    echo [错误] Docker 未运行！请先启动 Docker Desktop。
    pause
    exit /b 1
)
echo [OK] Docker 运行中
echo.

echo [2/3] 构建并启动容器...
cd /d "%~dp0"
docker-compose up -d --build
if errorlevel 1 (
    echo [错误] 启动失败，请检查日志。
    pause
    exit /b 1
)
echo.

echo [3/3] 等待服务就绪...
timeout /t 5 /nobreak >nul
echo.

echo ============================================
echo   服务启动完成！
echo ============================================
echo   前端访问地址:
echo   - 本地: http://localhost:2051
echo   - 本机IP: http://127.0.0.1:2051
echo.
echo   后端 API:
echo   - 本地: http://localhost:6051
echo   - 健康检查: http://localhost:6051/api/health
echo ============================================
echo.
echo  提示: 运行 stop.bat 可停止服务
echo ============================================
pause
