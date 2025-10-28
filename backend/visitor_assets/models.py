"""
Visitor & Asset Management Models
Handles visitors, contractors, assets, inventory, and movements
"""
from django.db import models
from django.contrib.postgres.fields import JSONField
from core.models import User, Organization


class Visitor(models.Model):
    """
    External visitors, contractors, vendors, guests
    """
    VISITOR_TYPES = [
        ('guest', 'Guest'),
        ('contractor', 'Contractor'),
        ('vendor', 'Vendor'),
        ('delivery', 'Delivery Person'),
        ('interviewer', 'Job Candidate'),
        ('vip', 'VIP'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pre_registered', 'Pre-Registered'),
        ('checked_in', 'Checked In'),
        ('on_premises', 'On Premises'),
        ('checked_out', 'Checked Out'),
        ('blacklisted', 'Blacklisted'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='visitors')
    
    # Personal Info
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=200, blank=True)
    
    visitor_type = models.CharField(max_length=20, choices=VISITOR_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pre_registered')
    
    # Identification
    id_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Driver's License, Passport, etc."
    )
    id_number = models.CharField(max_length=100, blank=True)
    
    # Photo
    photo_url = models.URLField(blank=True, help_text="Visitor photo")
    face_embedding = models.BinaryField(null=True, blank=True, help_text="Face recognition embedding")
    
    # Host & Purpose
    host = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hosted_visitors'
    )
    purpose_of_visit = models.TextField()
    department_to_visit = models.CharField(max_length=200, blank=True)
    
    # Security
    risk_score = models.FloatField(default=0.0, help_text="AI-calculated risk score 0-1")
    is_on_watchlist = models.BooleanField(default=False)
    watchlist_reason = models.TextField(blank=True)
    requires_escort = models.BooleanField(default=False)
    background_check_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('not_required', 'Not Required'),
        ],
        default='not_required'
    )
    
    # NDA & Agreements
    nda_signed = models.BooleanField(default=False)
    nda_signed_at = models.DateTimeField(null=True, blank=True)
    agreements = models.JSONField(default=list, blank=True, help_text="List of signed agreements")
    
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    visit_count = models.IntegerField(default=0, help_text="Number of visits")
    last_visit_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['email']),
            models.Index(fields=['host']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.company})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class VisitorPass(models.Model):
    """
    Temporary access pass for visitors
    """
    PASS_TYPES = [
        ('day_pass', 'Day Pass'),
        ('multi_day', 'Multi-Day Pass'),
        ('contractor', 'Contractor Pass'),
        ('temp_employee', 'Temporary Employee'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
        ('used', 'Used'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='visitor_passes')
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, related_name='passes')
    
    pass_type = models.CharField(max_length=20, choices=PASS_TYPES)
    pass_number = models.CharField(max_length=50, unique=True)
    qr_code = models.TextField(blank=True, help_text="QR code data for scanning")
    
    # Validity
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    
    # Access zones
    allowed_zones = models.JSONField(
        default=list,
        help_text="List of zone IDs visitor can access"
    )
    
    # Check-in/out
    checked_in_at = models.DateTimeField(null=True, blank=True)
    checked_out_at = models.DateTimeField(null=True, blank=True)
    check_in_location = models.CharField(max_length=200, blank=True)
    check_out_location = models.CharField(max_length=200, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Issued by
    issued_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='issued_passes'
    )
    issued_at = models.DateTimeField(auto_now_add=True)
    
    # Revocation
    revoked_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='revoked_passes'
    )
    revoked_at = models.DateTimeField(null=True, blank=True)
    revocation_reason = models.TextField(blank=True)
    
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-issued_at']
        indexes = [
            models.Index(fields=['pass_number']),
            models.Index(fields=['visitor', 'status']),
            models.Index(fields=['valid_from', 'valid_until']),
        ]

    def __str__(self):
        return f"Pass {self.pass_number} - {self.visitor.full_name}"


class Asset(models.Model):
    """
    Physical assets, equipment, devices, vehicles
    """
    ASSET_TYPES = [
        ('laptop', 'Laptop'),
        ('desktop', 'Desktop Computer'),
        ('phone', 'Phone'),
        ('tablet', 'Tablet'),
        ('vehicle', 'Vehicle'),
        ('equipment', 'Equipment'),
        ('furniture', 'Furniture'),
        ('access_card', 'Access Card'),
        ('key', 'Key'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('assigned', 'Assigned'),
        ('in_use', 'In Use'),
        ('maintenance', 'Under Maintenance'),
        ('lost', 'Lost'),
        ('stolen', 'Stolen'),
        ('retired', 'Retired'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='assets')
    
    # Basic Info
    name = models.CharField(max_length=200)
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPES)
    asset_tag = models.CharField(max_length=100, unique=True, help_text="Unique asset identifier")
    serial_number = models.CharField(max_length=200, blank=True)
    
    # Details
    manufacturer = models.CharField(max_length=200, blank=True)
    model = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    
    # Financial
    purchase_date = models.DateField(null=True, blank=True)
    purchase_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    current_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Location
    current_location = models.CharField(max_length=500)
    home_location = models.CharField(max_length=500, help_text="Default/assigned location")
    
    # GPS Tracking
    has_gps = models.BooleanField(default=False)
    last_gps_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    last_gps_lon = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    last_gps_update = models.DateTimeField(null=True, blank=True)
    
    # RFID/IoT
    rfid_tag = models.CharField(max_length=100, blank=True)
    iot_device_id = models.CharField(max_length=100, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    
    # Maintenance
    last_maintenance_date = models.DateField(null=True, blank=True)
    next_maintenance_date = models.DateField(null=True, blank=True)
    maintenance_interval_days = models.IntegerField(null=True, blank=True)
    
    # AI Predictions
    predicted_failure_date = models.DateField(null=True, blank=True, help_text="AI-predicted failure")
    failure_probability = models.FloatField(null=True, blank=True, help_text="Probability 0-1")
    
    # Ownership
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_assets'
    )
    assigned_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    photo_url = models.URLField(blank=True)
    qr_code = models.TextField(blank=True)
    meta = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['asset_tag']),
            models.Index(fields=['assigned_to']),
        ]

    def __str__(self):
        return f"{self.name} ({self.asset_tag})"


