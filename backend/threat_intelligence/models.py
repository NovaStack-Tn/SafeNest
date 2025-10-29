from django.db import models
from django.contrib.auth import get_user_model
from core.models import Organization

User = get_user_model()


class Threat(models.Model):
    """Potential security risks and threats"""
    THREAT_TYPES = [
        ('physical', 'Physical Security'),
        ('cyber', 'Cyber Security'),
        ('insider', 'Insider Threat'),
        ('terrorism', 'Terrorism'),
        ('fraud', 'Fraud'),
        ('data_breach', 'Data Breach'),
        ('social_engineering', 'Social Engineering'),
        ('other', 'Other'),
    ]
    
    SEVERITY_LEVELS = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
        ('info', 'Informational'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('investigating', 'Investigating'),
        ('confirmed', 'Confirmed'),
        ('mitigated', 'Mitigated'),
        ('resolved', 'Resolved'),
        ('false_positive', 'False Positive'),
    ]
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='threats')
    title = models.CharField(max_length=255)
    description = models.TextField()
    threat_type = models.CharField(max_length=50, choices=THREAT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    source = models.CharField(max_length=255, blank=True, help_text='Where this threat was identified')
    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # AI fields
    ai_analyzed = models.BooleanField(default=False)
    ai_confidence = models.FloatField(null=True, blank=True)
    ai_suggested_severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, null=True, blank=True)
    ai_analysis = models.JSONField(default=dict, blank=True)
    
    # Assignment and tracking
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_threats')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_threats')
    first_detected = models.DateTimeField(null=True, blank=True)
    last_activity = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['threat_type', 'severity']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.severity})"


class Alert(models.Model):
    """System-generated security alerts and notifications"""
    ALERT_TYPES = [
        ('intrusion', 'Intrusion Detection'),
        ('anomaly', 'Anomaly Detected'),
        ('unauthorized_access', 'Unauthorized Access'),
        ('suspicious_activity', 'Suspicious Activity'),
        ('policy_violation', 'Policy Violation'),
        ('system', 'System Alert'),
        ('face_recognition', 'Face Recognition'),
        ('other', 'Other'),
    ]
    
    SEVERITY_LEVELS = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
        ('info', 'Informational'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('acknowledged', 'Acknowledged'),
        ('investigating', 'Investigating'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='threat_alerts')
    title = models.CharField(max_length=255)
    description = models.TextField()
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    source = models.CharField(max_length=255, blank=True, help_text='System component that generated alert')
    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Linking
    threat = models.ForeignKey(Threat, on_delete=models.SET_NULL, null=True, blank=True, related_name='alerts')
    related_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='related_alerts')
    
    # Actions
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='acknowledged_alerts')
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_alerts')
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['alert_type', 'severity']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.severity})"


class RiskAssessment(models.Model):
    """Risk analysis and impact assessments for threats"""
    RISK_LEVELS = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
        ('negligible', 'Negligible'),
    ]
    
    LIKELIHOOD_LEVELS = [
        ('certain', 'Certain'),
        ('likely', 'Likely'),
        ('possible', 'Possible'),
        ('unlikely', 'Unlikely'),
        ('rare', 'Rare'),
    ]
    
    IMPACT_LEVELS = [
        ('catastrophic', 'Catastrophic'),
        ('severe', 'Severe'),
        ('moderate', 'Moderate'),
        ('minor', 'Minor'),
        ('insignificant', 'Insignificant'),
    ]
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='risk_assessments')
    threat = models.ForeignKey(Threat, on_delete=models.CASCADE, related_name='risk_assessments')
    
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS)
    likelihood = models.CharField(max_length=20, choices=LIKELIHOOD_LEVELS)
    impact = models.CharField(max_length=20, choices=IMPACT_LEVELS)
    
    # Analysis
    vulnerability_analysis = models.TextField(help_text='What makes us vulnerable?')
    impact_analysis = models.TextField(help_text='What could happen if exploited?')
    mitigation_strategy = models.TextField(help_text='How to reduce or eliminate the risk')
    residual_risk = models.TextField(blank=True, help_text='Risk remaining after mitigation')
    
    # Resources
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Cost to mitigate')
    required_resources = models.TextField(blank=True)
    timeline = models.CharField(max_length=255, blank=True, help_text='Timeline for mitigation')
    
    # AI fields
    ai_generated = models.BooleanField(default=False)
    ai_confidence = models.FloatField(null=True, blank=True)
    ai_recommendations = models.JSONField(default=dict, blank=True)
    
    # Tracking
    assessed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='risk_assessments')
    review_date = models.DateField(null=True, blank=True)
    next_review_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'risk_level']),
            models.Index(fields=['threat']),
        ]
    
    def __str__(self):
        return f"Risk Assessment: {self.threat.title} - {self.risk_level}"


