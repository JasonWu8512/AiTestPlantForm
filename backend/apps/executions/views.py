from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.executions.models import TestExecution
from apps.executions.serializers import SubmitResultSerializer, TestExecutionSerializer, TestResultSerializer
from core.permissions import IsAdminOrReadOnly
from core.responses import success_response


class TestExecutionViewSet(viewsets.ModelViewSet):
    serializer_class = TestExecutionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = TestExecution.objects.select_related("plan", "executor").prefetch_related("results__testcase")
        plan_id = self.request.query_params.get("plan")
        status_value = self.request.query_params.get("status")
        if plan_id:
            queryset = queryset.filter(plan_id=plan_id)
        if status_value:
            queryset = queryset.filter(status=status_value)
        return queryset

    def perform_create(self, serializer):
        serializer.save(executor=self.request.user)

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        execution = self.get_object()
        execution.status = "running"
        execution.started_at = execution.started_at or timezone.now()
        execution.save(update_fields=["status", "started_at", "updated_at"])
        return success_response(TestExecutionSerializer(execution).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        execution = self.get_object()
        execution.status = "canceled"
        execution.finished_at = timezone.now()
        execution.save(update_fields=["status", "finished_at", "updated_at"])
        return success_response(TestExecutionSerializer(execution).data)

    @action(detail=True, methods=["post"])
    def results(self, request, pk=None):
        execution = self.get_object()
        serializer = SubmitResultSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not execution.plan.plan_cases.filter(testcase_id=serializer.validated_data["testcase"]).exists():
            return Response({"code": 400, "message": "该用例不属于当前测试计划。", "data": None}, status=status.HTTP_400_BAD_REQUEST)
        result = serializer.save_result(execution, request.user)
        return success_response(TestResultSerializer(result).data)
