from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q, Count
from datetime import datetime

from .models import Threat, Alert, RiskAssessment, ThreatIndicator, Watchlist
from .serializers import (
    ThreatSerializer, AlertSerializer, RiskAssessmentSerializer,
    ThreatIndicatorSerializer, WatchlistSerializer
)
from . import ai_service


class ThreatViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Threat management
    Provides CRUD operations for security threats
    """
    serializer_class = ThreatSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['threat_type', 'severity', 'status', 'assigned_to']
    search_fields = ['title', 'description', 'source', 'tags']
    ordering_fields = ['created_at', 'updated_at', 'severity', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Threat.objects.filter(
            organization=self.request.user.organization
        ).select_related(
            'assigned_to', 'created_by'
        ).prefetch_related('alerts', 'indicators')
    
    def perform_create(self, serializer):
        """Set organization and created_by when creating a threat"""
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user
        )
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign threat to a user"""
        threat = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        threat.assigned_to_id = user_id
        threat.save()
        
        serializer = self.get_serializer(threat)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update threat status"""
        threat = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response(
                {'error': 'status is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        threat.status = new_status
        threat.last_activity = timezone.now()
        threat.save()
        
        serializer = self.get_serializer(threat)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get threat statistics"""
        queryset = self.get_queryset()
        
        # Get counts by severity
        severity_counts = {}
        for item in queryset.values('severity').annotate(count=Count('id')):
            severity_counts[item['severity']] = item['count']
        
        # Get counts by status
        status_counts = {}
        for item in queryset.values('status').annotate(count=Count('id')):
            status_counts[item['status']] = item['count']
        
        # Get counts by type
        type_counts = {}
        for item in queryset.values('threat_type').annotate(count=Count('id')):
            type_counts[item['threat_type']] = item['count']
        
        stats = {
            'total': queryset.count(),
            'by_severity': severity_counts,
            'by_status': status_counts,
            'by_type': type_counts,
            'new_count': queryset.filter(status='new').count(),
            'investigating_count': queryset.filter(status='investigating').count(),
        }
        
        return Response(stats)
    
    @action(detail=True, methods=['post'])
    def ai_analyze(self, request, pk=None):
        """AI-powered threat analysis"""
        threat = self.get_object()
        
        result = ai_service.analyze_threat(
            threat_description=threat.description,
            threat_type=threat.threat_type,
            source=threat.source
        )
        
        if result.get('success'):
            # Update threat with AI analysis
            threat.ai_analyzed = True
            threat.ai_confidence = result['analysis'].get('confidence', 0.0)
            threat.ai_suggested_severity = result['analysis'].get('severity')
            threat.ai_analysis = result['analysis']
            threat.save()
            
            serializer = self.get_serializer(threat)
            return Response({
                'threat': serializer.data,
                'analysis': result['analysis']
            })
        else:
            return Response(
                {'error': result.get('error')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def generate_risk_assessment(self, request, pk=None):
        """Generate AI-powered risk assessment for threat"""
        threat = self.get_object()
        
        result = ai_service.generate_risk_assessment(
            threat_title=threat.title,
            threat_description=threat.description,
            threat_type=threat.threat_type
        )
        
        if result.get('success'):
            assessment = result['assessment']
            
            # Create risk assessment record
            risk_assessment = RiskAssessment.objects.create(
                organization=request.user.organization,
                threat=threat,
                risk_level=assessment.get('risk_level', 'medium'),
                likelihood=assessment.get('likelihood', 'possible'),
                impact=assessment.get('impact', 'moderate'),
                vulnerability_analysis=assessment.get('vulnerability_analysis', ''),
                impact_analysis=assessment.get('impact_analysis', ''),
                mitigation_strategy=assessment.get('mitigation_strategy', ''),
                residual_risk=assessment.get('residual_risk', ''),
                timeline=assessment.get('timeline', ''),
                required_resources=assessment.get('required_resources', ''),
                ai_generated=True,
                ai_confidence=assessment.get('confidence', 0.0),
                ai_recommendations=assessment.get('recommendations', []),
                assessed_by=request.user
            )
            
            serializer = RiskAssessmentSerializer(risk_assessment, context={'request': request})
            return Response(serializer.data)
        else:
            return Response(
                {'error': result.get('error')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def extract_indicators(self, request, pk=None):
        """Extract threat indicators using AI"""
        threat = self.get_object()
        
        result = ai_service.extract_threat_indicators(
            description=threat.description,
            metadata=threat.metadata
        )
        
        if result.get('success'):
            # Create indicator records
            created_indicators = []
            for indicator_data in result.get('indicators', []):
                indicator, created = ThreatIndicator.objects.get_or_create(
                    organization=request.user.organization,
                    indicator_type=indicator_data.get('type', 'other'),
                    value=indicator_data.get('value', ''),
                    defaults={
                        'threat': threat,
                        'description': indicator_data.get('description', ''),
                        'confidence': indicator_data.get('confidence', 'medium'),
                        'first_seen': timezone.now(),
                        'last_seen': timezone.now(),
                        'tags': indicator_data.get('tags', []),
                        'added_by': request.user
                    }
                )
                if created:
                    created_indicators.append(indicator)
            
            serializer = ThreatIndicatorSerializer(created_indicators, many=True, context={'request': request})
            return Response({
                'indicators': serializer.data,
                'patterns': result.get('patterns', []),
                'summary': result.get('summary', '')
            })
        else:
            return Response(
                {'error': result.get('error')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AlertViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Alert management
    Provides CRUD operations for security alerts
    """
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['alert_type', 'severity', 'status', 'threat']
    search_fields = ['title', 'description', 'source', 'tags']
    ordering_fields = ['created_at', 'updated_at', 'severity', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Alert.objects.filter(
            organization=self.request.user.organization
        ).select_related(
            'threat', 'acknowledged_by', 'resolved_by', 'related_user'
        )
    
    def perform_create(self, serializer):
        """Set organization when creating an alert"""
        serializer.save(organization=self.request.user.organization)
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Acknowledge an alert"""
        alert = self.get_object()
        
        if alert.status == 'new':
            alert.status = 'acknowledged'
            alert.acknowledged_by = request.user
            alert.acknowledged_at = timezone.now()
            alert.save()
        
        serializer = self.get_serializer(alert)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve an alert"""
        alert = self.get_object()
        resolution_notes = request.data.get('resolution_notes', '')
        
        alert.status = 'resolved'
        alert.resolved_by = request.user
        alert.resolved_at = timezone.now()
        alert.resolution_notes = resolution_notes
        alert.save()
        
        serializer = self.get_serializer(alert)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        """Dismiss an alert"""
        alert = self.get_object()
        
        alert.status = 'dismissed'
        alert.resolved_by = request.user
        alert.resolved_at = timezone.now()
        alert.resolution_notes = request.data.get('reason', 'Dismissed')
        alert.save()
        
        serializer = self.get_serializer(alert)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get alert statistics"""
        queryset = self.get_queryset()
        
        # Get counts by severity
        severity_counts = {}
        for item in queryset.values('severity').annotate(count=Count('id')):
            severity_counts[item['severity']] = item['count']
        
        # Get counts by status
        status_counts = {}
        for item in queryset.values('status').annotate(count=Count('id')):
            status_counts[item['status']] = item['count']
        
        # Get counts by type
        type_counts = {}
        for item in queryset.values('alert_type').annotate(count=Count('id')):
            type_counts[item['alert_type']] = item['count']
        
        stats = {
            'total': queryset.count(),
            'by_severity': severity_counts,
            'by_status': status_counts,
            'by_type': type_counts,
            'new_count': queryset.filter(status='new').count(),
            'unresolved_count': queryset.exclude(status__in=['resolved', 'dismissed']).count(),
        }
        
        return Response(stats)


class RiskAssessmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Risk Assessment management
    Provides CRUD operations for risk assessments
    """
    serializer_class = RiskAssessmentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['threat', 'risk_level', 'likelihood', 'impact']
    search_fields = ['vulnerability_analysis', 'impact_analysis', 'mitigation_strategy']
    ordering_fields = ['created_at', 'updated_at', 'risk_level']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return RiskAssessment.objects.filter(
            organization=self.request.user.organization
        ).select_related('threat', 'assessed_by')
    
    def perform_create(self, serializer):
        """Set organization and assessed_by when creating a risk assessment"""
        serializer.save(
            organization=self.request.user.organization,
            assessed_by=self.request.user
        )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get risk assessment statistics"""
        queryset = self.get_queryset()
        
        stats = {
            'total': queryset.count(),
            'by_risk_level': dict(queryset.values_list('risk_level').annotate(count=Count('id'))),
            'by_likelihood': dict(queryset.values_list('likelihood').annotate(count=Count('id'))),
            'by_impact': dict(queryset.values_list('impact').annotate(count=Count('id'))),
            'critical_count': queryset.filter(risk_level='critical').count(),
            'high_count': queryset.filter(risk_level='high').count(),
        }
        
        return Response(stats)


class ThreatIndicatorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Threat Indicator (IOC) management
    Provides CRUD operations for threat indicators
    """
    serializer_class = ThreatIndicatorSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['indicator_type', 'confidence', 'is_active', 'is_false_positive', 'threat']
    search_fields = ['value', 'description', 'source', 'tags']
    ordering_fields = ['created_at', 'updated_at', 'last_seen', 'occurrence_count']
    ordering = ['-last_seen']
    
    def get_queryset(self):
        return ThreatIndicator.objects.filter(
            organization=self.request.user.organization
        ).select_related('threat', 'added_by')
    
    def perform_create(self, serializer):
        """Set organization and added_by when creating a threat indicator"""
        serializer.save(
            organization=self.request.user.organization,
            added_by=self.request.user
        )
    
    @action(detail=True, methods=['post'])
    def mark_false_positive(self, request, pk=None):
        """Mark indicator as false positive"""
        indicator = self.get_object()
        indicator.is_false_positive = True
        indicator.is_active = False
        indicator.save()
        
        serializer = self.get_serializer(indicator)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def increment_occurrence(self, request, pk=None):
        """Increment occurrence count when indicator is seen again"""
        indicator = self.get_object()
        indicator.occurrence_count += 1
        indicator.last_seen = timezone.now()
        indicator.save()
        
        serializer = self.get_serializer(indicator)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """Search for an indicator value"""
        value = request.data.get('value')
        
        if not value:
            return Response(
                {'error': 'value is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        indicators = self.get_queryset().filter(
            value__icontains=value,
            is_active=True
        )
        
        serializer = self.get_serializer(indicators, many=True)
        return Response({
            'found': indicators.exists(),
            'count': indicators.count(),
            'indicators': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get indicator statistics"""
        queryset = self.get_queryset()
        
        stats = {
            'total': queryset.count(),
            'by_type': dict(queryset.values_list('indicator_type').annotate(count=Count('id'))),
            'by_confidence': dict(queryset.values_list('confidence').annotate(count=Count('id'))),
            'active_count': queryset.filter(is_active=True).count(),
            'false_positive_count': queryset.filter(is_false_positive=True).count(),
        }
        
        return Response(stats)


class WatchlistViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Watchlist management
    Provides CRUD operations for watchlists
    """
    serializer_class = WatchlistSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['watchlist_type', 'risk_level', 'is_active', 'threat']
    search_fields = ['subject_name', 'subject_id', 'description', 'reason', 'notes']
    ordering_fields = ['created_at', 'updated_at', 'risk_level', 'detection_count', 'last_detected']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Watchlist.objects.filter(
            organization=self.request.user.organization
        ).select_related('threat', 'added_by')
    
    def perform_create(self, serializer):
        """Set organization and added_by when creating a watchlist entry"""
        serializer.save(
            organization=self.request.user.organization,
            added_by=self.request.user
        )
    
    @action(detail=True, methods=['post'])
    def record_detection(self, request, pk=None):
        """Record that this watchlist entry was detected"""
        watchlist_entry = self.get_object()
        watchlist_entry.detection_count += 1
        watchlist_entry.last_detected = timezone.now()
        watchlist_entry.save()
        
        # TODO: Send notifications if alert_on_detection is True
        
        serializer = self.get_serializer(watchlist_entry)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a watchlist entry"""
        watchlist_entry = self.get_object()
        watchlist_entry.is_active = False
        watchlist_entry.save()
        
        serializer = self.get_serializer(watchlist_entry)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def search_subject(self, request):
        """Search for a subject on watchlist"""
        subject_name = request.data.get('subject_name')
        subject_id = request.data.get('subject_id')
        
        if not subject_name and not subject_id:
            return Response(
                {'error': 'subject_name or subject_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(is_active=True)
        
        if subject_name:
            queryset = queryset.filter(subject_name__icontains=subject_name)
        if subject_id:
            queryset = queryset.filter(subject_id__icontains=subject_id)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'found': queryset.exists(),
            'count': queryset.count(),
            'entries': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get watchlist statistics"""
        queryset = self.get_queryset()
        
        stats = {
            'total': queryset.count(),
            'by_type': dict(queryset.values_list('watchlist_type').annotate(count=Count('id'))),
            'by_risk_level': dict(queryset.values_list('risk_level').annotate(count=Count('id'))),
            'active_count': queryset.filter(is_active=True).count(),
            'critical_count': queryset.filter(risk_level='critical', is_active=True).count(),
            'high_risk_count': queryset.filter(risk_level='high', is_active=True).count(),
        }
        
        return Response(stats)
