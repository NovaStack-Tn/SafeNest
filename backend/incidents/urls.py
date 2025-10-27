"""
URL routing for incidents app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IncidentViewSet, IncidentEventViewSet, EvidenceViewSet

router = DefaultRouter()
router.register(r'incidents', IncidentViewSet, basename='incident')
router.register(r'incident-events', IncidentEventViewSet, basename='incident-event')
router.register(r'evidence', EvidenceViewSet, basename='evidence')

urlpatterns = [
    path('', include(router.urls)),
]
