from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from apps.executions.models import TestExecution
from apps.reports.models import TestReport
from apps.reports.serializers import GenerateReportSerializer, TestReportSerializer
from apps.reports.tasks import generate_report_task
from core.permissions import IsAdminOrReadOnly
from core.responses import success_response


class TestReportViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TestReportSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = TestReport.objects.select_related("execution__plan")
        execution_id = self.request.query_params.get("execution")
        if execution_id:
            queryset = queryset.filter(execution_id=execution_id)
        return queryset

    @action(detail=False, methods=["post"])
    def generate(self, request):
        """
        生成测试报告（支持同步和异步两种模式）
        
        参数:
            - execution: 执行记录ID（必填）
            - async_mode: 是否异步生成（可选，默认False）
        """
        serializer = GenerateReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        execution_id = serializer.validated_data["execution"]
        async_mode = serializer.validated_data.get("async_mode", False)
        
        execution = get_object_or_404(TestExecution, pk=execution_id)
        
        if async_mode:
            # 异步模式：使用 Celery 任务
            task = generate_report_task.delay(execution_id)
            
            # 更新执行记录的 celery_task_id
            execution.celery_task_id = task.id
            execution.save(update_fields=["celery_task_id"])
            
            return Response({
                "success": True,
                "async_mode": True,
                "task_id": task.id,
                "message": "报告正在异步生成中，请稍后查询状态",
            })
        else:
            # 同步模式：直接生成
            from apps.reports.services import generate_report_for_execution
            report = generate_report_for_execution(execution_id)
            return success_response(TestReportSerializer(report).data)

    @action(detail=False, methods=["get"])
    def task_status(self, request):
        """
        查询异步任务状态
        
        参数:
            - task_id: Celery 任务ID
        """
        task_id = request.query_params.get("task_id")
        if not task_id:
            return Response({"error": "请提供 task_id"}, status=status.HTTP_400_BAD_REQUEST)
        
        from apps.reports.tasks import generate_report_task
        from celery.result import AsyncResult
        
        task_result = AsyncResult(task_id)
        
        return Response({
            "task_id": task_id,
            "status": task_result.status,
            "result": task_result.result if task_result.ready() else None,
        })
