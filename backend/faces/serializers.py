"""
Serializers for face recognition models.
"""
from rest_framework import serializers
from .models import Camera, FaceIdentity, FaceEmbedding, FaceDetection


class CameraSerializer(serializers.ModelSerializer):
    detection_count = serializers.IntegerField(source='detections.count', read_only=True)
    
    class Meta:
        model = Camera
        fields = [
            'id', 'organization', 'name', 'rtsp_url', 'location',
            'description', 'active', 'detection_interval',
            'confidence_threshold', 'last_detection_at',
            'detection_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['last_detection_at', 'created_at', 'updated_at']


class FaceEmbeddingSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaceEmbedding
        fields = [
            'id', 'identity', 'model_name', 'source_image',
            'quality_score', 'created_at'
        ]
        read_only_fields = ['created_at']


class FaceIdentitySerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    embedding_count = serializers.IntegerField(source='embeddings.count', read_only=True)
    detection_count = serializers.IntegerField(source='detections.count', read_only=True)
    
    class Meta:
        model = FaceIdentity
        fields = [
            'id', 'organization', 'person_label', 'person_meta',
            'photo', 'is_active', 'enrollment_status',
            'created_by', 'created_by_name', 'embedding_count',
            'detection_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['enrollment_status', 'created_at', 'updated_at']


class FaceIdentityDetailSerializer(FaceIdentitySerializer):
    """Detailed serializer with embeddings."""
    embeddings = FaceEmbeddingSerializer(many=True, read_only=True)
    
    class Meta(FaceIdentitySerializer.Meta):
        fields = FaceIdentitySerializer.Meta.fields + ['embeddings']


class FaceDetectionSerializer(serializers.ModelSerializer):
    camera_name = serializers.CharField(source='camera.name', read_only=True)
    identity_label = serializers.CharField(source='identity.person_label', read_only=True)
    frame_url = serializers.SerializerMethodField()
    
    class Meta:
        model = FaceDetection
        fields = [
            'id', 'camera', 'camera_name', 'frame_url', 'frame_image',
            'bbox', 'confidence', 'identity', 'identity_label',
            'similarity', 'is_match', 'age', 'gender',
            'landmarks', 'timestamp'
        ]
        read_only_fields = ['timestamp']
    
    def get_frame_url(self, obj):
        request = self.context.get('request')
        if obj.frame_image and request:
            return request.build_absolute_uri(obj.frame_image.url)
        return obj.frame_url


class EnrollFaceSerializer(serializers.Serializer):
    """Serializer for face enrollment endpoint."""
    identity_id = serializers.IntegerField()
    images = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        help_text="Multiple images for better enrollment"
    )


class DetectFaceSerializer(serializers.Serializer):
    """Serializer for face detection endpoint."""
    image = serializers.ImageField(required=True)
    camera_id = serializers.IntegerField(required=False)
    return_embeddings = serializers.BooleanField(default=False)
