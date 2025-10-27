"""
Celery tasks for face processing.
"""
import logging
from celery import shared_task
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from .models import FaceIdentity, FaceEmbedding, FaceDetection, Camera
from .services import InsightFaceService

logger = logging.getLogger(__name__)


@shared_task
def enroll_face_identity(identity_id, image_paths=None):
    """
    Enroll a face identity by processing images and creating embeddings.
    
    Args:
        identity_id: FaceIdentity ID
        image_paths: List of image file paths or None to use identity.photo
    """
    try:
        identity = FaceIdentity.objects.get(id=identity_id)
        service = InsightFaceService()
        
        if not image_paths and not identity.photo:
            logger.error(f"No images provided for identity {identity_id}")
            identity.enrollment_status = 'failed'
            identity.save()
            return
        
        # Use identity photo if no paths provided
        if not image_paths:
            image_paths = [identity.photo.path]
        
        embeddings_created = 0
        
        for img_path in image_paths:
            try:
                # Detect faces
                faces = service.detect_faces(img_path)
                
                if not faces:
                    logger.warning(f"No faces detected in {img_path}")
                    continue
                
                # Use the first (largest) face
                face = faces[0]
                
                # Extract embedding
                embedding = service.extract_embedding(face)
                if embedding is None:
                    continue
                
                # Get attributes
                attributes = service.get_face_attributes(face)
                bbox = service.get_face_bbox(face)
                
                # Save cropped face
                from PIL import Image
                img = Image.open(img_path)
                face_crop = service.save_face_crop(img, bbox, f'{identity.person_label}_{embeddings_created}.jpg')
                
                # Create embedding record
                FaceEmbedding.objects.create(
                    identity=identity,
                    vector=embedding.tolist(),
                    model_name=service.app.models.get('recognition', 'buffalo_l'),
                    source_image=face_crop,
                    quality_score=attributes.get('confidence', 0.0)
                )
                
                embeddings_created += 1
                logger.info(f"Created embedding {embeddings_created} for identity {identity.person_label}")
                
            except Exception as e:
                logger.error(f"Error processing image {img_path}: {e}")
                continue
        
        # Update enrollment status
        if embeddings_created > 0:
            identity.enrollment_status = 'enrolled'
            logger.info(f"Successfully enrolled identity {identity.person_label} with {embeddings_created} embeddings")
        else:
            identity.enrollment_status = 'failed'
            logger.error(f"Failed to enroll identity {identity.person_label}")
        
        identity.save()
        
    except FaceIdentity.DoesNotExist:
        logger.error(f"FaceIdentity {identity_id} not found")
    except Exception as e:
        logger.error(f"Error enrolling identity {identity_id}: {e}")


@shared_task
def detect_faces_in_image(image_path, camera_id=None, create_detection=True):
    """
    Detect faces in an image and optionally match with known identities.
    
    Args:
        image_path: Path to image file
        camera_id: Camera ID (optional)
        create_detection: Whether to create FaceDetection records
    
    Returns:
        List of detection data
    """
    try:
        service = InsightFaceService()
        
        # Detect faces
        faces = service.detect_faces(image_path)
        
        if not faces:
            logger.info(f"No faces detected in image")
            return []
        
        detections = []
        camera = None
        
        if camera_id:
            try:
                camera = Camera.objects.get(id=camera_id)
            except Camera.DoesNotExist:
                pass
        
        for face in faces:
            # Extract data
            embedding = service.extract_embedding(face)
            bbox = service.get_face_bbox(face)
            attributes = service.get_face_attributes(face)
            
            detection_data = {
                'bbox': bbox,
                'confidence': attributes.get('confidence', 0.0),
                'age': attributes.get('age'),
                'gender': attributes.get('gender'),
                'landmarks': attributes.get('landmarks', {}),
            }
            
            # Try to match with known identity
            if embedding is not None and camera and camera.organization:
                identity, similarity = recognize_face(
                    embedding,
                    camera.organization.id
                )
                
                if identity:
                    detection_data['identity_id'] = identity.id
                    detection_data['identity_label'] = identity.person_label
                    detection_data['similarity'] = similarity
                    detection_data['is_match'] = similarity >= camera.confidence_threshold
            
            detections.append(detection_data)
            
            # Create detection record
            if create_detection and camera:
                from PIL import Image
                img = Image.open(image_path)
                face_crop = service.save_face_crop(img, bbox, f'detection_{timezone.now().timestamp()}.jpg')
                
                FaceDetection.objects.create(
                    camera=camera,
                    frame_image=face_crop,
                    bbox=bbox,
                    confidence=detection_data['confidence'],
                    embedding_vector=embedding.tolist() if embedding is not None else None,
                    identity_id=detection_data.get('identity_id'),
                    similarity=detection_data.get('similarity'),
                    is_match=detection_data.get('is_match', False),
                    age=detection_data.get('age'),
                    gender=detection_data.get('gender'),
                    landmarks=detection_data.get('landmarks', {})
                )
        
        logger.info(f"Processed {len(detections)} faces from image")
        return detections
        
    except Exception as e:
        logger.error(f"Error detecting faces in image: {e}")
        return []


