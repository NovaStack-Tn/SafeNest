from django.contrib import admin
from .models import (
    Visitor,
    VisitorPass,
    Asset,
    AssetAssignment,
    MovementLog,
    VisitorAnalytics,
)


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'company', 'visitor_type', 'status', 'host', 'risk_score', 'visit_count']
    list_filter = ['visitor_type', 'status', 'is_on_watchlist', 'background_check_status']
    search_fields = ['first_name', 'last_name', 'email', 'company']
    readonly_fields = ['created_at', 'updated_at', 'visit_count']


@admin.register(VisitorPass)
class VisitorPassAdmin(admin.ModelAdmin):
    list_display = ['pass_number', 'visitor', 'pass_type', 'status', 'valid_from', 'valid_until']
    list_filter = ['pass_type', 'status']
    search_fields = ['pass_number', 'visitor__first_name', 'visitor__last_name']
    readonly_fields = ['issued_at']


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['name', 'asset_tag', 'asset_type', 'status', 'assigned_to', 'current_location']
    list_filter = ['asset_type', 'status', 'has_gps']
    search_fields = ['name', 'asset_tag', 'serial_number']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AssetAssignment)
class AssetAssignmentAdmin(admin.ModelAdmin):
    list_display = ['asset', 'assigned_to', 'assigned_at', 'expected_return_at', 'is_returned', 'is_overdue']
    list_filter = ['is_returned', 'is_overdue']
    search_fields = ['asset__name', 'assigned_to__username']
    readonly_fields = ['assigned_at']


@admin.register(MovementLog)
class MovementLogAdmin(admin.ModelAdmin):
    list_display = ['entity_type', 'event_type', 'to_location', 'timestamp', 'detection_method']
    list_filter = ['entity_type', 'event_type', 'detection_method']
    search_fields = ['to_location', 'zone']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'


@admin.register(VisitorAnalytics)
class VisitorAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['organization', 'date', 'hour', 'total_visitors', 'new_visitors', 'avg_visit_duration_minutes']
    list_filter = ['date']
    readonly_fields = ['created_at']
    date_hierarchy = 'date'
