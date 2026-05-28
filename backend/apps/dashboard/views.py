from django.db.models import Count
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.executions.models import TestExecution, TestResult
from apps.projects.models import Project
from apps.testcases.models import TestCase
from apps.testplans.models import TestPlan
from core.responses import success_response


class SummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return success_response(
            {
                "project_count": Project.objects.count(),
                "testcase_count": TestCase.objects.count(),
                "testplan_count": TestPlan.objects.count(),
                "execution_count": TestExecution.objects.count(),
            }
        )


class TrendsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.db.models import Count, Case, When, F
        from django.db.models.functions import TruncDate
        
        trends = (
            TestResult.objects
            .annotate(date=TruncDate("executed_at"))
            .values("date")
            .annotate(
                total=Count("id"),
                passed=Count(Case(When(status="passed", then=1)))
            )
            .filter(date__isnull=False)
            .order_by("date")[:14]
        )
        
        result = []
        for item in trends:
            pass_rate = round((item["passed"] / item["total"]) * 100, 1) if item["total"] > 0 else 0
            result.append({
                "date": item["date"].strftime("%Y-%m-%d"),
                "total": item["total"],
                "passed": item["passed"],
                "pass_rate": pass_rate
            })
        
        return success_response(result)


class RecentExecutionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        executions = TestExecution.objects.select_related("plan", "executor").order_by("-created_at")[:10]
        return success_response(
            [
                {
                    "id": item.id,
                    "plan_name": item.plan.name,
                    "executor_name": item.executor.username if item.executor else "",
                    "status": item.status,
                    "created_at": item.created_at,
                }
                for item in executions
            ]
        )
