from django.contrib.auth.models import Group, User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.executions.models import TestExecution, TestResult
from apps.projects.models import Project
from apps.testcases.models import TestCase as TestCaseModel
from apps.testplans.models import TestPlan, TestPlanCase


class TestExecutionApiTests(TestCase):
    def setUp(self):
        Group.objects.get_or_create(name="tester")
        self.tester = User.objects.create_user("tester", "tester@example.com", "tester123456")
        self.tester.groups.add(Group.objects.get(name="tester"))
        self.project = Project.objects.create(name="平台项目", created_by=self.tester)
        self.testcase = TestCaseModel.objects.create(project=self.project, title="登录成功", created_by=self.tester)
        self.other_case = TestCaseModel.objects.create(project=self.project, title="未加入计划", created_by=self.tester)
        self.plan = TestPlan.objects.create(project=self.project, name="冒烟测试", created_by=self.tester)
        TestPlanCase.objects.create(plan=self.plan, testcase=self.testcase)
        self.client = APIClient()
        self.client.force_authenticate(self.tester)

    def test_create_start_and_submit_result(self):
        create_response = self.client.post("/api/executions/", {"plan": self.plan.id}, format="json")
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        execution_id = create_response.data["id"]

        start_response = self.client.post(f"/api/executions/{execution_id}/start/")
        self.assertEqual(start_response.status_code, status.HTTP_200_OK)
        self.assertEqual(TestExecution.objects.get(id=execution_id).status, "running")

        result_response = self.client.post(
            f"/api/executions/{execution_id}/results/",
            {
                "testcase": self.testcase.id,
                "status": "passed",
                "actual_result": "登录成功",
                "remark": "",
            },
            format="json",
        )
        self.assertEqual(result_response.status_code, status.HTTP_200_OK)
        self.assertTrue(TestResult.objects.filter(execution_id=execution_id, testcase=self.testcase).exists())

    def test_submit_result_rejects_case_not_in_plan(self):
        execution = TestExecution.objects.create(plan=self.plan, executor=self.tester)

        response = self.client.post(
            f"/api/executions/{execution.id}/results/",
            {"testcase": self.other_case.id, "status": "failed"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
