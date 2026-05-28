#!/bin/bash
set -e

echo "=== 运行后端测试 ==="
cd backend

echo "安装依赖..."
pip install -r requirements.txt

echo "运行数据库迁移..."
python manage.py migrate

echo "运行单元测试..."
python manage.py test apps.users.tests apps.projects.tests apps.testcases.tests apps.executions.tests apps.reports.tests --verbosity=2

echo "=== 后端测试完成 ==="

cd ..

echo "=== 运行前端测试 ==="
cd frontend

echo "安装依赖..."
npm install

echo "运行前端测试..."
npm run test:run

echo "=== 前端测试完成 ==="

cd ..

echo "=== 运行前端构建 ==="
cd frontend
npm run build

echo "=== 前端构建完成 ==="

echo "=== 所有测试通过 ==="