class AssetAssignment(models.Model):
    """
    Track who has what asset when
    """
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='asset_assignments')
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='assignments')
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='asset_history')
    
    # Assignment period
    assigned_at = models.DateTimeField()
    returned_at = models.DateTimeField(null=True, blank=True)
    expected_return_at = models.DateTimeField(null=True, blank=True)
    
    # Assignment details
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_assets_to_others'
    )
    assignment_reason = models.TextField(blank=True)
    location_at_assignment = models.CharField(max_length=500, blank=True)
    
    # Condition
    condition_at_assignment = models.CharField(
        max_length=20,
        choices=[
            ('excellent', 'Excellent'),
            ('good', 'Good'),
            ('fair', 'Fair'),
            ('poor', 'Poor'),
        ],
        default='good'
    )
    condition_at_return = models.CharField(max_length=20, blank=True)
    condition_notes = models.TextField(blank=True)
    
    # Status
    is_overdue = models.BooleanField(default=False)
    is_returned = models.BooleanField(default=False)
    
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-assigned_at']
        indexes = [
            models.Index(fields=['asset', 'is_returned']),
            models.Index(fields=['assigned_to', 'is_returned']),
        ]

    def __str__(self):
        status = "Returned" if self.is_returned else "Active"
        return f"{self.asset.name} → {self.assigned_to.username} ({status})"


class MovementLog(models.Model):
    """
    Track movement of people and assets
    """
    ENTITY_TYPES = [
        ('visitor', 'Visitor'),
        ('asset', 'Asset'),
    ]
    
    EVENT_TYPES = [
        ('check_in', 'Check In'),
        ('check_out', 'Check Out'),
        ('zone_entry', 'Zone Entry'),
        ('zone_exit', 'Zone Exit'),
        ('location_change', 'Location Change'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='movement_logs')
    
    # Entity being tracked
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPES)
    visitor = models.ForeignKey(
        Visitor,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='movements'
    )
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='movements'
    )
    
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    
    # Location
    from_location = models.CharField(max_length=500, blank=True)
    to_location = models.CharField(max_length=500)
    zone = models.CharField(max_length=200, blank=True)
    
    # Geolocation
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Timestamp
    timestamp = models.DateTimeField(db_index=True)
    
    # Actor (who moved it)
    moved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movements_performed'
    )
    
    # Detection method
    detection_method = models.CharField(
        max_length=50,
        choices=[
            ('manual', 'Manual Entry'),
            ('rfid', 'RFID Scan'),
            ('gps', 'GPS Tracking'),
            ('camera', 'Camera Detection'),
            ('qr', 'QR Code Scan'),
        ],
        default='manual'
    )
    
    # Associated data
    photo_url = models.URLField(blank=True)
    meta = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['organization', 'timestamp']),
            models.Index(fields=['visitor', 'timestamp']),
            models.Index(fields=['asset', 'timestamp']),
        ]

    def __str__(self):
        entity = self.visitor.full_name if self.visitor else (self.asset.name if self.asset else "Unknown")
        return f"{self.event_type} - {entity} @ {self.to_location}"


class VisitorAnalytics(models.Model):
    """
    Aggregated visitor analytics and insights
    """
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='visitor_analytics')
    
    # Time period
    date = models.DateField(db_index=True)
    hour = models.IntegerField(null=True, blank=True, help_text="Hour of day 0-23")
    
    # Metrics
    total_visitors = models.IntegerField(default=0)
    new_visitors = models.IntegerField(default=0)
    repeat_visitors = models.IntegerField(default=0)
    vip_visitors = models.IntegerField(default=0)
    
    # By type
    guest_count = models.IntegerField(default=0)
    contractor_count = models.IntegerField(default=0)
    vendor_count = models.IntegerField(default=0)
    
    # Average metrics
    avg_visit_duration_minutes = models.FloatField(null=True, blank=True)
    avg_check_in_time_minutes = models.FloatField(null=True, blank=True)
    
    # Top departments visited
    top_departments = models.JSONField(default=list, blank=True)
    
    # Peak times
    peak_hour = models.IntegerField(null=True, blank=True)
    
    # AI Insights
    anomaly_count = models.IntegerField(default=0)
    high_risk_visitors = models.IntegerField(default=0)
    predicted_tomorrow = models.IntegerField(null=True, blank=True, help_text="AI prediction")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['organization', 'date', 'hour']
        ordering = ['-date', '-hour']
        indexes = [
            models.Index(fields=['organization', 'date']),
        ]

    def __str__(self):
        hour_str = f" {self.hour}:00" if self.hour is not None else ""
        return f"{self.organization.name} - {self.date}{hour_str}"
