"""
Access Control Serializers
"""
from rest_framework import serializers
from .models import (
    AccessPoint,
    AccessSchedule,
    AccessPermission,
    AccessCredential,
    AccessLog,
    AccessAnomaly,
)
from core.serializers import UserSerializer


class AccessPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessPoint
        fields = [
            'id', 'organization', 'name', 'point_type', 'location', 'description',
            'hardware_id', 'ip_address', 'status', 'is_secure', 'requires_escort',
            'allow_tailgating_detection', 'max_access_attempts', 'lockdown_enabled',
            'latitude', 'longitude', 'meta', 'created_at', 'updated_at', 'last_activity_at'
        ]
        read_only_fields = ['organization', 'created_at', 'updated_at', 'last_activity_at']


class AccessScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessSchedule
        fields = [
            'id', 'organization', 'name', 'description', 'days_of_week',
            'start_time', 'end_time', 'valid_from', 'valid_until',
            'exclude_holidays', 'holiday_calendar', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['organization', 'created_at', 'updated_at']


class AccessPermissionSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    access_point_name = serializers.CharField(source='access_point.name', read_only=True)
    schedule_name = serializers.CharField(source='schedule.name', read_only=True, allow_null=True)
    granted_by_name = serializers.CharField(source='granted_by.username', read_only=True, allow_null=True)

    class Meta:
        model = AccessPermission
        fields = [
            'id', 'organization', 'user', 'user_details', 'access_point', 'access_point_name',
            'permission_type', 'schedule', 'schedule_name', 'valid_from', 'valid_until',
            'requires_pin', 'requires_biometric', 'requires_approval', 'max_daily_entries',
            'is_active', 'is_revoked', 'revoked_at', 'revoked_by', 'revocation_reason',
            'granted_by', 'granted_by_name', 'granted_at', 'notes'
        ]
        read_only_fields = ['organization', 'granted_at', 'revoked_at']


class AccessCredentialSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = AccessCredential
        fields = [
            'id', 'organization', 'user', 'user_name', 'credential_type', 'credential_id',
            'status', 'issued_at', 'expires_at', 'last_used_at',
            'failed_attempts', 'is_locked', 'locked_until', 'notes'
        ]
        read_only_fields = ['organization', 'issued_at', 'last_used_at', 'failed_attempts']
        extra_kwargs = {
            'biometric_template': {'write_only': True},
            'pin_code': {'write_only': True},
        }


class AccessLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True, allow_null=True)
    access_point_name = serializers.CharField(source='access_point.name', read_only=True)
    credential_id = serializers.CharField(source='credential.credential_id', read_only=True, allow_null=True)

    class Meta:
        model = AccessLog
        fields = [
            'id', 'organization', 'access_point', 'access_point_name',
            'user', 'user_name', 'credential', 'credential_id',
            'event_type', 'is_granted', 'denial_reason', 'timestamp',
            'is_tailgating', 'is_anomaly', 'anomaly_score',
            'direction', 'companion_count', 'latitude', 'longitude',
            'device_info', 'photo_url', 'video_clip_url', 'notes'
        ]
        read_only_fields = ['organization', 'timestamp']


class AccessAnomalySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    access_log_details = AccessLogSerializer(source='access_log', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.username', read_only=True, allow_null=True)

    class Meta:
        model = AccessAnomaly
        fields = [
            'id', 'organization', 'access_log', 'access_log_details',
            'user', 'user_name', 'anomaly_type', 'severity', 'confidence_score',
            'description', 'ai_model_used', 'baseline_pattern', 'detected_pattern',
            'is_reviewed', 'is_false_positive', 'reviewed_by', 'reviewed_by_name',
            'reviewed_at', 'review_notes', 'detected_at'
        ]
        read_only_fields = ['organization', 'detected_at']


# Stats and analytics serializers
class AccessStatsSerializer(serializers.Serializer):
    """Statistics for access control"""
    total_access_points = serializers.IntegerField()
    active_points = serializers.IntegerField()
    total_permissions = serializers.IntegerField()
    active_permissions = serializers.IntegerField()
    today_logs = serializers.IntegerField()
    today_granted = serializers.IntegerField()
    today_denied = serializers.IntegerField()
    today_anomalies = serializers.IntegerField()
    top_access_points = serializers.ListField()
    access_by_hour = serializers.DictField()
