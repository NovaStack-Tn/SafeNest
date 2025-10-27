"""
Tools/functions that LLM assistants can call.
"""
import logging
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


class SafeNestTools:
    """Collection of tools that LLM can use."""
    
    def __init__(self, organization_id, user_id):
        self.organization_id = organization_id
        self.user_id = user_id
    
    def search_logs(self, query: str, time_range: str = '24h', event_type: str = 'all') -> dict:
        """Search login events, alerts, and incidents."""
        from security.models import LoginEvent, Alert
        from incidents.models import Incident
        
        # Parse time range
        time_map = {'1h': 1/24, '24h': 1, '7d': 7, '30d': 30}
        days = time_map.get(time_range, 1)
        since = timezone.now() - timedelta(days=days)
        
        results = {
            'time_range': time_range,
            'query': query,
            'login_events': [],
            'alerts': [],
            'incidents': []
        }
        
        try:
            # Search login events
            if event_type in ['login', 'all']:
                events = LoginEvent.objects.filter(
                    user__organization_id=self.organization_id,
                    timestamp__gte=since
                ).filter(
                    username__icontains=query
                ) | LoginEvent.objects.filter(
                    user__organization_id=self.organization_id,
                    timestamp__gte=since,
                    country_name__icontains=query
                )
                
                results['login_events'] = [
                    {
                        'id': e.id,
                        'username': e.username,
                        'ip': e.ip_address,
                        'country': e.country_name,
                        'success': e.success,
                        'is_anomaly': e.is_anomaly,
                        'timestamp': e.timestamp.isoformat()
                    }
                    for e in events[:10]
                ]
            
            # Search alerts
            if event_type in ['alert', 'all']:
                alerts = Alert.objects.filter(
                    organization_id=self.organization_id,
                    created_at__gte=since,
                    title__icontains=query
                ) | Alert.objects.filter(
                    organization_id=self.organization_id,
                    created_at__gte=since,
                    message__icontains=query
                )
                
                results['alerts'] = [
                    {
                        'id': a.id,
                        'title': a.title,
                        'severity': a.severity,
                        'status': a.status,
                        'created_at': a.created_at.isoformat()
                    }
                    for a in alerts[:10]
                ]
            
            # Search incidents
            if event_type in ['incident', 'all']:
                incidents = Incident.objects.filter(
                    organization_id=self.organization_id,
                    opened_at__gte=since,
                    title__icontains=query
                ) | Incident.objects.filter(
                    organization_id=self.organization_id,
                    opened_at__gte=since,
                    description__icontains=query
                )
                
                results['incidents'] = [
                    {
                        'id': i.id,
                        'title': i.title,
                        'type': i.incident_type,
                        'severity': i.severity,
                        'status': i.status,
                        'opened_at': i.opened_at.isoformat()
                    }
                    for i in incidents[:10]
                ]
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching logs: {e}")
            return {'error': str(e)}
    
    def create_incident(self, title: str, severity: str, description: str = '', incident_type: str = 'other') -> dict:
        """Create a new incident."""
        from incidents.models import Incident, IncidentEvent
        
        try:
            user = User.objects.get(id=self.user_id)
            
            incident = Incident.objects.create(
                organization_id=self.organization_id,
                title=title,
                description=description or f"Created by AI Assistant",
                incident_type=incident_type,
                severity=severity,
                created_by=user
            )
            
            # Create initial event
            IncidentEvent.objects.create(
                incident=incident,
                action='created',
                description=f"Incident created by AI Assistant",
                actor=user
            )
            
            return {
                'success': True,
                'incident_id': incident.id,
                'title': incident.title,
                'severity': incident.severity,
                'message': f"Incident #{incident.id} created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating incident: {e}")
            return {'error': str(e)}
    
    def get_incident(self, incident_id: int) -> dict:
        """Get incident details."""
        from incidents.models import Incident
        
        try:
            incident = Incident.objects.get(
                id=incident_id,
                organization_id=self.organization_id
            )
            
            return {
                'id': incident.id,
                'title': incident.title,
                'description': incident.description,
                'type': incident.incident_type,
                'severity': incident.severity,
                'status': incident.status,
                'assignee': incident.assignee.get_full_name() if incident.assignee else None,
                'opened_at': incident.opened_at.isoformat(),
                'event_count': incident.events.count(),
                'evidence_count': incident.evidence.count()
            }
            
        except Incident.DoesNotExist:
            return {'error': 'Incident not found'}
        except Exception as e:
            logger.error(f"Error getting incident: {e}")
            return {'error': str(e)}
    
    def who_is(self, label: str) -> dict:
        """Look up face identity."""
        from faces.models import FaceIdentity
        
        try:
            identities = FaceIdentity.objects.filter(
                organization_id=self.organization_id,
                person_label__icontains=label
            )[:5]
            
            if not identities:
                return {'error': 'No identities found'}
            
            return {
                'results': [
                    {
                        'id': i.id,
                        'label': i.person_label,
                        'meta': i.person_meta,
                        'status': i.enrollment_status,
                        'detection_count': i.detections.count()
                    }
                    for i in identities
                ]
            }
            
        except Exception as e:
            logger.error(f"Error looking up identity: {e}")
            return {'error': str(e)}
    
    def show_camera(self, camera_id: int) -> dict:
        """Get recent detections from camera."""
        from faces.models import Camera, FaceDetection
        
        try:
            camera = Camera.objects.get(
                id=camera_id,
                organization_id=self.organization_id
            )
            
            recent_detections = camera.detections.all()[:10]
            
            return {
                'camera_id': camera.id,
                'camera_name': camera.name,
                'location': camera.location,
                'active': camera.active,
                'detections': [
                    {
                        'id': d.id,
                        'identity': d.identity.person_label if d.identity else 'Unknown',
                        'is_match': d.is_match,
                        'similarity': d.similarity,
                        'timestamp': d.timestamp.isoformat()
                    }
                    for d in recent_detections
                ]
            }
            
        except Camera.DoesNotExist:
            return {'error': 'Camera not found'}
        except Exception as e:
            logger.error(f"Error getting camera detections: {e}")
            return {'error': str(e)}
