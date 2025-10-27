"""
Admin configuration for face recognition models.
"""
from django.contrib import admin
from .models import Camera, FaceIdentity, FaceEmbedding, FaceDetection


@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'location', 'active', 'last_detection_at', 'created_at']
    list_filter = ['organization', 'active', 'created_at']
    search_fields = ['name', 'location']
    readonly_fields = ['last_detection_at', 'created_at', 'updated_at']


class FaceEmbeddingInline(admin.TabularInline):
    model = FaceEmbedding
    extra = 0
    readonly_fields = ['created_at', 'quality_score']


@admin.register(FaceIdentity)
class FaceIdentityAdmin(admin.ModelAdmin):
    list_display = ['person_label', 'organization', 'enrollment_status', 'is_active', 'created_at']
    list_filter = ['organization', 'enrollment_status', 'is_active', 'created_at']
    search_fields = ['person_label']
    readonly_fields = ['enrollment_status', 'created_at', 'updated_at']
    inlines = [FaceEmbeddingInline]


@admin.register(FaceEmbedding)
class FaceEmbeddingAdmin(admin.ModelAdmin):
    list_display = ['identity', 'model_name', 'quality_score', 'created_at']
    list_filter = ['model_name', 'created_at']
    readonly_fields = ['created_at']


@admin.register(FaceDetection)
class FaceDetectionAdmin(admin.ModelAdmin):
    list_display = ['camera', 'identity', 'is_match', 'similarity', 'confidence', 'timestamp']
    list_filter = ['camera', 'is_match', 'timestamp']
    search_fields = ['identity__person_label']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
