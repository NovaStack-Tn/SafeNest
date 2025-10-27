"""
Security models: LoginEvent, AnomalyRule, Alert
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class LoginEvent(models.Model):
    """Track all login attempts for anomaly detection."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='login_events',
        null=True,
        blank=True
    )
    username = models.CharField(max_length=150)  # Store even if user not found
    success = models.BooleanField(default=True)
    
    # Location data
    ip_address = models.GenericIPAddressField()
    country_code = models.CharField(max_length=2, blank=True)
    country_name = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    # Device data
    user_agent = models.TextField()
    device_type = models.CharField(max_length=50, blank=True)  # mobile, desktop, tablet
    browser = models.CharField(max_length=50, blank=True)
    os = models.CharField(max_length=50, blank=True)
    device_fingerprint = models.CharField(max_length=255, blank=True)
    
    # Risk scoring
    risk_score = models.FloatField(default=0.0)
    is_anomaly = models.BooleanField(default=False)
    anomaly_reasons = ArrayField(
        models.CharField(max_length=100),
        default=list,
        blank=True
    )
    
    # Metadata
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['ip_address', '-timestamp']),
            models.Index(fields=['is_anomaly', '-timestamp']),
        ]
        verbose_name = _('Login Event')
        verbose_name_plural = _('Login Events')
    
    def __str__(self):
        status = 'Success' if self.success else 'Failed'
        return f"{self.username} - {status} from {self.ip_address} at {self.timestamp}"


class AnomalyRule(models.Model):
    """Rules for detecting anomalous behavior."""
    RULE_TYPE_CHOICES = [
        ('time', 'Time-based'),
        ('geo', 'Geo-location'),
        ('device', 'Device-based'),
        ('velocity', 'Impossible Travel'),
        ('frequency', 'Login Frequency'),
        ('ml', 'Machine Learning'),
    ]
    
    organization = models.ForeignKey(
        'core.Organization',
        on_delete=models.CASCADE,
        related_name='anomaly_rules'
    )
    name = models.CharField(max_length=255)
    rule_type = models.CharField(max_length=20, choices=RULE_TYPE_CHOICES)
    description = models.TextField(blank=True)
    
    # Rule configuration
    config = models.JSONField(default=dict, help_text="Rule-specific configuration")
    threshold = models.FloatField(default=0.5)
    severity = models.CharField(
        max_length=10,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')],
        default='medium'
    )
    
    # Status
    active = models.BooleanField(default=True)
    auto_create_incident = models.BooleanField(default=False)
    
    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_rules'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['organization', '-created_at']
        verbose_name = _('Anomaly Rule')
        verbose_name_plural = _('Anomaly Rules')
    
    def __str__(self):
        return f"{self.name} ({self.organization})"


class Alert(models.Model):
    """Security alerts triggered by anomalies or rules."""
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('investigating', 'Investigating'),
        ('resolved', 'Resolved'),
        ('false_positive', 'False Positive'),
        ('ignored', 'Ignored'),
    ]
    
    organization = models.ForeignKey(
        'core.Organization',
        on_delete=models.CASCADE,
        related_name='alerts'
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    # Related objects (generic relation would be better but keeping simple)
    related_model = models.CharField(max_length=100, blank=True)
    related_id = models.CharField(max_length=255, blank=True)
    
    # Rule that triggered this alert
    triggered_by_rule = models.ForeignKey(
        AnomalyRule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alerts'
    )
    
    # Assignment
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_alerts'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_alerts'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Additional data
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['organization', 'status', '-created_at']),
            models.Index(fields=['severity', '-created_at']),
        ]
        verbose_name = _('Alert')
        verbose_name_plural = _('Alerts')
    
    def __str__(self):
        return f"[{self.severity.upper()}] {self.title}"
