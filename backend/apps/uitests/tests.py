from django.contrib.auth.models import Group, User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.projects.models import Project
from apps.uitests.models import UITestCase


class UITestCaseApiTests(TestCase):
    def setUp(self):
        Group.objects.get_or_create(name="viewer")
        self.admin = User.objects.create_superuser("admin", "admin@example.com", "admin123456")
        self.viewer = User.objects.create_user("viewer", "viewer@example.com", "viewer123456")
        self.viewer.groups.add(Group.objects.get(name="viewer"))
        self.project = Project.objects.create(name="平台项目", created_by=self.admin)
        self.client = APIClient()

    def test_admin_can_create_uitestcase(self):
        self.client.force_authenticate(self.admin)

        response = self.client.post(
            "/api/ui-tests/",
            {
                "project": self.project.id,
                "name": "测试登录流程",
                "description": "验证用户登录功能",
                "browser": "chromium",
                "headless": True,
                "viewport_width": 1280,
                "viewport_height": 720,
                "base_url": "https://httpbin.org",
                "steps": [
                    {"type": "navigate", "url": "https://httpbin.org"},
                    {"type": "assert_title", "text": "httpbin"}
                ],
                "timeout": 30000,
                "priority": "P1",
                "status": "active",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        testcase = UITestCase.objects.get(name="测试登录流程")
        self.assertEqual(testcase.browser, "chromium")
        self.assertEqual(testcase.status, "active")

    def test_filter_uitestcases_by_project_and_status(self):
        UITestCase.objects.create(
            project=self.project,
            name="测试用例1",
            browser="chromium",
            status="active",
            created_by=self.admin
        )
        UITestCase.objects.create(
            project=self.project,
            name="测试用例2",
            browser="firefox",
            status="draft",
            created_by=self.admin
        )
        self.client.force_authenticate(self.admin)

        response = self.client.get(
            "/api/ui-tests/",
            {"project": self.project.id, "status": "active"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["count"], 1)

    def test_viewer_cannot_create_uitestcase(self):
        self.client.force_authenticate(self.viewer)

        response = self.client.post(
            "/api/ui-tests/",
            {
                "project": self.project.id,
                "name": "测试用例",
                "browser": "chromium",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
