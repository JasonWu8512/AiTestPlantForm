from rest_framework import serializers

from apps.reports.models import TestReport


class TestReportSerializer(serializers.ModelSerializer):
    execution_status = serializers.CharField(source="execution.status", read_only=True)
    plan_name = serializers.CharField(source="execution.plan.name", read_only=True)

    class Meta:
        model = TestReport
        fields = (
            "id",
            "execution",
            "execution_status",
            "plan_name",
            "name",
            "summary",
            "allure_report_path",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "execution_status", "plan_name", "summary", "status", "created_at", "updated_at")


class GenerateReportSerializer(serializers.Serializer):
    execution = serializers.IntegerField()
    allure_report_path = serializers.CharField(required=False, allow_blank=True)
    async_mode = serializers.BooleanField(required=False, default=False)
