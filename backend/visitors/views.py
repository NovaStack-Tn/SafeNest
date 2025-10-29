"""
Views for Visitor & Asset Management API
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q, Count, F
from datetime import timedelta
import uuid

from .models import Visitor, VisitorPass, Asset, AssetAssignment, MovementLog
from .serializers import (
    VisitorSerializer, VisitorListSerializer,
    VisitorPassSerializer,
    AssetSerializer, AssetListSerializer,
    AssetAssignmentSerializer,
    MovementLogSerializer,
    AIExtractionRequestSerializer,
    AIAccessLevelRequestSerializer,
    AIDurationPredictionRequestSerializer,
    AIAutoFillRequestSerializer,
    AIRiskAnalysisRequestSerializer
)
from .ai_service import VisitorAIService


class VisitorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing visitors
    
    Provides CRUD operations and AI-powered features for visitor management
    """
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'visitor_type', 'host', 'expected_arrival']
    search_fields = ['first_name', 'last_name', 'email', 'company', 'purpose']
    ordering_fields = ['expected_arrival', 'created_at', 'last_name']
    ordering = ['-expected_arrival']
    
    def get_queryset(self):
        """Filter by organization"""
        return Visitor.objects.filter(organization=self.request.user.organization)
    
    def get_serializer_class(self):
        """Use list serializer for list action"""
        if self.action == 'list':
            return VisitorListSerializer
        return VisitorSerializer
    
    @action(detail=False, methods=['post'], url_path='ai-extract')
    def ai_extract_info(self, request):
        """
        Extract visitor information from text using AI
        POST /visitors/ai-extract/
        
        Body: {
            "text": "Email or form content",
            "source_type": "email|form|message"
        }
        """
        serializer = AIExtractionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        ai_service = VisitorAIService()
        result = ai_service.extract_visitor_info(
            text=serializer.validated_data['text'],
            source_type=serializer.validated_data.get('source_type', 'email')
        )
        
        return Response(result)
    
    @action(detail=False, methods=['post'], url_path='ai-suggest-access')
    def ai_suggest_access_level(self, request):
        """
        Get AI suggestion for visitor access level
        POST /visitors/ai-suggest-access/
        """
        serializer = AIAccessLevelRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        ai_service = VisitorAIService()
        result = ai_service.suggest_access_level(serializer.validated_data)
        
        return Response(result)
    
    @action(detail=False, methods=['post'], url_path='ai-predict-duration')
    def ai_predict_duration(self, request):
        """
        Predict visit duration using AI
        POST /visitors/ai-predict-duration/
        """
        serializer = AIDurationPredictionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        ai_service = VisitorAIService()
        result = ai_service.predict_visit_duration(serializer.validated_data)
        
        return Response(result)
    
    @action(detail=False, methods=['post'], url_path='ai-autofill')
    def ai_autofill_form(self, request):
        """
        Auto-fill visitor form using AI
        POST /visitors/ai-autofill/
        """
        serializer = AIAutoFillRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        ai_service = VisitorAIService()
        result = ai_service.auto_fill_visitor_form(
            partial_data=serializer.validated_data['partial_data'],
            context=serializer.validated_data.get('context', '')
        )
        
        return Response(result)
    
    @action(detail=True, methods=['post'], url_path='analyze-risk')
    def analyze_risk(self, request, pk=None):
        """
        Analyze visitor risk using AI
        POST /visitors/{id}/analyze-risk/
        """
        visitor = self.get_object()
        
        # Get historical data for this visitor
        historical = Visitor.objects.filter(
            organization=request.user.organization,
            email=visitor.email
        ).exclude(id=visitor.id).values(
            'visitor_type', 'purpose', 'status', 'created_at'
        )
        
        visitor_data = VisitorSerializer(visitor).data
        
        ai_service = VisitorAIService()
        result = ai_service.analyze_visitor_risk(
            visitor_data=visitor_data,
            historical_data=list(historical) if historical.exists() else None
        )
        
        return Response(result)
    
    @action(detail=True, methods=['post'])
    def checkin(self, request, pk=None):
        """
        Check in a visitor
        POST /visitors/{id}/checkin/
        """
        visitor = self.get_object()
        
        if visitor.status == 'checked_in':
            return Response(
                {'error': 'Visitor is already checked in'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        visitor.status = 'checked_in'
        visitor.actual_arrival = timezone.now()
        visitor.save()
        
        # Create movement log
        MovementLog.objects.create(
            movement_type='visitor_checkin',
            visitor=visitor,
            to_location=visitor.department or 'Reception',
            verified_by=request.user,
            verification_method=request.data.get('verification_method', 'manual'),
            organization=request.user.organization
        )
        
        return Response(VisitorSerializer(visitor).data)
    
    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        """
        Check out a visitor
        POST /visitors/{id}/checkout/
        """
        visitor = self.get_object()
        
        if visitor.status != 'checked_in':
            return Response(
                {'error': 'Visitor is not checked in'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        visitor.status = 'checked_out'
        visitor.actual_departure = timezone.now()
        visitor.save()
        
        # Create movement log
        MovementLog.objects.create(
            movement_type='visitor_checkout',
            visitor=visitor,
            from_location=visitor.department or 'Reception',
            verified_by=request.user,
            verification_method=request.data.get('verification_method', 'manual'),
            organization=request.user.organization
        )
        
        return Response(VisitorSerializer(visitor).data)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """
        Get currently checked-in visitors
        GET /visitors/current/
        """
        visitors = self.get_queryset().filter(status='checked_in')
        serializer = self.get_serializer(visitors, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """
        Get overdue visitors (checked in past expected departure)
        GET /visitors/overdue/
        """
        visitors = self.get_queryset().filter(
            status='checked_in',
            expected_departure__lt=timezone.now()
        )
        serializer = self.get_serializer(visitors, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get visitor statistics
        GET /visitors/stats/
        """
        queryset = self.get_queryset()
        
        stats = {
            'total': queryset.count(),
            'checked_in': queryset.filter(status='checked_in').count(),
            'expected_today': queryset.filter(
                expected_arrival__date=timezone.now().date()
            ).count(),
            'overdue': queryset.filter(
                status='checked_in',
                expected_departure__lt=timezone.now()
            ).count(),
            'by_type': dict(
                queryset.values('visitor_type').annotate(count=Count('id')).values_list('visitor_type', 'count')
            ),
            'by_status': dict(
                queryset.values('status').annotate(count=Count('id')).values_list('status', 'count')
            )
        }
        
        return Response(stats)


class VisitorPassViewSet(viewsets.ModelViewSet):
    """ViewSet for managing visitor passes"""
    
    serializer_class = VisitorPassSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['visitor', 'status', 'pass_type']
    ordering = ['-issued_at']
    
    def get_queryset(self):
        """Filter by organization through visitor"""
        return VisitorPass.objects.filter(visitor__organization=self.request.user.organization)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a visitor pass"""
        pass_obj = self.get_object()
        pass_obj.status = 'active'
        pass_obj.save()
        return Response(self.get_serializer(pass_obj).data)
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """Revoke a visitor pass"""
        pass_obj = self.get_object()
        pass_obj.status = 'revoked'
        pass_obj.revoked_by = request.user
        pass_obj.revoked_at = timezone.now()
        pass_obj.revocation_reason = request.data.get('reason', '')
        pass_obj.save()
        return Response(self.get_serializer(pass_obj).data)
    
    @action(detail=True, methods=['post'])
    def use(self, request, pk=None):
        """Record pass usage"""
        pass_obj = self.get_object()
        
        if not pass_obj.is_valid:
            return Response(
                {'error': 'Pass is not valid'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        pass_obj.record_usage()
        return Response(self.get_serializer(pass_obj).data)
    
    def create(self, request, *args, **kwargs):
        """Generate unique pass code on creation"""
        if 'pass_code' not in request.data:
            request.data['pass_code'] = str(uuid.uuid4())
        return super().create(request, *args, **kwargs)


class AssetViewSet(viewsets.ModelViewSet):
    """ViewSet for managing assets"""
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'asset_type', 'condition', 'current_assignee']
    search_fields = ['name', 'asset_tag', 'serial_number', 'description']
    ordering_fields = ['asset_tag', 'name', 'purchase_date', 'created_at']
    ordering = ['asset_tag']
    
    def get_queryset(self):
        """Filter by organization"""
        return Asset.objects.filter(organization=self.request.user.organization)
    
    def get_serializer_class(self):
        """Use list serializer for list action"""
        if self.action == 'list':
            return AssetListSerializer
        return AssetSerializer
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get available assets"""
        assets = self.get_queryset().filter(status='available')
        serializer = self.get_serializer(assets, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def assigned(self, request):
        """Get assigned assets"""
        assets = self.get_queryset().filter(status='assigned')
        serializer = self.get_serializer(assets, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """
        Assign asset to a user
        POST /assets/{id}/assign/
        Body: {
            "assignee": user_id,
            "expected_return": datetime,
            "notes": "..."
        }
        """
        asset = self.get_object()
        
        if asset.status not in ['available', 'assigned']:
            return Response(
                {'error': f'Asset is {asset.status} and cannot be assigned'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        assignment_data = {
            'asset': asset.id,
            'assignee': request.data.get('assignee'),
            'expected_return': request.data.get('expected_return'),
            'assignment_notes': request.data.get('notes', ''),
            'condition_on_assignment': asset.condition
        }
        
        serializer = AssetAssignmentSerializer(data=assignment_data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def return_asset(self, request, pk=None):
        """
        Return an assigned asset
        POST /assets/{id}/return_asset/
        """
        asset = self.get_object()
        
        if asset.status != 'assigned':
            return Response(
                {'error': 'Asset is not currently assigned'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find active assignment
        assignment = asset.assignments.filter(status='active').first()
        if not assignment:
            return Response(
                {'error': 'No active assignment found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        assignment.status = 'returned'
        assignment.actual_return = timezone.now()
        assignment.condition_on_return = request.data.get('condition', asset.condition)
        assignment.return_notes = request.data.get('notes', '')
        assignment.save()
        
        asset.current_assignee = None
        asset.assigned_at = None
        asset.status = 'available'
        asset.condition = assignment.condition_on_return
        asset.save()
        
        return Response(AssetSerializer(asset).data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get asset statistics"""
        queryset = self.get_queryset()
        
        stats = {
            'total': queryset.count(),
            'available': queryset.filter(status='available').count(),
            'assigned': queryset.filter(status='assigned').count(),
            'maintenance': queryset.filter(status='maintenance').count(),
            'by_type': dict(
                queryset.values('asset_type').annotate(count=Count('id')).values_list('asset_type', 'count')
            ),
            'by_status': dict(
                queryset.values('status').annotate(count=Count('id')).values_list('status', 'count')
            ),
            'warranty_expiring_soon': queryset.filter(
                warranty_expiry__lte=timezone.now().date() + timedelta(days=30),
                warranty_expiry__gte=timezone.now().date()
            ).count()
        }
        
        return Response(stats)


class AssetAssignmentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing asset assignments"""
    
    serializer_class = AssetAssignmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'assignee', 'asset']
    ordering = ['-assigned_at']
    
    def get_queryset(self):
        """Filter by organization through asset"""
        return AssetAssignment.objects.filter(asset__organization=self.request.user.organization)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active assignments"""
        assignments = self.get_queryset().filter(status='active')
        serializer = self.get_serializer(assignments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue assignments"""
        assignments = self.get_queryset().filter(
            status='active',
            expected_return__lt=timezone.now()
        )
        serializer = self.get_serializer(assignments, many=True)
        return Response(serializer.data)


class MovementLogViewSet(viewsets.ModelViewSet):
    """ViewSet for movement logs"""
    
    serializer_class = MovementLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['movement_type', 'asset', 'visitor', 'user']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        """Filter by organization"""
        return MovementLog.objects.filter(organization=self.request.user.organization)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent movements (last 24 hours)"""
        since = timezone.now() - timedelta(hours=24)
        logs = self.get_queryset().filter(timestamp__gte=since)
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
