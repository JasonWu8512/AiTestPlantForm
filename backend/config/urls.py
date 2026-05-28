from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from apps.executions.views import TestExecutionViewSet
from apps.projects.views import ProjectViewSet
from apps.reports.views import TestReportViewSet
from apps.reports.views_allure import AllureReportView
from apps.testcases.views import TestCaseViewSet
from apps.testplans.views import TestPlanViewSet
from apps.users.views import UserViewSet
from apps.apitests.views import ApiTestCaseViewSet, ApiTestExecutionViewSet
from apps.uitests.views import UITestCaseViewSet, UITestExecutionViewSet


router = DefaultRouter()
router.register("projects", ProjectViewSet, basename="projects")
router.register("testcases", TestCaseViewSet, basename="testcases")
router.register("testplans", TestPlanViewSet, basename="testplans")
router.register("executions", TestExecutionViewSet, basename="executions")
router.register("reports", TestReportViewSet, basename="reports")
router.register("users", UserViewSet, basename="users")
router.register("api-tests", ApiTestCaseViewSet, basename="api-tests")
router.register("api-test-executions", ApiTestExecutionViewSet, basename="api-test-executions")
router.register("ui-tests", UITestCaseViewSet, basename="ui-tests")
router.register("ui-test-executions", UITestExecutionViewSet, basename="ui-test-executions")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/auth/", include("apps.users.urls")),
    path("api/dashboard/", include("apps.dashboard.urls")),
    path("api/notifications/", include("apps.notifications.urls")),
    path("api/", include(router.urls)),
    path("allure-report/<int:execution_id>/", AllureReportView.as_view(), name="allure-report"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
