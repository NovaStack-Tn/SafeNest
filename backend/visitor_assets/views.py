"""
Visitor & Asset Management Views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Count, Q, Avg
from datetime import datetime, timedelta

from .models import (
    Visitor,
    VisitorPass,
    Asset,
    AssetAssignment,
    MovementLog,
    VisitorAnalytics,
)
from .serializers import (
    VisitorSerializer,
    VisitorPassSerializer,
    AssetSerializer,
    AssetAssignmentSerializer,
    MovementLogSerializer,
    VisitorAnalyticsSerializer,
    VisitorStatsSerializer,
    AssetStatsSerializer,
)
from .ai_service import VisitorAIService


class VisitorViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Visitors
    """
    serializer_class = VisitorSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['visitor_type', 'status', 'host', 'is_on_watchlist']
    search_fields = ['first_name', 'last_name', 'email', 'company']
    ordering_fields = ['created_at', 'last_visit_at', 'risk_score']

    def get_queryset(self):
        return Visitor.objects.filter(
            organization=self.request.user.organization
        ).select_related('host')

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)

    @action(detail=True, methods=['post'])
    def check_in(self, request, pk=None):
        """Check in a visitor"""
        visitor = self.get_object()
        visitor.status = 'checked_in'
        visitor.visit_count += 1
        visitor.last_visit_at = timezone.now()
        visitor.save()

        # Create movement log
        MovementLog.objects.create(
            organization=visitor.organization,
            entity_type='visitor',
            visitor=visitor,
            event_type='check_in',
            to_location=request.data.get('location', 'Reception'),
            timestamp=timezone.now(),
            detection_method='manual'
        )

        return Response({'status': 'visitor checked in'})

    @action(detail=True, methods=['post'])
    def check_out(self, request, pk=None):
        """Check out a visitor"""
        visitor = self.get_object()
        visitor.status = 'checked_out'
        visitor.save()

        # Create movement log
        MovementLog.objects.create(
            organization=visitor.organization,
            entity_type='visitor',
            visitor=visitor,
            event_type='check_out',
            to_location=request.data.get('location', 'Exit'),
            timestamp=timezone.now(),
            detection_method='manual'
        )

        return Response({'status': 'visitor checked out'})

    @action(detail=True, methods=['post'])
    def add_to_watchlist(self, request, pk=None):
        """Add visitor to watchlist"""
        visitor = self.get_object()
        visitor.is_on_watchlist = True
        visitor.watchlist_reason = request.data.get('reason', '')
        visitor.save()
        return Response({'status': 'added to watchlist'})
    
    # AI-Powered Endpoints (Gemini 2.5 Flash)
    
    @action(detail=False, methods=['post'], url_path='ai-extract')
    def ai_extract_info(self, request):
        """
        Extract visitor information from text using AI
        POST /api/visitors/visitors/ai-extract/
        Body: {"text": "Email content", "source_type": "email|form|message"}
        """
        text = request.data.get('text')
        source_type = request.data.get('source_type', 'email')
        
        if not text:
            return Response({'error': 'Text is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        ai_service = VisitorAIService()
        result = ai_service.extract_visitor_info(text=text, source_type=source_type)
        
        return Response(result)
    
    @action(detail=False, methods=['post'], url_path='ai-suggest-access')
    def ai_suggest_access_level(self, request):
        """
        Get AI suggestion for visitor access level
        POST /api/visitors/visitors/ai-suggest-access/
        """
        ai_service = VisitorAIService()
        result = ai_service.suggest_access_level(request.data)
        return Response(result)
    
    @action(detail=False, methods=['post'], url_path='ai-predict-duration')
    def ai_predict_duration(self, request):
        """
        Predict visit duration using AI
        POST /api/visitors/visitors/ai-predict-duration/
        """
        ai_service = VisitorAIService()
        result = ai_service.predict_visit_duration(request.data)
        return Response(result)
    
    @action(detail=False, methods=['post'], url_path='ai-autofill')
    def ai_autofill_form(self, request):
        """
        Auto-fill visitor form using AI
        POST /api/visitors/visitors/ai-autofill/
        """
        partial_data = request.data.get('partial_data', {})
        context = request.data.get('context', '')
        
        ai_service = VisitorAIService()
        result = ai_service.auto_fill_visitor_form(
            partial_data=partial_data,
            context=context
        )
        return Response(result)
    
    @action(detail=True, methods=['post'], url_path='analyze-risk')
    def analyze_risk(self, request, pk=None):
        """
        Analyze visitor risk using AI
        POST /api/visitors/visitors/{id}/analyze-risk/
        """
        visitor = self.get_object()
        
        # Get historical data for this visitor
        historical = Visitor.objects.filter(
            organization=request.user.organization,
            email=visitor.email
        ).exclude(id=visitor.id).values(
            'visitor_type', 'purpose_of_visit', 'status', 'created_at'
        )
        
        visitor_data = VisitorSerializer(visitor).data
        
        ai_service = VisitorAIService()
        result = ai_service.analyze_visitor_risk(
            visitor_data=visitor_data,
            historical_data=list(historical) if historical.exists() else None
        )
        
        return Response(result)

    @action(detail=False, methods=['get'])
    def on_premises(self, request):
        """Get all visitors currently on premises"""
        visitors = self.get_queryset().filter(status='on_premises')
        serializer = self.get_serializer(visitors, many=True)
        return Response(serializer.data)


class VisitorPassViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Visitor Passes
    """
    serializer_class = VisitorPassSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['visitor', 'pass_type', 'status']
    search_fields = ['pass_number', 'visitor__first_name', 'visitor__last_name']
    ordering_fields = ['issued_at', 'valid_until']

    def get_queryset(self):
        return VisitorPass.objects.filter(
            organization=self.request.user.organization
        ).select_related('visitor', 'issued_by')

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            issued_by=self.request.user
        )

    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """Revoke a visitor pass"""
        pass_obj = self.get_object()
        pass_obj.status = 'revoked'
        pass_obj.revoked_by = request.user
        pass_obj.revoked_at = timezone.now()
        pass_obj.revocation_reason = request.data.get('reason', '')
        pass_obj.save()
        return Response({'status': 'pass revoked'})

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active passes"""
        now = timezone.now()
        passes = self.get_queryset().filter(
            status='active',
            valid_from__lte=now,
            valid_until__gte=now
        )
        serializer = self.get_serializer(passes, many=True)
        return Response(serializer.data)


class AssetViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Assets
    """
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['asset_type', 'status', 'assigned_to', 'has_gps']
    search_fields = ['name', 'asset_tag', 'serial_number']
    ordering_fields = ['name', 'created_at', 'purchase_date']

    def get_queryset(self):
        return Asset.objects.filter(
            organization=self.request.user.organization
        ).select_related('assigned_to')

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign asset to a user"""
        asset = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'user_id required'}, status=400)

        # Create assignment
        AssetAssignment.objects.create(
            organization=asset.organization,
            asset=asset,
            assigned_to_id=user_id,
            assigned_by=request.user,
            assigned_at=timezone.now(),
            assignment_reason=request.data.get('reason', ''),
            condition_at_assignment='good'
        )

        # Update asset
        asset.status = 'assigned'
        asset.assigned_to_id = user_id
        asset.assigned_at = timezone.now()
        asset.save()

        return Response({'status': 'asset assigned'})

    @action(detail=True, methods=['post'])
    def return_asset(self, request, pk=None):
        """Return an assigned asset"""
        asset = self.get_object()
        
        # Find active assignment
        assignment = AssetAssignment.objects.filter(
            asset=asset,
            is_returned=False
        ).first()

        if assignment:
            assignment.is_returned = True
            assignment.returned_at = timezone.now()
            assignment.condition_at_return = request.data.get('condition', 'good')
            assignment.save()

        asset.status = 'available'
        asset.assigned_to = None
        asset.save()

        return Response({'status': 'asset returned'})

    @action(detail=True, methods=['post'])
    def report_lost(self, request, pk=None):
        """Report asset as lost"""
        asset = self.get_object()
        asset.status = 'lost'
        asset.save()
        return Response({'status': 'asset marked as lost'})

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get all available assets"""
        assets = self.get_queryset().filter(status='available')
        serializer = self.get_serializer(assets, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def maintenance_due(self, request):
        """Get assets with maintenance due"""
        today = timezone.now().date()
        assets = self.get_queryset().filter(
            next_maintenance_date__lte=today,
            status__in=['available', 'assigned']
        )
        serializer = self.get_serializer(assets, many=True)
        return Response(serializer.data)


class AssetAssignmentViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Asset Assignments
    """
    serializer_class = AssetAssignmentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['asset', 'assigned_to', 'is_returned', 'is_overdue']
    search_fields = ['asset__name', 'assigned_to__username']
    ordering_fields = ['assigned_at', 'expected_return_at']

    def get_queryset(self):
        return AssetAssignment.objects.filter(
            organization=self.request.user.organization
        ).select_related('asset', 'assigned_to', 'assigned_by')

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            assigned_by=self.request.user
        )

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue assignments"""
        assignments = self.get_queryset().filter(is_overdue=True, is_returned=False)
        serializer = self.get_serializer(assignments, many=True)
        return Response(serializer.data)


class MovementLogViewSet(viewsets.ModelViewSet):
    """
    Movement logs for visitors and assets
    """
    serializer_class = MovementLogSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['entity_type', 'event_type', 'visitor', 'asset', 'detection_method']
    search_fields = ['to_location', 'zone']
    ordering_fields = ['timestamp']
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        return MovementLog.objects.filter(
            organization=self.request.user.organization
        ).select_related('visitor', 'asset', 'moved_by')

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent movements"""
        hours = int(request.query_params.get('hours', 24))
        since = timezone.now() - timedelta(hours=hours)
        movements = self.get_queryset().filter(timestamp__gte=since)
        serializer = self.get_serializer(movements, many=True)
        return Response(serializer.data)


class VisitorAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Visitor analytics and insights
    """
    serializer_class = VisitorAnalyticsSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['date']

    def get_queryset(self):
        return VisitorAnalytics.objects.filter(
            organization=self.request.user.organization
        )


class StatsViewSet(viewsets.ViewSet):
    """
    Statistics for visitors and assets
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def visitor_summary(self, request):
        """Get visitor statistics"""
        org = request.user.organization
        today = timezone.now().date()

        stats = {
            'total_visitors': Visitor.objects.filter(organization=org).count(),
            'active_visitors': Visitor.objects.filter(
                organization=org,
                status__in=['checked_in', 'on_premises']
            ).count(),
            'today_check_ins': MovementLog.objects.filter(
                organization=org,
                entity_type='visitor',
                event_type='check_in',
                timestamp__date=today
            ).count(),
            'today_check_outs': MovementLog.objects.filter(
                organization=org,
                entity_type='visitor',
                event_type='check_out',
                timestamp__date=today
            ).count(),
            'high_risk_count': Visitor.objects.filter(
                organization=org,
                risk_score__gte=0.7
            ).count(),
            'on_watchlist': Visitor.objects.filter(
                organization=org,
                is_on_watchlist=True
            ).count(),
            'top_companies': list(
                Visitor.objects.filter(organization=org)
                .values('company')
                .annotate(count=Count('id'))
                .order_by('-count')[:5]
            ),
            'visitor_trends': {}
        }

        serializer = VisitorStatsSerializer(stats)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def asset_summary(self, request):
        """Get asset statistics"""
        org = request.user.organization
        today = timezone.now().date()

        stats = {
            'total_assets': Asset.objects.filter(organization=org).count(),
            'assigned_assets': Asset.objects.filter(
                organization=org,
                status='assigned'
            ).count(),
            'available_assets': Asset.objects.filter(
                organization=org,
                status='available'
            ).count(),
            'maintenance_due': Asset.objects.filter(
                organization=org,
                next_maintenance_date__lte=today
            ).count(),
            'overdue_returns': AssetAssignment.objects.filter(
                organization=org,
                is_overdue=True,
                is_returned=False
            ).count(),
            'predicted_failures': Asset.objects.filter(
                organization=org,
                failure_probability__gte=0.7
            ).count(),
            'asset_by_type': dict(
                Asset.objects.filter(organization=org)
                .values_list('asset_type')
                .annotate(count=Count('id'))
            ),
            'top_assignees': list(
                AssetAssignment.objects.filter(organization=org, is_returned=False)
                .values('assigned_to__username')
                .annotate(count=Count('id'))
                .order_by('-count')[:5]
            )
        }

        serializer = AssetStatsSerializer(stats)
        return Response(serializer.data)
