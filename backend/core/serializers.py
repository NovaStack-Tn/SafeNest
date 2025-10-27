"""
Serializers for core models.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Organization, Role, Team, AuditLog

User = get_user_model()


class OrganizationSerializer(serializers.ModelSerializer):
    user_count = serializers.IntegerField(source='users.count', read_only=True)
    
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'slug', 'settings', 'is_active',
            'face_retention_days', 'consent_required', 'data_residency',
            'user_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'permissions', 'created_at']
        read_only_fields = ['created_at']


class UserSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'organization', 'organization_name', 'role', 'role_name',
            'phone', 'avatar', 'department', 'employee_id',
            'two_factor_enabled', 'is_active', 'is_staff',
            'last_login', 'date_joined', 'created_at', 'updated_at'
        ]
        read_only_fields = ['last_login', 'date_joined', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name',
            'organization', 'role', 'phone', 'department', 'employee_id'
        ]
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class TeamSerializer(serializers.ModelSerializer):
    member_count = serializers.IntegerField(source='members.count', read_only=True)
    lead_name = serializers.CharField(source='lead.get_full_name', read_only=True)
    
    class Meta:
        model = Team
        fields = [
            'id', 'organization', 'name', 'description',
            'members', 'member_count', 'lead', 'lead_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_name', 'organization', 'action',
            'model_name', 'object_id', 'changes', 'ip_address',
            'user_agent', 'timestamp'
        ]
        read_only_fields = ['timestamp']
