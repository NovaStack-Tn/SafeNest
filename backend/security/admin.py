"""
Admin configuration for security models.
"""
from django.contrib import admin
from .models import LoginEvent, AnomalyRule, Alert


@admin.register(LoginEvent)
class LoginEventAdmin(admin.ModelAdmin):
    list_display = ['username', 'success', 'ip_address', 'country_name', 'device_type', 'is_anomaly', 'risk_score', 'timestamp']
    list_filter = ['success', 'is_anomaly', 'device_type', 'timestamp']
    search_fields = ['username', 'ip_address', 'country_name', 'city']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'


@admin.register(AnomalyRule)
class AnomalyRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'rule_type', 'severity', 'active', 'created_at']
    list_filter = ['organization', 'rule_type', 'severity', 'active']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'organization', 'severity', 'status', 'assigned_to', 'created_at']
    list_filter = ['organization', 'severity', 'status', 'created_at']
    search_fields = ['title', 'message']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
