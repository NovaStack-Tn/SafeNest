from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class Visitor(models.Model):
    """Model for tracking visitors, guests, contractors, and vendors"""
    
    VISITOR_TYPE_CHOICES = [
        ('guest', 'Guest'),
        ('contractor', 'Contractor'),
        ('vendor', 'Vendor'),
        ('delivery', 'Delivery Personnel'),
        ('maintenance', 'Maintenance'),
        ('emergency', 'Emergency Services'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pre_registered', 'Pre-Registered'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('cancelled', 'Cancelled'),
        ('blacklisted', 'Blacklisted'),
    ]
    
    # Basic Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    company = models.CharField(max_length=200, blank=True)
    visitor_type = models.CharField(max_length=20, choices=VISITOR_TYPE_CHOICES, default='guest')
    
    # Identification
    id_type = models.CharField(max_length=50, blank=True)  # Passport, Driver's License, etc.
    id_number = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to='visitors/photos/', blank=True, null=True)
    
    # Visit Details
    purpose = models.TextField()
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='hosted_visitors')
    department = models.CharField(max_length=100, blank=True)
    
    # Status & Dates
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pre_registered')
    expected_arrival = models.DateTimeField()
    expected_departure = models.DateTimeField()
    actual_arrival = models.DateTimeField(null=True, blank=True)
    actual_departure = models.DateTimeField(null=True, blank=True)
    
    # AI-Enhanced Fields
    ai_extracted = models.BooleanField(default=False)  # Was info extracted by AI?
    ai_confidence = models.FloatField(null=True, blank=True)  # Confidence score
    ai_suggested_access_level = models.CharField(max_length=50, blank=True)
    ai_predicted_duration = models.IntegerField(null=True, blank=True, help_text="Predicted visit duration in minutes")
    extracted_data = models.JSONField(default=dict, blank=True)  # Raw AI extraction
    
    # Additional Info
    notes = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    emergency_phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    vehicle_plate = models.CharField(max_length=20, blank=True)
    
    # Metadata
    organization = models.ForeignKey('core.Organization', on_delete=models.CASCADE, related_name='visitors')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_visitors')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-expected_arrival']
        indexes = [
            models.Index(fields=['status', 'expected_arrival']),
            models.Index(fields=['organization', 'status']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.visitor_type}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_checked_in(self):
        return self.status == 'checked_in'
    
    @property
    def is_overdue(self):
        """Check if visitor has overstayed expected departure"""
        if self.status == 'checked_in' and self.expected_departure:
            return timezone.now() > self.expected_departure
        return False


class VisitorPass(models.Model):
    """Temporary access credentials for visitors"""
    
    PASS_TYPE_CHOICES = [
        ('qr_code', 'QR Code'),
        ('nfc', 'NFC Card'),
        ('biometric', 'Biometric'),
        ('pin', 'PIN Code'),
        ('digital', 'Digital Pass'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
        ('pending', 'Pending Activation'),
    ]
    
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, related_name='passes')
    pass_type = models.CharField(max_length=20, choices=PASS_TYPE_CHOICES, default='qr_code')
    pass_code = models.CharField(max_length=100, unique=True)  # QR code, PIN, NFC ID
    
    # Access Control
    access_level = models.CharField(max_length=50, default='visitor')
    allowed_areas = models.JSONField(default=list)  # List of area IDs/names
    access_points = models.ManyToManyField('access_control.AccessPoint', blank=True, related_name='visitor_passes')
    
    # Validity
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Usage Tracking
    times_used = models.IntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)
    max_uses = models.IntegerField(null=True, blank=True)  # Optional usage limit
    
    # Metadata
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    revoked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='revoked_passes', blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    revocation_reason = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-issued_at']
        indexes = [
            models.Index(fields=['pass_code']),
            models.Index(fields=['status', 'valid_until']),
        ]
    
    def __str__(self):
        return f"Pass for {self.visitor.full_name} - {self.pass_type}"
    
    @property
    def is_valid(self):
        """Check if pass is currently valid"""
        now = timezone.now()
        if self.status != 'active':
            return False
        if self.max_uses and self.times_used >= self.max_uses:
            return False
        return self.valid_from <= now <= self.valid_until
    
    def record_usage(self):
        """Record a pass usage"""
        self.times_used += 1
        self.last_used = timezone.now()
        self.save()