def recognize_face(embedding, organization_id, top_k=3):
    """
    Recognize a face by finding nearest embeddings in database.
    
    Args:
        embedding: numpy array or list
        organization_id: Organization ID to search within
        top_k: Number of top matches to return
    
    Returns:
        (FaceIdentity, similarity) or (None, None)
    """
    from django.conf import settings
    from django.db import connection
    
    try:
        # Convert to list if numpy array
        if hasattr(embedding, 'tolist'):
            embedding = embedding.tolist()
        
        # Query with pgvector cosine similarity
        # 1 - (vector <=> %s) gives cosine similarity
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    fe.identity_id,
                    1 - (fe.vector <=> %s::vector) AS similarity
                FROM faces_faceembedding fe
                INNER JOIN faces_faceidentity fi ON fe.identity_id = fi.id
                WHERE fi.organization_id = %s 
                    AND fi.is_active = true
                    AND fi.enrollment_status = 'enrolled'
                ORDER BY fe.vector <=> %s::vector
                LIMIT %s
            """, [str(embedding), organization_id, str(embedding), top_k])
            
            results = cursor.fetchall()
        
        if not results:
            return None, None
        
        # Get best match
        identity_id, similarity = results[0]
        
        threshold = settings.INSIGHTFACE_SIMILARITY_THRESHOLD
        
        if similarity >= threshold:
            identity = FaceIdentity.objects.get(id=identity_id)
            logger.info(f"Recognized face as {identity.person_label} with similarity {similarity:.3f}")
            return identity, float(similarity)
        
        return None, None
        
    except Exception as e:
        logger.error(f"Error recognizing face: {e}")
        return None, None


@shared_task
def process_rtsp_stream(camera_id):
    """
    Process RTSP stream from camera (for continuous monitoring).
    
    Args:
        camera_id: Camera ID
    """
    try:
        import cv2
        
        camera = Camera.objects.get(id=camera_id)
        
        if not camera.active or not camera.rtsp_url:
            logger.warning(f"Camera {camera.name} is not active or has no RTSP URL")
            return
        
        # Open stream
        cap = cv2.VideoCapture(camera.rtsp_url)
        
        if not cap.isOpened():
            logger.error(f"Failed to open RTSP stream for camera {camera.name}")
            return
        
        logger.info(f"Started processing stream for camera {camera.name}")
        
        frame_count = 0
        service = InsightFaceService()
        
        while camera.active:
            ret, frame = cap.read()
            
            if not ret:
                logger.warning(f"Failed to read frame from camera {camera.name}")
                break
            
            frame_count += 1
            
            # Process every Nth frame based on detection_interval
            if frame_count % (camera.detection_interval * 30) != 0:  # Assuming 30 FPS
                continue
            
            # Detect faces
            faces = service.detect_faces(frame)
            
            if not faces:
                continue
            
            # Process each detected face
            for face in faces:
                embedding = service.extract_embedding(face)
                bbox = service.get_face_bbox(face)
                attributes = service.get_face_attributes(face)
                
                # Recognize
                identity, similarity = recognize_face(
                    embedding,
                    camera.organization.id
                )
                
                # Save cropped face
                from PIL import Image
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(frame_rgb)
                face_crop = service.save_face_crop(pil_img, bbox, f'stream_{camera.id}_{timezone.now().timestamp()}.jpg')
                
                # Create detection
                detection = FaceDetection.objects.create(
                    camera=camera,
                    frame_image=face_crop,
                    bbox=bbox,
                    confidence=attributes.get('confidence', 0.0),
                    embedding_vector=embedding.tolist() if embedding is not None else None,
                    identity=identity,
                    similarity=similarity,
                    is_match=similarity is not None and similarity >= camera.confidence_threshold,
                    age=attributes.get('age'),
                    gender=attributes.get('gender'),
                    landmarks=attributes.get('landmarks', {})
                )
                
                # Broadcast via WebSocket if matched
                if detection.is_match:
                    from security.consumers import broadcast_alert
                    broadcast_alert(camera.organization.id, {
                        'type': 'face_detected',
                        'severity': 'low',
                        'message': f"Recognized {identity.person_label} at {camera.name}",
                        'data': {
                            'detection_id': detection.id,
                            'identity': identity.person_label,
                            'camera': camera.name,
                            'similarity': similarity,
                        }
                    })
            
            # Update camera last detection time
            camera.last_detection_at = timezone.now()
            camera.save(update_fields=['last_detection_at'])
        
        cap.release()
        logger.info(f"Stopped processing stream for camera {camera.name}")
        
    except Camera.DoesNotExist:
        logger.error(f"Camera {camera_id} not found")
    except Exception as e:
        logger.error(f"Error processing RTSP stream: {e}")


@shared_task
def cleanup_old_face_detections():
    """
    Delete old face detections based on organization retention policy.
    """
    from core.models import Organization
    
    logger.info("Starting face detection cleanup")
    
    for org in Organization.objects.filter(is_active=True):
        try:
            retention_days = org.face_retention_days
            cutoff_date = timezone.now() - timedelta(days=retention_days)
            
            # Delete old detections
            deleted_count, _ = FaceDetection.objects.filter(
                camera__organization=org,
                timestamp__lt=cutoff_date
            ).delete()
            
            logger.info(f"Deleted {deleted_count} old detections for {org.name}")
            
        except Exception as e:
            logger.error(f"Error cleaning up detections for {org.name}: {e}")
    
    logger.info("Face detection cleanup completed")
