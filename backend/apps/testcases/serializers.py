from rest_framework import serializers

from apps.testcases.models import TestCase


class TestCaseSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = TestCase
        fields = (
            "id",
            "project",
            "project_name",
            "title",
            "description",
            "precondition",
            "steps",
            "expected_result",
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
            raise serializers.ValidationError("测试步骤必须是数组。")
        return value
