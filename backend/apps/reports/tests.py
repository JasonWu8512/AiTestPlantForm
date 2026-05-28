import json
import tempfile
from pathlib import Path

from django.contrib.auth.models import Group, User
from django.test import TestCase, RequestFactory
from rest_framework import status
from rest_framework.test import APIClient

from apps.executions.models import TestExecution, TestResult
from apps.projects.models import Project
from apps.reports.views_allure import AllureReportView
from apps.testcases.models import TestCase as TestCaseModel
from apps.testplans.models import TestPlan, TestPlanCase


class AllureReportViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = AllureReportView()

    def test_process_result_passed(self):
        result_data = {
            "status": "passed",
            "testCaseName": "测试用例1",
            "fullName": "test_module.TestClass.test_method1"
        }
        
        processed = self.view._process_result(result_data)
        
        self.assertEqual(processed['status'], 'passed')
        self.assertEqual(processed['status_class'], 'success')
        self.assertEqual(processed['test_name'], '测试用例1')
        self.assertEqual(processed['message'], '')

    def test_process_result_failed(self):
        result_data = {
            "status": "failed",
            "testCaseName": "失败测试",
            "statusDetails": {
                "message": "AssertionError: expected 200 but got 500"
            }
        }
        
        processed = self.view._process_result(result_data)
        
        self.assertEqual(processed['status'], 'failed')
        self.assertEqual(processed['status_class'], 'danger')
        self.assertEqual(processed['test_name'], '失败测试')
        self.assertIn('AssertionError', processed['message'])

    def test_process_result_unknown_status(self):
        result_data = {
            "status": "unknown",
            "fullName": "test_module.TestClass.test_method"
        }
        
        processed = self.view._process_result(result_data)
        
        self.assertEqual(processed['status'], 'unknown')
        self.assertEqual(processed['status_class'], 'secondary')
        self.assertEqual(processed['test_name'], 'test_module.TestClass.test_method')

    def test_calculate_stats_with_results(self):
        results = [
            {'status': 'passed'},
            {'status': 'passed'},
            {'status': 'failed'},
            {'status': 'blocked'},
            {'status': 'skipped'}
        ]
        
        stats = self.view._calculate_stats(results)
        
        self.assertEqual(stats['total'], 5)
        self.assertEqual(stats['passed'], 2)
        self.assertEqual(stats['failed'], 1)
        self.assertEqual(stats['blocked'], 1)
        self.assertEqual(stats['skipped'], 1)
        self.assertEqual(stats['pass_rate'], 40.0)

    def test_calculate_stats_empty_results(self):
        stats = self.view._calculate_stats([])
        
        self.assertEqual(stats['total'], 0)
        self.assertEqual(stats['passed'], 0)
        self.assertEqual(stats['failed'], 0)
        self.assertEqual(stats['blocked'], 0)
        self.assertEqual(stats['skipped'], 0)
        self.assertEqual(stats['pass_rate'], 0)

    def test_get_view_empty_results(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            results_dir = Path(tmpdir) / "allure-results" / "123"
            results_dir.mkdir(parents=True)
            
            from django.conf import settings
            original_media_root = settings.MEDIA_ROOT
            settings.MEDIA_ROOT = tmpdir
            
            try:
                request = self.factory.get('/reports/allure/123/')
                response = self.view.get(request, '123')
                
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, '暂无测试结果')
            finally:
                settings.MEDIA_ROOT = original_media_root


class TestReportApiTests(TestCase):
    def setUp(self):
        Group.objects.get_or_create(name="tester")
        self.tester = User.objects.create_user("tester", "tester@example.com", "tester123456")
        self.tester.groups.add(Group.objects.get(name="tester"))
        self.project = Project.objects.create(name="平台项目", created_by=self.tester)
        self.testcase = TestCaseModel.objects.create(project=self.project, title="登录成功", created_by=self.tester)
        self.plan = TestPlan.objects.create(project=self.project, name="冒烟测试", created_by=self.tester)
        TestPlanCase.objects.create(plan=self.plan, testcase=self.testcase)
        self.execution = TestExecution.objects.create(plan=self.plan, executor=self.tester, status="completed")
        TestResult.objects.create(execution=self.execution, testcase=self.testcase, status="passed", executed_by=self.tester)
        self.client = APIClient()
        self.client.force_authenticate(self.tester)

    def test_generate_report(self):
        response = self.client.post(
            "/api/reports/generate/",
            {"execution": self.execution.id, "allure_report_path": "/reports/demo/index.html"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["summary"]["passed"], 1)
        self.assertEqual(response.data["data"]["summary"]["pass_rate"], 100)
