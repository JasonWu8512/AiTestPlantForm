# AI 测试平台

本项目是一个基于 Django + Vue 3 的测试管理平台。一期先完成测试管理闭环：项目、用例、计划、执行、结果、报告和 Dashboard。

## 一期功能

- 用户登录与用户管理（支持 admin、tester、viewer 三种角色）
- 项目管理
- 测试用例管理（支持步骤、预期结果、优先级）
- 测试计划管理（支持添加/移除用例）
- 测试执行管理（支持开始、取消、结果录入）
- 测试报告查看（Allure 报告入口）
- Dashboard 数据概览

## 技术栈

| 层面 | 技术 |
|------|------|
| 后端 | Python 3.10+ / Django 4.2 / Django REST Framework |
| 前端 | Vue 3 / Vite / Element Plus / Pinia |
| 数据库 | SQLite（开发）/ MySQL（生产） |
| 缓存/任务 | Redis / Celery |
| 认证 | JWT |

## 环境要求

- Windows
- Python 3.10+
- Node.js 18 LTS 或 20 LTS
- Yarn 1.22+ 或 npm
- MySQL 8.0+（可选）
- Redis 6.0+（可选，用于 Celery）

## 快速启动

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

### 3. 启动后端服务

```powershell
.\.venv\Scripts\python.exe .\backend\manage.py runserver 127.0.0.1:8000
```

### 4. 启动前端服务

```powershell
cd frontend
npm install
npm run dev
```

### 5. 启动 Celery Worker（可选）

```powershell
docker-compose -f docker-compose.dev.yml up -d
.\.venv\Scripts\celery.exe -A tasks.celery worker -l info
```

## 访问地址

| 服务 | URL |
|------|-----|
| 前端 | http://localhost:5173 |
| 后端 | http://localhost:8000 |
| API文档 | http://localhost:8000/api/docs/ |
| Django Admin | http://localhost:8000/admin/ |

## 项目结构

```
AiTestPlantForm/
├── backend/
│   ├── apps/
│   │   ├── users/        # 用户管理
│   │   ├── projects/     # 项目管理
│   │   ├── testcases/    # 测试用例
│   │   ├── testplans/    # 测试计划
│   │   ├── executions/   # 测试执行
│   │   ├── reports/      # 测试报告
│   │   └── dashboard/    # Dashboard
│   ├── core/             # 公共模块
│   ├── config/           # Django 配置
│   └── tasks/            # Celery 任务
├── frontend/
│   ├── src/
│   │   ├── api/          # API 请求封装
│   │   ├── components/   # 公共组件
│   │   ├── router/       # 路由配置
│   │   ├── stores/       # Pinia 状态管理
│   │   └── views/        # 页面组件
│   └── vite.config.js
├── design.md             # 设计文档
├── develop.md            # 开发计划
└── README.md
```

## Docker 部署

### 完整 Docker 部署

```bash
cd d:\Work\Projects\AiTestPlantForm
docker-compose up -d --build
docker exec -it aitest-backend python manage.py migrate
```

### 本地开发模式

```bash
docker-compose -f docker-compose.dev.yml up -d
cd backend && python manage.py runserver
cd frontend && npm run dev
```

### Docker 常用命令

```bash
docker-compose ps
docker-compose logs -f backend
docker-compose stop
docker-compose restart
```

## 数据库配置

### 使用 SQLite（默认）

在 `.env` 中设置：
```env
DB_ENGINE=sqlite
```

### 使用 MySQL

在 `.env` 中设置：
```env
DB_ENGINE=mysql
MYSQL_HOST=mysql
MYSQL_PORT=3306
MYSQL_DATABASE=aitest_platform
MYSQL_USER=aitest
MYSQL_PASSWORD=aitest_password
```

## Redis 配置

```env
REDIS_URL=redis://127.0.0.1:6379/0
```

### 启动 Redis

```bash
docker-compose -f docker-compose.dev.yml up -d redis
```

## API 接口

### 认证接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/login/` | 用户登录 |
| POST | `/api/auth/logout/` | 用户登出 |
| POST | `/api/auth/refresh/` | 刷新 Token |
| GET | `/api/auth/me/` | 获取当前用户 |

