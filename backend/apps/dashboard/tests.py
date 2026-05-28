from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.executions.models import TestExecution, TestResult
from apps.projects.models import Project
from apps.testcases.models import TestCase as TestCaseModel
from apps.testplans.models import TestPlan, TestPlanCase


class DashboardApiTests(TestCase):
    def setUp(self):
        Group.objects.get_or_create(name="viewer")
        self.viewer = User.objects.create_user("viewer", "viewer@example.com", "viewer123456")
        self.viewer.groups.add(Group.objects.get(name="viewer"))
        project = Project.objects.create(name="平台项目", created_by=self.viewer)
        testcase = TestCaseModel.objects.create(project=project, title="登录成功", created_by=self.viewer)
        plan = TestPlan.objects.create(project=project, name="冒烟测试", created_by=self.viewer)
        TestPlanCase.objects.create(plan=plan, testcase=testcase)
        execution = TestExecution.objects.create(plan=plan, executor=self.viewer, status="completed")
        TestResult.objects.create(
            execution=execution,
            testcase=testcase,
            status="passed",
            executed_by=self.viewer,
            executed_at=timezone.now()
        )
        self.client = APIClient()
        self.client.force_authenticate(self.viewer)

    def test_summary_and_trends(self):
        summary_response = self.client.get("/api/dashboard/summary/")
        trends_response = self.client.get("/api/dashboard/trends/")

        self.assertEqual(summary_response.status_code, status.HTTP_200_OK)
        self.assertEqual(summary_response.data["data"]["project_count"], 1)
        self.assertEqual(trends_response.status_code, status.HTTP_200_OK)
        trends_data = trends_response.data["data"]
        self.assertIsInstance(trends_data, list)
        self.assertEqual(len(trends_data), 1)
        self.assertEqual(trends_data[0]["passed"], 1)
        self.assertEqual(trends_data[0]["total"], 1)
        self.assertEqual(trends_data[0]["pass_rate"], 100.0)
