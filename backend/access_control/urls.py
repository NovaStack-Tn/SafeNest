from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AccessPointViewSet,
    AccessScheduleViewSet,
    AccessPermissionViewSet,
    AccessCredentialViewSet,
    AccessLogViewSet,
    AccessAnomalyViewSet,
    AccessStatsViewSet,
)

router = DefaultRouter()
router.register(r'access-points', AccessPointViewSet, basename='access-point')
router.register(r'schedules', AccessScheduleViewSet, basename='access-schedule')
router.register(r'permissions', AccessPermissionViewSet, basename='access-permission')
router.register(r'credentials', AccessCredentialViewSet, basename='access-credential')
router.register(r'access-logs', AccessLogViewSet, basename='access-log')
router.register(r'access-anomalies', AccessAnomalyViewSet, basename='access-anomaly')
router.register(r'stats', AccessStatsViewSet, basename='access-stats')

urlpatterns = [
    path('', include(router.urls)),
]
