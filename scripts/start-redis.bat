@echo off
REM Redis 启动脚本
REM 用于Windows环境下的Redis服务管理

set REDIS_DIR=%REDIS_HOME%
if "%REDIS_DIR%"=="" set "REDIS_DIR=C:\Program Files\Redis"

set REDIS_SERVER=%REDIS_DIR%\redis-server.exe
set REDIS_CLI=%REDIS_DIR%\redis-cli.exe

if "%1"=="" goto usage
if "%1"=="start" goto start
if "%1"=="stop" goto stop
if "%1"=="status" goto status
if "%1"=="restart" goto restart
goto usage

:start
echo Starting Redis server...
if exist "%REDIS_SERVER%" (
    "%REDIS_SERVER%" --service-install
    "%REDIS_SERVER%" --service-start
    echo Redis server started on redis://127.0.0.1:6379
) else (
    echo Redis server not found at %REDIS_SERVER%
    echo Please install Redis from: https://github.com/microsoftarchive/redis/releases
    exit /b 1
)
goto end

:stop
echo Stopping Redis server...
if exist "%REDIS_SERVER%" (
    "%REDIS_SERVER%" --service-stop
    "%REDIS_SERVER%" --service-uninstall
    echo Redis server stopped
)
goto end

:status
if exist "%REDIS_CLI%" (
    "%REDIS_CLI%" ping
) else (
    echo Redis CLI not found
    exit /b 1
)
goto end

:restart
call :stop
call :start
goto end

:usage
echo Usage: start-redis.bat {start^|stop^|status^|restart}
exit /b 1

:end
