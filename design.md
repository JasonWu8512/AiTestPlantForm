# AI 测试平台设计文档

## 1. 项目目标

开发一个测试管理平台，提供完整的测试管理闭环：项目、用例、计划、执行、结果、报告和 Dashboard。

**一期目标**：完成本地可运行、功能闭环的单体系统。

**一期范围**：
- ✅ 用户登录与用户管理
- ✅ 项目管理
- ✅ 测试用例管理
- ✅ 测试计划管理
- ✅ 测试执行管理
- ✅ 测试结果记录
- ✅ 测试报告查看
- ✅ Dashboard 数据概览

**一期暂不实现**：Docker/K8s 部署、微服务拆分、插件化、多租户、自动化执行引擎。

## 2. 技术栈

### 后端
| 分类 | 技术 | 版本 |
|------|------|------|
| 语言 | Python | 3.10+ |
| 框架 | Django | 4.2 LTS |
| API | Django REST Framework | - |
| 认证 | JWT | - |
| 数据库 | MySQL/SQLite | 8.0+ |
| 缓存/队列 | Redis | 6.0+ |
| 异步任务 | Celery | - |
| 报告 | Allure | - |

### 前端
| 分类 | 技术 | 版本 |
|------|------|------|
| 框架 | Vue | 3 |
| 构建 | Vite | - |
| UI | Element Plus | - |
| 路由 | Vue Router | - |
| 状态 | Pinia | - |
| 图表 | ECharts | - |

## 3. 系统架构

```
┌─────────────┐    HTTP/JSON    ┌──────────────┐    ORM    ┌─────────┐
│   Vue 前端   │ ──────────────► │  Django API   │ ───────► │  MySQL  │
└─────────────┘                 └──────────────┘           └─────────┘
                                      │
                                      ▼
                              ┌──────────────┐
                              │   Redis      │
                              └──────┬───────┘
                                     │
                                     ▼
                              ┌──────────────┐
                              │ Celery Worker│
                              └──────────────┘
```

### 模块结构

**后端** (`backend/`):
- `apps/users/` - 用户与权限
- `apps/projects/` - 项目管理
- `apps/testcases/` - 测试用例
- `apps/testplans/` - 测试计划
- `apps/executions/` - 测试执行
- `apps/reports/` - 测试报告
- `apps/dashboard/` - 统计概览
- `core/` - 公共能力（权限、分页、异常处理）
- `tasks/` - Celery 异步任务

**前端** (`frontend/src/`):
- `api/` - 接口请求封装
- `components/` - 公共组件
- `router/` - 路由配置
- `stores/` - Pinia 状态管理
- `views/` - 页面组件

## 4. 核心数据模型

### 用户模型
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| username | CharField | 用户名 |
| password | CharField | 加密密码 |
| email | EmailField | 邮箱 |
| is_active | BooleanField | 是否启用 |
| date_joined | DateTimeField | 创建时间 |

### 项目模型
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | CharField | 项目名称 |
| description | TextField | 描述 |
| status | CharField | active/archived |
| created_by | ForeignKey | 创建人 |
| created_at | DateTimeField | 创建时间 |

### 测试用例模型
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| project | ForeignKey | 所属项目 |
| title | CharField | 用例标题 |
| steps | JSONField | 测试步骤 |
| expected_result | TextField | 预期结果 |
| priority | CharField | P0/P1/P2/P3 |
| status | CharField | draft/active/archived |

### 测试计划模型
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| project | ForeignKey | 所属项目 |
| name | CharField | 计划名称 |
| description | TextField | 描述 |
| start_time | DateTimeField | 开始时间 |
| end_time | DateTimeField | 结束时间 |

### 测试执行模型
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| plan | ForeignKey | 关联计划 |
| executor | ForeignKey | 执行人 |
| status | CharField | pending/running/completed/failed/canceled |
| celery_task_id | CharField | 异步任务ID |

### 测试结果模型
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| execution | ForeignKey | 关联执行 |
| testcase | ForeignKey | 关联用例 |
| status | CharField | passed/failed/blocked/skipped |
| actual_result | TextField | 实际结果 |
| remark | TextField | 备注 |

### 测试报告模型
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| execution | ForeignKey | 关联执行 |
| name | CharField | 报告名称 |
| summary | JSONField | 报告摘要 |
| allure_report_path | CharField | Allure报告路径 |
| status | CharField | pending/generated/failed |

## 5. API 接口设计

### 通用规范
- 前缀：`/api/`
- 格式：JSON
- 分页：支持
- 认证：JWT

### 接口列表

| 模块 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 认证 | POST | `/api/auth/login/` | 登录 |
| 认证 | POST | `/api/auth/logout/` | 登出 |
| 认证 | POST | `/api/auth/refresh/` | 刷新Token |
| 认证 | GET | `/api/auth/me/` | 当前用户 |
| 用户 | CRUD | `/api/users/` | 用户管理 |
| 项目 | CRUD | `/api/projects/` | 项目管理 |
| 用例 | CRUD | `/api/testcases/` | 用例管理 |
| 计划 | CRUD | `/api/testplans/` | 计划管理 |
| 计划 | POST | `/api/testplans/{id}/cases/` | 添加用例 |
| 计划 | DELETE | `/api/testplans/{id}/cases/{case_id}/` | 移除用例 |
| 执行 | CRUD | `/api/executions/` | 执行管理 |
| 执行 | POST | `/api/executions/{id}/start/` | 开始执行 |
| 执行 | POST | `/api/executions/{id}/cancel/` | 取消执行 |
| 执行 | POST | `/api/executions/{id}/results/` | 提交结果 |
| 报告 | GET | `/api/reports/` | 报告列表 |
| 报告 | POST | `/api/reports/generate/` | 生成报告 |
| Dashboard | GET | `/api/dashboard/summary/` | 统计摘要 |
| Dashboard | GET | `/api/dashboard/trends/` | 趋势数据 |

## 6. 权限设计

### 角色定义
| 角色 | 权限 |
|------|------|
| admin | 全部权限，可管理用户 |
| tester | 可管理项目、用例、计划、执行、报告 |
| viewer | 只读权限，仅查看 |

### 权限规则
- 未登录用户仅可访问登录接口
- 用户管理仅 admin 可操作
- 删除操作限 admin 或数据创建人
- viewer 禁止创建、修改、删除

## 7. 安全设计

1. 密码使用 Django 默认加密机制
2. JWT 设置过期时间和刷新机制
3. 后端接口必须校验权限
4. 敏感配置通过环境变量读取
5. `.env`、密钥文件不提交仓库
6. 文件上传限制大小和类型
7. 列表查询分页处理

## 8. 配置设计

### 环境变量
```env
DJANGO_SECRET_KEY=xxx
DJANGO_DEBUG=True
DB_ENGINE=sqlite|mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=aitest_platform
MYSQL_USER=aitest
MYSQL_PASSWORD=xxx
REDIS_URL=redis://127.0.0.1:6379/0
```

### 配置文件结构
```
config/settings/
├── base.py       # 基础配置
├── development.py # 开发环境
└── production.py  # 生产环境
```

## 9. 后续扩展方向

### 接口自动化测试
- API 测试集合
- 请求参数管理
- 响应断言
- 执行结果记录

### UI 自动化测试
- 页面元素管理
- UI 操作步骤
- 截图记录
- Playwright/Selenium 集成

### CI/CD 集成
- Webhook 触发测试
- Jenkins/GitLab CI 回调
- 测试结果推送

### 插件化能力
- 执行器插件
- 报告插件
- 通知插件