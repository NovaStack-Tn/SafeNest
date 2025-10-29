"""
Access Control Views
"""
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Count, Q
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

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
        access_log = serializer.save(organization=self.request.user.organization)
        
        # Automatic AI anomaly detection for granted accesses
        if access_log.user and access_log.is_granted:
            self._detect_anomalies(access_log)
    
    def _detect_anomalies(self, access_log):
        """Detect anomalies using AI"""
        from .ai_service import AccessAnomalyDetector
        
        try:
            detector = AccessAnomalyDetector(access_log.organization)
            anomaly = detector.analyze_user_access(access_log.user, access_log)
            
            if anomaly:
                # Create anomaly record
                AccessAnomaly.objects.create(
                    organization=access_log.organization,
                    access_log=access_log,
                    user=access_log.user,
                    anomaly_type=anomaly['type'],
                    severity=anomaly['severity'],
                    confidence_score=anomaly['confidence'],
                    description=anomaly['description'],
                    baseline_pattern=anomaly['baseline'],
                    detected_pattern=anomaly['detected']
                )
                
                # Update access log
                access_log.is_anomaly = True
                access_log.anomaly_score = anomaly['confidence']
                access_log.save()
                
                logger.info(f"Anomaly detected: {anomaly['type']} for user {access_log.user.username}")
                
        except Exception as e:
            # Don't fail the request if anomaly detection fails
            logger.error(f"Anomaly detection failed: {e}")

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

        # Get hourly access distribution
        from django.db.models.functions import ExtractHour
        hour_distribution = AccessLog.objects.filter(
            organization=org,
            timestamp__date=today
        ).annotate(hour=ExtractHour('timestamp')).values('hour').annotate(
            count=Count('id')
        ).order_by('hour')
        
        access_by_hour = {str(item['hour']): item['count'] for item in hour_distribution}

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
            'access_by_hour': access_by_hour
        }

        serializer = AccessStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Advanced analytics with AI predictions"""
        from .ai_service import AccessPredictor
        
        org = request.user.organization
        predictor = AccessPredictor(org)
        
        # Get busy hours prediction
        busy_hours = predictor.predict_busy_hours()
        
        # Get optimization suggestions
        suggestions = predictor.suggest_access_optimizations()
        
        # Weekly trend
        seven_days_ago = timezone.now() - timedelta(days=7)
        daily_accesses = AccessLog.objects.filter(
            organization=org,
            timestamp__gte=seven_days_ago
        ).extra({'date': 'date(timestamp)'}).values('date').annotate(
            total=Count('id'),
            granted=Count('id', filter=Q(is_granted=True)),
            denied=Count('id', filter=Q(is_granted=False))
        ).order_by('date')
        
        return Response({
            'busy_hours_prediction': busy_hours,
            'optimization_suggestions': suggestions,
            'weekly_trend': list(daily_accesses),
            'generated_at': timezone.now().isoformat()
        })
    
    @action(detail=False, methods=['get'])
    def user_profile(self, request):
        """Get behavioral profile for a specific user"""
        from .ai_service import AccessAnomalyDetector
        from core.models import User
        
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'error': 'user_id required'}, status=400)
        
        try:
            user = User.objects.get(id=user_id, organization=request.user.organization)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
        
        detector = AccessAnomalyDetector(request.user.organization)
        profile = detector.get_user_behavior_profile(user)
        
        if not profile:
            return Response({
                'error': 'Insufficient data to generate profile',
                'message': 'User needs at least 5 access events in the last 30 days'
            }, status=400)
        
        return Response(profile)
    
    @action(detail=False, methods=['get'])
    def gemini_suggestions(self, request):
        """Get AI-powered suggestions using Gemini"""
        from .gemini_service import get_gemini_service
        
        # Get current stats
        org = request.user.organization
        today = timezone.now().date()
        
        from django.db.models.functions import ExtractHour
        hour_distribution = AccessLog.objects.filter(
            organization=org,
            timestamp__date=today
        ).annotate(hour=ExtractHour('timestamp')).values('hour').annotate(
            count=Count('id')
        ).order_by('hour')
        
        access_by_hour = {str(item['hour']): item['count'] for item in hour_distribution}
        
        stats_data = {
            'total_access_points': AccessPoint.objects.filter(organization=org).count(),
            'active_points': AccessPoint.objects.filter(organization=org, status='active').count(),
            'today_logs': AccessLog.objects.filter(
                organization=org,
                timestamp__date=today
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
            'access_by_hour': access_by_hour
        }
        
        gemini_service = get_gemini_service()
        suggestions = gemini_service.generate_access_point_suggestions(stats_data)
        
        return Response({
            'suggestions': suggestions,
            'generated_at': timezone.now().isoformat(),
            'stats_snapshot': stats_data
        })
    
    @action(detail=False, methods=['get'])
    def gemini_alerts(self, request):
        """Get AI-powered security alerts using Gemini"""
        from .gemini_service import get_gemini_service
        
        org = request.user.organization
        hours = int(request.query_params.get('hours', 24))
        since = timezone.now() - timedelta(hours=hours)
        
        # Get recent logs
        logs = AccessLog.objects.filter(
            organization=org,
            timestamp__gte=since
        ).values(
            'id', 'is_granted', 'is_anomaly', 'event_type', 
            'access_point__name', 'user__username', 'timestamp'
        )
        
        # Get recent anomalies
        anomalies = AccessAnomaly.objects.filter(
            organization=org,
            detected_at__gte=since
        ).values(
            'anomaly_type', 'severity', 'confidence_score',
            'user__username', 'access_log__access_point__name'
        )
        
        gemini_service = get_gemini_service()
        alerts = gemini_service.generate_security_alerts(
            list(logs),
            list(anomalies)
        )
        
        return Response({
            'alerts': alerts,
            'generated_at': timezone.now().isoformat(),
            'period_hours': hours
        })
    
    @action(detail=False, methods=['get'])
    def gemini_report(self, request):
        """Generate daily executive report using Gemini"""
        from .gemini_service import get_gemini_service
        
        org = request.user.organization
        today = timezone.now().date()
        
        # Comprehensive summary
        summary_data = {
            'date': str(today),
            'total_events': AccessLog.objects.filter(
                organization=org, timestamp__date=today
            ).count(),
            'granted': AccessLog.objects.filter(
                organization=org, timestamp__date=today, is_granted=True
            ).count(),
            'denied': AccessLog.objects.filter(
                organization=org, timestamp__date=today, is_granted=False
            ).count(),
            'anomalies': AccessAnomaly.objects.filter(
                organization=org, detected_at__date=today
            ).count(),
            'unique_users': AccessLog.objects.filter(
                organization=org, timestamp__date=today
            ).values('user').distinct().count(),
            'top_access_points': list(
                AccessLog.objects.filter(organization=org, timestamp__date=today)
                .values('access_point__name')
                .annotate(count=Count('id'))
                .order_by('-count')[:5]
            )
        }
        
        gemini_service = get_gemini_service()
        report = gemini_service.generate_daily_report(summary_data)
        
        return Response({
            'report': report,
            'generated_at': timezone.now().isoformat(),
            'data': summary_data
        })
