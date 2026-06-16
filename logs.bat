@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 显示实时日志，按 Ctrl+C 退出...
echo ============================================
docker-compose logs -f
