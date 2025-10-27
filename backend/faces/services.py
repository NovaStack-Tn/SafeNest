"""
InsightFace service for face detection and recognition.
"""
import logging
import numpy as np
import cv2
from io import BytesIO
from PIL import Image
from django.conf import settings
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)


class InsightFaceService:
    """Service for face detection and embedding extraction using InsightFace."""
    
    def __init__(self):
        self.app = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize InsightFace model."""
        try:
            import insightface
            from insightface.app import FaceAnalysis
            
            model_name = settings.INSIGHTFACE_MODEL_NAME
            det_size = settings.INSIGHTFACE_DET_SIZE
            
            self.app = FaceAnalysis(
                name=model_name,
                providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
            )
            self.app.prepare(ctx_id=0, det_size=det_size)
            
            logger.info(f"InsightFace model '{model_name}' initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize InsightFace: {e}")
            self.app = None
    
    def detect_faces(self, image_data):
        """
        Detect faces in an image.
        
        Args:
            image_data: PIL Image, numpy array, or bytes
        
        Returns:
            list of face objects with embeddings, bboxes, landmarks
        """
        if self.app is None:
            logger.error("InsightFace model not initialized")
            return []
        
        try:
            # Convert to numpy array if needed
            img_array = self._prepare_image(image_data)
            
            # Detect faces
            faces = self.app.get(img_array)
            
            logger.info(f"Detected {len(faces)} faces")
            return faces
        except Exception as e:
            logger.error(f"Error detecting faces: {e}")
            return []
    
    def extract_embedding(self, face):
        """
        Extract embedding vector from detected face.
        
        Args:
            face: Face object from detect_faces()
        
        Returns:
            numpy array of embedding (512-dim)
        """
        try:
            if hasattr(face, 'embedding'):
                return face.embedding
            elif hasattr(face, 'normed_embedding'):
                return face.normed_embedding
            else:
                logger.error("Face object has no embedding attribute")
                return None
        except Exception as e:
            logger.error(f"Error extracting embedding: {e}")
            return None
    
    def get_face_bbox(self, face):
        """
        Get bounding box coordinates from face.
        
        Returns:
            dict with x, y, width, height
        """
        try:
            bbox = face.bbox.astype(int)
            return {
                'x': int(bbox[0]),
                'y': int(bbox[1]),
                'width': int(bbox[2] - bbox[0]),
                'height': int(bbox[3] - bbox[1])
            }
        except Exception as e:
            logger.error(f"Error extracting bbox: {e}")
            return {'x': 0, 'y': 0, 'width': 0, 'height': 0}
    
    def get_face_attributes(self, face):
        """
        Extract additional attributes like age, gender, landmarks.
        
        Returns:
            dict with attributes
        """
        attributes = {}
        
        try:
            if hasattr(face, 'age'):
                attributes['age'] = int(face.age)
            
            if hasattr(face, 'gender'):
                attributes['gender'] = 'male' if face.gender == 1 else 'female'
            
            if hasattr(face, 'landmark'):
                attributes['landmarks'] = face.landmark.tolist()
            
            if hasattr(face, 'det_score'):
                attributes['confidence'] = float(face.det_score)
        except Exception as e:
            logger.error(f"Error extracting attributes: {e}")
        
        return attributes
    
    def crop_face(self, image_data, bbox):
        """
        Crop face from image using bounding box.
        
        Args:
            image_data: Image data
            bbox: dict with x, y, width, height
        
        Returns:
            Cropped PIL Image
        """
        try:
            img = self._prepare_image(image_data, as_pil=True)
            x, y, w, h = bbox['x'], bbox['y'], bbox['width'], bbox['height']
            
            # Add padding
            padding = int(min(w, h) * 0.2)
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = w + 2 * padding
            h = h + 2 * padding
            
            cropped = img.crop((x, y, x + w, y + h))
            return cropped
        except Exception as e:
            logger.error(f"Error cropping face: {e}")
            return None
    
    def calculate_similarity(self, embedding1, embedding2):
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1, embedding2: numpy arrays
        
        Returns:
            float similarity score (0-1)
        """
        try:
            # Normalize
            emb1 = embedding1 / np.linalg.norm(embedding1)
            emb2 = embedding2 / np.linalg.norm(embedding2)
            
            # Cosine similarity
            similarity = np.dot(emb1, emb2)
            
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def _prepare_image(self, image_data, as_pil=False):
        """
        Convert various image formats to numpy array or PIL Image.
        
        Args:
            image_data: PIL Image, numpy array, bytes, or file path
            as_pil: If True, return PIL Image instead of numpy
        
        Returns:
            numpy array (BGR) or PIL Image
        """
        try:
            # If already numpy array
            if isinstance(image_data, np.ndarray):
                if as_pil:
                    # Convert BGR to RGB for PIL
                    return Image.fromarray(cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB))
                return image_data
            
            # If PIL Image
            if isinstance(image_data, Image.Image):
                if as_pil:
                    return image_data
                # Convert RGB to BGR for OpenCV
                return cv2.cvtColor(np.array(image_data), cv2.COLOR_RGB2BGR)
            
            # If bytes
            if isinstance(image_data, bytes):
                pil_img = Image.open(BytesIO(image_data))
                if as_pil:
                    return pil_img
                return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            
            # If file path
            if isinstance(image_data, str):
                pil_img = Image.open(image_data)
                if as_pil:
                    return pil_img
                return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            
            logger.error(f"Unsupported image data type: {type(image_data)}")
            return None
        except Exception as e:
            logger.error(f"Error preparing image: {e}")
            return None
    
    def save_face_crop(self, image_data, bbox, file_name='face_crop.jpg'):
        """
        Save cropped face to a file-like object.
        
        Returns:
            ContentFile suitable for Django FileField
        """
        try:
            cropped = self.crop_face(image_data, bbox)
            if cropped is None:
                return None
            
            # Save to BytesIO
            buffer = BytesIO()
            cropped.save(buffer, format='JPEG', quality=95)
            buffer.seek(0)
            
            return ContentFile(buffer.read(), name=file_name)
        except Exception as e:
            logger.error(f"Error saving face crop: {e}")
            return None
