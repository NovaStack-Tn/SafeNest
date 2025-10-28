"""
InsightFace-based Face Recognition Service
"""
import os
import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis
from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class FaceRecognitionService:
    """Face detection and recognition using InsightFace"""
    
    def __init__(self, model_name='buffalo_l', similarity_threshold=0.4):
        """
        Initialize InsightFace model
        
        Args:
            model_name: InsightFace model name (buffalo_l is recommended)
            similarity_threshold: Threshold for face matching (0-1)
        """
        self.model_name = model_name
        self.similarity_threshold = similarity_threshold
        self.app = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the face analysis model"""
        try:
            self.app = FaceAnalysis(
                name=self.model_name,
                providers=['CPUExecutionProvider']  # Use CPU, change to CUDAExecutionProvider for GPU
            )
            self.app.prepare(ctx_id=0, det_size=(640, 640))
            logger.info(f"✅ InsightFace model '{self.model_name}' initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize InsightFace: {e}")
            raise
    
    def detect_faces(self, image_path: str) -> List[Dict]:
        """
        Detect all faces in an image
        
        Args:
            image_path: Path to image file
            
        Returns:
            List of face detections with bounding boxes and embeddings
        """
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                logger.error(f"Failed to read image: {image_path}")
                return []
            
            # Detect faces
            faces = self.app.get(img)
            
            results = []
            for idx, face in enumerate(faces):
                result = {
                    'face_id': idx,
                    'bbox': face.bbox.tolist(),  # [x1, y1, x2, y2]
                    'confidence': float(face.det_score),
                    'embedding': face.normed_embedding.tolist(),  # 512-dim vector
                    'age': int(face.age) if hasattr(face, 'age') else None,
                    'gender': 'M' if face.gender == 1 else 'F' if hasattr(face, 'gender') else None,
                    'landmarks': face.kps.tolist() if hasattr(face, 'kps') else None,
                }
                results.append(result)
            
            logger.info(f"Detected {len(results)} face(s) in {image_path}")
            return results
            
        except Exception as e:
            logger.error(f"Error detecting faces: {e}")
            return []
    
    def detect_faces_from_array(self, img_array: np.ndarray) -> List[Dict]:
        """
        Detect faces from numpy array (for video frames)
        
        Args:
            img_array: Image as numpy array (BGR format)
            
        Returns:
            List of face detections
        """
        try:
            faces = self.app.get(img_array)
            
            results = []
            for idx, face in enumerate(faces):
                result = {
                    'face_id': idx,
                    'bbox': face.bbox.tolist(),
                    'confidence': float(face.det_score),
                    'embedding': face.normed_embedding.tolist(),
                    'age': int(face.age) if hasattr(face, 'age') else None,
                    'gender': 'M' if face.gender == 1 else 'F' if hasattr(face, 'gender') else None,
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error detecting faces from array: {e}")
            return []
    
    def extract_embedding(self, image_path: str) -> Optional[List[float]]:
        """
        Extract face embedding from image (expects single face)
        
        Args:
            image_path: Path to image file
            
        Returns:
            512-dim embedding vector or None
        """
        faces = self.detect_faces(image_path)
        if not faces:
            logger.warning(f"No face detected in {image_path}")
            return None
        
        if len(faces) > 1:
            logger.warning(f"Multiple faces detected, using first face")
        
        return faces[0]['embedding']
    
    def compare_faces(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate similarity between two face embeddings using cosine similarity
        
        Args:
            embedding1: First face embedding
            embedding2: Second face embedding
            
        Returns:
            Similarity score (0-1, higher is more similar)
        """
        emb1 = np.array(embedding1)
        emb2 = np.array(embedding2)
        
        # Cosine similarity
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        return float(similarity)
    
    def match_face(self, query_embedding: List[float], known_embeddings: List[Tuple[str, List[float]]]) -> Optional[Dict]:
        """
        Match a face against a database of known faces
        
        Args:
            query_embedding: Embedding of face to identify
            known_embeddings: List of (identity_id, embedding) tuples
            
        Returns:
            Best match with identity_id and similarity score, or None if no match
        """
        if not known_embeddings:
            return None
        
        best_match = None
        best_similarity = 0.0
        
        for identity_id, embedding in known_embeddings:
            similarity = self.compare_faces(query_embedding, embedding)
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = {
                    'identity_id': identity_id,
                    'similarity': similarity,
                    'is_match': similarity >= self.similarity_threshold
                }
        
        if best_match and best_match['is_match']:
            logger.info(f"Face matched: {best_match['identity_id']} (similarity: {best_similarity:.3f})")
            return best_match
        
        return None
    
    def verify_face(self, embedding1: List[float], embedding2: List[float]) -> Dict:
        """
        Verify if two face embeddings belong to same person
        
        Args:
            embedding1: First face embedding
            embedding2: Second face embedding
            
        Returns:
            Verification result with similarity and match decision
        """
        similarity = self.compare_faces(embedding1, embedding2)
        
        return {
            'similarity': similarity,
            'is_match': similarity >= self.similarity_threshold,
            'threshold': self.similarity_threshold
        }
    
    def draw_detections(self, image_path: str, output_path: str, detections: List[Dict]):
        """
        Draw bounding boxes on image
        
        Args:
            image_path: Input image path
            output_path: Output image path
            detections: List of face detections
        """
        img = cv2.imread(image_path)
        
        for face in detections:
            bbox = face['bbox']
            x1, y1, x2, y2 = map(int, bbox)
            
            # Draw rectangle
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Add confidence score
            text = f"{face['confidence']:.2f}"
            cv2.putText(img, text, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        cv2.imwrite(output_path, img)
        logger.info(f"Saved annotated image to {output_path}")


# Global instance
_face_service = None

def get_face_service() -> FaceRecognitionService:
    """Get or create global FaceRecognitionService instance"""
    global _face_service
    if _face_service is None:
        model_name = os.environ.get('INSIGHTFACE_MODEL_NAME', 'buffalo_l')
        threshold = float(os.environ.get('INSIGHTFACE_SIMILARITY_THRESHOLD', '0.4'))
        _face_service = FaceRecognitionService(model_name=model_name, similarity_threshold=threshold)
    return _face_service
