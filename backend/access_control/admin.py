from django.contrib import admin
from .models import (
    AccessPoint,
    AccessSchedule,
    AccessPermission,
    AccessCredential,
    AccessLog,
    AccessAnomaly,
)


@admin.register(AccessPoint)
class AccessPointAdmin(admin.ModelAdmin):
    list_display = ['name', 'point_type', 'location', 'status', 'is_secure', 'last_activity_at']
    list_filter = ['point_type', 'status', 'organization']
    search_fields = ['name', 'location', 'hardware_id']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AccessSchedule)
class AccessScheduleAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_time', 'end_time', 'is_active']
    list_filter = ['is_active', 'organization']
    search_fields = ['name']


@admin.register(AccessPermission)
class AccessPermissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'access_point', 'permission_type', 'valid_from', 'valid_until', 'is_active']
    list_filter = ['permission_type', 'is_active', 'is_revoked']
    search_fields = ['user__username', 'access_point__name']
    readonly_fields = ['granted_at']


@admin.register(AccessCredential)
class AccessCredentialAdmin(admin.ModelAdmin):
    list_display = ['user', 'credential_type', 'credential_id', 'status', 'issued_at', 'expires_at']
    list_filter = ['credential_type', 'status']
    search_fields = ['user__username', 'credential_id']
    readonly_fields = ['issued_at', 'last_used_at']


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'access_point', 'event_type', 'is_granted', 'is_anomaly', 'timestamp']
    list_filter = ['event_type', 'is_granted', 'is_anomaly', 'is_tailgating']
    search_fields = ['user__username', 'access_point__name']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'


@admin.register(AccessAnomaly)
class AccessAnomalyAdmin(admin.ModelAdmin):
    list_display = ['user', 'anomaly_type', 'severity', 'confidence_score', 'is_reviewed', 'detected_at']
    list_filter = ['anomaly_type', 'severity', 'is_reviewed', 'is_false_positive']
    search_fields = ['user__username']
    readonly_fields = ['detected_at']
    date_hierarchy = 'detected_at'
