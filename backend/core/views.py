"""
API views for core app.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from .models import Organization, Role, Team, AuditLog
from .serializers import (
    OrganizationSerializer, RoleSerializer, UserSerializer,
    UserCreateSerializer, TeamSerializer, AuditLogSerializer
)

User = get_user_model()


class OrganizationViewSet(viewsets.ModelViewSet):
    """API endpoint for organizations."""
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'slug']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class RoleViewSet(viewsets.ModelViewSet):
    """API endpoint for roles."""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class UserViewSet(viewsets.ModelViewSet):
    """API endpoint for users."""
    queryset = User.objects.select_related('organization', 'role')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['organization', 'role', 'is_active', 'department']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'employee_id']
    ordering_fields = ['username', 'email', 'date_joined']
    ordering = ['-date_joined']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def get_queryset(self):
        """Filter users by organization for non-admin users."""
        user = self.request.user
        queryset = super().get_queryset()
        
        if not user.is_staff and user.organization:
            queryset = queryset.filter(organization=user.organization)
        
        return queryset
    
    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        """Get or update current user profile."""
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        elif request.method == 'PATCH':
            serializer = self.get_serializer(request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='change-password')
    def change_password(self, request):
        """Change current user's password."""
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password or not new_password:
            return Response(
                {'error': 'Both old and new passwords are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not user.check_password(old_password):
            return Response(
                {'error': 'Old password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(new_password) < 8:
            return Response(
                {'error': 'New password must be at least 8 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        
        return Response({'message': 'Password changed successfully'})
    
    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """Admin can reset user password."""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admins can reset passwords'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = self.get_object()
        new_password = request.data.get('new_password')
        
        if not new_password or len(new_password) < 8:
            return Response(
                {'error': 'Password must be at least 8 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        
        return Response({'message': 'Password reset successfully'})


class TeamViewSet(viewsets.ModelViewSet):
    """API endpoint for teams."""
    queryset = Team.objects.select_related('organization', 'lead').prefetch_related('members')
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['organization']
    search_fields = ['name', 'description']
    
    def get_queryset(self):
        """Filter teams by organization for non-admin users."""
        user = self.request.user
        queryset = super().get_queryset()
        
        if not user.is_staff and user.organization:
            queryset = queryset.filter(organization=user.organization)
        
        return queryset


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for audit logs (read-only)."""
    queryset = AuditLog.objects.select_related('user', 'organization')
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'organization', 'action', 'model_name']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
