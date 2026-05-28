from rest_framework import serializers

from apps.testcases.serializers import TestCaseSerializer
from apps.testplans.models import TestPlan, TestPlanCase


class TestPlanCaseSerializer(serializers.ModelSerializer):
    testcase_detail = TestCaseSerializer(source="testcase", read_only=True)

    class Meta:
        model = TestPlanCase
        fields = ("id", "plan", "testcase", "testcase_detail", "sort_order", "created_at")
        read_only_fields = ("id", "plan", "testcase_detail", "created_at")


class TestPlanSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)
    cases = TestPlanCaseSerializer(source="plan_cases", many=True, read_only=True)

    class Meta:
        model = TestPlan
        fields = (
            "id",
            "project",
            "project_name",
            "name",
            "description",
            "status",
            "start_time",
            "end_time",
            "created_by",
            "created_by_name",
            "cases",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_by", "created_by_name", "cases", "created_at", "updated_at")


class AddPlanCaseSerializer(serializers.Serializer):
    testcase = serializers.IntegerField()
    sort_order = serializers.IntegerField(required=False, min_value=0)
