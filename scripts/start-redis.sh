#!/bin/bash

# Redis 启动脚本
# 用于Windows环境下的Redis服务管理

REDIS_DIR="${REDIS_HOME:-C:\Program Files\Redis}"
REDIS_SERVER="$REDIS_DIR\redis-server.exe"
REDIS_CLI="$REDIS_DIR\redis-cli.exe"

start_redis() {
    if [ -f "$REDIS_SERVER" ]; then
        echo "Starting Redis server..."
        "$REDIS_SERVER" --service-install
        "$REDIS_SERVER" --service-start
        echo "Redis server started on redis://127.0.0.1:6379"
    else
        echo "Redis server not found at $REDIS_SERVER"
        echo "Please install Redis from: https://github.com/microsoftarchive/redis/releases"
        exit 1
    fi
}

stop_redis() {
    echo "Stopping Redis server..."
    "$REDIS_SERVER" --service-stop
    "$REDIS_SERVER" --service-uninstall
    echo "Redis server stopped"
}

status_redis() {
    if [ -f "$REDIS_CLI" ]; then
        "$REDIS_CLI" ping
    else
        echo "Redis CLI not found"
        exit 1
    fi
}

case "$1" in
    start)
        start_redis
        ;;
    stop)
        stop_redis
        ;;
    status)
        status_redis
        ;;
    restart)
        stop_redis
        start_redis
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart}"
        exit 1
        ;;
esac
