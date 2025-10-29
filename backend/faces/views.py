"""
API views for face recognition.
"""
import os
import tempfile
import logging
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

logger = logging.getLogger(__name__)
from .models import Camera, FaceIdentity, FaceEmbedding, FaceDetection
from .serializers import (
    CameraSerializer, FaceIdentitySerializer, FaceIdentityDetailSerializer,
    FaceEmbeddingSerializer, FaceDetectionSerializer,
    EnrollFaceSerializer, DetectFaceSerializer
)
from .tasks import enroll_face_identity, detect_faces_in_image


class CameraViewSet(viewsets.ModelViewSet):
    """API endpoint for cameras."""
    queryset = Camera.objects.select_related('organization')
    serializer_class = CameraSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['organization', 'active']
    search_fields = ['name', 'location']
    
    def get_queryset(self):
        """Filter by organization for non-admin users."""
        user = self.request.user
        queryset = super().get_queryset()
        
        if not user.is_staff and user.organization:
            queryset = queryset.filter(organization=user.organization)
        
        return queryset
    
    def perform_create(self, serializer):
        """Auto-assign organization from logged-in user."""
        serializer.save(organization=self.request.user.organization)
    
    @action(detail=True, methods=['post'])
    def start_stream(self, request, pk=None):
        """Start processing RTSP stream."""
        camera = self.get_object()
        
        if not camera.rtsp_url:
            return Response(
                {'error': 'Camera has no RTSP URL configured'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Start stream processing task
        from .tasks import process_rtsp_stream
        process_rtsp_stream.delay(camera.id)
        
        return Response({
            'message': f'Started stream processing for camera {camera.name}',
            'camera_id': camera.id
        })
    
    @action(detail=True, methods=['get'])
    def last_detections(self, request, pk=None):
        """Get last N detections from camera."""
        camera = self.get_object()
        limit = int(request.query_params.get('limit', 10))
        
        detections = camera.detections.all()[:limit]
        serializer = FaceDetectionSerializer(detections, many=True, context={'request': request})
        
        return Response(serializer.data)


class FaceIdentityViewSet(viewsets.ModelViewSet):
    """API endpoint for face identities."""
    queryset = FaceIdentity.objects.select_related('organization', 'created_by').prefetch_related('embeddings')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['organization', 'is_active', 'enrollment_status']
    search_fields = ['person_label', 'person_meta']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return FaceIdentityDetailSerializer
        return FaceIdentitySerializer
    
    def get_queryset(self):
        """Filter by organization for non-admin users."""
        user = self.request.user
        queryset = super().get_queryset()
        
        if not user.is_staff and user.organization:
            queryset = queryset.filter(organization=user.organization)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set created_by and organization to current user's."""
        serializer.save(
            created_by=self.request.user,
            organization=self.request.user.organization
        )
    
    @action(detail=True, methods=['post'])
    def enroll(self, request, pk=None):
        """Enroll face identity with provided images."""
        identity = self.get_object()
        
        # Get images from request
        images = request.FILES.getlist('images')
        
        if not images and not identity.photo:
            return Response(
                {'error': 'No images provided for enrollment'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save images temporarily
        temp_paths = []
        for img in images:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                for chunk in img.chunks():
                    tmp.write(chunk)
                temp_paths.append(tmp.name)
        
        # Start enrollment task
        enroll_face_identity.delay(identity.id, temp_paths if temp_paths else None)
        
        return Response({
            'message': f'Started enrollment for {identity.person_label}',
            'identity_id': identity.id,
            'status': 'processing'
        })
    
    @action(detail=True, methods=['get'])
    def detections(self, request, pk=None):
        """Get all detections for this identity."""
        identity = self.get_object()
        limit = int(request.query_params.get('limit', 50))
        
        detections = identity.detections.all()[:limit]
        serializer = FaceDetectionSerializer(detections, many=True, context={'request': request})
        
        return Response(serializer.data)


class FaceEmbeddingViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for face embeddings (read-only)."""
    queryset = FaceEmbedding.objects.select_related('identity')
    serializer_class = FaceEmbeddingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['identity']
    
    def get_queryset(self):
        """Filter by organization for non-admin users."""
        user = self.request.user
        queryset = super().get_queryset()
        
        if not user.is_staff and user.organization:
            queryset = queryset.filter(identity__organization=user.organization)
        
        return queryset


class FaceDetectionViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for face detections (read-only)."""
    queryset = FaceDetection.objects.select_related('camera', 'identity')
    serializer_class = FaceDetectionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['camera', 'identity', 'is_match']
    ordering_fields = ['timestamp', 'similarity']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        """Filter by organization for non-admin users."""
        user = self.request.user
        queryset = super().get_queryset()
        
        if not user.is_staff and user.organization:
            queryset = queryset.filter(camera__organization=user.organization)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def detect(self, request):
        """Detect faces in uploaded image."""
        from .models import Camera
        
        serializer = DetectFaceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        image = serializer.validated_data['image']
        camera_id = serializer.validated_data.get('camera_id')
        
        # Get or create a default "Live Surveillance" camera for this user's organization
        camera = None
        if request.user.organization:
            camera, created = Camera.objects.get_or_create(
                organization=request.user.organization,
                name='Live Surveillance Camera',
                defaults={
                    'location': 'Web Browser',
                    'description': 'Live camera surveillance from web interface',
                    'active': True,
                    'detection_interval': 3,
                    'confidence_threshold': 0.6
                }
            )
            camera_id = camera.id
            if created:
                logger.info(f"Created default Live Surveillance camera for org {request.user.organization.id}")
        
        # Save image temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
            for chunk in image.chunks():
                tmp.write(chunk)
            temp_path = tmp.name
        
        try:
            # Run detection with organization for face recognition
            # Always create detection records
            detections = detect_faces_in_image(
                temp_path,
                camera_id=camera_id,
                organization_id=request.user.organization.id if request.user.organization else None,
                create_detection=True  # Always save detections
            )
            
            return Response({
                'detections': detections,
                'count': len(detections)
            })
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get detection statistics."""
        queryset = self.get_queryset()
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        
        stats = {
            'total': queryset.count(),
            'matched': queryset.filter(is_match=True).count(),
            'unmatched': queryset.filter(is_match=False).count(),
            'today': queryset.filter(timestamp__date=today).count(),
            'last_24h': queryset.filter(timestamp__gte=timezone.now() - timedelta(hours=24)).count(),
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent detections for live monitoring."""
        limit = int(request.query_params.get('limit', 50))
        queryset = self.get_queryset()[:limit]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def alerts(self, request):
        """Get unmatched face alerts (suspected/unknown faces)."""
        limit = int(request.query_params.get('limit', 20))
        queryset = self.get_queryset().filter(is_match=False)[:limit]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class FaceAPIView(viewsets.ViewSet):
    """Additional face API endpoints."""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def enroll(self, request):
        """Enroll face identity with images."""
        serializer = EnrollFaceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        identity_id = serializer.validated_data['identity_id']
        images = request.FILES.getlist('images')
        
        try:
            identity = FaceIdentity.objects.get(id=identity_id)
            
            # Check access
            if not request.user.is_staff and identity.organization != request.user.organization:
                return Response(
                    {'error': 'Access denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Save images temporarily
            temp_paths = []
            for img in images:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                    for chunk in img.chunks():
                        tmp.write(chunk)
                    temp_paths.append(tmp.name)
            
            # Start enrollment
            enroll_face_identity.delay(identity.id, temp_paths)
            
            return Response({
                'message': 'Enrollment started',
                'identity_id': identity.id
            })
            
        except FaceIdentity.DoesNotExist:
            return Response(
                {'error': 'Identity not found'},
                status=status.HTTP_404_NOT_FOUND
            )