class ThreatIndicator(models.Model):
    """Indicators of Compromise (IOCs) and suspicious patterns"""
    INDICATOR_TYPES = [
        ('ip_address', 'IP Address'),
        ('domain', 'Domain'),
        ('url', 'URL'),
        ('file_hash', 'File Hash'),
        ('email', 'Email Address'),
        ('username', 'Username'),
        ('phone', 'Phone Number'),
        ('license_plate', 'License Plate'),
        ('device_id', 'Device ID'),
        ('pattern', 'Behavior Pattern'),
        ('other', 'Other'),
    ]
    
    CONFIDENCE_LEVELS = [
        ('high', 'High Confidence'),
        ('medium', 'Medium Confidence'),
        ('low', 'Low Confidence'),
    ]
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='threat_indicators')
    threat = models.ForeignKey(Threat, on_delete=models.CASCADE, null=True, blank=True, related_name='indicators')
    
    indicator_type = models.CharField(max_length=50, choices=INDICATOR_TYPES)
    value = models.CharField(max_length=500, help_text='The actual indicator value')
    description = models.TextField(blank=True)
    confidence = models.CharField(max_length=20, choices=CONFIDENCE_LEVELS, default='medium')
    
    # Context
    source = models.CharField(max_length=255, blank=True, help_text='Where this IOC was found')
    first_seen = models.DateTimeField()
    last_seen = models.DateTimeField()
    occurrence_count = models.IntegerField(default=1)
    
    # Classification
    is_active = models.BooleanField(default=True)
    is_false_positive = models.BooleanField(default=False)
    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Actions
    action_taken = models.TextField(blank=True, help_text='Actions taken for this indicator')
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='added_indicators')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-last_seen']
        indexes = [
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['indicator_type', 'value']),
            models.Index(fields=['last_seen']),
        ]
        unique_together = [['organization', 'indicator_type', 'value']]
    
    def __str__(self):
        return f"{self.indicator_type}: {self.value}"


class Watchlist(models.Model):
    """Persons, vehicles, or entities of interest for monitoring"""
    WATCHLIST_TYPES = [
        ('person', 'Person of Interest'),
        ('vehicle', 'Vehicle of Interest'),
        ('organization', 'Organization of Interest'),
        ('location', 'Location of Interest'),
        ('device', 'Device of Interest'),
    ]
    
    RISK_LEVELS = [
        ('critical', 'Critical Risk'),
        ('high', 'High Risk'),
        ('medium', 'Medium Risk'),
        ('low', 'Low Risk'),
        ('monitor', 'Monitor Only'),
    ]
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='watchlists')
    threat = models.ForeignKey(Threat, on_delete=models.SET_NULL, null=True, blank=True, related_name='watchlist_entries')
    
    watchlist_type = models.CharField(max_length=50, choices=WATCHLIST_TYPES)
    subject_name = models.CharField(max_length=255, help_text='Name or identifier')
    subject_id = models.CharField(max_length=255, blank=True, help_text='ID number, plate, etc.')
    description = models.TextField(blank=True)
    
    # Classification
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS)
    reason = models.TextField(help_text='Why this subject is on watchlist')
    
    # Attributes (flexible JSON for different types)
    attributes = models.JSONField(default=dict, blank=True, help_text='Type-specific attributes')
    # For person: photo_url, known_associates, aliases
    # For vehicle: make, model, color, last_seen_location
    # etc.
    
    # Actions
    alert_on_detection = models.BooleanField(default=True)
    auto_notify = models.JSONField(default=list, blank=True, help_text='User IDs to notify')
    action_instructions = models.TextField(blank=True, help_text='What to do if detected')
    
    # Tracking
    is_active = models.BooleanField(default=True)
    detection_count = models.IntegerField(default=0)
    last_detected = models.DateTimeField(null=True, blank=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='watchlist_entries')
    notes = models.TextField(blank=True)
    expiry_date = models.DateField(null=True, blank=True, help_text='When to remove from watchlist')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['watchlist_type', 'risk_level']),
            models.Index(fields=['subject_name']),
        ]
    
    def __str__(self):
        return f"{self.watchlist_type}: {self.subject_name} ({self.risk_level})"
