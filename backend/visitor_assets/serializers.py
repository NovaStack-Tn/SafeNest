"""
Visitor & Asset Management Serializers
"""
from rest_framework import serializers
from .models import (
    Visitor,
    VisitorPass,
    Asset,
    AssetAssignment,
    MovementLog,
    VisitorAnalytics,
)
from core.serializers import UserSerializer


class VisitorSerializer(serializers.ModelSerializer):
    host_name = serializers.CharField(source='host.username', read_only=True, allow_null=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Visitor
        fields = [
            'id', 'organization', 'first_name', 'last_name', 'full_name', 'email', 'phone', 'company',
            'visitor_type', 'status', 'id_type', 'id_number', 'photo_url',
            'host', 'host_name', 'purpose_of_visit', 'department_to_visit',
            'risk_score', 'is_on_watchlist', 'watchlist_reason', 'requires_escort',
            'background_check_status', 'nda_signed', 'nda_signed_at', 'agreements',
            'notes', 'created_at', 'updated_at', 'visit_count', 'last_visit_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'visit_count', 'last_visit_at', 'risk_score']
        extra_kwargs = {
            'face_embedding': {'write_only': True},
        }


class VisitorPassSerializer(serializers.ModelSerializer):
    visitor_name = serializers.CharField(source='visitor.full_name', read_only=True)
    issued_by_name = serializers.CharField(source='issued_by.username', read_only=True, allow_null=True)

    class Meta:
        model = VisitorPass
        fields = [
            'id', 'organization', 'visitor', 'visitor_name', 'pass_type', 'pass_number', 'qr_code',
            'valid_from', 'valid_until', 'allowed_zones',
            'checked_in_at', 'checked_out_at', 'check_in_location', 'check_out_location',
            'status', 'issued_by', 'issued_by_name', 'issued_at',
            'revoked_by', 'revoked_at', 'revocation_reason', 'notes'
        ]
        read_only_fields = ['issued_at', 'revoked_at']


class AssetSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True, allow_null=True)

    class Meta:
        model = Asset
        fields = [
            'id', 'organization', 'name', 'asset_type', 'asset_tag', 'serial_number',
            'manufacturer', 'model', 'description',
            'purchase_date', 'purchase_cost', 'current_value',
            'current_location', 'home_location',
            'has_gps', 'last_gps_lat', 'last_gps_lon', 'last_gps_update',
            'rfid_tag', 'iot_device_id', 'status',
            'last_maintenance_date', 'next_maintenance_date', 'maintenance_interval_days',
            'predicted_failure_date', 'failure_probability',
            'assigned_to', 'assigned_to_name', 'assigned_at',
            'photo_url', 'qr_code', 'meta', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'predicted_failure_date', 'failure_probability']


class AssetAssignmentSerializer(serializers.ModelSerializer):
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.username', read_only=True, allow_null=True)

    class Meta:
        model = AssetAssignment
        fields = [
            'id', 'organization', 'asset', 'asset_name',
            'assigned_to', 'assigned_to_name', 'assigned_at', 'returned_at', 'expected_return_at',
            'assigned_by', 'assigned_by_name', 'assignment_reason', 'location_at_assignment',
            'condition_at_assignment', 'condition_at_return', 'condition_notes',
            'is_overdue', 'is_returned', 'notes'
        ]
        read_only_fields = ['assigned_at', 'is_overdue']


class MovementLogSerializer(serializers.ModelSerializer):
    visitor_name = serializers.CharField(source='visitor.full_name', read_only=True, allow_null=True)
    asset_name = serializers.CharField(source='asset.name', read_only=True, allow_null=True)
    moved_by_name = serializers.CharField(source='moved_by.username', read_only=True, allow_null=True)

    class Meta:
        model = MovementLog
        fields = [
            'id', 'organization', 'entity_type',
            'visitor', 'visitor_name', 'asset', 'asset_name',
            'event_type', 'from_location', 'to_location', 'zone',
            'latitude', 'longitude', 'timestamp',
            'moved_by', 'moved_by_name', 'detection_method',
            'photo_url', 'meta', 'notes'
        ]
        read_only_fields = ['timestamp']


class VisitorAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitorAnalytics
        fields = [
            'id', 'organization', 'date', 'hour',
            'total_visitors', 'new_visitors', 'repeat_visitors', 'vip_visitors',
            'guest_count', 'contractor_count', 'vendor_count',
            'avg_visit_duration_minutes', 'avg_check_in_time_minutes',
            'top_departments', 'peak_hour',
            'anomaly_count', 'high_risk_visitors', 'predicted_tomorrow',
            'created_at'
        ]
        read_only_fields = ['created_at']


# Stats serializers
class VisitorStatsSerializer(serializers.Serializer):
    """Statistics for visitors"""
    total_visitors = serializers.IntegerField()
    active_visitors = serializers.IntegerField()
    today_check_ins = serializers.IntegerField()
    today_check_outs = serializers.IntegerField()
    high_risk_count = serializers.IntegerField()
    on_watchlist = serializers.IntegerField()
    top_companies = serializers.ListField()
    visitor_trends = serializers.DictField()


class AssetStatsSerializer(serializers.Serializer):
    """Statistics for assets"""
    total_assets = serializers.IntegerField()
    assigned_assets = serializers.IntegerField()
    available_assets = serializers.IntegerField()
    maintenance_due = serializers.IntegerField()
    overdue_returns = serializers.IntegerField()
    predicted_failures = serializers.IntegerField()
    asset_by_type = serializers.DictField()
    top_assignees = serializers.ListField()
