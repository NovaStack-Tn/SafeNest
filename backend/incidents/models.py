"""
Incident management models: Incident, IncidentEvent, Evidence
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class IncidentCategory(models.Model):
    """Configurable incident categories (theft, violence, breach, etc.)."""
    organization = models.ForeignKey(
        'core.Organization',
        on_delete=models.CASCADE,
        related_name='incident_categories'
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#6b7280')  # Hex color
    icon = models.CharField(max_length=50, blank=True)  # Icon name
    severity_default = models.CharField(
        max_length=10,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        default='medium'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        unique_together = ['organization', 'name']
        verbose_name = _('Incident Category')
        verbose_name_plural = _('Incident Categories')
    
    def __str__(self):
        return self.name


class Incident(models.Model):
    """Security incident with workflow."""
    TYPE_CHOICES = [
        ('unauthorized_access', 'Unauthorized Access'),
        ('data_breach', 'Data Breach'),
        ('anomalous_login', 'Anomalous Login'),
        ('policy_violation', 'Policy Violation'),
        ('suspicious_activity', 'Suspicious Activity'),
        ('other', 'Other'),
    ]
    
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('investigating', 'Investigating'),
        ('contained', 'Contained'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    organization = models.ForeignKey(
        'core.Organization',
        on_delete=models.CASCADE,
        related_name='incidents'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    incident_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    category = models.ForeignKey(
        IncidentCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incidents'
    )
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    # AI-generated fields
    ai_generated = models.BooleanField(default=False)
    ai_confidence = models.FloatField(null=True, blank=True)  # Confidence score for AI classification
    extracted_entities = models.JSONField(default=dict, blank=True)  # NLP extracted entities
    
    # Assignment
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_incidents'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_incidents'
    )
    
    # Timestamps
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional data
    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-opened_at']
        indexes = [
            models.Index(fields=['-opened_at']),
            models.Index(fields=['organization', 'status', '-opened_at']),
            models.Index(fields=['severity', '-opened_at']),
        ]
        verbose_name = _('Incident')
        verbose_name_plural = _('Incidents')
    
    def __str__(self):
        return f"[{self.severity.upper()}] {self.title}"


class IncidentEvent(models.Model):
    """Timeline events for incident tracking."""
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('assigned', 'Assigned'),
        ('status_changed', 'Status Changed'),
        ('comment_added', 'Comment Added'),
        ('evidence_added', 'Evidence Added'),
        ('closed', 'Closed'),
    ]
    
    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name='events'
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField(blank=True)
    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['incident', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.incident.title} - {self.action} at {self.timestamp}"


class Evidence(models.Model):
    """Evidence files attached to incidents."""
    KIND_CHOICES = [
        ('frame', 'Video Frame'),
        ('image', 'Image'),
        ('log', 'Log File'),
        ('document', 'Document'),
        ('other', 'Other'),
    ]
    
    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name='evidence'
    )
    file = models.FileField(upload_to='evidence/%Y/%m/%d/')
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    file_hash = models.CharField(max_length=64)  # SHA-256
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default='other')
    description = models.TextField(blank=True)
    
    # Metadata
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = _('Evidence')
        verbose_name_plural = _('Evidence')
    
    def __str__(self):
        return f"{self.file_name} - {self.incident.title}"


class IncidentResolution(models.Model):
    """Resolution details for closed incidents."""
    RESOLUTION_TYPE_CHOICES = [
        ('resolved', 'Resolved'),
        ('false_positive', 'False Positive'),
        ('duplicate', 'Duplicate'),
        ('mitigated', 'Mitigated'),
        ('escalated', 'Escalated'),
        ('cannot_fix', 'Cannot Fix'),
    ]
    
    incident = models.OneToOneField(
        Incident,
        on_delete=models.CASCADE,
        related_name='resolution'
    )
    resolution_type = models.CharField(max_length=20, choices=RESOLUTION_TYPE_CHOICES)
    summary = models.TextField()  # What happened
    actions_taken = models.TextField()  # What was done
    root_cause = models.TextField(blank=True)  # Why it happened
    preventive_measures = models.TextField(blank=True)  # Future prevention
    
    # References
    related_incidents = models.ManyToManyField(
        Incident,
        blank=True,
        related_name='related_resolutions'
    )
    
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='resolved_incidents'
    )
    resolved_at = models.DateTimeField(auto_now_add=True)
    
    # Time tracking
    time_to_detect = models.DurationField(null=True, blank=True)  # Time from occurrence to detection
    time_to_resolve = models.DurationField(null=True, blank=True)  # Time from detection to resolution
    
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-resolved_at']
        verbose_name = _('Incident Resolution')
        verbose_name_plural = _('Incident Resolutions')
    
    def __str__(self):
        return f"Resolution for {self.incident.title}"
