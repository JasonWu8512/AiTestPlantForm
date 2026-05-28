# AI 测试平台设计文档

## 1. 项目目标

本项目计划开发一个测试管理平台，用于管理测试用例、测试计划、测试执行结果和测试报告。

一期目标是先完成一个可本地运行、可维护、功能闭环的单体系统，满足个人或小团队的测试管理需求。后续再逐步扩展接口自动化、UI 自动化、CI/CD 集成、Docker/K8s 部署等能力。

## 2. 一期功能范围

一期只做核心闭环功能：

1. 用户登录与用户管理
2. 项目管理
3. 测试用例管理
4. 测试计划管理
5. 测试执行管理
6. 测试结果记录
7. 测试报告查看
8. Dashboard 数据概览

一期暂不实现：

1. Docker 部署
2. Kubernetes 管理
3. 微服务拆分
4. 插件动态加载
5. 多租户
6. 客户端 SDK
7. 复杂测试资源池
8. UI 自动化录制器

这些能力保留设计空间，但不作为一期交付内容。

## 3. 技术栈

### 3.1 后端

- 语言：Python 3.10+
- Web 框架：Django 4.2 LTS
- API 框架：Django REST Framework
- 认证：JWT
- 数据库：MySQL 8.0+
- 缓存：Redis 6.0+
- 异步任务：Celery
- API 文档：drf-spectacular 或 drf-yasg
- 测试报告：Allure

说明：

- Django 4.2 是长期支持版本，更适合新项目。
- JWT 用于前后端分离场景的登录认证。
- Redis 同时用于缓存和 Celery Broker，减少一期部署复杂度。
- Allure 一期主要用于存储和展示测试报告入口，不先做复杂的报告二次解析。

### 3.2 前端

- 框架：Vue 3
- 构建工具：Vite
- 包管理：Yarn
- UI 组件库：Element Plus
- 路由：Vue Router
- 状态管理：Pinia
- HTTP 请求：Axios
- 图表：ECharts

### 3.3 开发与运行环境

- 操作系统：Windows
- 后端运行环境：Python 3.10+
- 前端运行环境：Node.js 18 LTS 或 20 LTS
- 数据库：MySQL 8.0+
- 缓存：Redis 6.0+

## 4. 系统架构

系统采用前后端分离架构：

```text
Vue 前端
   |
   | HTTP / JSON
   v
Django REST API
   |
   | ORM
   v
MySQL

Django REST API -> Redis -> Celery Worker
Celery Worker -> Allure 报告文件
```

### 4.1 后端模块

建议按 Django App 拆分：

```text
backend/
├── config/          # Django 项目配置
├── apps/
│   ├── users/       # 用户与权限
│   ├── projects/    # 项目管理
│   ├── testcases/   # 测试用例
│   ├── testplans/   # 测试计划
│   ├── executions/  # 测试执行与结果
│   ├── reports/     # 测试报告
│   └── dashboard/   # 首页统计
├── core/            # 公共能力：权限、分页、异常、响应格式
├── tasks/           # Celery 配置与异步任务
├── manage.py
└── requirements.txt
```

### 4.2 前端模块

```text
frontend/
├── public/
├── src/
│   ├── api/         # 接口请求
│   ├── assets/      # 静态资源
│   ├── components/  # 公共组件
│   ├── router/      # 路由
│   ├── stores/      # Pinia 状态
│   ├── utils/       # 工具函数
│   ├── views/       # 页面
│   ├── App.vue
│   └── main.js
├── package.json
├── yarn.lock
└── vite.config.js
```

## 5. 核心业务流程

### 5.1 测试管理主流程

```text
创建项目
  -> 创建测试用例
  -> 创建测试计划
  -> 选择测试用例加入计划
  -> 创建执行记录
  -> 录入每条用例执行结果
  -> 生成或查看测试报告
  -> Dashboard 汇总展示
```

### 5.2 测试执行状态

测试执行建议使用以下状态：

- pending：待执行
- running：执行中
- completed：已完成
- failed：执行失败
- canceled：已取消

测试结果建议使用以下状态：

- passed：通过
- failed：失败
- blocked：阻塞
- skipped：跳过

## 6. 数据库设计

### 6.1 User 用户表

可以优先使用 Django 自带 User 模型，后续如需要扩展字段，再使用用户 Profile 或自定义用户模型。

关键字段：

- id：主键
- username：用户名
- password：密码，必须加密存储
- email：邮箱
- is_active：是否启用
- is_staff：是否可进入后台
- date_joined：创建时间

### 6.2 Project 项目表

- id：主键
- name：项目名称
- description：项目描述
- status：状态，active / archived
- created_by：创建人
- created_at：创建时间
- updated_at：更新时间

### 6.3 TestCase 测试用例表

- id：主键
- project：所属项目
- title：用例标题
- description：用例描述
- precondition：前置条件
- steps：测试步骤，建议一期用 JSON 存储
- expected_result：预期结果
- priority：优先级，P0 / P1 / P2 / P3
- status：状态，draft / active / archived
- created_by：创建人
- created_at：创建时间
- updated_at：更新时间

