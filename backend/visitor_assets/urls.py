from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VisitorViewSet,
    VisitorPassViewSet,
    AssetViewSet,
    AssetAssignmentViewSet,
    MovementLogViewSet,
    VisitorAnalyticsViewSet,
    StatsViewSet,
)

router = DefaultRouter()
router.register(r'visitors', VisitorViewSet, basename='visitor')
router.register(r'passes', VisitorPassViewSet, basename='visitor-pass')
router.register(r'assets', AssetViewSet, basename='asset')
router.register(r'assignments', AssetAssignmentViewSet, basename='asset-assignment')
router.register(r'movements', MovementLogViewSet, basename='movement-log')
router.register(r'analytics', VisitorAnalyticsViewSet, basename='visitor-analytics')
router.register(r'stats', StatsViewSet, basename='stats')

urlpatterns = [
    path('', include(router.urls)),
]
