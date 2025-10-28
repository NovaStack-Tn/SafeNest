"""
Access Control Management Models
Handles physical/digital access points, permissions, logs, credentials, and schedules
"""
from django.db import models
from django.contrib.postgres.fields import JSONField
from core.models import User, Organization


class AccessPoint(models.Model):
    """
    Physical or digital access point (door, gate, turnstile, zone, system)
    """
    POINT_TYPES = [
        ('door', 'Door'),
        ('gate', 'Gate'),
        ('turnstile', 'Turnstile'),
        ('elevator', 'Elevator'),
        ('zone', 'Security Zone'),
        ('system', 'Digital System'),
        ('parking', 'Parking Barrier'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Under Maintenance'),
        ('error', 'Error'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='access_points')
    name = models.CharField(max_length=200)
    point_type = models.CharField(max_length=20, choices=POINT_TYPES)
    location = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    
    # Hardware details
    hardware_id = models.CharField(max_length=100, unique=True, help_text="Physical device ID")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Status & monitoring
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_secure = models.BooleanField(default=True, help_text="Is the point physically secured?")
    requires_escort = models.BooleanField(default=False)
    
    # Configuration
    allow_tailgating_detection = models.BooleanField(default=True)
    max_access_attempts = models.IntegerField(default=3)
    lockdown_enabled = models.BooleanField(default=False)
    
    # Geolocation
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Metadata
    meta = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['location', 'name']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['hardware_id']),
        ]

    def __str__(self):
        return f"{self.name} ({self.location})"


class AccessSchedule(models.Model):
    """
    Time-based access rules (e.g., office hours, weekends, holidays)
    """
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='access_schedules')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Time rules
    days_of_week = models.JSONField(
        default=list,
        help_text="List of days: ['monday', 'tuesday', ...] or [] for all days"
    )
    start_time = models.TimeField(help_text="Access allowed from this time")
    end_time = models.TimeField(help_text="Access allowed until this time")
    
    # Date range (optional)
    valid_from = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    
    # Special dates
    exclude_holidays = models.BooleanField(default=False)
    holiday_calendar = models.JSONField(default=list, blank=True, help_text="List of holiday dates")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class AccessPermission(models.Model):
    """
    Grants user access to specific access points with optional schedule constraints
    """
    PERMISSION_TYPES = [
        ('permanent', 'Permanent Access'),
        ('temporary', 'Temporary Access'),
        ('scheduled', 'Scheduled Access'),
        ('visitor', 'Visitor Access'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='access_permissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access_permissions')
    access_point = models.ForeignKey(AccessPoint, on_delete=models.CASCADE, related_name='permissions')
    
    permission_type = models.CharField(max_length=20, choices=PERMISSION_TYPES)
    schedule = models.ForeignKey(
        AccessSchedule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='permissions'
    )
    
    # Validity period
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField(null=True, blank=True)
    
    # Additional constraints
    requires_pin = models.BooleanField(default=False)
    requires_biometric = models.BooleanField(default=False)
    requires_approval = models.BooleanField(default=False)
    max_daily_entries = models.IntegerField(null=True, blank=True, help_text="Limit entries per day")
    
    # Status
    is_active = models.BooleanField(default=True)
    is_revoked = models.BooleanField(default=False)
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='revoked_permissions'
    )
    revocation_reason = models.TextField(blank=True)
    
    # Audit
    granted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='granted_permissions'
    )
    granted_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['user', 'access_point']
        ordering = ['-granted_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['access_point', 'is_active']),
        ]

    def __str__(self):
        return f"{self.user.username} → {self.access_point.name}"


