"""
URL routing for Visitor & Asset Management API
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VisitorViewSet,
    VisitorPassViewSet,
    AssetViewSet,
    AssetAssignmentViewSet,
    MovementLogViewSet
)

router = DefaultRouter()
router.register(r'visitors', VisitorViewSet, basename='visitor')
router.register(r'visitor-passes', VisitorPassViewSet, basename='visitorpass')
router.register(r'assets', AssetViewSet, basename='asset')
router.register(r'asset-assignments', AssetAssignmentViewSet, basename='assetassignment')
router.register(r'movements', MovementLogViewSet, basename='movementlog')

urlpatterns = [
    path('', include(router.urls)),
]
