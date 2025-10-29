from django.contrib import admin
from .models import Visitor, VisitorPass, Asset, AssetAssignment, MovementLog


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    """Admin configuration for Visitor model"""
    
    list_display = ['full_name', 'company', 'visitor_type', 'status', 'expected_arrival', 'host', 'is_checked_in']
    list_filter = ['status', 'visitor_type', 'expected_arrival', 'ai_extracted']
    search_fields = ['first_name', 'last_name', 'email', 'company', 'phone', 'purpose']
    readonly_fields = ['created_at', 'updated_at', 'is_checked_in', 'is_overdue']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'company', 'visitor_type')
        }),
        ('Identification', {
            'fields': ('id_type', 'id_number', 'photo')
        }),
        ('Visit Details', {
            'fields': ('purpose', 'host', 'department', 'status')
        }),
        ('Schedule', {
            'fields': ('expected_arrival', 'expected_departure', 'actual_arrival', 'actual_departure')
        }),
        ('AI Enhancement', {
            'fields': ('ai_extracted', 'ai_confidence', 'ai_suggested_access_level', 
                      'ai_predicted_duration', 'extracted_data'),
            'classes': ('collapse',)
        }),
        ('Additional Info', {
            'fields': ('notes', 'emergency_contact', 'emergency_phone', 'vehicle_plate')
        }),
        ('Metadata', {
            'fields': ('organization', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    date_hierarchy = 'expected_arrival'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(organization=request.user.organization)


@admin.register(VisitorPass)
class VisitorPassAdmin(admin.ModelAdmin):
    """Admin configuration for VisitorPass model"""
    
    list_display = ['visitor', 'pass_type', 'pass_code', 'status', 'valid_from', 'valid_until', 'times_used']
    list_filter = ['status', 'pass_type', 'valid_from', 'valid_until']
    search_fields = ['pass_code', 'visitor__first_name', 'visitor__last_name']
    readonly_fields = ['issued_at', 'times_used', 'last_used', 'is_valid']
    
    fieldsets = (
        ('Pass Information', {
            'fields': ('visitor', 'pass_type', 'pass_code', 'status')
        }),
        ('Access Control', {
            'fields': ('access_level', 'allowed_areas', 'access_points')
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_until', 'is_valid')
        }),
        ('Usage', {
            'fields': ('times_used', 'last_used', 'max_uses')
        }),
        ('Metadata', {
            'fields': ('issued_by', 'issued_at', 'revoked_by', 'revoked_at', 'revocation_reason'),
            'classes': ('collapse',)
        })
    )


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    """Admin configuration for Asset model"""
    
    list_display = ['asset_tag', 'name', 'asset_type', 'status', 'condition', 'current_assignee', 'location']
    list_filter = ['status', 'asset_type', 'condition', 'purchase_date']
    search_fields = ['asset_tag', 'serial_number', 'name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'is_available', 'warranty_active']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'asset_type', 'asset_tag', 'serial_number')
        }),
        ('Details', {
            'fields': ('description', 'manufacturer', 'model', 'specifications')
        }),
        ('Financial', {
            'fields': ('purchase_date', 'purchase_price', 'warranty_expiry', 'warranty_active')
        }),
        ('Status & Location', {
            'fields': ('status', 'condition', 'location')
        }),
        ('Assignment', {
            'fields': ('current_assignee', 'assigned_at')
        }),
        ('Additional', {
            'fields': ('image', 'notes')
        }),
        ('Metadata', {
            'fields': ('organization', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    date_hierarchy = 'purchase_date'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(organization=request.user.organization)


@admin.register(AssetAssignment)
class AssetAssignmentAdmin(admin.ModelAdmin):
    """Admin configuration for AssetAssignment model"""
    
    list_display = ['asset', 'assignee', 'assigned_by', 'assigned_at', 'expected_return', 'status', 'is_overdue']
    list_filter = ['status', 'assigned_at', 'expected_return']
    search_fields = ['asset__asset_tag', 'asset__name', 'assignee__username']
    readonly_fields = ['assigned_at', 'is_overdue']
    
    fieldsets = (
        ('Assignment', {
            'fields': ('asset', 'assignee', 'assigned_by', 'assigned_at', 'status')
        }),
        ('Timeline', {
            'fields': ('expected_return', 'actual_return', 'is_overdue')
        }),
        ('Condition', {
            'fields': ('condition_on_assignment', 'condition_on_return')
        }),
        ('Notes', {
            'fields': ('assignment_notes', 'return_notes')
        })
    )
    
    date_hierarchy = 'assigned_at'


@admin.register(MovementLog)
class MovementLogAdmin(admin.ModelAdmin):
    """Admin configuration for MovementLog model"""
    
    list_display = ['timestamp', 'movement_type', 'asset', 'visitor', 'user', 'from_location', 'to_location']
    list_filter = ['movement_type', 'timestamp']
    search_fields = ['asset__asset_tag', 'visitor__first_name', 'visitor__last_name', 'user__username']
    readonly_fields = ['timestamp']
    
    fieldsets = (
        ('Movement Info', {
            'fields': ('movement_type', 'timestamp')
        }),
        ('Related Objects', {
            'fields': ('asset', 'visitor', 'user')
        }),
        ('Location', {
            'fields': ('from_location', 'to_location', 'access_point')
        }),
        ('Verification', {
            'fields': ('verified_by', 'verification_method')
        }),
        ('Additional', {
            'fields': ('notes', 'metadata', 'organization')
        })
    )
    
    date_hierarchy = 'timestamp'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(organization=request.user.organization)
