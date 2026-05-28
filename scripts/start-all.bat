@echo off
REM 项目服务启动脚本
REM 启动后端服务、Celery Worker 和前端开发服务器

echo ============================================
echo   AI Test Platform - 服务启动脚本
echo ============================================
echo.

REM 检查 Redis 是否运行
echo [1/4] 检查 Redis 服务...
redis-cli ping >nul 2>&1
if %errorlevel% neq 0 (
    echo   WARNING: Redis 未运行
    echo   如果需要异步报告生成功能，请先启动 Redis:
    echo   powershell .\scripts\start-redis.ps1 start
    echo.
    echo   或者启用 Eager 模式（在 .env 中设置 CELERY_TASK_ALWAYS_EAGER=True）
    echo.
)

REM 启动后端服务
echo [2/4] 启动后端服务 (Django)...
start "Django Backend" cmd /k "cd /d %~dp0backend && python manage.py runserver 127.0.0.1:8000"

REM 等待后端启动
timeout /t 3 /nobreak >nul

REM 启动 Celery Worker（如果 Redis 可用）
echo [3/4] 启动 Celery Worker...
start "Celery Worker" cmd /k "cd /d %~dp0backend && celery -A tasks.celery worker --loglevel=info"

REM 启动前端开发服务器
echo [4/4] 启动前端服务 (Vite)...
cd /d %~dp0frontend
start "Frontend" cmd /k "npm run dev"

cd /d %~dp0

echo.
echo ============================================
echo   所有服务已启动！
echo ============================================
echo.
echo   - 后端服务: http://127.0.0.1:8000
echo   - 前端服务: http://127.0.0.1:5173 (或 5174)
echo   - API 文档: http://127.0.0.1:8000/api/docs/
echo   - Django Admin: http://127.0.0.1:8000/admin/
echo.
echo   按任意键退出此窗口...
pause >nul