说明：

- 一期可以把步骤存在 JSON 字段中，降低表结构复杂度。
- 如果后续要支持步骤级结果、复用步骤、步骤统计，再拆成独立的 TestCaseStep 表。

### 6.4 TestPlan 测试计划表

- id：主键
- project：所属项目
- name：计划名称
- description：计划描述
- status：状态，draft / active / archived
- start_time：计划开始时间
- end_time：计划结束时间
- created_by：创建人
- created_at：创建时间
- updated_at：更新时间

### 6.5 TestPlanCase 测试计划用例关联表

- id：主键
- plan：测试计划
- testcase：测试用例
- sort_order：执行顺序
- created_at：创建时间

约束：

- 同一个测试计划中，同一个测试用例只能添加一次。

### 6.6 TestExecution 测试执行表

- id：主键
- plan：测试计划
- executor：执行人
- status：执行状态
- started_at：实际开始时间
- finished_at：实际结束时间
- celery_task_id：异步任务 ID，可为空
- created_at：创建时间
- updated_at：更新时间

### 6.7 TestResult 测试结果表

- id：主键
- execution：所属执行记录
- testcase：测试用例
- status：结果状态
- actual_result：实际结果
- remark：备注
- attachments：附件信息，建议一期用 JSON 存储
- executed_by：执行人
- executed_at：执行时间
- created_at：创建时间
- updated_at：更新时间

约束：

- 同一个执行记录中，同一个测试用例只能有一条最终结果。

### 6.8 TestReport 测试报告表

- id：主键
- execution：所属执行记录
- name：报告名称
- summary：报告摘要，JSON 格式
- allure_report_path：Allure 报告目录或入口地址
- status：生成状态，pending / generated / failed
- created_at：创建时间
- updated_at：更新时间

## 7. API 设计

### 7.1 通用规范

- API 前缀统一使用 `/api/`
- 请求和响应统一使用 JSON
- 列表接口支持分页
- 列表接口支持关键字搜索和常用筛选
- 需要登录的接口必须校验 JWT
- 返回错误时使用统一错误格式

建议统一响应格式：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

### 7.2 认证接口

- `POST /api/auth/login/`：登录
- `POST /api/auth/logout/`：登出
- `POST /api/auth/refresh/`：刷新 Token
- `GET /api/auth/me/`：获取当前用户信息

### 7.3 用户管理接口

- `GET /api/users/`：用户列表
- `POST /api/users/`：创建用户
- `GET /api/users/{id}/`：用户详情
- `PUT /api/users/{id}/`：更新用户
- `DELETE /api/users/{id}/`：删除用户

### 7.4 项目管理接口

- `GET /api/projects/`：项目列表
- `POST /api/projects/`：创建项目
- `GET /api/projects/{id}/`：项目详情
- `PUT /api/projects/{id}/`：更新项目
- `DELETE /api/projects/{id}/`：删除项目

### 7.5 测试用例接口

- `GET /api/testcases/`：测试用例列表
- `POST /api/testcases/`：创建测试用例
- `GET /api/testcases/{id}/`：测试用例详情
- `PUT /api/testcases/{id}/`：更新测试用例
- `DELETE /api/testcases/{id}/`：删除测试用例

### 7.6 测试计划接口

- `GET /api/testplans/`：测试计划列表
- `POST /api/testplans/`：创建测试计划
- `GET /api/testplans/{id}/`：测试计划详情
- `PUT /api/testplans/{id}/`：更新测试计划
- `DELETE /api/testplans/{id}/`：删除测试计划
- `POST /api/testplans/{id}/cases/`：添加用例到计划
- `DELETE /api/testplans/{id}/cases/{case_id}/`：从计划移除用例

### 7.7 测试执行接口

- `GET /api/executions/`：执行记录列表
- `POST /api/executions/`：创建执行记录
- `GET /api/executions/{id}/`：执行记录详情
- `POST /api/executions/{id}/start/`：开始执行
- `POST /api/executions/{id}/cancel/`：取消执行
- `POST /api/executions/{id}/results/`：提交或更新用例结果

### 7.8 测试报告接口

- `GET /api/reports/`：报告列表
- `GET /api/reports/{id}/`：报告详情
- `POST /api/reports/generate/`：生成报告
- `GET /api/reports/{id}/download/`：下载报告

### 7.9 Dashboard 接口

- `GET /api/dashboard/summary/`：核心统计
- `GET /api/dashboard/trends/`：趋势数据
- `GET /api/dashboard/recent-executions/`：最近执行记录

## 8. 前端页面设计

### 8.1 页面列表

1. 登录页
2. Dashboard 首页
3. 项目管理页
4. 用户管理页
5. 测试用例列表页
6. 测试用例编辑页
7. 测试计划列表页
8. 测试计划详情页
9. 测试执行页
10. 测试报告页

### 8.2 页面要点

Dashboard：

- 项目数量
- 用例数量
- 计划数量
- 最近执行结果
- 通过率趋势

测试用例：

