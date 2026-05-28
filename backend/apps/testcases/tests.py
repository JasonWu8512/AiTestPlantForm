from django.contrib.auth.models import Group, User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.projects.models import Project
from apps.testcases.models import TestCase as TestCaseModel


class TestCaseApiTests(TestCase):
    def setUp(self):
        Group.objects.get_or_create(name="viewer")
        self.admin = User.objects.create_superuser("admin", "admin@example.com", "admin123456")
        self.viewer = User.objects.create_user("viewer", "viewer@example.com", "viewer123456")
        self.viewer.groups.add(Group.objects.get(name="viewer"))
        self.project = Project.objects.create(name="平台项目", created_by=self.admin)
        self.client = APIClient()

    def test_admin_can_create_testcase_with_steps(self):
        self.client.force_authenticate(self.admin)

        response = self.client.post(
            "/api/testcases/",
            {
                "project": self.project.id,
                "title": "登录成功",
                "description": "验证用户可以登录",
                "precondition": "用户已存在",
                "steps": [{"action": "输入账号密码"}, {"action": "点击登录"}],
                "expected_result": "进入 Dashboard",
                "priority": "P1",
                "status": "active",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        testcase = TestCaseModel.objects.get(title="登录成功")
        self.assertEqual(len(testcase.steps), 2)

    def test_filter_testcases_by_project_priority_and_status(self):
        TestCaseModel.objects.create(project=self.project, title="P1 用例", priority="P1", status="active")
        TestCaseModel.objects.create(project=self.project, title="P3 用例", priority="P3", status="draft")
        self.client.force_authenticate(self.viewer)

        response = self.client.get(
            "/api/testcases/",
            {"project": self.project.id, "priority": "P1", "status": "active"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["count"], 1)
