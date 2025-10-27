"""
Incident management models: Incident, IncidentEvent, Evidence
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


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
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
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
