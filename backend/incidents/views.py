"""
API views for incidents app.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Incident, IncidentEvent, Evidence
from .serializers import (
    IncidentSerializer, IncidentDetailSerializer, IncidentCreateSerializer,
    IncidentEventSerializer, EvidenceSerializer
)


class IncidentViewSet(viewsets.ModelViewSet):
    """API endpoint for incidents."""
    queryset = Incident.objects.select_related(
        'organization', 'assignee', 'created_by'
    ).prefetch_related('events', 'evidence')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['organization', 'incident_type', 'severity', 'status', 'assignee']
    search_fields = ['title', 'description']
    ordering_fields = ['opened_at', 'severity', 'updated_at']
    ordering = ['-opened_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return IncidentDetailSerializer
        elif self.action == 'create':
            return IncidentCreateSerializer
        return IncidentSerializer
    
    def get_queryset(self):
        """Filter by organization for non-admin users."""
        user = self.request.user
        queryset = super().get_queryset()
        
        if not user.is_staff and user.organization:
            queryset = queryset.filter(organization=user.organization)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set created_by and create initial event."""
        incident = serializer.save(created_by=self.request.user)
        
        # Create initial event
        IncidentEvent.objects.create(
            incident=incident,
            action='created',
            description=f"Incident created: {incident.title}",
            actor=self.request.user
        )
    
    def perform_update(self, serializer):
        """Create event on update."""
        old_status = serializer.instance.status
        incident = serializer.save()
        
        if old_status != incident.status:
            IncidentEvent.objects.create(
                incident=incident,
                action='status_changed',
                description=f"Status changed from {old_status} to {incident.status}",
                actor=self.request.user,
                metadata={'old_status': old_status, 'new_status': incident.status}
            )
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign incident to a user."""
        incident = self.get_object()
        user_id = request.data.get('user_id')
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            user = User.objects.get(id=user_id)
            incident.assignee = user
            incident.save()
            
            # Create event
            IncidentEvent.objects.create(
                incident=incident,
                action='assigned',
                description=f"Assigned to {user.get_full_name()}",
                actor=request.user,
                metadata={'assignee_id': user.id}
            )
            
            return Response({
                'id': incident.id,
                'assignee': user.get_full_name(),
                'message': 'Incident assigned successfully'
            })
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """Add comment to incident."""
        incident = self.get_object()
        comment = request.data.get('comment', '')
        
        if not comment:
            return Response(
                {'error': 'Comment is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        event = IncidentEvent.objects.create(
            incident=incident,
            action='comment_added',
            description=comment,
            actor=request.user
        )
        
        return Response({
            'id': event.id,
            'message': 'Comment added successfully'
        })
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close incident."""
        incident = self.get_object()
        incident.status = 'closed'
        incident.closed_at = timezone.now()
        incident.save()
        
        IncidentEvent.objects.create(
            incident=incident,
            action='closed',
            description='Incident closed',
            actor=request.user
        )
        
        return Response({
            'id': incident.id,
            'status': incident.status,
            'message': 'Incident closed successfully'
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get incident statistics."""
        queryset = self.get_queryset()
        
        stats = {
            'total': queryset.count(),
            'open': queryset.filter(status='open').count(),
            'investigating': queryset.filter(status='investigating').count(),
            'resolved': queryset.filter(status='resolved').count(),
            'closed': queryset.filter(status='closed').count(),
            'by_severity': {
                'low': queryset.filter(severity='low').count(),
                'medium': queryset.filter(severity='medium').count(),
                'high': queryset.filter(severity='high').count(),
                'critical': queryset.filter(severity='critical').count(),
            },
            'by_type': {}
        }
        
        # Count by type
        for choice in Incident.TYPE_CHOICES:
            type_key = choice[0]
            stats['by_type'][type_key] = queryset.filter(incident_type=type_key).count()
        
        return Response(stats)


class IncidentEventViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for incident events."""
    queryset = IncidentEvent.objects.select_related('incident', 'actor')
    serializer_class = IncidentEventSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['incident', 'action']


class EvidenceViewSet(viewsets.ModelViewSet):
    """API endpoint for evidence."""
    queryset = Evidence.objects.select_related('incident', 'uploaded_by')
    serializer_class = EvidenceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['incident', 'kind']
    
    def get_queryset(self):
        """Filter by organization for non-admin users."""
        user = self.request.user
        queryset = super().get_queryset()
        
        if not user.is_staff and user.organization:
            queryset = queryset.filter(incident__organization=user.organization)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set uploaded_by and create incident event."""
        evidence = serializer.save(uploaded_by=self.request.user)
        
        # Create incident event
        IncidentEvent.objects.create(
            incident=evidence.incident,
            action='evidence_added',
            description=f"Evidence added: {evidence.file_name}",
            actor=self.request.user,
            metadata={'evidence_id': evidence.id}
        )
