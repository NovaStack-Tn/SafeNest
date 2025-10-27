"""
URL routing for security app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoginEventViewSet, AnomalyRuleViewSet, AlertViewSet

router = DefaultRouter()
router.register(r'login-events', LoginEventViewSet, basename='login-event')
router.register(r'anomaly-rules', AnomalyRuleViewSet, basename='anomaly-rule')
router.register(r'alerts', AlertViewSet, basename='alert')

urlpatterns = [
    path('', include(router.urls)),
]
