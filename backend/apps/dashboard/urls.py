from django.urls import path

from apps.dashboard.views import RecentExecutionsView, SummaryView, TrendsView


urlpatterns = [
    path("summary/", SummaryView.as_view(), name="dashboard_summary"),
    path("trends/", TrendsView.as_view(), name="dashboard_trends"),
    path("recent-executions/", RecentExecutionsView.as_view(), name="dashboard_recent_executions"),
]
