"""
URL routing for incidents app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    IncidentViewSet, IncidentEventViewSet, EvidenceViewSet,
    IncidentCategoryViewSet, IncidentResolutionViewSet
)

router = DefaultRouter()
router.register(r'incidents', IncidentViewSet, basename='incident')
router.register(r'incident-events', IncidentEventViewSet, basename='incident-event')
router.register(r'evidence', EvidenceViewSet, basename='evidence')
router.register(r'categories', IncidentCategoryViewSet, basename='incident-category')
router.register(r'resolutions', IncidentResolutionViewSet, basename='incident-resolution')

urlpatterns = [
    path('', include(router.urls)),
]
