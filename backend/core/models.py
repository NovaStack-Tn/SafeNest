"""
Core models for SafeNest: Organizations, Users, Roles, Permissions, Teams
"""
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.translation import gettext_lazy as _


class Organization(models.Model):
    """Multi-tenant organization model."""
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    settings = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Privacy & Compliance Settings
    face_retention_days = models.IntegerField(default=90)
    consent_required = models.BooleanField(default=True)
    data_residency = models.CharField(max_length=50, default='us-east-1')
    
    class Meta:
        ordering = ['name']
        verbose_name = _('Organization')
        verbose_name_plural = _('Organizations')
    
    def __str__(self):
        return self.name


class Role(models.Model):
    """Custom role model for RBAC."""
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('sec_officer', 'Security Officer'),
        ('employee', 'Employee'),
        ('viewer', 'Viewer'),
    ]
    
    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(Permission, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.get_name_display()


class User(AbstractUser):
    """Extended user model with organization and role."""
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='users',
        null=True,
        blank=True
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    department = models.CharField(max_length=100, blank=True)
    employee_id = models.CharField(max_length=50, blank=True, unique=True, null=True)
    
    # Security settings
    two_factor_enabled = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_login_location = models.CharField(max_length=255, blank=True)
    failed_login_attempts = models.IntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_joined']
        verbose_name = _('User')
        verbose_name_plural = _('Users')
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.organization})"
    
    def has_role(self, role_name):
        """Check if user has specific role."""
        return self.role and self.role.name == role_name
    
    def is_admin(self):
        return self.has_role('admin')
    
    def is_security_officer(self):
        return self.has_role('sec_officer')


class Team(models.Model):
    """Team model for grouping users."""
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='teams'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    members = models.ManyToManyField(User, related_name='teams', blank=True)
    lead = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='led_teams'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['organization', 'name']
        unique_together = ['organization', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.organization})"


class AuditLog(models.Model):
    """Audit trail for all admin actions."""
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='audit_logs',
        null=True
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=255)
    changes = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['organization', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.action} {self.model_name} at {self.timestamp}"
