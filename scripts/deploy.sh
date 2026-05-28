#!/bin/bash
set -e

ENV=${1:-production}
COMPOSE_FILE="docker-compose.prod.yml"

echo "=== 部署到 ${ENV} 环境 ==="

echo "停止现有服务..."
docker-compose -f ${COMPOSE_FILE} down

echo "拉取最新代码..."
git pull origin main

echo "构建并启动服务..."
docker-compose -f ${COMPOSE_FILE} up -d --build

echo "等待服务启动..."
sleep 30

echo "检查服务状态..."
docker-compose -f ${COMPOSE_FILE} ps

echo "=== 部署完成 ==="