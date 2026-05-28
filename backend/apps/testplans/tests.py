from django.contrib.auth.models import Group, User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.projects.models import Project
from apps.testcases.models import TestCase as TestCaseModel
from apps.testplans.models import TestPlan, TestPlanCase


class TestPlanApiTests(TestCase):
    def setUp(self):
        Group.objects.get_or_create(name="tester")
        self.tester = User.objects.create_user("tester", "tester@example.com", "tester123456")
        self.tester.groups.add(Group.objects.get(name="tester"))
        self.project = Project.objects.create(name="平台项目", created_by=self.tester)
        self.testcase = TestCaseModel.objects.create(project=self.project, title="登录成功", created_by=self.tester)
        self.client = APIClient()
        self.client.force_authenticate(self.tester)

    def test_create_plan_and_add_case(self):
        plan_response = self.client.post(
            "/api/testplans/",
            {"project": self.project.id, "name": "冒烟测试", "status": "active"},
            format="json",
        )
        self.assertEqual(plan_response.status_code, status.HTTP_201_CREATED)

        add_response = self.client.post(
            f"/api/testplans/{plan_response.data['id']}/cases/",
            {"testcase": self.testcase.id, "sort_order": 1},
            format="json",
        )
        self.assertEqual(add_response.status_code, status.HTTP_200_OK)
        self.assertTrue(TestPlanCase.objects.filter(plan_id=plan_response.data["id"], testcase=self.testcase).exists())

    def test_duplicate_case_in_plan_is_rejected(self):
        plan = TestPlan.objects.create(project=self.project, name="冒烟测试", created_by=self.tester)
        TestPlanCase.objects.create(plan=plan, testcase=self.testcase)

        response = self.client.post(
            f"/api/testplans/{plan.id}/cases/",
            {"testcase": self.testcase.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