### 业务接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/projects/` | 项目列表/创建 |
| GET/PUT/DELETE | `/api/projects/{id}/` | 项目详情/更新/删除 |
| GET/POST | `/api/testcases/` | 用例列表/创建 |
| GET/PUT/DELETE | `/api/testcases/{id}/` | 用例详情/更新/删除 |
| GET/POST | `/api/testplans/` | 计划列表/创建 |
| POST | `/api/testplans/{id}/cases/` | 添加用例到计划 |
| DELETE | `/api/testplans/{id}/cases/{case_id}/` | 从计划移除用例 |
| GET/POST | `/api/executions/` | 执行列表/创建 |
| POST | `/api/executions/{id}/start/` | 开始执行 |
| POST | `/api/executions/{id}/cancel/` | 取消执行 |
| GET | `/api/reports/` | 报告列表 |
| GET | `/api/dashboard/summary/` | Dashboard 统计数据 |

## 异步报告生成

### API 说明

**POST** `/api/reports/generate/`

```json
{
  "execution": 1,
  "async_mode": false
}
```

**GET** `/api/reports/task_status/?task_id=xxx`

## 二期功能计划

### P0 核心能力
- ✅ 数据导入导出
- ✅ Celery 异步执行报告

### P1 用户体验优化
- 前端自动化测试
- 精细化权限控制
- Allure 报告集成
- 附件管理
- Dashboard 图表

### P2 基础设施完善
- Redis 完整功能
- 测试计划模板
- CI/CD 集成
- 用例版本管理

### P3 长远规划
- 接口自动化测试
- UI 自动化测试
- 插件化架构
- Docker/K8s 部署
- 团队功能

## 测试验证

### 后端测试

```bash
# 进入后端目录
cd backend

# 运行所有测试
python manage.py test

# 运行特定应用测试
python manage.py test apps.users
python manage.py test apps.projects
python manage.py test apps.testcases
python manage.py test apps.testplans
python manage.py test apps.executions
python manage.py test apps.reports
```

### 前端构建测试

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 生产构建
npm run build

# 开发模式
npm run dev
```

### 功能测试清单

| 功能 | 状态 | 说明 |
|------|------|------|
| 用户登录/登出 | ✅ | Token 自动刷新正常 |
| 用户管理 | ✅ | Admin/Tester/Viewer 角色控制正常 |
| 项目管理 | ✅ | CRUD 操作正常 |
| 测试用例管理 | ✅ | CRUD、筛选、搜索正常 |
| 测试计划管理 | ✅ | 添加/移除用例正常 |
| 测试执行管理 | ✅ | 结果录入正常 |
| 测试报告 | ✅ | 报告生成正常 |
| Dashboard | ✅ | 统计数据展示正常 |
| 数据导入导出 | ✅ | Excel/JSON 格式支持 |
| Celery 异步报告 | ✅ | 同步/异步模式支持 |

## CI/CD 集成

本项目已集成 Jenkins CI/CD 流水线，实现自动化构建、测试和部署流程。

### 相关文件

- `Jenkinsfile` - Jenkins 流水线配置
- `docker-compose.prod.yml` - 生产环境 Docker Compose 配置
- `docker-compose.jenkins.yml` - Jenkins 服务配置

### 快速启动 Jenkins

```bash
# 使用 Docker 启动 Jenkins
docker-compose -f docker-compose.jenkins.yml up -d

# 获取初始密码
docker exec aitest-jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

访问 Jenkins: http://localhost:8080

### Jenkins 配置步骤

1. **解锁 Jenkins** - 粘贴初始密码
2. **安装推荐插件** - Git, Pipeline, Docker 等
3. **创建管理员账户** - admin/admin123
4. **创建流水线任务**
   - 任务名称：`AITest-Platform-CI`
   - 类型：流水线
5. **配置 SCM**
   - 选择「Pipeline script from SCM」
   - SCM：Git
   - 仓库地址：你的 Git 仓库
   - 脚本路径：`Jenkinsfile`

### 流水线流程

```
Checkout → Backend Tests → Frontend Install → Frontend Build 
→ Build Docker Images → Push Docker Images → Deploy
```

### 分支策略

| 分支 | 触发操作 |
|------|----------|
| `develop` | 构建测试 → 部署到测试环境 |
| `main` | 构建测试 → 推送镜像 → 部署到生产环境 |

## 重要说明

- `.env` 不要提交到仓库
- 默认管理员账号：admin / admin123