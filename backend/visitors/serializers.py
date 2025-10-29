"""
Serializers for Visitor & Asset Management
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Visitor, VisitorPass, Asset, AssetAssignment, MovementLog

User = get_user_model()


class VisitorSerializer(serializers.ModelSerializer):
    """Serializer for Visitor model"""
    
    host_name = serializers.CharField(source='host.username', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    full_name = serializers.CharField(read_only=True)
    is_checked_in = serializers.BooleanField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Visitor
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 'phone',
            'company', 'visitor_type', 'id_type', 'id_number', 'photo',
            'purpose', 'host', 'host_name', 'department',
            'status', 'expected_arrival', 'expected_departure',
            'actual_arrival', 'actual_departure',
            'ai_extracted', 'ai_confidence', 'ai_suggested_access_level',
            'ai_predicted_duration', 'extracted_data',
            'notes', 'emergency_contact', 'emergency_phone', 'vehicle_plate',
            'organization', 'created_by', 'created_by_name',
            'created_at', 'updated_at',
            'is_checked_in', 'is_overdue'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'organization']
    
    def create(self, validated_data):
        # Set created_by and organization from request
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
            validated_data['organization'] = request.user.organization
        return super().create(validated_data)


class VisitorListSerializer(serializers.ModelSerializer):
    """Simplified serializer for visitor lists"""
    
    full_name = serializers.CharField(read_only=True)
    host_name = serializers.CharField(source='host.username', read_only=True)
    
    class Meta:
        model = Visitor
        fields = [
            'id', 'full_name', 'company', 'visitor_type', 'status',
            'expected_arrival', 'expected_departure', 'host_name',
            'purpose', 'is_checked_in', 'is_overdue'
        ]


class VisitorPassSerializer(serializers.ModelSerializer):
    """Serializer for VisitorPass model"""
    
    visitor_name = serializers.CharField(source='visitor.full_name', read_only=True)
    issued_by_name = serializers.CharField(source='issued_by.username', read_only=True)
    is_valid = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = VisitorPass
        fields = [
            'id', 'visitor', 'visitor_name', 'pass_type', 'pass_code',
            'access_level', 'allowed_areas', 'access_points',
            'valid_from', 'valid_until', 'status',
            'times_used', 'last_used', 'max_uses',
            'issued_by', 'issued_by_name', 'issued_at',
            'revoked_by', 'revoked_at', 'revocation_reason',
            'is_valid'
        ]
        read_only_fields = ['id', 'issued_at', 'issued_by', 'times_used', 'last_used']
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['issued_by'] = request.user
        return super().create(validated_data)


class AssetSerializer(serializers.ModelSerializer):
    """Serializer for Asset model"""
    
    current_assignee_name = serializers.CharField(source='current_assignee.username', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    warranty_active = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Asset
        fields = [
            'id', 'name', 'asset_type', 'asset_tag', 'serial_number',
            'description', 'manufacturer', 'model',
            'purchase_date', 'purchase_price', 'warranty_expiry',
            'status', 'condition', 'location',
            'current_assignee', 'current_assignee_name', 'assigned_at',
            'image', 'notes', 'specifications',
            'organization', 'created_by', 'created_by_name',
            'created_at', 'updated_at',
            'is_available', 'warranty_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'organization']
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
            validated_data['organization'] = request.user.organization
        return super().create(validated_data)


class AssetListSerializer(serializers.ModelSerializer):
    """Simplified serializer for asset lists"""
    
    current_assignee_name = serializers.CharField(source='current_assignee.username', read_only=True)
    
    class Meta:
        model = Asset
        fields = [
            'id', 'asset_tag', 'name', 'asset_type', 'status',
            'condition', 'location', 'current_assignee_name'
        ]


class AssetAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for AssetAssignment model"""
    
    asset_tag = serializers.CharField(source='asset.asset_tag', read_only=True)
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    assignee_name = serializers.CharField(source='assignee.username', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.username', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = AssetAssignment
        fields = [
            'id', 'asset', 'asset_tag', 'asset_name',
            'assignee', 'assignee_name',
            'assigned_by', 'assigned_by_name', 'assigned_at',
            'expected_return', 'actual_return',
            'status', 'condition_on_assignment', 'condition_on_return',
            'assignment_notes', 'return_notes',
            'is_overdue'
        ]
        read_only_fields = ['id', 'assigned_at', 'assigned_by']
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['assigned_by'] = request.user
        
        # Update asset status when creating assignment
        asset = validated_data['asset']
        asset.current_assignee = validated_data['assignee']
        asset.assigned_at = validated_data.get('assigned_at')
        asset.status = 'assigned'
        asset.save()
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # If marking as returned, update asset
        if validated_data.get('status') == 'returned' and instance.status != 'returned':
            asset = instance.asset
            asset.current_assignee = None
            asset.assigned_at = None
            asset.status = 'available'
            asset.save()
        
        return super().update(instance, validated_data)


class MovementLogSerializer(serializers.ModelSerializer):
    """Serializer for MovementLog model"""
    
    asset_tag = serializers.CharField(source='asset.asset_tag', read_only=True)
    visitor_name = serializers.CharField(source='visitor.full_name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    verified_by_name = serializers.CharField(source='verified_by.username', read_only=True)
    access_point_name = serializers.CharField(source='access_point.name', read_only=True)
    
    class Meta:
        model = MovementLog
        fields = [
            'id', 'movement_type', 'timestamp',
            'asset', 'asset_tag',
            'visitor', 'visitor_name',
            'user', 'user_name',
            'from_location', 'to_location',
            'access_point', 'access_point_name',
            'verified_by', 'verified_by_name', 'verification_method',
            'notes', 'metadata',
            'organization'
        ]
        read_only_fields = ['id', 'timestamp', 'organization']
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['organization'] = request.user.organization
        return super().create(validated_data)


# AI-specific serializers

class AIExtractionRequestSerializer(serializers.Serializer):
    """Serializer for AI extraction requests"""
    
    text = serializers.CharField(
        required=True,
        help_text="Text to extract visitor information from (email, form, etc.)"
    )
    source_type = serializers.ChoiceField(
        choices=['email', 'form', 'message'],
        default='email',
        help_text="Type of source document"
    )


class AIAccessLevelRequestSerializer(serializers.Serializer):
    """Serializer for AI access level suggestion requests"""
    
    visitor_type = serializers.CharField(required=True)
    purpose = serializers.CharField(required=True)
    company = serializers.CharField(required=False, allow_blank=True)
    department = serializers.CharField(required=False, allow_blank=True)
    expected_duration = serializers.IntegerField(required=False)


class AIDurationPredictionRequestSerializer(serializers.Serializer):
    """Serializer for AI duration prediction requests"""
    
    visitor_type = serializers.CharField(required=True)
    purpose = serializers.CharField(required=True)
    company = serializers.CharField(required=False, allow_blank=True)


class AIAutoFillRequestSerializer(serializers.Serializer):
    """Serializer for AI auto-fill requests"""
    
    partial_data = serializers.JSONField(required=True)
    context = serializers.CharField(required=False, allow_blank=True, default="")


class AIRiskAnalysisRequestSerializer(serializers.Serializer):
    """Serializer for AI risk analysis requests"""
    
    visitor_data = serializers.JSONField(required=True)
    include_history = serializers.BooleanField(default=False)
