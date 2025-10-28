"""
Threat Intelligence Management URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ThreatViewSet,
    AlertViewSet,
    RiskAssessmentViewSet,
    ThreatIndicatorViewSet,
    WatchlistViewSet,
    ThreatFeedViewSet,
    ThreatHuntingQueryViewSet,
    AnomalyDetectionViewSet,
    ThreatScoringViewSet,
    PredictiveAnalyticsViewSet,
    AlertAggregationViewSet,
    ThreatHuntingViewSet
)

app_name = 'threat_intelligence'

# Create router for standard CRUD operations
router = DefaultRouter()
router.register(r'threats', ThreatViewSet, basename='threat')
router.register(r'alerts', AlertViewSet, basename='alert')
router.register(r'risk-assessments', RiskAssessmentViewSet, basename='risk-assessment')
router.register(r'indicators', ThreatIndicatorViewSet, basename='indicator')
router.register(r'watchlist', WatchlistViewSet, basename='watchlist')
router.register(r'feeds', ThreatFeedViewSet, basename='feed')
router.register(r'hunting-queries', ThreatHuntingQueryViewSet, basename='hunting-query')

# AI Service endpoints
router.register(r'ai/anomaly-detection', AnomalyDetectionViewSet, basename='anomaly-detection')
router.register(r'ai/threat-scoring', ThreatScoringViewSet, basename='threat-scoring')
router.register(r'ai/predictive-analytics', PredictiveAnalyticsViewSet, basename='predictive-analytics')
router.register(r'ai/alert-aggregation', AlertAggregationViewSet, basename='alert-aggregation')
router.register(r'ai/threat-hunting', ThreatHuntingViewSet, basename='threat-hunting')

urlpatterns = [
    path('', include(router.urls)),
]
