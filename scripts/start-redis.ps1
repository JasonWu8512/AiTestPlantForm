# Redis 启动脚本
# 用于Windows环境下的Redis服务管理

param(
    [Parameter(Position=0)]
    [ValidateSet("start", "stop", "status", "restart")]
    [string]$Action = "start"
)

$REDIS_DIR = $env:REDIS_HOME
if (-not $REDIS_DIR) {
    $REDIS_DIR = "C:\Program Files\Redis"
}

$REDIS_SERVER = Join-Path $REDIS_DIR "redis-server.exe"
$REDIS_CLI = Join-Path $REDIS_DIR "redis-cli.exe"

function Start-RedisServer {
    if (Test-Path $REDIS_SERVER) {
        Write-Host "Starting Redis server..."
        & $REDIS_SERVER --service-install
        & $REDIS_SERVER --service-start
        Write-Host "Redis server started on redis://127.0.0.1:6379"
    } else {
        Write-Host "Redis server not found at $REDIS_SERVER"
        Write-Host "Please install Redis from: https://github.com/microsoftarchive/redis/releases"
        exit 1
    }
}

function Stop-RedisServer {
    Write-Host "Stopping Redis server..."
    if (Test-Path $REDIS_SERVER) {
        & $REDIS_SERVER --service-stop
        & $REDIS_SERVER --service-uninstall
        Write-Host "Redis server stopped"
    }
}

function Get-RedisStatus {
    if (Test-Path $REDIS_CLI) {
        & $REDIS_CLI ping
    } else {
        Write-Host "Redis CLI not found at $REDIS_CLI"
        exit 1
    }
}

switch ($Action) {
    "start" { Start-RedisServer }
    "stop" { Stop-RedisServer }
    "status" { Get-RedisStatus }
    "restart" {
        Stop-RedisServer
        Start-RedisServer
    }
}