- 支持按项目、优先级、状态筛选
- 支持关键字搜索
- 支持新增、编辑、删除
- 支持维护步骤和预期结果

测试计划：

- 支持选择项目
- 支持添加和移除测试用例
- 支持调整用例执行顺序

测试执行：

- 展示计划下的用例列表
- 支持逐条记录通过、失败、阻塞、跳过
- 支持填写实际结果和备注

测试报告：

- 展示执行汇总
- 展示通过率、失败数、阻塞数、跳过数
- 提供 Allure 报告入口

## 9. 异步任务设计

一期 Celery 主要处理耗时或可延后的任务：

1. 生成 Allure 报告
2. 导入导出测试用例
3. 清理过期临时文件

测试执行本身一期可以先做人工执行记录，不强制做自动化执行器。

后续接入接口自动化或 UI 自动化后，再把执行任务放入 Celery。

## 10. 权限设计

一期使用简单角色控制：

- admin：管理员，可以管理用户和全部数据
- tester：测试人员，可以管理项目、用例、计划、执行和报告
- viewer：只读用户，只能查看数据和报告

权限规则：

1. 未登录用户只能访问登录接口
2. 用户管理仅 admin 可操作
3. 删除操作仅 admin 或数据创建人可操作
4. viewer 不允许创建、修改、删除数据

## 11. 安全设计

1. 密码必须使用 Django 默认加密机制保存
2. JWT 需要设置过期时间和刷新机制
3. 后端接口必须校验权限
4. 前端不能保存明文密码、Token 以外的敏感信息
5. 生产环境配置必须通过环境变量读取
6. `.env`、密钥、证书文件不能提交到仓库
7. 文件上传需要限制大小和类型
8. 列表查询需要分页，避免一次性返回大量数据

## 12. 配置设计

后端配置建议分环境管理：

```text
config/settings/
├── base.py
├── development.py
└── production.py
```

常见环境变量：

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `MYSQL_HOST`
- `MYSQL_PORT`
- `MYSQL_DATABASE`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `REDIS_URL`
- `JWT_ACCESS_TOKEN_LIFETIME`
- `JWT_REFRESH_TOKEN_LIFETIME`

## 13. 部署规划

一期部署方式：

1. 本地 Windows 开发运行
2. 后端使用 Django 开发服务器或 gunicorn 等生产服务
3. 前端使用 Vite 开发服务器，构建后可由 Nginx 托管
4. MySQL 和 Redis 可使用本机服务或 Docker 单独启动

后续部署规划：

1. Docker Compose：适合个人或小团队部署
2. Kubernetes：适合后续多服务、资源隔离和弹性扩容

注意：Docker 和 K8s 不作为一期必做内容，避免前期开发复杂度过高。

## 14. 后续扩展方向

### 14.1 接口自动化测试

后续可新增 API 测试模块：

- API 测试集合
- API 测试步骤
- 环境变量
- 请求参数
- 响应断言
- 执行结果

推荐执行技术：

- requests
- pytest
- allure-pytest

### 14.2 UI 自动化测试

后续可新增 UI 测试模块：

- 页面元素管理
- UI 操作步骤
- 截图记录
- 执行日志

推荐执行技术：

- Playwright
- Selenium

### 14.3 CI/CD 集成

后续可提供：

- Webhook 触发测试计划
- Jenkins / GitLab CI 回调
- 测试结果推送
- 报告链接回写

### 14.4 插件化能力

插件化不建议一期实现，只保留接口边界即可。后续可以从以下方向扩展：

- 执行器插件
- 报告插件
- 通知插件
- 数据导入导出插件

## 15. 一期验收标准

一期完成后，需要满足：

1. 可以正常登录和退出
2. 可以创建、编辑、删除项目
3. 可以创建、编辑、删除测试用例
4. 可以创建测试计划，并添加测试用例
5. 可以创建执行记录，并录入每条用例结果
6. 可以查看执行汇总和测试报告
7. Dashboard 可以展示核心统计数据
8. 后端 API 有基础权限控制
9. 前端主要页面可正常跳转和操作
10. README 中有本地启动说明

## 16. 当前文档中已明确的技术要点

1. 技术架构：前后端分离
2. 后端框架：Python + Django + DRF
3. 前端框架：Vue 3 + Vite + Element Plus
4. 数据存储：MySQL
5. 缓存和异步队列：Redis + Celery
6. 报告能力：Allure
7. 一期边界：先做测试管理闭环，不先做复杂自动化执行平台

## 17. 需要后续确认的问题

开发前建议再确认以下问题：

1. 登录是否只需要账号密码，还是要接入第三方登录？
2. 测试用例步骤一期是否允许用 JSON 存储，后续再拆表？
3. 测试执行一期是否以人工记录为主，自动化执行后续再做？
4. Allure 报告一期是只保存链接，还是需要解析报告数据入库？
5. 是否需要文件附件，例如失败截图、日志、接口响应文件？
6. 用户角色是否只需要 admin、tester、viewer 三类？
7. 项目是否需要归属团队，还是个人项目即可？
