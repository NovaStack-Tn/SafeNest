"""
Admin configuration for incident models.
"""
from django.contrib import admin
from .models import Incident, IncidentEvent, Evidence, IncidentCategory, IncidentResolution


class IncidentEventInline(admin.TabularInline):
    model = IncidentEvent
    extra = 0
    readonly_fields = ['timestamp']


class EvidenceInline(admin.TabularInline):
    model = Evidence
    extra = 0
    readonly_fields = ['uploaded_at', 'file_hash', 'file_size']


@admin.register(IncidentCategory)
class IncidentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'severity_default', 'is_active', 'created_at']
    list_filter = ['organization', 'is_active', 'severity_default']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ['title', 'organization', 'category', 'incident_type', 'severity', 'status', 'assignee', 'ai_generated', 'opened_at']
    list_filter = ['organization', 'category', 'incident_type', 'severity', 'status', 'ai_generated', 'opened_at']
    search_fields = ['title', 'description']
    readonly_fields = ['opened_at', 'updated_at', 'ai_generated', 'ai_confidence', 'extracted_entities']
    date_hierarchy = 'opened_at'
    inlines = [IncidentEventInline, EvidenceInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'title', 'description', 'category', 'incident_type')
        }),
        ('Classification', {
            'fields': ('severity', 'status', 'assignee')
        }),
        ('AI Analysis', {
            'fields': ('ai_generated', 'ai_confidence', 'extracted_entities'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('tags', 'metadata', 'opened_at', 'closed_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(IncidentEvent)
class IncidentEventAdmin(admin.ModelAdmin):
    list_display = ['incident', 'action', 'actor', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['description']
    readonly_fields = ['timestamp']


@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'incident', 'kind', 'uploaded_by', 'uploaded_at']
    list_filter = ['kind', 'uploaded_at']
    search_fields = ['file_name', 'description']
    readonly_fields = ['uploaded_at', 'file_hash', 'file_size']


@admin.register(IncidentResolution)
class IncidentResolutionAdmin(admin.ModelAdmin):
    list_display = ['incident', 'resolution_type', 'resolved_by', 'resolved_at']
    list_filter = ['resolution_type', 'resolved_at']
    search_fields = ['summary', 'actions_taken', 'root_cause']
    readonly_fields = ['resolved_at']
    filter_horizontal = ['related_incidents']