class AccessCredential(models.Model):
    """
    Physical or digital credentials (badge, RFID, biometric, PIN)
    """
    CREDENTIAL_TYPES = [
        ('badge', 'Badge/Card'),
        ('rfid', 'RFID Tag'),
        ('biometric', 'Biometric'),
        ('pin', 'PIN Code'),
        ('mobile', 'Mobile App'),
        ('qr', 'QR Code'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('lost', 'Lost/Stolen'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='credentials')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access_credentials')
    
    credential_type = models.CharField(max_length=20, choices=CREDENTIAL_TYPES)
    credential_id = models.CharField(max_length=200, unique=True, help_text="Card number, RFID ID, etc.")
    
    # For biometric
    biometric_template = models.BinaryField(null=True, blank=True, help_text="Encrypted biometric data")
    
    # For PIN
    pin_code = models.CharField(max_length=100, blank=True, help_text="Hashed PIN")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    issued_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    
    # Security
    failed_attempts = models.IntegerField(default=0)
    is_locked = models.BooleanField(default=False)
    locked_until = models.DateTimeField(null=True, blank=True)
    
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-issued_at']
        indexes = [
            models.Index(fields=['credential_id']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.credential_type} ({self.credential_id})"


class AccessLog(models.Model):
    """
    Records every access attempt (granted or denied)
    """
    EVENT_TYPES = [
        ('entry', 'Entry'),
        ('exit', 'Exit'),
        ('denied', 'Access Denied'),
        ('forced', 'Forced Entry'),
        ('held_open', 'Door Held Open'),
    ]
    
    DENIAL_REASONS = [
        ('no_permission', 'No Permission'),
        ('invalid_credential', 'Invalid Credential'),
        ('expired', 'Expired'),
        ('outside_schedule', 'Outside Allowed Schedule'),
        ('revoked', 'Revoked'),
        ('lockdown', 'Lockdown Active'),
        ('max_attempts', 'Max Attempts Exceeded'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='access_logs')
    access_point = models.ForeignKey(AccessPoint, on_delete=models.CASCADE, related_name='logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='access_logs')
    credential = models.ForeignKey(
        AccessCredential,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs'
    )
    
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    is_granted = models.BooleanField(default=False)
    denial_reason = models.CharField(max_length=50, choices=DENIAL_REASONS, blank=True)
    
    # Timestamp
    timestamp = models.DateTimeField(db_index=True)
    
    # Detection metadata
    is_tailgating = models.BooleanField(default=False, help_text="Multiple persons detected")
    is_anomaly = models.BooleanField(default=False, help_text="Flagged by AI")
    anomaly_score = models.FloatField(null=True, blank=True, help_text="AI anomaly score 0-1")
    
    # Additional context
    direction = models.CharField(max_length=10, choices=[('in', 'In'), ('out', 'Out')], blank=True)
    companion_count = models.IntegerField(default=0, help_text="Number of people accompanying")
    
    # Geolocation (if mobile access)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Device info
    device_info = models.JSONField(default=dict, blank=True)
    
    # Associated media
    photo_url = models.URLField(blank=True, help_text="Photo captured at access point")
    video_clip_url = models.URLField(blank=True)
    
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['organization', 'timestamp']),
            models.Index(fields=['access_point', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['is_anomaly', 'timestamp']),
        ]

    def __str__(self):
        status = "✓ Granted" if self.is_granted else "✗ Denied"
        user_str = self.user.username if self.user else "Unknown"
        return f"{status} - {user_str} @ {self.access_point.name} ({self.timestamp})"


class AccessAnomaly(models.Model):
    """
    AI-detected anomalies in access patterns
    """
    ANOMALY_TYPES = [
        ('unusual_time', 'Unusual Time Access'),
        ('unusual_location', 'Unusual Location'),
        ('rapid_sequence', 'Rapid Sequential Access'),
        ('simultaneous', 'Simultaneous Access Different Locations'),
        ('tailgating', 'Tailgating Detected'),
        ('pattern_break', 'Pattern Break'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='access_anomalies')
    access_log = models.ForeignKey(AccessLog, on_delete=models.CASCADE, related_name='anomalies')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access_anomalies')
    
    anomaly_type = models.CharField(max_length=30, choices=ANOMALY_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    confidence_score = models.FloatField(help_text="AI confidence 0-1")
    
    description = models.TextField()
    ai_model_used = models.CharField(max_length=100, default='isolation_forest')
    
    # Context
    baseline_pattern = models.JSONField(default=dict, help_text="User's normal pattern")
    detected_pattern = models.JSONField(default=dict, help_text="Anomalous pattern")
    
    # Status
    is_reviewed = models.BooleanField(default=False)
    is_false_positive = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_anomalies'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    
    detected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Access anomalies'
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['severity', 'is_reviewed']),
            models.Index(fields=['user', 'detected_at']),
        ]

    def __str__(self):
        return f"{self.anomaly_type} - {self.user.username} ({self.severity})"
