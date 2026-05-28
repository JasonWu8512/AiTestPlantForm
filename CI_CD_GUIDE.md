# CI/CD 集成指南

## 概述

本项目使用 Jenkins 实现持续集成和持续部署（CI/CD），支持自动构建、测试和部署流程。

## 环境要求

- Jenkins LTS 版本
- Docker（已安装并配置）
- Git 仓库访问权限

## Jenkins 配置

### 1. 启动 Jenkins

```bash
# 启动 Jenkins 容器
docker-compose -f docker-compose.jenkins.yml up -d

# 获取初始管理员密码
docker exec aitest-jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

### 2. 安装必要插件

登录 Jenkins 后，安装以下插件：
- Git Plugin
- Docker Plugin
- Docker Pipeline Plugin
- Pipeline Plugin
- NodeJS Plugin
- Slack Notification Plugin（可选）

### 3. 配置工具

1. **NodeJS 配置**
   - 进入「全局工具配置」
   - 添加 NodeJS 安装，版本选择 20.x
   - 设置别名：`node20`

2. **Python 配置（可选）**
   - 确保 Jenkins 服务器安装了 Python 3.11+

### 4. 配置凭证

1. **Git 凭证**
   - 添加用户名/密码或 SSH 密钥凭证
   - ID 设置为：`git-credentials`

2. **Docker Registry 凭证（可选）**
   - 如果需要推送镜像到远程仓库，添加 Docker Hub 或私有仓库凭证

## 创建流水线任务

### 步骤 1：新建任务

1. 点击「新建任务」
2. 输入任务名称：`aitest-platform-pipeline`
3. 选择「流水线」类型
4. 点击「确定」

### 步骤 2：配置任务

#### 通用配置
- 勾选「丢弃旧的构建」
- 保留构建天数：30
- 保留构建最大个数：10

#### 源码管理
- 选择「Git」
- Repository URL：你的 Git 仓库地址
- Credentials：选择之前配置的 Git 凭证
- Branches to build：`*/main` 和 `*/develop`

#### 构建触发器
- 勾选「GitHub hook trigger for GITScm polling」（如果使用 GitHub）
- 或配置定时构建：`H/15 * * * *`（每15分钟检查一次）

#### 流水线配置
- Definition：选择「Pipeline script from SCM」
- SCM：选择「Git」
- Repository URL：你的 Git 仓库地址
- Credentials：选择 Git 凭证
- Branch Specifier：`*/main`
- Script Path：`Jenkinsfile`

### 步骤 3：保存并运行

点击「保存」后，点击「立即构建」测试流水线。

## 流水线流程

### 完整流程

```
Checkout → Backend Tests → Frontend Install → Frontend Tests → Frontend Build → Build Docker Images → Push Docker Images → Deploy → Post Deploy
```

### 各阶段说明

| 阶段 | 说明 | 条件 |
|------|------|------|
| Checkout | 从 Git 仓库检出代码 | 始终执行 |
| Backend Tests | 运行后端单元测试 | 始终执行 |
| Frontend Install | 安装前端依赖 | 始终执行 |
| Frontend Tests | 运行前端测试 | 始终执行 |
| Frontend Build | 构建前端生产版本 | 始终执行 |
| Build Docker Images | 构建后端和前端 Docker 镜像 | 始终执行 |
| Push Docker Images | 推送镜像到 Docker 仓库 | 仅 main 分支 |
| Deploy to Staging | 部署到测试环境 | 仅 develop 分支 |
| Deploy to Production | 部署到生产环境 | 仅 main 分支 |
| Post Deploy | 部署后检查服务状态 | main 或 develop 分支 |

## 分支策略

### develop 分支
- 用于开发和测试
- 推送代码自动触发构建和测试
- 成功后部署到测试环境

### main 分支
- 用于生产发布
- 推送代码自动触发构建和测试
- 成功后推送镜像并部署到生产环境

## 环境变量配置

在 Jenkins 任务配置中添加以下环境变量：

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| DOCKER_REGISTRY | Docker 仓库地址 | 空（不推送） |
| BACKEND_IMAGE | 后端镜像名称 | aitest-backend |
| FRONTEND_IMAGE | 前端镜像名称 | aitest-frontend |
| COMPOSE_FILE | 生产环境 Compose 文件 | docker-compose.prod.yml |

## 通知配置

### Slack 通知（可选）

1. 在 Jenkins 中安装 Slack Notification Plugin
2. 配置 Slack 工作区和通知频道
3. 在 Jenkinsfile 中已包含 Slack 通知逻辑

## 部署脚本说明

### run-tests.sh
运行前后端测试和前端构建

```bash
./scripts/run-tests.sh
```

### deploy.sh
部署到指定环境

```bash
# 部署到生产环境（默认）
./scripts/deploy.sh

# 部署到测试环境
./scripts/deploy.sh staging
```

## 故障排除

### 常见问题

1. **权限问题**
   - 确保 Jenkins 用户有 Docker 执行权限
   - 检查 `/var/run/docker.sock` 权限

2. **测试失败**
   - 检查测试日志定位失败原因
   - 确保数据库服务正常运行

3. **构建失败**
   - 检查 Node.js 和 Python 版本是否符合要求
   - 检查依赖安装是否成功

4. **部署失败**
   - 检查 Docker Compose 文件配置
   - 检查端口是否被占用

## 安全注意事项

1. 不要在 Jenkinsfile 中硬编码敏感信息
2. 使用 Jenkins 凭证管理功能
3. 限制 Jenkins 服务器访问权限
4. 定期更新 Jenkins 和插件版本

## 附录

### Jenkins 访问地址
- 本地访问：http://localhost:8080
- 默认端口：8080

### 目录结构

```
.
├── Jenkinsfile              # 流水线配置文件
├── docker-compose.jenkins.yml  # Jenkins Docker 配置
├── docker-compose.prod.yml     # 生产环境配置
├── scripts/
│   ├── run-tests.sh         # 测试脚本
│   ├── deploy.sh            # 部署脚本
│   └── start-jenkins.sh     # Jenkins 启动脚本
```