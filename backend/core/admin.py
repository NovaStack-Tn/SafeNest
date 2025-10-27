"""
Admin configuration for core models.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Organization, Role, User, Team, AuditLog


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    filter_horizontal = ['permissions']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'organization', 'role', 'is_staff']
    list_filter = ['is_staff', 'is_active', 'organization', 'role']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'employee_id']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Organization & Role', {'fields': ('organization', 'role', 'department', 'employee_id')}),
        ('Contact', {'fields': ('phone', 'avatar')}),
        ('Security', {'fields': ('two_factor_enabled', 'last_login_ip', 'last_login_location')}),
        ('Metadata', {'fields': ('metadata',)}),
    )


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'lead', 'created_at']
    list_filter = ['organization', 'created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['members']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model_name', 'object_id', 'timestamp']
    list_filter = ['action', 'model_name', 'timestamp']
    search_fields = ['user__username', 'model_name', 'object_id']
    readonly_fields = ['user', 'organization', 'action', 'model_name', 'object_id', 'changes', 'ip_address', 'user_agent', 'timestamp']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
