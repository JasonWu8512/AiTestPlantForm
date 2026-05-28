from rest_framework import serializers

from apps.apitests.models import ApiTestCase, ApiTestExecution, ApiTestResult


class ApiTestCaseSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = ApiTestCase
        fields = (
            "id",
            "project",
            "project_name",
            "name",
            "description",
            "method",
            "url",
            "headers",
            "params",
            "body_type",
            "body",
            "expected_status",
            "validation_rules",
            "timeout",
            "priority",
            "status",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_by", "created_by_name", "created_at", "updated_at")

    def validate_headers(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("请求头必须是字典格式。")
        return value

    def validate_params(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("URL参数必须是字典格式。")
        return value

    def validate_body(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("请求体必须是字典格式。")
        return value

    def validate_validation_rules(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("验证规则必须是数组格式。")
        return value


class ApiTestResultSerializer(serializers.ModelSerializer):
    testcase_name = serializers.CharField(source="testcase.name", read_only=True)
    testcase_method = serializers.CharField(source="testcase.method", read_only=True)
    testcase_url = serializers.CharField(source="testcase.url", read_only=True)

    class Meta:
        model = ApiTestResult
        fields = (
            "id",
            "execution",
            "testcase",
            "testcase_name",
            "testcase_method",
            "testcase_url",
            "status",
            "response_status",
            "response_body",
            "response_time",
            "validation_results",
            "error_message",
            "executed_at",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class ApiTestExecutionSerializer(serializers.ModelSerializer):
    executor_name = serializers.CharField(source="executor.username", read_only=True)
    pass_rate = serializers.FloatField(read_only=True)
    results = ApiTestResultSerializer(many=True, read_only=True)

    class Meta:
        model = ApiTestExecution
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


class ExecuteApiTestSerializer(serializers.Serializer):
    testcase_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="要执行的用例ID列表，为空则执行所有启用的用例"
    )
    async_mode = serializers.BooleanField(default=False, help_text="是否异步执行")
