"""
Admin configuration for incident models.
"""
from django.contrib import admin
from .models import Incident, IncidentEvent, Evidence


class IncidentEventInline(admin.TabularInline):
    model = IncidentEvent
    extra = 0
    readonly_fields = ['timestamp']


class EvidenceInline(admin.TabularInline):
    model = Evidence
    extra = 0
    readonly_fields = ['uploaded_at', 'file_hash', 'file_size']


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ['title', 'organization', 'incident_type', 'severity', 'status', 'assignee', 'opened_at']
    list_filter = ['organization', 'incident_type', 'severity', 'status', 'opened_at']
    search_fields = ['title', 'description']
    readonly_fields = ['opened_at', 'updated_at']
    date_hierarchy = 'opened_at'
    inlines = [IncidentEventInline, EvidenceInline]


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
