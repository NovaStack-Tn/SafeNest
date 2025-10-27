"""
API views for security app.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import LoginEvent, AnomalyRule, Alert
from .serializers import (
    LoginEventSerializer, AnomalyRuleSerializer,
    AlertSerializer, AlertCreateSerializer
)


class LoginEventViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for login events (read-only)."""
    queryset = LoginEvent.objects.select_related('user')
    serializer_class = LoginEventSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'success', 'is_anomaly', 'country_code', 'device_type']
    ordering_fields = ['timestamp', 'risk_score']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        """Filter by organization for non-admin users."""
        user = self.request.user
        queryset = super().get_queryset()
        
        if not user.is_staff and user.organization:
            queryset = queryset.filter(user__organization=user.organization)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def anomalies(self, request):
        """Get only anomalous login events."""
        queryset = self.filter_queryset(
            self.get_queryset().filter(is_anomaly=True)
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AnomalyRuleViewSet(viewsets.ModelViewSet):
    """API endpoint for anomaly rules."""
    queryset = AnomalyRule.objects.select_related('organization', 'created_by')
    serializer_class = AnomalyRuleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['organization', 'rule_type', 'active', 'severity']
    search_fields = ['name', 'description']
    
    def get_queryset(self):
        """Filter by organization for non-admin users."""
        user = self.request.user
        queryset = super().get_queryset()
        
        if not user.is_staff and user.organization:
            queryset = queryset.filter(organization=user.organization)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set created_by to current user."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle rule active status."""
        rule = self.get_object()
        rule.active = not rule.active
        rule.save()
        
        return Response({
            'id': rule.id,
            'active': rule.active,
            'message': f"Rule {'activated' if rule.active else 'deactivated'}"
        })


class AlertViewSet(viewsets.ModelViewSet):
    """API endpoint for alerts."""
    queryset = Alert.objects.select_related(
        'organization', 'triggered_by_rule', 'assigned_to', 'created_by'
    )
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['organization', 'severity', 'status', 'assigned_to']
    search_fields = ['title', 'message']
    ordering_fields = ['created_at', 'severity']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AlertCreateSerializer
        return AlertSerializer
    
    def get_queryset(self):
        """Filter by organization for non-admin users."""
        user = self.request.user
        queryset = super().get_queryset()
        
        if not user.is_staff and user.organization:
            queryset = queryset.filter(organization=user.organization)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set created_by to current user."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign alert to a user."""
        alert = self.get_object()
        user_id = request.data.get('user_id')
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            user = User.objects.get(id=user_id)
            alert.assigned_to = user
            alert.status = 'investigating'
            alert.save()
            
            return Response({
                'id': alert.id,
                'assigned_to': user.get_full_name(),
                'message': 'Alert assigned successfully'
            })
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark alert as resolved."""
        alert = self.get_object()
        alert.status = 'resolved'
        alert.resolved_at = timezone.now()
        alert.save()
        
        return Response({
            'id': alert.id,
            'status': alert.status,
            'message': 'Alert resolved successfully'
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get alert statistics."""
        user = request.user
        queryset = self.get_queryset()
        
        stats = {
            'total': queryset.count(),
            'open': queryset.filter(status='open').count(),
            'investigating': queryset.filter(status='investigating').count(),
            'resolved': queryset.filter(status='resolved').count(),
            'by_severity': {
                'low': queryset.filter(severity='low').count(),
                'medium': queryset.filter(severity='medium').count(),
                'high': queryset.filter(severity='high').count(),
                'critical': queryset.filter(severity='critical').count(),
            }
        }
        
        return Response(stats)
