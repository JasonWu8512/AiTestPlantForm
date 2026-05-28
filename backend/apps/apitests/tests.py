from django.contrib.auth.models import Group, User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.apitests.models import ApiTestCase, ApiTestExecution
from apps.projects.models import Project


class ApiTestCaseApiTests(TestCase):
    def setUp(self):
        Group.objects.get_or_create(name="viewer")
        self.admin = User.objects.create_superuser("admin", "admin@example.com", "admin123456")
        self.viewer = User.objects.create_user("viewer", "viewer@example.com", "viewer123456")
        self.viewer.groups.add(Group.objects.get(name="viewer"))
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

    def test_viewer_cannot_create_api_testcase(self):
        self.client.force_authenticate(self.viewer)

        response = self.client.post(
            "/api/api-tests/",
            {
                "project": self.project.id,
                "name": "测试用例",
                "method": "GET",
                "url": "https://httpbin.org/get",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


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

    def test_execute_all_active_api_tests(self):
        ApiTestCase.objects.create(
            project=self.project,
            name="测试用例2",
            method="POST",
            url="https://httpbin.org/post",
            status="active",
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
