from django.utils import timezone
from rest_framework import serializers

from apps.executions.models import TestExecution, TestResult
from apps.testplans.serializers import TestPlanSerializer


class TestResultSerializer(serializers.ModelSerializer):
    testcase_title = serializers.CharField(source="testcase.title", read_only=True)
    executed_by_name = serializers.CharField(source="executed_by.username", read_only=True)

    class Meta:
        model = TestResult
        fields = (
            "id",
            "execution",
            "testcase",
            "testcase_title",
            "status",
            "actual_result",
            "remark",
            "attachments",
            "executed_by",
            "executed_by_name",
            "executed_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "execution", "executed_by", "executed_by_name", "executed_at", "created_at", "updated_at")


class TestExecutionSerializer(serializers.ModelSerializer):
    plan_detail = TestPlanSerializer(source="plan", read_only=True)
    executor_name = serializers.CharField(source="executor.username", read_only=True)
    results = TestResultSerializer(many=True, read_only=True)

    class Meta:
        model = TestExecution
        fields = (
            "id",
            "plan",
            "plan_detail",
            "executor",
            "executor_name",
            "status",
            "started_at",
            "finished_at",
            "celery_task_id",
            "results",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "executor", "executor_name", "celery_task_id", "results", "created_at", "updated_at")


class SubmitResultSerializer(serializers.Serializer):
    testcase = serializers.IntegerField()
    status = serializers.ChoiceField(choices=("passed", "failed", "blocked", "skipped"))
    actual_result = serializers.CharField(required=False, allow_blank=True)
    remark = serializers.CharField(required=False, allow_blank=True)
    attachments = serializers.ListField(required=False)

    def save_result(self, execution, user):
        data = self.validated_data
        result, _ = TestResult.objects.update_or_create(
            execution=execution,
            testcase_id=data["testcase"],
            defaults={
                "status": data["status"],
                "actual_result": data.get("actual_result", ""),
                "remark": data.get("remark", ""),
                "attachments": data.get("attachments", []),
                "executed_by": user,
                "executed_at": timezone.now(),
            },
        )
        return result
