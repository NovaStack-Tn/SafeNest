"""
URL routing for faces app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CameraViewSet, FaceIdentityViewSet, FaceEmbeddingViewSet,
    FaceDetectionViewSet
)

router = DefaultRouter()
router.register(r'cameras', CameraViewSet, basename='camera')
router.register(r'identities', FaceIdentityViewSet, basename='face-identity')
router.register(r'embeddings', FaceEmbeddingViewSet, basename='face-embedding')
router.register(r'detections', FaceDetectionViewSet, basename='face-detection')

urlpatterns = [
    path('', include(router.urls)),
]