class Asset(models.Model):
    """Equipment, devices, vehicles, and inventory items"""
    
    ASSET_TYPE_CHOICES = [
        ('laptop', 'Laptop'),
        ('desktop', 'Desktop Computer'),
        ('mobile', 'Mobile Device'),
        ('tablet', 'Tablet'),
        ('vehicle', 'Vehicle'),
        ('equipment', 'Equipment'),
        ('tool', 'Tool'),
        ('key', 'Key/Access Card'),
        ('camera', 'Camera/Recording Device'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('assigned', 'Assigned'),
        ('in_use', 'In Use'),
        ('maintenance', 'Under Maintenance'),
        ('retired', 'Retired'),
        ('lost', 'Lost'),
        ('damaged', 'Damaged'),
    ]
    
    CONDITION_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=200)
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPE_CHOICES)
    asset_tag = models.CharField(max_length=100, unique=True)  # Barcode/QR/ID
    serial_number = models.CharField(max_length=100, blank=True, unique=True, null=True)
    
    # Details
    description = models.TextField(blank=True)
    manufacturer = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    warranty_expiry = models.DateField(null=True, blank=True)
    
    # Status & Condition
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good')
    location = models.CharField(max_length=200)  # Current physical location
    
    # Assignment
    current_assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_assets')
    assigned_at = models.DateTimeField(null=True, blank=True)
    
    # Additional Info
    image = models.ImageField(upload_to='assets/images/', blank=True, null=True)
    notes = models.TextField(blank=True)
    specifications = models.JSONField(default=dict, blank=True)  # Technical specs
    
    # Metadata
    organization = models.ForeignKey('core.Organization', on_delete=models.CASCADE, related_name='assets')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_assets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['asset_tag']
        indexes = [
            models.Index(fields=['asset_tag']),
            models.Index(fields=['status', 'asset_type']),
            models.Index(fields=['organization', 'status']),
        ]
    
    def __str__(self):
        return f"{self.asset_tag} - {self.name}"
    
    @property
    def is_available(self):
        return self.status == 'available'
    
    @property
    def warranty_active(self):
        if self.warranty_expiry:
            return timezone.now().date() <= self.warranty_expiry
        return False


class AssetAssignment(models.Model):
    """Track who has what asset and for how long"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
        ('lost', 'Lost/Missing'),
    ]
    
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='assignments')
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='asset_assignments')
    
    # Assignment Details
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='issued_assignments')
    assigned_at = models.DateTimeField(auto_now_add=True)
    expected_return = models.DateTimeField(null=True, blank=True)
    actual_return = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    condition_on_assignment = models.CharField(max_length=20, blank=True)
    condition_on_return = models.CharField(max_length=20, blank=True)
    
    # Notes
    assignment_notes = models.TextField(blank=True)
    return_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-assigned_at']
        indexes = [
            models.Index(fields=['status', 'expected_return']),
            models.Index(fields=['assignee', 'status']),
        ]
    
    def __str__(self):
        return f"{self.asset.asset_tag} → {self.assignee.username}"
    
    @property
    def is_overdue(self):
        """Check if assignment is overdue for return"""
        if self.status == 'active' and self.expected_return:
            return timezone.now() > self.expected_return
        return False
    
    @property
    def duration(self):
        """Get assignment duration"""
        end_time = self.actual_return or timezone.now()
        return end_time - self.assigned_at


class MovementLog(models.Model):
    """Track asset check-in/check-out and visitor movements"""
    
    MOVEMENT_TYPE_CHOICES = [
        ('asset_checkout', 'Asset Check-Out'),
        ('asset_checkin', 'Asset Check-In'),
        ('visitor_checkin', 'Visitor Check-In'),
        ('visitor_checkout', 'Visitor Check-Out'),
        ('location_transfer', 'Location Transfer'),
        ('zone_entry', 'Zone Entry'),
        ('zone_exit', 'Zone Exit'),
    ]
    
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPE_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Related Objects (use GenericForeignKey for flexibility)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, null=True, blank=True, related_name='movements')
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, null=True, blank=True, related_name='movements')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='movements')
    
    # Location Details
    from_location = models.CharField(max_length=200, blank=True)
    to_location = models.CharField(max_length=200, blank=True)
    access_point = models.ForeignKey('access_control.AccessPoint', on_delete=models.SET_NULL, null=True, blank=True, related_name='visitor_movements')
    
    # Verification
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='verified_movements')
    verification_method = models.CharField(max_length=50, blank=True)  # QR, NFC, Manual, Biometric
    
    # Additional Data
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)  # GPS coords, device info, etc.
    
    # Metadata
    organization = models.ForeignKey('core.Organization', on_delete=models.CASCADE, related_name='movement_logs')
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['movement_type', 'timestamp']),
            models.Index(fields=['organization', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.movement_type} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
