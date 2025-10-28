"""
Threat Intelligence Management Models
Handles threats, alerts, risk assessments, indicators, and watchlists
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from core.models import Organization
from access_control.models import AccessPoint

User = get_user_model()


class Threat(models.Model):
    """
    Potential security risks and threats detected or reported
    """
    THREAT_TYPES = [
        ('malware', 'Malware'),
        ('phishing', 'Phishing'),
        ('unauthorized_access', 'Unauthorized Access'),
        ('data_breach', 'Data Breach'),
        ('insider_threat', 'Insider Threat'),
        ('physical_security', 'Physical Security'),
        ('social_engineering', 'Social Engineering'),
        ('ddos', 'DDoS Attack'),
        ('ransomware', 'Ransomware'),
        ('apt', 'Advanced Persistent Threat'),
        ('zero_day', 'Zero Day Exploit'),
        ('other', 'Other'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('investigating', 'Investigating'),
        ('confirmed', 'Confirmed'),
        ('mitigated', 'Mitigated'),
        ('resolved', 'Resolved'),
        ('false_positive', 'False Positive'),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='threats'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    threat_type = models.CharField(max_length=50, choices=THREAT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    
    # Risk scoring
    risk_score = models.FloatField(
        default=0.0,
        help_text="AI-calculated risk score (0-100)"
    )
    confidence_score = models.FloatField(
        default=0.0,
        help_text="Confidence in threat detection (0-1)"
    )
    
    # Source
    source = models.CharField(
        max_length=100,
        help_text="Detection source (AI, manual, external feed, etc.)"
    )
    external_ref = models.CharField(
        max_length=255,
        blank=True,
        help_text="External reference ID (CVE, etc.)"
    )
    
    # Assignment
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_threats'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_threats'
    )
    
    # Relationships
    related_users = models.ManyToManyField(
        User,
        blank=True,
        related_name='related_threats'
    )
    related_access_points = models.ManyToManyField(
        AccessPoint,
        blank=True,
        related_name='threats'
    )
    
    # Geolocation
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    location_name = models.CharField(max_length=255, blank=True)
    
    # Metadata
    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    attack_vector = models.JSONField(default=dict, blank=True)
    impact_analysis = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    first_detected_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-first_detected_at']
        indexes = [
            models.Index(fields=['organization', 'status', '-first_detected_at']),
            models.Index(fields=['severity', '-first_detected_at']),
            models.Index(fields=['threat_type', '-first_detected_at']),
            models.Index(fields=['-risk_score']),
        ]
        verbose_name = _('Threat')
        verbose_name_plural = _('Threats')
    
    def __str__(self):
        return f"[{self.severity.upper()}] {self.title}"


class Alert(models.Model):
    """
    System-generated notifications for security events
    """
    ALERT_TYPES = [
        ('anomaly_detected', 'Anomaly Detected'),
        ('threshold_exceeded', 'Threshold Exceeded'),
        ('pattern_match', 'Pattern Match'),
        ('failed_login', 'Failed Login'),
        ('unauthorized_access', 'Unauthorized Access'),
        ('suspicious_activity', 'Suspicious Activity'),
        ('policy_violation', 'Policy Violation'),
        ('system_health', 'System Health'),
        ('threat_detected', 'Threat Detected'),
    ]
    
    SEVERITY_LEVELS = [
        ('info', 'Info'),
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('acknowledged', 'Acknowledged'),
        ('investigating', 'Investigating'),
        ('resolved', 'Resolved'),
        ('false_positive', 'False Positive'),
        ('suppressed', 'Suppressed'),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='alerts'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    
    # Relationships
    threat = models.ForeignKey(
        Threat,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='alerts'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alerts'
    )
    access_point = models.ForeignKey(
        AccessPoint,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alerts'
    )
    
    # Detection details
    detection_method = models.CharField(max_length=100)
    confidence_score = models.FloatField(default=0.0)
    
    # Assignment and handling
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_alerts'
    )
    acknowledged_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_alerts'
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    # Aggregation tracking
    is_aggregated = models.BooleanField(default=False)
    parent_alert = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='child_alerts'
    )
    aggregation_count = models.IntegerField(default=1)
    
    # Metadata
    source_data = models.JSONField(default=dict, blank=True)
    context = models.JSONField(default=dict, blank=True)
    tags = models.JSONField(default=list, blank=True)
    
    # Timestamps
    triggered_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-triggered_at']
        indexes = [
            models.Index(fields=['organization', 'status', '-triggered_at']),
            models.Index(fields=['severity', 'status']),
            models.Index(fields=['alert_type', '-triggered_at']),
            models.Index(fields=['user', '-triggered_at']),
        ]
        verbose_name = _('Alert')
        verbose_name_plural = _('Alerts')
    
    def __str__(self):
        return f"[{self.severity.upper()}] {self.title}"


class RiskAssessment(models.Model):
    """
    Threat level and impact analysis for users, locations, or events
    """
    ASSESSMENT_TYPES = [
        ('user', 'User Risk'),
        ('location', 'Location Risk'),
        ('access_point', 'Access Point Risk'),
        ('event', 'Event Risk'),
        ('asset', 'Asset Risk'),
        ('network', 'Network Risk'),
    ]
    
    RISK_LEVELS = [
        ('minimal', 'Minimal'),
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
        ('severe', 'Severe'),
        ('critical', 'Critical'),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='risk_assessments'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    assessment_type = models.CharField(max_length=50, choices=ASSESSMENT_TYPES)
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS)
    
    # Risk scoring
    risk_score = models.FloatField(help_text="Calculated risk score (0-100)")
    likelihood = models.FloatField(help_text="Likelihood of occurrence (0-1)")
    impact = models.FloatField(help_text="Potential impact (0-1)")
    
    # Subject of assessment
    subject_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='risk_assessments'
    )
    subject_access_point = models.ForeignKey(
        AccessPoint,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='risk_assessments'
    )
    subject_identifier = models.CharField(
        max_length=255,
        blank=True,
        help_text="Generic identifier for other subjects"
    )
    
    # Analysis
    risk_factors = models.JSONField(
        default=list,
        help_text="List of identified risk factors"
    )
    vulnerabilities = models.JSONField(
        default=list,
        help_text="Identified vulnerabilities"
    )
    mitigation_recommendations = models.JSONField(
        default=list,
        help_text="Recommended mitigation actions"
    )
    
    # Assessment details
    assessed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conducted_assessments'
    )
    assessment_method = models.CharField(
        max_length=100,
        help_text="AI model or manual"
    )
    
    # Validity
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    assessed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-assessed_at']
        indexes = [
            models.Index(fields=['organization', 'is_active', '-assessed_at']),
            models.Index(fields=['risk_level', '-assessed_at']),
            models.Index(fields=['assessment_type', '-assessed_at']),
            models.Index(fields=['subject_user', '-assessed_at']),
        ]
        verbose_name = _('Risk Assessment')
        verbose_name_plural = _('Risk Assessments')
    
    def __str__(self):
        return f"[{self.risk_level.upper()}] {self.title}"


class ThreatIndicator(models.Model):
    """
    Indicators of Compromise (IOCs) and suspicious patterns
    """
    INDICATOR_TYPES = [
        ('ip_address', 'IP Address'),
        ('domain', 'Domain'),
        ('url', 'URL'),
        ('email', 'Email Address'),
        ('file_hash', 'File Hash'),
        ('user_agent', 'User Agent'),
        ('behavior_pattern', 'Behavior Pattern'),
        ('credential', 'Credential'),
        ('geolocation', 'Geolocation'),
        ('device_fingerprint', 'Device Fingerprint'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('expired', 'Expired'),
        ('whitelisted', 'Whitelisted'),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='threat_indicators'
    )
    indicator_type = models.CharField(max_length=50, choices=INDICATOR_TYPES)
    indicator_value = models.TextField(help_text="The actual IOC value")
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Relationships
    threat = models.ForeignKey(
        Threat,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='indicators'
    )
    
    # Detection tracking
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    times_detected = models.IntegerField(default=1)
    
    # Confidence and scoring
    confidence_score = models.FloatField(
        default=0.0,
        help_text="Confidence in indicator (0-1)"
    )
    false_positive_rate = models.FloatField(default=0.0)
    
    # Source
    source = models.CharField(
        max_length=100,
        help_text="Detection/feed source"
    )
    external_references = models.JSONField(
        default=list,
        blank=True,
        help_text="External threat intel references"
    )
    
    # Expiration
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Additional context
    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Attribution
    added_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='added_indicators'
    )
    
    class Meta:
        ordering = ['-last_seen']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['indicator_type', 'status']),
            models.Index(fields=['severity', '-last_seen']),
            models.Index(fields=['threat', '-last_seen']),
        ]
        verbose_name = _('Threat Indicator')
        verbose_name_plural = _('Threat Indicators')
    
    def __str__(self):
        return f"[{self.indicator_type}] {self.indicator_value[:50]}"


class Watchlist(models.Model):
    """
    Persons, vehicles, or entities of interest for monitoring
    """
    WATCHLIST_TYPES = [
        ('person', 'Person'),
        ('vehicle', 'Vehicle'),
        ('device', 'Device'),
        ('credential', 'Credential'),
        ('ip_address', 'IP Address'),
        ('email', 'Email'),
        ('organization', 'Organization'),
    ]
    
    THREAT_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('expired', 'Expired'),
        ('resolved', 'Resolved'),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='watchlists'
    )
    watchlist_type = models.CharField(max_length=50, choices=WATCHLIST_TYPES)
    name = models.CharField(max_length=255)
    description = models.TextField()
    threat_level = models.CharField(max_length=20, choices=THREAT_LEVELS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Subject identification
    subject_identifier = models.CharField(
        max_length=255,
        help_text="License plate, email, name, etc."
    )
    subject_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='watchlist_entries'
    )
    
    # Detection preferences
    alert_on_detection = models.BooleanField(
        default=True,
        help_text="Generate alert when detected"
    )
    auto_block = models.BooleanField(
        default=False,
        help_text="Automatically block access"
    )
    
    # Monitoring
    times_detected = models.IntegerField(default=0)
    last_detected_at = models.DateTimeField(null=True, blank=True)
    last_detected_location = models.CharField(max_length=255, blank=True)
    
    # Reason and context
    reason = models.TextField(help_text="Reason for watchlist inclusion")
    notes = models.TextField(blank=True)
    
    # Relationships
    related_threats = models.ManyToManyField(
        Threat,
        blank=True,
        related_name='watchlist_entries'
    )
    
    # Validity
    valid_from = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    
    # Attribution
    added_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='added_watchlist_entries'
    )
    
    # Metadata
    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['watchlist_type', 'status']),
            models.Index(fields=['threat_level', '-created_at']),
            models.Index(fields=['subject_identifier']),
        ]
        verbose_name = _('Watchlist Entry')
        verbose_name_plural = _('Watchlist Entries')
    
    def __str__(self):
        return f"[{self.threat_level.upper()}] {self.name}"


class ThreatFeed(models.Model):
    """
    External threat intelligence feed integrations
    """
    FEED_TYPES = [
        ('alienvault', 'AlienVault OTX'),
        ('misp', 'MISP'),
        ('threatconnect', 'ThreatConnect'),
        ('virustotal', 'VirusTotal'),
        ('custom', 'Custom Feed'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('error', 'Error'),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='threat_feeds'
    )
    name = models.CharField(max_length=255)
    feed_type = models.CharField(max_length=50, choices=FEED_TYPES)
    description = models.TextField(blank=True)
    
    # Connection details
    api_url = models.URLField()
    api_key = models.CharField(max_length=500, blank=True)
    authentication_method = models.CharField(max_length=50, default='api_key')
    
    # Configuration
    update_frequency = models.IntegerField(
        default=3600,
        help_text="Update frequency in seconds"
    )
    auto_import = models.BooleanField(default=True)
    trust_score = models.FloatField(
        default=0.8,
        help_text="Trust level for this feed (0-1)"
    )
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    last_sync_at = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True)
    
    # Statistics
    total_indicators_imported = models.IntegerField(default=0)
    last_import_count = models.IntegerField(default=0)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        unique_together = ['organization', 'name']
        verbose_name = _('Threat Feed')
        verbose_name_plural = _('Threat Feeds')
    
    def __str__(self):
        return f"{self.name} ({self.feed_type})"


class ThreatHuntingQuery(models.Model):
    """
    Saved threat hunting queries and hypotheses
    """
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='threat_hunting_queries'
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    
    # Query details
    query_text = models.TextField(help_text="Natural language or SQL query")
    query_type = models.CharField(
        max_length=50,
        choices=[
            ('natural_language', 'Natural Language'),
            ('sql', 'SQL'),
            ('dsl', 'DSL'),
        ]
    )
    
    # Hypothesis
    hypothesis = models.TextField(
        blank=True,
        help_text="Threat hunting hypothesis"
    )
    expected_outcome = models.TextField(blank=True)
    
    # Execution tracking
    times_executed = models.IntegerField(default=0)
    last_executed_at = models.DateTimeField(null=True, blank=True)
    last_result_count = models.IntegerField(default=0)
    
    # Results analysis
    findings = models.JSONField(default=list, blank=True)
    threats_discovered = models.ManyToManyField(
        Threat,
        blank=True,
        related_name='hunting_queries'
    )
    
    # Sharing
    is_public = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='threat_hunting_queries'
    )
    
    # Metadata
    tags = models.JSONField(default=list, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = _('Threat Hunting Query')
        verbose_name_plural = _('Threat Hunting Queries')
    
    def __str__(self):
        return self.name
