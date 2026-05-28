# AI 测试平台

基于 Django + Vue 3 的测试管理平台，提供完整的测试管理闭环：项目、用例、计划、执行、结果、报告和 Dashboard。

## ✨ 功能特性

- **用户管理**：支持 admin、tester、viewer 三种角色
- **项目管理**：项目的创建、编辑、删除和权限控制
- **测试用例**：支持步骤、预期结果、优先级管理
- **测试计划**：用例的批量添加和管理
- **测试执行**：执行记录创建、状态管理、结果录入
- **测试报告**：Allure 报告集成，支持同步/异步生成
- **Dashboard**：核心数据统计和趋势展示
- **数据导入导出**：支持 Excel/JSON 格式

## 🛠️ 技术栈

| 层面 | 技术 |
|------|------|
| 后端 | Python 3.10+ / Django 4.2 / DRF |
| 前端 | Vue 3 / Vite / Element Plus / Pinia |
| 数据库 | SQLite（开发）/ MySQL（生产） |
| 缓存/任务 | Redis / Celery |
| 认证 | JWT |

## 📋 环境要求

- Windows / Linux / macOS
- Python 3.10+
- Node.js 18 LTS+
- Redis 6.0+（可选，用于异步任务）

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd AiTestPlantForm
```

### 2. 配置后端

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r .\backend\requirements.txt
Copy-Item .\.env.example .\.env
.\.venv\Scripts\python.exe .\backend\manage.py migrate
.\.venv\Scripts\python.exe .\backend\manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123')"
```

### 3. 启动服务

**后端：**
```powershell
.\.venv\Scripts\python.exe .\backend\manage.py runserver 127.0.0.1:8000
```

**前端：**
```powershell
cd frontend
npm install
npm run dev
```

**Celery Worker（可选）：**
```powershell
docker-compose -f docker-compose.dev.yml up -d
.\.venv\Scripts\celery.exe -A tasks.celery worker -l info
```

### 4. Docker 部署

```bash
docker-compose up -d --build
docker exec -it aitest-backend python manage.py migrate
```

## 🌐 访问地址

| 服务 | URL |
|------|-----|
| 前端 | http://localhost:5173 |
| 后端 | http://localhost:8000 |
| API 文档 | http://localhost:8000/api/docs/ |
| Django Admin | http://localhost:8000/admin/ |

## 📁 项目结构

```
AiTestPlantForm/
├── backend/              # 后端服务
│   ├── apps/             # 业务模块
│   ├── core/             # 公共模块
│   ├── config/           # Django 配置
│   └── tasks/            # Celery 任务
├── frontend/             # 前端应用
│   └── src/              # 源代码
├── scripts/              # 脚本文件
├── design.md             # 设计文档
├── develop.md            # 开发计划
└── README.md
```

## 🔧 配置说明

### 数据库切换

在 `.env` 文件中设置：
```env
# SQLite（默认）
DB_ENGINE=sqlite

# MySQL
DB_ENGINE=mysql
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_DATABASE=aitest_platform
MYSQL_USER=aitest
MYSQL_PASSWORD=aitest_password
```

### Redis 配置

```env
REDIS_URL=redis://127.0.0.1:6379/0
```

## 📝 测试运行

```bash
# 后端测试
cd backend
python manage.py test

# 前端构建
cd frontend
npm run build
```

## 🔐 默认账号

- 用户名：`admin`
- 密码：`admin123`

## 📄 相关文档

- [`design.md`](./design.md) - 设计文档
- [`develop.md`](./develop.md) - 开发计划

---

**注意**：`.env` 文件包含敏感信息，不应提交到仓库。