"""
Threat Intelligence Management Views
CRUD operations and AI-powered endpoints
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q
import logging

from .models import (
    Threat,
    Alert,
    RiskAssessment,
    ThreatIndicator,
    Watchlist,
    ThreatFeed,
    ThreatHuntingQuery
)
from .serializers import (
    ThreatSerializer,
    ThreatListSerializer,
    AlertSerializer,
    AlertListSerializer,
    RiskAssessmentSerializer,
    RiskAssessmentListSerializer,
    ThreatIndicatorSerializer,
    ThreatIndicatorListSerializer,
    WatchlistSerializer,
    WatchlistListSerializer,
    ThreatFeedSerializer,
    ThreatFeedListSerializer,
    ThreatHuntingQuerySerializer,
    ThreatHuntingQueryListSerializer,
    AnomalyDetectionInputSerializer,
    ThreatScoringInputSerializer,
    ThreatScoringOutputSerializer,
    PredictiveThreatAnalyticsInputSerializer,
    AlertAggregationInputSerializer
)
from .services import (
    AnomalyDetectionService,
    ThreatScoringService,
    PredictiveThreatAnalytics,
    AlertAggregationService,
    ThreatHuntingAssistant
)
from .services.threat_ai_analysis import ThreatAIAnalysisService

logger = logging.getLogger(__name__)


class ThreatViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Threat CRUD operations
    """
    queryset = Threat.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['threat_type', 'severity', 'status', 'organization']
    search_fields = ['title', 'description', 'external_ref']
    ordering_fields = ['first_detected_at', 'risk_score', 'severity']
    ordering = ['-first_detected_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ThreatListSerializer
        return ThreatSerializer
    
    def get_queryset(self):
        """Filter threats by user's organization"""
        user = self.request.user
        if user.is_superuser:
            return Threat.objects.all()
        return Threat.objects.filter(organization=user.organization)
    
    def perform_create(self, serializer):
        """Set organization and created_by on creation"""
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user
        )
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign threat to a user"""
        threat = self.get_object()
        assigned_to_id = request.data.get('assigned_to')
        
        if not assigned_to_id:
            return Response(
                {'error': 'assigned_to is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from core.models import User
        try:
            user = User.objects.get(id=assigned_to_id)
            threat.assigned_to = user
            threat.save()
            
            return Response({
                'status': 'success',
                'message': f'Threat assigned to {user.get_full_name()}'
            })
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update threat status"""
        threat = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Threat.STATUS_CHOICES).keys():
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        threat.status = new_status
        if new_status == 'resolved':
            from django.utils import timezone
            threat.resolved_at = timezone.now()
        threat.save()
        
        return Response({
            'status': 'success',
            'new_status': new_status
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get threat statistics"""
        organization_id = request.user.organization.id
        threats = Threat.objects.filter(organization_id=organization_id)
        
        stats = {
            'total': threats.count(),
            'by_severity': {},
            'by_status': {},
            'by_type': {},
            'critical_open': threats.filter(
                severity='critical',
                status__in=['new', 'investigating']
            ).count()
        }
        
        for severity, _ in Threat.SEVERITY_LEVELS:
            stats['by_severity'][severity] = threats.filter(severity=severity).count()
        
        for status_key, _ in Threat.STATUS_CHOICES:
            stats['by_status'][status_key] = threats.filter(status=status_key).count()
        
        for threat_type, _ in Threat.THREAT_TYPES:
            count = threats.filter(threat_type=threat_type).count()
            if count > 0:
                stats['by_type'][threat_type] = count
        
        return Response(stats)
    
    @action(detail=True, methods=['post'])
    def ai_analyze(self, request, pk=None):
        """Get AI-powered analysis for a specific threat"""
        threat = self.get_object()
        
        ai_service = ThreatAIAnalysisService()
        analysis = ai_service.analyze_threat(threat)
        
        return Response(analysis)
    
    @action(detail=True, methods=['post'])
    def ai_action_plan(self, request, pk=None):
        """Generate AI-powered action plan for a threat"""
        threat = self.get_object()
        
        ai_service = ThreatAIAnalysisService()
        action_plan = ai_service.generate_action_plan(threat)
        
        return Response(action_plan)
    
    @action(detail=True, methods=['post'])
    def ai_mitigation(self, request, pk=None):
        """Get AI-powered mitigation suggestions for a threat"""
        threat = self.get_object()
        
        ai_service = ThreatAIAnalysisService()
        mitigation = ai_service.suggest_mitigation(threat)
        
        return Response(mitigation)
    
    @action(detail=False, methods=['post'])
    def ai_bulk_analyze(self, request):
        """Analyze multiple threats with AI"""
        limit = int(request.data.get('limit', 10))
        
        queryset = self.get_queryset()
        ai_service = ThreatAIAnalysisService()
        results = ai_service.bulk_analyze_threats(queryset, limit=limit)
        
        return Response(results)


class AlertViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Alert CRUD operations
    """
    queryset = Alert.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['alert_type', 'severity', 'status', 'organization', 'user']
    search_fields = ['title', 'description']
    ordering_fields = ['triggered_at', 'severity', 'confidence_score']
    ordering = ['-triggered_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AlertListSerializer
        return AlertSerializer
    
    def get_queryset(self):
        """Filter alerts by user's organization"""
        user = self.request.user
        if user.is_superuser:
            return Alert.objects.all()
        return Alert.objects.filter(organization=user.organization)
    
    def perform_create(self, serializer):
        """Set organization on creation"""
        serializer.save(organization=self.request.user.organization)
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Acknowledge an alert"""
        alert = self.get_object()
        
        from django.utils import timezone
        alert.status = 'acknowledged'
        alert.acknowledged_by = request.user
        alert.acknowledged_at = timezone.now()
        alert.save()
        
        return Response({
            'status': 'success',
            'message': 'Alert acknowledged'
        })
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve an alert"""
        alert = self.get_object()
        
        from django.utils import timezone
        alert.status = 'resolved'
        alert.resolved_at = timezone.now()
        alert.save()
        
        return Response({
            'status': 'success',
            'message': 'Alert resolved'
        })
    
    @action(detail=False, methods=['post'])
    def bulk_acknowledge(self, request):
        """Acknowledge multiple alerts"""
        alert_ids = request.data.get('alert_ids', [])
        
        from django.utils import timezone
        updated = Alert.objects.filter(
            id__in=alert_ids,
            organization=request.user.organization
        ).update(
            status='acknowledged',
            acknowledged_by=request.user,
            acknowledged_at=timezone.now()
        )
        
        return Response({
            'status': 'success',
            'updated_count': updated
        })
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get alert dashboard data"""
        organization_id = request.user.organization.id
        alerts = Alert.objects.filter(organization_id=organization_id)
        
        from datetime import timedelta
        from django.utils import timezone
        last_24h = timezone.now() - timedelta(hours=24)
        
        dashboard = {
            'total_alerts': alerts.count(),
            'new_alerts': alerts.filter(status='new').count(),
            'critical_alerts': alerts.filter(severity='critical').count(),
            'alerts_last_24h': alerts.filter(triggered_at__gte=last_24h).count(),
            'by_severity': {},
            'by_type': {}
        }
        
        for severity, _ in Alert.SEVERITY_LEVELS:
            dashboard['by_severity'][severity] = alerts.filter(severity=severity).count()
        
        for alert_type, _ in Alert.ALERT_TYPES:
            count = alerts.filter(alert_type=alert_type).count()
            if count > 0:
                dashboard['by_type'][alert_type] = count
        
        return Response(dashboard)


class RiskAssessmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Risk Assessment CRUD operations
    """
    queryset = RiskAssessment.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['assessment_type', 'risk_level', 'is_active', 'organization']
    search_fields = ['title', 'description']
    ordering_fields = ['assessed_at', 'risk_score']
    ordering = ['-assessed_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return RiskAssessmentListSerializer
        return RiskAssessmentSerializer
    
    def get_queryset(self):
        """Filter assessments by user's organization"""
        user = self.request.user
        if user.is_superuser:
            return RiskAssessment.objects.all()
        return RiskAssessment.objects.filter(organization=user.organization)
    
    def perform_create(self, serializer):
        """Set organization and assessed_by on creation"""
        serializer.save(
            organization=self.request.user.organization,
            assessed_by=self.request.user
        )


class ThreatIndicatorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Threat Indicator CRUD operations
    """
    queryset = ThreatIndicator.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['indicator_type', 'severity', 'status', 'organization']
    search_fields = ['indicator_value', 'description']
    ordering_fields = ['last_seen', 'severity', 'confidence_score']
    ordering = ['-last_seen']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ThreatIndicatorListSerializer
        return ThreatIndicatorSerializer
    
    def get_queryset(self):
        """Filter indicators by user's organization"""
        user = self.request.user
        if user.is_superuser:
            return ThreatIndicator.objects.all()
        return ThreatIndicator.objects.filter(organization=user.organization)
    
    def perform_create(self, serializer):
        """Set organization and added_by on creation"""
        serializer.save(
            organization=self.request.user.organization,
            added_by=self.request.user
        )
    
    @action(detail=True, methods=['post'])
    def whitelist(self, request, pk=None):
        """Whitelist an indicator"""
        indicator = self.get_object()
        indicator.status = 'whitelisted'
        indicator.save()
        
        return Response({
            'status': 'success',
            'message': 'Indicator whitelisted'
        })


class WatchlistViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Watchlist CRUD operations
    """
    queryset = Watchlist.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['watchlist_type', 'threat_level', 'status', 'organization']
    search_fields = ['name', 'subject_identifier', 'description']
    ordering_fields = ['created_at', 'threat_level', 'times_detected']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return WatchlistListSerializer
        return WatchlistSerializer
    
    def get_queryset(self):
        """Filter watchlist by user's organization"""
        user = self.request.user
        if user.is_superuser:
            return Watchlist.objects.all()
        return Watchlist.objects.filter(organization=user.organization)
    
    def perform_create(self, serializer):
        """Set organization and added_by on creation"""
        serializer.save(
            organization=self.request.user.organization,
            added_by=self.request.user
        )


class ThreatFeedViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Threat Feed CRUD operations
    """
    queryset = ThreatFeed.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['feed_type', 'status', 'organization']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'last_sync_at']
    ordering = ['-last_sync_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ThreatFeedListSerializer
        return ThreatFeedSerializer
    
    def get_queryset(self):
        """Filter feeds by user's organization"""
        user = self.request.user
        if user.is_superuser:
            return ThreatFeed.objects.all()
        return ThreatFeed.objects.filter(organization=user.organization)
    
    def perform_create(self, serializer):
        """Set organization on creation"""
        serializer.save(organization=self.request.user.organization)
    
    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """Sync threat feed"""
        feed = self.get_object()
        
        # Placeholder for actual sync logic
        return Response({
            'status': 'success',
            'message': f'Sync initiated for {feed.name}'
        })


class ThreatHuntingQueryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Threat Hunting Query CRUD operations
    """
    queryset = ThreatHuntingQuery.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['query_type', 'is_public', 'organization']
    search_fields = ['name', 'description', 'query_text']
    ordering_fields = ['created_at', 'updated_at', 'times_executed']
    ordering = ['-updated_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ThreatHuntingQueryListSerializer
        return ThreatHuntingQuerySerializer
    
    def get_queryset(self):
        """Filter queries by user's organization and public queries"""
        user = self.request.user
        if user.is_superuser:
            return ThreatHuntingQuery.objects.all()
        
        return ThreatHuntingQuery.objects.filter(
            Q(organization=user.organization) | Q(is_public=True)
        )
    
    def perform_create(self, serializer):
        """Set organization and created_by on creation"""
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user
        )
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute a threat hunting query"""
        query = self.get_object()
        
        # Increment execution count
        query.times_executed += 1
        from django.utils import timezone
        query.last_executed_at = timezone.now()
        query.save()
        
        # Execute query using ThreatHuntingAssistant
        assistant = ThreatHuntingAssistant()
        result = assistant.execute_natural_language_query(
            organization_id=request.user.organization.id,
            query_text=query.query_text,
            created_by=request.user
        )
        
        # Update last result count
        if 'results' in result and 'count' in result['results']:
            query.last_result_count = result['results']['count']
            query.save()
        
        return Response(result)


# AI Service Endpoints
class AnomalyDetectionViewSet(viewsets.ViewSet):
    """
    ViewSet for Anomaly Detection AI service
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def detect_user_anomalies(self, request):
        """Detect anomalies in user behavior"""
        serializer = AnomalyDetectionInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        service = AnomalyDetectionService()
        result = service.detect_user_behavior_anomalies(
            user_id=serializer.validated_data.get('user_id'),
            time_range_days=serializer.validated_data.get('time_range_days', 30)
        )
        
        return Response(result)
    
    @action(detail=False, methods=['post'])
    def detect_login_anomalies(self, request):
        """Detect anomalies in login patterns"""
        time_range_days = request.data.get('time_range_days', 30)
        
        service = AnomalyDetectionService()
        result = service.detect_login_pattern_anomalies(
            organization_id=request.user.organization.id,
            time_range_days=time_range_days
        )
        
        return Response(result)
    
    @action(detail=False, methods=['post'])
    def detect_traffic_anomalies(self, request):
        """Detect anomalies in network traffic"""
        access_point_id = request.data.get('access_point_id')
        time_range_days = request.data.get('time_range_days', 7)
        
        if not access_point_id:
            return Response(
                {'error': 'access_point_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = AnomalyDetectionService()
        result = service.detect_network_traffic_anomalies(
            access_point_id=access_point_id,
            time_range_days=time_range_days
        )
        
        return Response(result)


class ThreatScoringViewSet(viewsets.ViewSet):
    """
    ViewSet for Threat Scoring AI service
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def calculate_risk(self, request):
        """Calculate risk score for entity"""
        serializer = ThreatScoringInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        service = ThreatScoringService()
        entity_type = serializer.validated_data['entity_type']
        entity_id = serializer.validated_data['entity_id']
        time_range_days = serializer.validated_data.get('time_range_days', 30)
        
        if entity_type == 'user':
            result = service.calculate_user_risk_score(entity_id, time_range_days)
        elif entity_type == 'access_point':
            result = service.calculate_access_point_risk_score(entity_id, time_range_days)
        elif entity_type == 'location':
            # Placeholder - needs location name
            result = {'status': 'error', 'message': 'Location scoring not yet implemented'}
        else:
            result = {'status': 'error', 'message': 'Invalid entity type'}
        
        return Response(result)
    
    @action(detail=False, methods=['post'])
    def update_dynamic_levels(self, request):
        """Update dynamic threat levels across organization"""
        service = ThreatScoringService()
        result = service.update_dynamic_threat_levels(
            organization_id=request.user.organization.id
        )
        
        return Response(result)


class PredictiveAnalyticsViewSet(viewsets.ViewSet):
    """
    ViewSet for Predictive Threat Analytics AI service
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def forecast_threats(self, request):
        """Forecast threat trends"""
        serializer = PredictiveThreatAnalyticsInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        service = PredictiveThreatAnalytics()
        result = service.forecast_threat_trends(
            organization_id=request.user.organization.id,
            threat_type=serializer.validated_data.get('threat_type'),
            forecast_days=serializer.validated_data.get('prediction_days', 7),
            historical_days=30
        )
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def emerging_patterns(self, request):
        """Identify emerging threat patterns"""
        time_range_days = int(request.query_params.get('time_range_days', 30))
        
        service = PredictiveThreatAnalytics()
        result = service.identify_emerging_patterns(
            organization_id=request.user.organization.id,
            time_range_days=time_range_days
        )
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def predict_attack_vectors(self, request):
        """Predict likely attack vectors"""
        time_range_days = int(request.query_params.get('time_range_days', 60))
        
        service = PredictiveThreatAnalytics()
        result = service.predict_attack_vectors(
            organization_id=request.user.organization.id,
            time_range_days=time_range_days
        )
        
        return Response(result)


class AlertAggregationViewSet(viewsets.ViewSet):
    """
    ViewSet for Alert Aggregation service
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def deduplicate(self, request):
        """De-duplicate similar alerts"""
        serializer = AlertAggregationInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        service = AlertAggregationService(
            similarity_threshold=serializer.validated_data.get('similarity_threshold', 0.8)
        )
        result = service.deduplicate_alerts(
            organization_id=request.user.organization.id,
            time_window_minutes=serializer.validated_data.get('time_window_minutes', 60),
            max_alerts=serializer.validated_data.get('max_alerts', 100)
        )
        
        return Response(result)
    
    @action(detail=False, methods=['post'])
    def correlate(self, request):
        """Correlate alerts into incidents"""
        time_window_hours = request.data.get('time_window_hours', 24)
        
        service = AlertAggregationService()
        result = service.correlate_alerts_to_incidents(
            organization_id=request.user.organization.id,
            time_window_hours=time_window_hours
        )
        
        return Response(result)
    
    @action(detail=False, methods=['post'])
    def smart_filter(self, request):
        """Apply smart filtering to alerts"""
        confidence_threshold = request.data.get('confidence_threshold', 0.7)
        
        service = AlertAggregationService()
        result = service.apply_smart_filtering(
            organization_id=request.user.organization.id,
            confidence_threshold=confidence_threshold
        )
        
        return Response(result)
    
    @action(detail=False, methods=['post'])
    def run_full_aggregation(self, request):
        """Run complete aggregation pipeline with LLM insights"""
        service = AlertAggregationService()
        result = service.run_full_aggregation(
            organization_id=request.user.organization.id
        )
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get alert summary"""
        time_range_hours = int(request.query_params.get('time_range_hours', 24))
        
        service = AlertAggregationService()
        result = service.generate_alert_summary(
            organization_id=request.user.organization.id,
            time_range_hours=time_range_hours
        )
        
        return Response(result)


class ThreatHuntingViewSet(viewsets.ViewSet):
    """
    ViewSet for Threat Hunting Assistant
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def query(self, request):
        """Execute natural language threat hunting query"""
        query_text = request.data.get('query')
        
        if not query_text:
            return Response(
                {'error': 'query is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        assistant = ThreatHuntingAssistant()
        result = assistant.execute_natural_language_query(
            organization_id=request.user.organization.id,
            query_text=query_text,
            created_by=request.user
        )
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def suggest_hypotheses(self, request):
        """Get suggested threat hunting hypotheses"""
        time_range_days = int(request.query_params.get('time_range_days', 7))
        
        assistant = ThreatHuntingAssistant()
        result = assistant.suggest_hunting_hypotheses(
            organization_id=request.user.organization.id,
            time_range_days=time_range_days
        )
        
        return Response(result)
    
    @action(detail=False, methods=['post'])
    def generate_report(self, request):
        """Generate threat report"""
        report_type = request.data.get('report_type', 'summary')
        time_range_days = request.data.get('time_range_days', 7)
        
        assistant = ThreatHuntingAssistant()
        result = assistant.generate_threat_report(
            organization_id=request.user.organization.id,
            report_type=report_type,
            time_range_days=time_range_days
        )
        
        return Response(result)
