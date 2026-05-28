from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationConfigViewSet, NotificationRecordViewSet

router = DefaultRouter()
router.register(r'configs', NotificationConfigViewSet)
router.register(r'records', NotificationRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
]