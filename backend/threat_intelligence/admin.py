"""
Threat Intelligence Management Admin Configuration
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Threat,
    Alert,
    RiskAssessment,
    ThreatIndicator,
    Watchlist,
    ThreatFeed,
    ThreatHuntingQuery
)


@admin.register(Threat)
class ThreatAdmin(admin.ModelAdmin):
    """Admin interface for Threat model"""
    list_display = [
        'id', 'title', 'threat_type', 'severity_badge', 'status_badge',
        'risk_score', 'organization', 'first_detected_at'
    ]
    list_filter = [
        'threat_type', 'severity', 'status', 'organization',
        'first_detected_at'
    ]
    search_fields = ['title', 'description', 'external_ref']
    readonly_fields = ['first_detected_at', 'last_seen_at', 'risk_score']
    date_hierarchy = 'first_detected_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'title', 'description', 'threat_type')
        }),
        ('Risk Assessment', {
            'fields': ('severity', 'status', 'risk_score', 'confidence_score')
        }),
        ('Source & Reference', {
            'fields': ('source', 'external_ref')
        }),
        ('Assignment', {
            'fields': ('assigned_to', 'created_by')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude', 'location_name'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('tags', 'metadata', 'attack_vector', 'impact_analysis'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('first_detected_at', 'last_seen_at', 'resolved_at'),
            'classes': ('collapse',)
        })
    )
    
    def severity_badge(self, obj):
        """Display severity as colored badge"""
        colors = {
            'critical': '#dc3545',
            'high': '#fd7e14',
            'medium': '#ffc107',
            'low': '#28a745'
        }
        color = colors.get(obj.severity, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.get_severity_display()
        )
    severity_badge.short_description = 'Severity'
    
    def status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            'new': '#007bff',
            'investigating': '#17a2b8',
            'confirmed': '#ffc107',
            'mitigated': '#28a745',
            'resolved': '#6c757d',
            'false_positive': '#6c757d'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    """Admin interface for Alert model"""
    list_display = [
        'id', 'title', 'alert_type', 'severity_badge', 'status_badge',
        'user', 'organization', 'triggered_at'
    ]
    list_filter = [
        'alert_type', 'severity', 'status', 'organization',
        'triggered_at', 'is_aggregated'
    ]
    search_fields = ['title', 'description']
    readonly_fields = ['triggered_at', 'confidence_score']
    date_hierarchy = 'triggered_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'title', 'description', 'alert_type')
        }),
        ('Severity & Status', {
            'fields': ('severity', 'status', 'confidence_score')
        }),
        ('Relationships', {
            'fields': ('threat', 'user', 'access_point')
        }),
        ('Detection', {
            'fields': ('detection_method',)
        }),
        ('Assignment', {
            'fields': ('assigned_to', 'acknowledged_by', 'acknowledged_at')
        }),
        ('Aggregation', {
            'fields': ('is_aggregated', 'parent_alert', 'aggregation_count'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('source_data', 'context', 'tags'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('triggered_at', 'resolved_at'),
            'classes': ('collapse',)
        })
    )
    
    def severity_badge(self, obj):
        """Display severity as colored badge"""
        colors = {
            'critical': '#dc3545',
            'high': '#fd7e14',
            'medium': '#ffc107',
            'low': '#28a745',
            'info': '#17a2b8'
        }
        color = colors.get(obj.severity, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.get_severity_display()
        )
    severity_badge.short_description = 'Severity'
    
    def status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            'new': '#dc3545',
            'acknowledged': '#ffc107',
            'investigating': '#17a2b8',
            'resolved': '#28a745',
            'false_positive': '#6c757d',
            'suppressed': '#6c757d'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(RiskAssessment)
class RiskAssessmentAdmin(admin.ModelAdmin):
    """Admin interface for RiskAssessment model"""
    list_display = [
        'id', 'title', 'assessment_type', 'risk_level_badge',
        'risk_score', 'is_active', 'organization', 'assessed_at'
    ]
    list_filter = [
        'assessment_type', 'risk_level', 'is_active',
        'organization', 'assessed_at'
    ]
    search_fields = ['title', 'description']
    readonly_fields = ['assessed_at', 'updated_at']
    date_hierarchy = 'assessed_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'title', 'description', 'assessment_type')
        }),
        ('Risk Metrics', {
            'fields': ('risk_level', 'risk_score', 'likelihood', 'impact')
        }),
        ('Subject', {
            'fields': ('subject_user', 'subject_access_point', 'subject_identifier')
        }),
        ('Analysis', {
            'fields': ('risk_factors', 'vulnerabilities', 'mitigation_recommendations')
        }),
        ('Assessment Details', {
            'fields': ('assessed_by', 'assessment_method')
        }),
        ('Validity', {
            'fields': ('is_active', 'valid_from', 'valid_until')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('assessed_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def risk_level_badge(self, obj):
        """Display risk level as colored badge"""
        colors = {
            'critical': '#dc3545',
            'severe': '#fd7e14',
            'high': '#ffc107',
            'moderate': '#17a2b8',
            'low': '#28a745',
            'minimal': '#6c757d'
        }
        color = colors.get(obj.risk_level, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.get_risk_level_display()
        )
    risk_level_badge.short_description = 'Risk Level'


@admin.register(ThreatIndicator)
class ThreatIndicatorAdmin(admin.ModelAdmin):
    """Admin interface for ThreatIndicator model"""
    list_display = [
        'id', 'indicator_type', 'indicator_value_short',
        'severity_badge', 'status_badge', 'confidence_score',
        'organization', 'last_seen'
    ]
    list_filter = [
        'indicator_type', 'severity', 'status',
        'organization', 'first_seen'
    ]
    search_fields = ['indicator_value', 'description']
    readonly_fields = ['first_seen', 'last_seen', 'times_detected']
    date_hierarchy = 'first_seen'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'indicator_type', 'indicator_value', 'description')
        }),
        ('Severity & Status', {
            'fields': ('severity', 'status', 'confidence_score', 'false_positive_rate')
        }),
        ('Relationship', {
            'fields': ('threat',)
        }),
        ('Detection Tracking', {
            'fields': ('first_seen', 'last_seen', 'times_detected')
        }),
        ('Source', {
            'fields': ('source', 'external_references')
        }),
        ('Expiration', {
            'fields': ('expires_at',)
        }),
        ('Metadata', {
            'fields': ('tags', 'metadata', 'added_by'),
            'classes': ('collapse',)
        })
    )
    
    def indicator_value_short(self, obj):
        """Display shortened indicator value"""
        if len(obj.indicator_value) > 50:
            return obj.indicator_value[:50] + '...'
        return obj.indicator_value
    indicator_value_short.short_description = 'Indicator Value'
    
    def severity_badge(self, obj):
        """Display severity as colored badge"""
        colors = {
            'critical': '#dc3545',
            'high': '#fd7e14',
            'medium': '#ffc107',
            'low': '#28a745'
        }
        color = colors.get(obj.severity, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.get_severity_display()
        )
    severity_badge.short_description = 'Severity'
    
    def status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            'active': '#dc3545',
            'inactive': '#6c757d',
            'expired': '#6c757d',
            'whitelisted': '#28a745'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    """Admin interface for Watchlist model"""
    list_display = [
        'id', 'name', 'watchlist_type', 'threat_level_badge',
        'status_badge', 'subject_identifier', 'times_detected',
        'organization', 'created_at'
    ]
    list_filter = [
        'watchlist_type', 'threat_level', 'status',
        'organization', 'alert_on_detection', 'auto_block'
    ]
    search_fields = ['name', 'subject_identifier', 'description']
    readonly_fields = ['created_at', 'updated_at', 'times_detected']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'watchlist_type', 'name', 'description')
        }),
        ('Threat Level & Status', {
            'fields': ('threat_level', 'status')
        }),
        ('Subject', {
            'fields': ('subject_identifier', 'subject_user')
        }),
        ('Detection Settings', {
            'fields': ('alert_on_detection', 'auto_block')
        }),
        ('Monitoring', {
            'fields': ('times_detected', 'last_detected_at', 'last_detected_location')
        }),
        ('Context', {
            'fields': ('reason', 'notes')
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_until')
        }),
        ('Metadata', {
            'fields': ('tags', 'metadata', 'added_by'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def threat_level_badge(self, obj):
        """Display threat level as colored badge"""
        colors = {
            'critical': '#dc3545',
            'high': '#fd7e14',
            'medium': '#ffc107',
            'low': '#28a745'
        }
        color = colors.get(obj.threat_level, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.get_threat_level_display()
        )
    threat_level_badge.short_description = 'Threat Level'
    
    def status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            'active': '#dc3545',
            'inactive': '#6c757d',
            'expired': '#6c757d',
            'resolved': '#28a745'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(ThreatFeed)
class ThreatFeedAdmin(admin.ModelAdmin):
    """Admin interface for ThreatFeed model"""
    list_display = [
        'id', 'name', 'feed_type', 'status_badge',
        'auto_import', 'last_sync_at', 'total_indicators_imported',
        'organization'
    ]
    list_filter = [
        'feed_type', 'status', 'auto_import', 'organization'
    ]
    search_fields = ['name', 'description', 'api_url']
    readonly_fields = [
        'created_at', 'updated_at', 'last_sync_at',
        'total_indicators_imported', 'last_import_count'
    ]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'name', 'feed_type', 'description')
        }),
        ('Connection', {
            'fields': ('api_url', 'api_key', 'authentication_method')
        }),
        ('Configuration', {
            'fields': ('update_frequency', 'auto_import', 'trust_score')
        }),
        ('Status', {
            'fields': ('status', 'last_sync_at', 'last_error')
        }),
        ('Statistics', {
            'fields': ('total_indicators_imported', 'last_import_count')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            'active': '#28a745',
            'inactive': '#6c757d',
            'error': '#dc3545'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(ThreatHuntingQuery)
class ThreatHuntingQueryAdmin(admin.ModelAdmin):
    """Admin interface for ThreatHuntingQuery model"""
    list_display = [
        'id', 'name', 'query_type', 'times_executed',
        'is_public', 'created_by', 'organization', 'updated_at'
    ]
    list_filter = [
        'query_type', 'is_public', 'organization', 'created_at'
    ]
    search_fields = ['name', 'description', 'query_text']
    readonly_fields = [
        'created_at', 'updated_at', 'times_executed',
        'last_executed_at', 'last_result_count'
    ]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'name', 'description')
        }),
        ('Query Details', {
            'fields': ('query_text', 'query_type')
        }),
        ('Hypothesis', {
            'fields': ('hypothesis', 'expected_outcome')
        }),
        ('Execution Tracking', {
            'fields': ('times_executed', 'last_executed_at', 'last_result_count')
        }),
        ('Results', {
            'fields': ('findings',)
        }),
        ('Sharing', {
            'fields': ('is_public', 'created_by')
        }),
        ('Metadata', {
            'fields': ('tags',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
