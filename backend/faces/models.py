"""
Face recognition models: Camera, FaceIdentity, FaceEmbedding, FaceDetection
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
# Temporarily disabled - install pgvector extension first
# from pgvector.django import VectorField
from django.utils.translation import gettext_lazy as _
from access_control.models import AccessPoint

User = get_user_model()


class Camera(models.Model):
    """Camera/stream configuration."""
    organization = models.ForeignKey(
        'core.Organization',
        on_delete=models.CASCADE,
        related_name='cameras'
    )
    name = models.CharField(max_length=255)
    rtsp_url = models.URLField(blank=True, help_text="RTSP stream URL")
    location = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    
    # Mapping to Access Control: which access point this camera observes
    access_point = models.ForeignKey(
        AccessPoint,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cameras',
        help_text="Optional: link this camera to an access point"
    )
    
    # Configuration
    detection_interval = models.IntegerField(
        default=1,
        help_text="Seconds between detection runs"
    )
    confidence_threshold = models.FloatField(default=0.5)
    
    # Metadata
    last_detection_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['organization', 'name']
        verbose_name = _('Camera')
        verbose_name_plural = _('Cameras')
    
    def __str__(self):
        return f"{self.name} ({self.organization})"


class FaceIdentity(models.Model):
    """Represents a known person in the system."""
    organization = models.ForeignKey(
        'core.Organization',
        on_delete=models.CASCADE,
        related_name='face_identities'
    )
    person_label = models.CharField(max_length=255)
    person_meta = models.JSONField(
        default=dict,
        blank=True,
        help_text="Employee ID, department, etc."
    )
    
    # Photos for enrollment
    photo = models.ImageField(upload_to='face_identities/%Y/%m/%d/', null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    enrollment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('enrolled', 'Enrolled'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    
    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_identities'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['organization', 'person_label']
        unique_together = ['organization', 'person_label']
        verbose_name = _('Face Identity')
        verbose_name_plural = _('Face Identities')
    
    def __str__(self):
        return f"{self.person_label} ({self.organization})"


class FaceEmbedding(models.Model):
    """Face embedding vectors for recognition."""
    identity = models.ForeignKey(
        FaceIdentity,
        on_delete=models.CASCADE,
        related_name='embeddings'
    )
    # Temporarily using TextField - will change to VectorField after pgvector installation
    vector = models.TextField(help_text="Face embedding vector (temp: install pgvector)")
    model_name = models.CharField(max_length=50, default='buffalo_l')
    
    # Source image info
    source_image = models.ImageField(upload_to='face_embeddings/%Y/%m/%d/', null=True, blank=True)
    quality_score = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['identity', '-created_at']),
        ]
    
    def __str__(self):
        return f"Embedding for {self.identity.person_label}"


class FaceDetection(models.Model):
    """Detected face in a frame with optional identity match."""
    camera = models.ForeignKey(
        Camera,
        on_delete=models.CASCADE,
        related_name='detections'
    )
    frame_url = models.URLField(blank=True)
    frame_image = models.ImageField(upload_to='detections/%Y/%m/%d/', null=True, blank=True)
    
    # Detection data
    bbox = models.JSONField(help_text="Bounding box coordinates [x, y, w, h]")
    confidence = models.FloatField(help_text="Detection confidence score")
    # Temporarily using TextField - will change to VectorField after pgvector installation
    embedding_vector = models.TextField(null=True, blank=True, help_text="Face embedding vector (temp)")
    
    # Recognition result
    identity = models.ForeignKey(
        FaceIdentity,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='detections'
    )
    similarity = models.FloatField(
        null=True,
        blank=True,
        help_text="Cosine similarity with matched identity"
    )
    is_match = models.BooleanField(default=False)
    
    # Additional data
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    landmarks = models.JSONField(default=dict, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['camera', '-timestamp']),
            models.Index(fields=['identity', '-timestamp']),
            models.Index(fields=['is_match', '-timestamp']),
        ]
        verbose_name = _('Face Detection')
        verbose_name_plural = _('Face Detections')
    
    def __str__(self):
        identity_str = f" - {self.identity.person_label}" if self.identity else ""
        return f"Detection from {self.camera.name}{identity_str} at {self.timestamp}"
