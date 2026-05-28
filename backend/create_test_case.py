import os
import sys
import django
import json
import time
import requests
import io
from datetime import datetime

# 设置标准输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 设置Django环境
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.contrib.auth.models import User, Group
from django.utils import timezone
from apps.projects.models import Project
from apps.apitests.models import ApiTestCase, ApiTestExecution, ApiTestResult
from apps.apitests.services import ApiTestSuiteExecutor


def setup_initial_data():
    """初始化基础数据"""
    print("\n=== 初始化基础数据 ===")

    # 创建用户组
    Group.objects.get_or_create(name="admin")
    Group.objects.get_or_create(name="tester")
    Group.objects.get_or_create(name="viewer")

    # 创建管理员用户
    admin, created = User.objects.get_or_create(
        username="test_admin",
        defaults={
            "email": "test_admin@example.com",
            "is_staff": True,
            "is_superuser": True
        }
    )
    if created:
        admin.set_password("test123456")
        admin.save()
        print("[OK] 创建管理员用户: test_admin")
    else:
        print("[OK] 使用现有管理员用户: test_admin")

    return admin


def create_test_project(admin_user):
    """创建测试项目"""
    print("\n=== 创建测试项目 ===")

    project, created = Project.objects.get_or_create(
        name="功能验证项目",
        defaults={
            "description": "用于验证接口测试功能的演示项目",
            "status": "active",
            "created_by": admin_user
        }
    )

    if created:
        print(f"[OK] 创建项目: {project.name} (ID: {project.id})")
    else:
        print(f"[OK] 使用现有项目: {project.name} (ID: {project.id})")

    return project


def create_api_testcase(project, admin_user):
    """创建API测试用例"""
    print("\n=== 创建API测试用例 ===")

    # 创建一个验证JSON响应字段的测试用例
    testcase_data = {
        "project": project,
        "name": "验证httpbin GET接口响应",
        "description": "验证httpbin.org的GET接口能够正确返回JSON格式的响应",
        "method": "GET",
        "url": "https://httpbin.org/get",
        "headers": {
            "Content-Type": "application/json",
            "User-Agent": "AI-Test-Platform/1.0"
        },
        "params": {},
        "body_type": "json",
        "body": {},
        "expected_status": 200,
        "validation_rules": [
            {
                "type": "status_code",
                "params": {"expected": 200}
            },
            {
                "type": "json_path",
                "params": {
                    "json_path": "url",
                    "operator": "contains",
                    "expected": "httpbin.org"
                }
            },
            {
                "type": "json_path",
                "params": {
                    "json_path": "headers",
                    "operator": "exists"
                }
            }
        ],
        "timeout": 30,
        "priority": "P1",
        "status": "active",
        "created_by": admin_user
    }

    testcase, created = ApiTestCase.objects.get_or_create(
        name=testcase_data["name"],
        project=project,
        defaults=testcase_data
    )

    if created:
        print(f"[OK] 创建测试用例: {testcase.name} (ID: {testcase.id})")
        print(f"     - 方法: {testcase.method}")
        print(f"     - URL: {testcase.url}")
        print(f"     - 期望状态码: {testcase.expected_status}")
        print(f"     - 验证规则数量: {len(testcase.validation_rules)}")
    else:
        print(f"[OK] 使用现有测试用例: {testcase.name} (ID: {testcase.id})")

    return testcase


