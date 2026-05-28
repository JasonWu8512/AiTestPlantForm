from rest_framework import serializers

from apps.uitests.models import UITestCase, UITestExecution, UITestResult


class UITestCaseSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = UITestCase
        fields = (
            "id",
            "project",
            "project_name",
            "name",
            "description",
            "browser",
            "headless",
            "viewport_width",
            "viewport_height",
            "base_url",
            "steps",
            "timeout",
            "priority",
            "status",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_by", "created_by_name", "created_at", "updated_at")

    def validate_steps(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("测试步骤必须是数组格式。")
        return value


class UITestResultSerializer(serializers.ModelSerializer):
    testcase_name = serializers.CharField(source="testcase.name", read_only=True)
    testcase_browser = serializers.CharField(source="testcase.browser", read_only=True)

    class Meta:
        model = UITestResult
        fields = (
            "id",
            "execution",
            "testcase",
            "testcase_name",
            "testcase_browser",
            "status",
            "screenshot",
            "video_path",
            "logs",
            "error_message",
            "duration",
            "executed_at",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class UITestExecutionSerializer(serializers.ModelSerializer):
    executor_name = serializers.CharField(source="executor.username", read_only=True)
    pass_rate = serializers.FloatField(read_only=True)
    results = UITestResultSerializer(many=True, read_only=True)

    class Meta:
        model = UITestExecution
        fields = (
            "id",
            "project",
            "name",
            "status",
            "total",
            "passed",
            "failed",
            "pass_rate",
            "executor",
            "executor_name",
            "started_at",
            "finished_at",
            "celery_task_id",
            "results",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "executor", "executor_name", "created_at", "updated_at")


class ExecuteUITestSerializer(serializers.Serializer):
    testcase_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="要执行的用例ID列表，为空则执行所有启用的用例"
    )
    async_mode = serializers.BooleanField(default=False, help_text="是否异步执行")
