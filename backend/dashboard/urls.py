"""
URL routing for dashboard app.
"""
from django.urls import path
from .views import DashboardStatsView, RecentActivityView, RiskMapView

urlpatterns = [
    path('stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('activity/', RecentActivityView.as_view(), name='recent-activity'),
    path('risk-map/', RiskMapView.as_view(), name='risk-map'),
]
