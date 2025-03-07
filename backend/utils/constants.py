"""
常量模块，定义系统中使用的常量

作者: AiTestPlantForm团队
创建日期: 2023-06-01
最后修改: 2023-06-10
"""

# 用户角色
USER_ROLE_ADMIN = 'admin'
USER_ROLE_USER = 'user'
USER_ROLE_CHOICES = (
    (USER_ROLE_ADMIN, '管理员'),
    (USER_ROLE_USER, '普通用户'),
)

# 用户状态
USER_STATUS_ACTIVE = 'active'
USER_STATUS_INACTIVE = 'inactive'
USER_STATUS_CHOICES = (
    (USER_STATUS_ACTIVE, '启用'),
    (USER_STATUS_INACTIVE, '禁用'),
)

# 测试用例优先级
TEST_CASE_PRIORITY_HIGH = 'high'
TEST_CASE_PRIORITY_MEDIUM = 'medium'
TEST_CASE_PRIORITY_LOW = 'low'
TEST_CASE_PRIORITY_CHOICES = (
    (TEST_CASE_PRIORITY_HIGH, '高'),
    (TEST_CASE_PRIORITY_MEDIUM, '中'),
    (TEST_CASE_PRIORITY_LOW, '低'),
)

# 测试用例状态
TEST_CASE_STATUS_DRAFT = 'draft'
TEST_CASE_STATUS_ACTIVE = 'active'
TEST_CASE_STATUS_DEPRECATED = 'deprecated'
TEST_CASE_STATUS_CHOICES = (
    (TEST_CASE_STATUS_DRAFT, '草稿'),
    (TEST_CASE_STATUS_ACTIVE, '激活'),
    (TEST_CASE_STATUS_DEPRECATED, '废弃'),
)

# 测试计划状态
TEST_PLAN_STATUS_DRAFT = 'draft'
TEST_PLAN_STATUS_ACTIVE = 'active'
TEST_PLAN_STATUS_COMPLETED = 'completed'
TEST_PLAN_STATUS_CANCELLED = 'cancelled'
TEST_PLAN_STATUS_CHOICES = (
    (TEST_PLAN_STATUS_DRAFT, '草稿'),
    (TEST_PLAN_STATUS_ACTIVE, '进行中'),
    (TEST_PLAN_STATUS_COMPLETED, '已完成'),
    (TEST_PLAN_STATUS_CANCELLED, '已取消'),
)

# 测试执行状态
TEST_EXECUTION_STATUS_PENDING = 'pending'
TEST_EXECUTION_STATUS_RUNNING = 'running'
TEST_EXECUTION_STATUS_COMPLETED = 'completed'
TEST_EXECUTION_STATUS_FAILED = 'failed'
TEST_EXECUTION_STATUS_CANCELLED = 'cancelled'
TEST_EXECUTION_STATUS_CHOICES = (
    (TEST_EXECUTION_STATUS_PENDING, '待执行'),
    (TEST_EXECUTION_STATUS_RUNNING, '执行中'),
    (TEST_EXECUTION_STATUS_COMPLETED, '已完成'),
    (TEST_EXECUTION_STATUS_FAILED, '执行失败'),
    (TEST_EXECUTION_STATUS_CANCELLED, '已取消'),
)

# 测试结果状态
TEST_RESULT_STATUS_PASS = 'pass'
TEST_RESULT_STATUS_FAIL = 'fail'
TEST_RESULT_STATUS_BLOCKED = 'blocked'
TEST_RESULT_STATUS_CHOICES = (
    (TEST_RESULT_STATUS_PASS, '通过'),
    (TEST_RESULT_STATUS_FAIL, '失败'),
    (TEST_RESULT_STATUS_BLOCKED, '阻塞'),
)

# 项目状态
PROJECT_STATUS_ACTIVE = 'active'
PROJECT_STATUS_INACTIVE = 'inactive'
PROJECT_STATUS_ARCHIVED = 'archived'
PROJECT_STATUS_CHOICES = (
    (PROJECT_STATUS_ACTIVE, '活跃'),
    (PROJECT_STATUS_INACTIVE, '不活跃'),
    (PROJECT_STATUS_ARCHIVED, '已归档'),
) 