def execute_testcase(testcase):
    """执行测试用例"""
    print("\n=== 执行测试用例 ===")
    print(f"测试用例: {testcase.name}")
    print(f"URL: {testcase.method} {testcase.url}")
    print("-" * 60)

    # 记录开始时间
    start_time = timezone.now()

    # 创建执行记录
    execution = ApiTestExecution.objects.create(
        project=testcase.project,
        name=f"手动执行 - {testcase.name} - {start_time.strftime('%Y-%m-%d %H:%M:%S')}",
        status="running",
        total=1,
        executor=testcase.created_by,
        started_at=start_time
    )
    print(f"[OK] 创建执行记录 (ID: {execution.id})")

    # 执行测试
    executor = ApiTestSuiteExecutor([testcase])
    results = executor.execute_all()
    result = results[0]

    # 记录结束时间
    end_time = timezone.now()

    # 保存结果
    test_result = ApiTestResult.objects.create(
        execution=execution,
        testcase=testcase,
        status=result["status"],
        response_status=result.get("response_status"),
        response_body=result.get("response_body", {}),
        response_time=result.get("response_time"),
        validation_results=result.get("validation_results", {}),
        error_message=result.get("error_message", ""),
        executed_at=result.get("executed_at", end_time)
    )

    # 更新执行记录
    execution.status = "completed"
    execution.passed = 1 if result["status"] == "passed" else 0
    execution.failed = 1 if result["status"] != "passed" else 0
    execution.finished_at = end_time
    execution.save()

    return execution, test_result, result


def print_results(execution, test_result, result):
    """打印测试结果"""
    print("\n" + "=" * 60)
    print("测试执行结果")
    print("=" * 60)
    print(f"执行ID: {execution.id}")
    print(f"执行时间: {execution.created_at}")
    print(f"开始时间: {execution.started_at}")
    print(f"结束时间: {execution.finished_at}")

    if execution.finished_at and execution.started_at:
        duration = (execution.finished_at - execution.started_at).total_seconds()
        print(f"总耗时: {duration:.2f}秒")

    print(f"\n执行状态: {execution.status}")
    print(f"通过数: {execution.passed}")
    print(f"失败数: {execution.failed}")
    print(f"通过率: {execution.pass_rate}%")

    print("\n--- 详细结果 ---")
    print(f"用例状态: {test_result.status}")
    print(f"响应状态码: {test_result.response_status}")
    print(f"响应时间: {test_result.response_time}ms")

    # 打印响应内容（如果存在）
    if result.get("response_body"):
        print("\n响应内容预览:")
        print(json.dumps(result["response_body"], indent=2, ensure_ascii=False)[:500])

    # 打印验证结果
    validation = result.get("validation_results", {})
    if validation:
        print("\n验证结果:")
        print(f"  全部通过: {validation.get('all_passed', False)}")

        checks = validation.get("checks", [])
        for i, check in enumerate(checks, 1):
            status_icon = "[PASS]" if check.get("passed") else "[FAIL]"
            print(f"  {status_icon} 检查{i}: {check.get('type')}")

            if check.get("type") == "status_code":
                print(f"      期望: {check.get('expected')}, 实际: {check.get('actual')}")
            elif check.get("type") == "json_path":
                print(f"      JSON路径: {check.get('json_path')}")
                print(f"      操作符: {check.get('operator')}")
                print(f"      期望: {check.get('expected')}, 实际: {check.get('actual')}")

        errors = validation.get("errors", [])
        if errors:
            print("\n错误信息:")
            for error in errors:
                print(f"  - {error}")

    # 打印错误信息（如果有）
    if result.get("error_message"):
        print("\n错误信息:")
        print(f"  {result['error_message']}")

    print("\n" + "=" * 60)


def main():
    """主函数"""
    print("=" * 60)
    print("AI测试平台 - 接口测试功能验证")
    print("=" * 60)

    try:
        # 1. 初始化数据
        admin_user = setup_initial_data()

        # 2. 创建测试项目
        project = create_test_project(admin_user)

        # 3. 创建测试用例
        testcase = create_api_testcase(project, admin_user)

        # 4. 执行测试
        execution, test_result, result = execute_testcase(testcase)

        # 5. 打印结果
        print_results(execution, test_result, result)

        # 返回状态码
        if test_result.status == "passed":
            print("\n[SUCCESS] 接口测试功能验证成功!")
            return 0
        else:
            print("\n[WARNING] 接口测试功能验证未完全通过，请检查上述错误信息。")
            return 1

    except Exception as e:
        print(f"\n[ERROR] 执行过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
