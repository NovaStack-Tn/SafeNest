"""
Celery tasks for face processing.
"""
import logging
import json
from celery import shared_task
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from .models import FaceIdentity, FaceEmbedding, FaceDetection, Camera
from access_control.models import AccessLog
from django.contrib.auth import get_user_model
from .ai import get_face_service

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
        service = get_face_service()
        
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
                # Detect faces and extract embedding
                embedding = service.extract_embedding(img_path)
                
                if embedding is None:
                    logger.warning(f"No faces detected in {img_path}")
                    continue
                
                # Detect to get all face info
                faces = service.detect_faces(img_path)
                if not faces:
                    continue
                    
                face_data = faces[0]  # Use first face
                
                # Create embedding record (temporarily store as JSON string)
                FaceEmbedding.objects.create(
                    identity=identity,
                    vector=json.dumps(embedding),  # Store as JSON temporarily
                    model_name=service.model_name,
                    quality_score=face_data.get('confidence', 0.0)
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
def detect_faces_in_image(image_path, camera_id=None, organization_id=None, create_detection=True):
    """
    Detect faces in an image and optionally create detection records.
    
    Args:
        image_path: Path to image file
        camera_id: Optional camera ID for detection record
        organization_id: Organization ID for face recognition matching
        create_detection: Whether to create detection records in database
    
    Returns:
        List of detection dictionaries
    """
    from .ai import get_face_service
    from .models import Camera, FaceDetection, FaceIdentity
    import json
    
    try:
        service = get_face_service()
        faces = service.detect_faces(image_path)
        
        detections = []
        camera = None
        
        if camera_id:
            try:
                camera = Camera.objects.get(id=camera_id)
                if not organization_id:
                    organization_id = camera.organization.id
            except Camera.DoesNotExist:
                pass
        
        for face in faces:
            # Extract data from detection result
            embedding = face.get('embedding')
            bbox = face.get('bbox')
            
            detection_data = {
                'bbox': bbox,
                'confidence': face.get('confidence', 0.0),
                'age': face.get('age'),
                'gender': face.get('gender'),
                'landmarks': face.get('landmarks', []),
            }
            
            # Try to match with known identity (if we have organization)
            if embedding is not None and organization_id:
                identity, similarity = recognize_face(
                    embedding,
                    organization_id
                )
                
                if identity:
                    detection_data['identity_id'] = identity.id
                    detection_data['identity_label'] = identity.person_label
                    detection_data['person_meta'] = identity.person_meta
                    detection_data['photo'] = identity.photo.url if identity.photo else None
                    detection_data['similarity'] = similarity
                    detection_data['is_match'] = similarity >= 0.6  # Default threshold
                    if camera:
                        detection_data['is_match'] = similarity >= camera.confidence_threshold
            
            detections.append(detection_data)
            
            # Create detection record
            if create_detection and camera:
                # Crop face from original image
                from PIL import Image
                from django.core.files.base import ContentFile
                import io
                from datetime import datetime
                
                detection_obj = FaceDetection(
                    camera=camera,
                    bbox=bbox,
                    confidence=detection_data['confidence'],
                    embedding_vector=json.dumps(embedding) if embedding else None,
                    identity_id=detection_data.get('identity_id'),
                    similarity=detection_data.get('similarity'),
                    is_match=detection_data.get('is_match', False),
                    age=detection_data.get('age'),
                    gender=detection_data.get('gender'),
                    landmarks=detection_data.get('landmarks', [])
                )
                
                # Save cropped face image
                try:
                    img = Image.open(image_path)
                    x, y, w, h = bbox
                    # Add padding
                    padding = 20
                    x1 = max(0, int(x - padding))
                    y1 = max(0, int(y - padding))
                    x2 = min(img.width, int(x + w + padding))
                    y2 = min(img.height, int(y + h + padding))
                    
                    face_img = img.crop((x1, y1, x2, y2))
                    
                    # Save to BytesIO
                    buffer = io.BytesIO()
                    face_img.save(buffer, format='JPEG', quality=95)
                    buffer.seek(0)
                    
                    # Generate filename
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                    filename = f'face_{timestamp}.jpg'
                    
                    detection_obj.frame_image.save(
                        filename,
                        ContentFile(buffer.read()),
                        save=False
                    )
                except Exception as e:
                    logger.error(f"Error saving face image: {e}")
                
                detection_obj.save()
                
                # Send email alert for unknown persons
                if not detection_data.get('is_match', False) and camera.organization:
                    try:
                        from .emails import send_unknown_person_alert
                        send_unknown_person_alert(detection_obj, camera.organization)
                        logger.info(f"Email alert sent for unknown person detection {detection_obj.id}")
                    except Exception as e:
                        logger.error(f"Failed to send email alert: {e}")
                
                # Create AccessLog if camera is linked to an AccessPoint
                try:
                    if camera.access_point:
                        matched = bool(detection_data.get('is_match', False))
                        user_obj = None
                        # Best-effort user resolution from FaceIdentity.person_meta
                        if detection_obj.identity and detection_data.get('person_meta'):
                            meta = detection_data.get('person_meta') or {}
                            User = get_user_model()
                            for key in ['user_id', 'id']:
                                uid = meta.get(key)
                                if uid:
                                    try:
                                        user_obj = User.objects.get(id=uid)
                                        break
                                    except Exception:
                                        pass
                            if not user_obj:
                                for key in ['username', 'email']:
                                    val = meta.get(key)
                                    if val:
                                        try:
                                            lookup = {key: val}
                                            user_obj = User.objects.get(**lookup)
                                            break
                                        except Exception:
                                            pass
                        AccessLog.objects.create(
                            organization=camera.organization,
                            access_point=camera.access_point,
                            user=user_obj,
                            event_type='entry',
                            is_granted=matched,
                            denial_reason='' if matched else 'no_permission',
                            timestamp=timezone.now(),
                            direction='in',
                            photo_url=detection_obj.frame_image.url if detection_obj.frame_image else '',
                            device_info={'camera': camera.name}
                        )
                except Exception as e:
                    logger.error(f"Failed to create AccessLog from detection {detection_obj.id}: {e}")
        
        logger.info(f"Processed {len(detections)} faces from image")
        return detections
        
    except Exception as e:
        logger.error(f"Error detecting faces in image: {e}")
        return []


def recognize_face(embedding, organization_id, top_k=3):
    """
    Recognize a face by finding nearest embeddings in database.
    Uses cosine similarity with JSON-stored embeddings (temporary fallback).
    
    Args:
        embedding: numpy array or list
        organization_id: Organization ID to search within
        top_k: Number of top matches to return
    
    Returns:
        (FaceIdentity, similarity) or (None, None)
    """
    from django.conf import settings
    from .models import FaceEmbedding, FaceIdentity
    import numpy as np
    import json
    
    try:
        # Convert to numpy array if needed
        if not isinstance(embedding, np.ndarray):
            embedding = np.array(embedding)
        
        # Normalize embedding
        embedding_norm = embedding / np.linalg.norm(embedding)
        
        # Get all embeddings for active identities in organization
        identities = FaceIdentity.objects.filter(
            organization_id=organization_id,
            is_active=True,
            enrollment_status='enrolled'
        ).prefetch_related('embeddings')
        
        best_match = None
        best_similarity = 0.0
        
        for identity in identities:
            for face_embedding in identity.embeddings.all():
                try:
                    # Parse JSON-stored embedding
                    stored_embedding = json.loads(face_embedding.vector)
                    stored_array = np.array(stored_embedding)
                    
                    # Normalize stored embedding
                    stored_norm = stored_array / np.linalg.norm(stored_array)
                    
                    # Calculate cosine similarity
                    similarity = float(np.dot(embedding_norm, stored_norm))
                    
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = identity
                        
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"Error parsing embedding {face_embedding.id}: {e}")
                    continue
        
        threshold = getattr(settings, 'INSIGHTFACE_SIMILARITY_THRESHOLD', 0.6)
        
        if best_match and best_similarity >= threshold:
            logger.info(f"Recognized face as {best_match.person_label} with similarity {best_similarity:.3f}")
            return best_match, best_similarity
        
        logger.info(f"No match found (best similarity: {best_similarity:.3f}, threshold: {threshold})")
        return None, None
        
    except Exception as e:
        logger.error(f"Error recognizing face: {e}")
        import traceback
        logger.error(traceback.format_exc())
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
