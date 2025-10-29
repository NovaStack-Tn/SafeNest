from django.contrib import admin
from .models import Threat, Alert, RiskAssessment, ThreatIndicator, Watchlist


@admin.register(Threat)
class ThreatAdmin(admin.ModelAdmin):
    list_display = ['title', 'threat_type', 'severity', 'status', 'organization', 'created_at']
    list_filter = ['threat_type', 'severity', 'status', 'created_at']
    search_fields = ['title', 'description', 'source']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['assigned_to', 'created_by']


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'alert_type', 'severity', 'status', 'organization', 'created_at']
    list_filter = ['alert_type', 'severity', 'status', 'created_at']
    search_fields = ['title', 'description', 'source']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['threat', 'acknowledged_by', 'resolved_by']


@admin.register(RiskAssessment)
class RiskAssessmentAdmin(admin.ModelAdmin):
    list_display = ['threat', 'risk_level', 'likelihood', 'impact', 'organization', 'created_at']
    list_filter = ['risk_level', 'likelihood', 'impact', 'created_at']
    search_fields = ['threat__title', 'mitigation_strategy']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['threat', 'assessed_by']


@admin.register(ThreatIndicator)
class ThreatIndicatorAdmin(admin.ModelAdmin):
    list_display = ['indicator_type', 'value', 'confidence', 'is_active', 'organization', 'created_at']
    list_filter = ['indicator_type', 'confidence', 'is_active', 'created_at']
    search_fields = ['value', 'description', 'source']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['threat', 'added_by']


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ['subject_name', 'watchlist_type', 'risk_level', 'is_active', 'organization', 'created_at']
    list_filter = ['watchlist_type', 'risk_level', 'is_active', 'created_at']
    search_fields = ['subject_name', 'subject_id', 'reason', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['threat', 'added_by']
