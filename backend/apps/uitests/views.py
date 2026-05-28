from django.utils import timezone
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.uitests.models import UITestCase, UITestExecution, UITestResult
from apps.uitests.serializers import (
    UITestCaseSerializer,
    UITestExecutionSerializer,
    UITestResultSerializer,
    ExecuteUITestSerializer,
)
from apps.uitests.services import UITestSuiteExecutor
from apps.uitests.tasks import run_ui_tests_task
from core.permissions import IsAdminOrReadOnly
from core.responses import success_response


class UITestCaseViewSet(viewsets.ModelViewSet):
    serializer_class = UITestCaseSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "description"]

    def get_queryset(self):
        queryset = UITestCase.objects.select_related("project", "created_by").all()
        project_id = self.request.query_params.get("project")
        priority = self.request.query_params.get("priority")
        status_filter = self.request.query_params.get("status")
        browser = self.request.query_params.get("browser")

        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if priority:
            queryset = queryset.filter(priority=priority)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if browser:
            queryset = queryset.filter(browser=browser)

        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=["post"])
    def execute(self, request):
        serializer = ExecuteUITestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        project_id = request.data.get("project")
        testcase_ids = serializer.validated_data.get("testcase_ids", [])
        async_mode = serializer.validated_data.get("async_mode", False)

        if not project_id:
            return Response(
                {"code": 400, "message": "请指定项目ID", "data": None},
                status=status.HTTP_400_BAD_REQUEST
            )

        if testcase_ids:
            testcases = UITestCase.objects.filter(id__in=testcase_ids, project_id=project_id, status="active")
        else:
            testcases = UITestCase.objects.filter(project_id=project_id, status="active")

        testcases = list(testcases)
        if not testcases:
            return Response(
                {"code": 404, "message": "没有找到可执行的用例", "data": None},
                status=status.HTTP_404_NOT_FOUND
            )

        execution = UITestExecution.objects.create(
            project_id=project_id,
            name=f"UI测试执行 {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}",
            total=len(testcases),
            executor=request.user,
        )

        if async_mode:
            task = run_ui_tests_task.delay(execution.id, testcase_ids)
            return success_response({
                "execution_id": execution.id,
                "task_id": task.id,
                "async_mode": True,
            })
        else:
            execution.status = "running"
            execution.started_at = timezone.now()
            execution.save()

            suite_executor = UITestSuiteExecutor(testcases)
            results = suite_executor.execute_all()

            passed_count = 0
            failed_count = 0

            for result in results:
                testcase_id = result.pop("testcase_id")
                UITestResult.objects.create(
                    execution=execution,
                    testcase_id=testcase_id,
                    status=result["status"],
                    screenshot=result.get("screenshot", ""),
                    video_path=result.get("video_path", ""),
                    logs=result.get("logs", ""),
                    error_message=result.get("error_message", ""),
                    duration=result.get("duration"),
                    executed_at=result.get("executed_at"),
                )

                if result["status"] == "passed":
                    passed_count += 1
                else:
                    failed_count += 1

            execution.passed = passed_count
            execution.failed = failed_count
            execution.status = "completed"
            execution.finished_at = timezone.now()
            execution.save()

            return success_response({
                "execution_id": execution.id,
                "total": len(testcases),
                "passed": passed_count,
                "failed": failed_count,
                "pass_rate": execution.pass_rate,
                "async_mode": False,
            })


class UITestExecutionViewSet(viewsets.ModelViewSet):
    serializer_class = UITestExecutionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = UITestExecution.objects.select_related("project", "executor").prefetch_related("results").all()
        project_id = self.request.query_params.get("project")
        status_value = self.request.query_params.get("status")

        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if status_value:
            queryset = queryset.filter(status=status_value)

        return queryset

    def perform_create(self, serializer):
        serializer.save(executor=self.request.user)

    @action(detail=True, methods=["get"])
    def results(self, request, pk=None):
        execution = self.get_object()
        results = execution.results.select_related("testcase").all()
        serializer = UITestResultSerializer(results, many=True)
        return success_response(serializer.data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        execution = self.get_object()
        if execution.status not in ["pending", "running"]:
            return Response(
                {"code": 400, "message": "当前状态不允许取消", "data": None},
                status=status.HTTP_400_BAD_REQUEST
            )

        execution.status = "canceled"
        execution.finished_at = timezone.now()
        execution.save(update_fields=["status", "finished_at", "updated_at"])

        return success_response(UITestExecutionSerializer(execution).data)
