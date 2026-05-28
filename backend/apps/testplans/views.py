from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.testcases.models import TestCase
from apps.testplans.models import TestPlan, TestPlanCase
from apps.testplans.serializers import AddPlanCaseSerializer, TestPlanCaseSerializer, TestPlanSerializer
from core.permissions import IsAdminOrReadOnly
from core.responses import success_response


class TestPlanViewSet(viewsets.ModelViewSet):
    serializer_class = TestPlanSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "description"]

    def get_queryset(self):
        queryset = TestPlan.objects.select_related("project", "created_by").prefetch_related("plan_cases__testcase")
        project_id = self.request.query_params.get("project")
        status_value = self.request.query_params.get("status")
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if status_value:
            queryset = queryset.filter(status=status_value)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"], url_path="cases")
    def add_case(self, request, pk=None):
        plan = self.get_object()
        serializer = AddPlanCaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        testcase = get_object_or_404(TestCase, pk=serializer.validated_data["testcase"], project=plan.project)
        sort_order = serializer.validated_data.get("sort_order")
        if sort_order is None:
            sort_order = plan.plan_cases.count()
        plan_case, created = TestPlanCase.objects.get_or_create(
            plan=plan,
            testcase=testcase,
            defaults={"sort_order": sort_order},
        )
        if not created:
            return Response({"code": 400, "message": "该用例已在计划中。", "data": None}, status=status.HTTP_400_BAD_REQUEST)
        return success_response(TestPlanCaseSerializer(plan_case).data)

    @action(detail=True, methods=["delete"], url_path=r"cases/(?P<case_id>[^/.]+)")
    def remove_case(self, request, pk=None, case_id=None):
        plan = self.get_object()
        deleted, _ = TestPlanCase.objects.filter(plan=plan, testcase_id=case_id).delete()
        if not deleted:
            return Response({"code": 404, "message": "计划中不存在该用例。", "data": None}, status=status.HTTP_404_NOT_FOUND)
        return success_response(message="removed")

    @action(detail=True, methods=["post"], url_path="cases/reorder")
    def reorder_cases(self, request, pk=None):
        plan = self.get_object()
        cases = request.data.get("cases", [])
        for index, case_id in enumerate(cases):
            TestPlanCase.objects.filter(plan=plan, testcase_id=case_id).update(sort_order=index)
        return success_response(message="reordered")
