from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ThreatViewSet, AlertViewSet, RiskAssessmentViewSet,
    ThreatIndicatorViewSet, WatchlistViewSet
)

router = DefaultRouter()
router.register(r'threats', ThreatViewSet, basename='threat')
router.register(r'alerts', AlertViewSet, basename='alert')
router.register(r'risk-assessments', RiskAssessmentViewSet, basename='risk-assessment')
router.register(r'indicators', ThreatIndicatorViewSet, basename='indicator')
router.register(r'watchlists', WatchlistViewSet, basename='watchlist')

urlpatterns = [
    path('', include(router.urls)),
]
