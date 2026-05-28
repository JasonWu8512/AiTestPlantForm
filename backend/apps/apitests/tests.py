from unittest import skip

from django.contrib.auth.models import Group, User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.apitests.models import ApiTestCase, ApiTestExecution, ApiTestResult
from apps.projects.models import Project


class ApiTestCaseApiTests(TestCase):
    def setUp(self):
        Group.objects.get_or_create(name="viewer")
        Group.objects.get_or_create(name="tester")
        self.admin = User.objects.create_superuser("admin", "admin@example.com", "admin123456")
        self.viewer = User.objects.create_user("viewer", "viewer@example.com", "viewer123456")
        self.viewer.groups.add(Group.objects.get(name="viewer"))
        self.tester = User.objects.create_user("tester", "tester@example.com", "tester123456")
        self.tester.groups.add(Group.objects.get(name="tester"))
        self.project = Project.objects.create(name="平台项目", created_by=self.admin)
        self.client = APIClient()

    def test_admin_can_create_api_testcase(self):
        self.client.force_authenticate(self.admin)

        response = self.client.post(
            "/api/api-tests/",
            {
                "project": self.project.id,
                "name": "测试登录接口",
                "description": "验证用户登录功能",
                "method": "POST",
                "url": "https://httpbin.org/post",
                "headers": {"Content-Type": "application/json"},
                "params": {},
                "body_type": "json",
                "body": {"username": "test", "password": "123456"},
                "expected_status": 200,
                "validation_rules": [
                    {"type": "status_code", "params": {"expected": 200}}
                ],
                "timeout": 30,
                "priority": "P1",
                "status": "active",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        testcase = ApiTestCase.objects.get(name="测试登录接口")
        self.assertEqual(testcase.method, "POST")
        self.assertEqual(testcase.status, "active")
        self.assertEqual(testcase.project.id, self.project.id)

    def test_create_api_testcase_missing_required_fields(self):
        self.client.force_authenticate(self.admin)

        response = self.client.post(
            "/api/api-tests/",
            {
                "project": self.project.id,
                "name": "测试用例",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_can_update_api_testcase(self):
        testcase = ApiTestCase.objects.create(
            project=self.project,
            name="原始用例",
            method="GET",
            url="https://httpbin.org/get",
            status="active",
            created_by=self.admin
        )
        self.client.force_authenticate(self.admin)

        response = self.client.put(
            f"/api/api-tests/{testcase.id}/",
            {
                "project": self.project.id,
                "name": "更新后的用例",
                "method": "POST",
                "url": "https://httpbin.org/post",
                "status": "active",
                "expected_status": 200,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        testcase.refresh_from_db()
        self.assertEqual(testcase.name, "更新后的用例")
        self.assertEqual(testcase.method, "POST")

    def test_admin_can_delete_api_testcase(self):
        testcase = ApiTestCase.objects.create(
            project=self.project,
            name="待删除用例",
            method="GET",
            url="https://httpbin.org/get",
            created_by=self.admin
        )
        self.client.force_authenticate(self.admin)

        response = self.client.delete(f"/api/api-tests/{testcase.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ApiTestCase.objects.filter(id=testcase.id).exists())

    def test_viewer_can_read_but_cannot_create_api_testcase(self):
        ApiTestCase.objects.create(
            project=self.project,
            name="查看用例",
            method="GET",
            url="https://httpbin.org/get",
            created_by=self.admin
        )
        self.client.force_authenticate(self.viewer)

        list_response = self.client.get("/api/api-tests/")
        create_response = self.client.post(
            "/api/api-tests/",
            {
                "project": self.project.id,
                "name": "新用例",
                "method": "GET",
                "url": "https://httpbin.org/get",
            },
            format="json",
        )

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(create_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_api_testcases_by_project_and_status(self):
        ApiTestCase.objects.create(
            project=self.project,
            name="测试用例1",
            method="GET",
            url="https://httpbin.org/get",
            priority="P1",
            status="active"
        )
        ApiTestCase.objects.create(
            project=self.project,
            name="测试用例2",
            method="POST",
            url="https://httpbin.org/post",
            priority="P3",
            status="draft"
        )
        self.client.force_authenticate(self.admin)

        response = self.client.get(
            "/api/api-tests/",
            {"project": self.project.id, "priority": "P1", "status": "active"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["count"], 1)

    def test_filter_api_testcases_by_method(self):
        ApiTestCase.objects.create(
            project=self.project,
            name="GET用例",
            method="GET",
            url="https://httpbin.org/get",
            status="active"
        )
        ApiTestCase.objects.create(
            project=self.project,
            name="POST用例",
            method="POST",
            url="https://httpbin.org/post",
            status="active"
        )
        self.client.force_authenticate(self.admin)

        response = self.client.get("/api/api-tests/", {"method": "GET"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["count"], 1)

    def test_search_api_testcases(self):
        ApiTestCase.objects.create(
            project=self.project,
            name="用户登录接口",
            method="POST",
            url="https://httpbin.org/post",
            status="active"
        )
        ApiTestCase.objects.create(
            project=self.project,
            name="订单查询接口",
            method="GET",
            url="https://httpbin.org/get",
            status="active"
        )
        self.client.force_authenticate(self.admin)

        response = self.client.get("/api/api-tests/", {"search": "登录"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["count"], 1)


class ApiTestExecutionApiTests(TestCase):
    def setUp(self):
        Group.objects.get_or_create(name="viewer")
        self.admin = User.objects.create_superuser("admin", "admin@example.com", "admin123456")
        self.project = Project.objects.create(name="平台项目", created_by=self.admin)
        self.testcase = ApiTestCase.objects.create(
            project=self.project,
            name="测试用例",
            method="GET",
            url="https://httpbin.org/get",
            status="active",
            expected_status=200,
            created_by=self.admin
        )
        self.client = APIClient()

    def test_execute_api_test_sync(self):
        self.client.force_authenticate(self.admin)

        response = self.client.post(
            "/api/api-tests/execute/",
            {
                "project": self.project.id,
                "testcase_ids": [self.testcase.id],
                "async_mode": False
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("execution_id", response.data["data"])
        self.assertEqual(response.data["data"]["total"], 1)

        execution = ApiTestExecution.objects.get(id=response.data["data"]["execution_id"])
        self.assertEqual(execution.status, "completed")
        self.assertEqual(execution.total, 1)
        self.assertEqual(execution.passed, 1)

    def test_execute_all_active_api_tests(self):
        ApiTestCase.objects.create(
            project=self.project,
            name="测试用例2",
            method="POST",
            url="https://httpbin.org/post",
            status="active",
            expected_status=200,
            created_by=self.admin
        )
        self.client.force_authenticate(self.admin)

        response = self.client.post(
            "/api/api-tests/execute/",
            {
                "project": self.project.id,
                "async_mode": False
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["total"], 2)
        self.assertEqual(response.data["data"]["passed"], 2)

    @skip("Requires Celery worker, skipped in unit tests")
    def test_execute_api_test_async(self):
        self.client.force_authenticate(self.admin)

        response = self.client.post(
            "/api/api-tests/execute/",
            {
                "project": self.project.id,
                "testcase_ids": [self.testcase.id],
                "async_mode": True
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("execution_id", response.data["data"])
        self.assertIn("task_id", response.data["data"])
        self.assertTrue(response.data["data"]["async_mode"])

        execution = ApiTestExecution.objects.get(id=response.data["data"]["execution_id"])
        self.assertEqual(execution.status, "pending")

    def test_execute_api_test_no_project(self):
        self.client.force_authenticate(self.admin)

        response = self.client.post(
            "/api/api-tests/execute/",
            {
                "testcase_ids": [self.testcase.id],
                "async_mode": False
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], 400)

    def test_execute_api_test_no_testcases_found(self):
        self.client.force_authenticate(self.admin)

        response = self.client.post(
            "/api/api-tests/execute/",
            {
                "project": 999,
                "async_mode": False
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["code"], 404)

    def test_get_execution_results(self):
        execution = ApiTestExecution.objects.create(
            project=self.project,
            name="测试执行",
            status="completed",
            total=1,
            passed=1,
            executor=self.admin
        )
        ApiTestResult.objects.create(
            execution=execution,
            testcase=self.testcase,
            status="passed",
            response_status=200
        )
        self.client.force_authenticate(self.admin)

        response = self.client.get(f"/api/api-test-executions/{execution.id}/results/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)

    def test_cancel_execution(self):
        execution = ApiTestExecution.objects.create(
            project=self.project,
            name="测试执行",
            status="pending",
            total=1,
            executor=self.admin
        )
        self.client.force_authenticate(self.admin)

        response = self.client.post(f"/api/api-test-executions/{execution.id}/cancel/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        execution.refresh_from_db()
        self.assertEqual(execution.status, "canceled")

    def test_cancel_completed_execution(self):
        execution = ApiTestExecution.objects.create(
            project=self.project,
            name="测试执行",
            status="completed",
            total=1,
            passed=1,
            executor=self.admin
        )
        self.client.force_authenticate(self.admin)

        response = self.client.post(f"/api/api-test-executions/{execution.id}/cancel/")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_executions_by_project_and_status(self):
        execution1 = ApiTestExecution.objects.create(
            project=self.project,
            name="执行1",
            status="completed",
            total=1,
            passed=1,
            executor=self.admin
        )
        execution2 = ApiTestExecution.objects.create(
            project=self.project,
            name="执行2",
            status="running",
            total=1,
            executor=self.admin
        )
        self.client.force_authenticate(self.admin)

        response = self.client.get(
            "/api/api-test-executions/",
            {"project": self.project.id, "status": "completed"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["count"], 1)