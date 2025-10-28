"""
Access Control Views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Count, Q
from datetime import datetime, timedelta

from .models import (
    AccessPoint,
    AccessSchedule,
    AccessPermission,
    AccessCredential,
    AccessLog,
    AccessAnomaly,
)
from .serializers import (
    AccessPointSerializer,
    AccessScheduleSerializer,
    AccessPermissionSerializer,
    AccessCredentialSerializer,
    AccessLogSerializer,
    AccessAnomalySerializer,
    AccessStatsSerializer,
)


class AccessPointViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Access Points
    """
    serializer_class = AccessPointSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['point_type', 'status', 'location']
    search_fields = ['name', 'location', 'hardware_id']
    ordering_fields = ['name', 'location', 'created_at']

    def get_queryset(self):
        return AccessPoint.objects.filter(organization=self.request.user.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)

    @action(detail=True, methods=['post'])
    def lockdown(self, request, pk=None):
        """Activate lockdown for this access point"""
        access_point = self.get_object()
        access_point.lockdown_enabled = True
        access_point.save()
        return Response({'status': 'lockdown activated'})

    @action(detail=True, methods=['post'])
    def unlock(self, request, pk=None):
        """Deactivate lockdown"""
        access_point = self.get_object()
        access_point.lockdown_enabled = False
        access_point.save()
        return Response({'status': 'lockdown deactivated'})

    @action(detail=False, methods=['get'])
    def status_summary(self, request):
        """Get summary of access point statuses"""
        queryset = self.get_queryset()
        summary = queryset.values('status').annotate(count=Count('id'))
        return Response(summary)


class AccessScheduleViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Access Schedules
    """
    serializer_class = AccessScheduleSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_active']
    search_fields = ['name']

    def get_queryset(self):
        return AccessSchedule.objects.filter(organization=self.request.user.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)


class AccessPermissionViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Access Permissions
    """
    serializer_class = AccessPermissionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['user', 'access_point', 'permission_type', 'is_active', 'is_revoked']
    search_fields = ['user__username', 'access_point__name']
    ordering_fields = ['granted_at', 'valid_from']

    def get_queryset(self):
        return AccessPermission.objects.filter(
            organization=self.request.user.organization
        ).select_related('user', 'access_point', 'schedule', 'granted_by')

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            granted_by=self.request.user
        )

    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """Revoke a permission"""
        permission = self.get_object()
        permission.is_revoked = True
        permission.is_active = False
        permission.revoked_at = timezone.now()
        permission.revoked_by = request.user
        permission.revocation_reason = request.data.get('reason', '')
        permission.save()
        return Response({'status': 'permission revoked'})

    @action(detail=False, methods=['get'])
    def by_user(self, request):
        """Get all permissions for a specific user"""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'user_id required'}, status=400)
        
        permissions = self.get_queryset().filter(user_id=user_id, is_active=True)
        serializer = self.get_serializer(permissions, many=True)
        return Response(serializer.data)


class AccessCredentialViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Access Credentials
    """
    serializer_class = AccessCredentialSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['user', 'credential_type', 'status']
    search_fields = ['user__username', 'credential_id']

    def get_queryset(self):
        return AccessCredential.objects.filter(
            organization=self.request.user.organization
        ).select_related('user')

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a credential"""
        credential = self.get_object()
        credential.status = 'inactive'
        credential.save()
        return Response({'status': 'credential deactivated'})

    @action(detail=True, methods=['post'])
    def report_lost(self, request, pk=None):
        """Report credential as lost/stolen"""
        credential = self.get_object()
        credential.status = 'lost'
        credential.is_locked = True
        credential.notes += f"\nReported lost on {timezone.now()}"
        credential.save()
        return Response({'status': 'credential marked as lost'})


class AccessLogViewSet(viewsets.ModelViewSet):
    """
    Access logs (read-only for most operations)
    """
    serializer_class = AccessLogSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['access_point', 'user', 'event_type', 'is_granted', 'is_anomaly']
    search_fields = ['user__username', 'access_point__name']
    ordering_fields = ['timestamp']
    http_method_names = ['get', 'post', 'head', 'options']  # No PUT/PATCH/DELETE

    def get_queryset(self):
        return AccessLog.objects.filter(
            organization=self.request.user.organization
        ).select_related('access_point', 'user', 'credential')

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent access logs"""
        hours = int(request.query_params.get('hours', 24))
        since = timezone.now() - timedelta(hours=hours)
        logs = self.get_queryset().filter(timestamp__gte=since)
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def anomalies(self, request):
        """Get logs flagged as anomalies"""
        logs = self.get_queryset().filter(is_anomaly=True)
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)


class AccessAnomalyViewSet(viewsets.ModelViewSet):
    """
    Access anomalies detected by AI
    """
    serializer_class = AccessAnomalySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['anomaly_type', 'severity', 'is_reviewed', 'is_false_positive']
    search_fields = ['user__username']
    ordering_fields = ['detected_at', 'confidence_score']

    def get_queryset(self):
        return AccessAnomaly.objects.filter(
            organization=self.request.user.organization
        ).select_related('access_log', 'user', 'reviewed_by')

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)

    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        """Mark anomaly as reviewed"""
        anomaly = self.get_object()
        anomaly.is_reviewed = True
        anomaly.reviewed_by = request.user
        anomaly.reviewed_at = timezone.now()
        anomaly.is_false_positive = request.data.get('is_false_positive', False)
        anomaly.review_notes = request.data.get('notes', '')
        anomaly.save()
        return Response({'status': 'anomaly reviewed'})

    @action(detail=False, methods=['get'])
    def unreviewed(self, request):
        """Get unreviewed anomalies"""
        anomalies = self.get_queryset().filter(is_reviewed=False)
        serializer = self.get_serializer(anomalies, many=True)
        return Response(serializer.data)


class AccessStatsViewSet(viewsets.ViewSet):
    """
    Access control statistics and analytics
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get access control statistics summary"""
        org = request.user.organization
        today = timezone.now().date()

        stats = {
            'total_access_points': AccessPoint.objects.filter(organization=org).count(),
            'active_points': AccessPoint.objects.filter(organization=org, status='active').count(),
            'total_permissions': AccessPermission.objects.filter(organization=org).count(),
            'active_permissions': AccessPermission.objects.filter(
                organization=org,
                is_active=True,
                is_revoked=False
            ).count(),
            'today_logs': AccessLog.objects.filter(
                organization=org,
                timestamp__date=today
            ).count(),
            'today_granted': AccessLog.objects.filter(
                organization=org,
                timestamp__date=today,
                is_granted=True
            ).count(),
            'today_denied': AccessLog.objects.filter(
                organization=org,
                timestamp__date=today,
                is_granted=False
            ).count(),
            'today_anomalies': AccessAnomaly.objects.filter(
                organization=org,
                detected_at__date=today
            ).count(),
            'top_access_points': list(
                AccessLog.objects.filter(organization=org, timestamp__date=today)
                .values('access_point__name')
                .annotate(count=Count('id'))
                .order_by('-count')[:5]
            ),
            'access_by_hour': {}
        }

        serializer = AccessStatsSerializer(stats)
        return Response(serializer.data)
