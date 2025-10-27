"""
Celery tasks for security processing.
"""
import logging
from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import LoginEvent, AnomalyRule, Alert
from .utils import parse_user_agent, get_ip_geolocation, calculate_device_fingerprint, calculate_travel_velocity
from .services import AnomalyDetectionService

User = get_user_model()
logger = logging.getLogger(__name__)


@shared_task
def process_login_event(event_id):
    """Process a login event: enrich data and check for anomalies."""
    try:
        event = LoginEvent.objects.get(id=event_id)
        
        # Parse user agent
        ua_data = parse_user_agent(event.user_agent)
        event.device_type = ua_data.get('device_type', '')
        event.browser = ua_data.get('browser', '')
        event.os = ua_data.get('os', '')
        
        # Get geolocation
        geo_data = get_ip_geolocation(event.ip_address)
        event.country_code = geo_data.get('country_code', '')
        event.country_name = geo_data.get('country_name', '')
        event.city = geo_data.get('city', '')
        event.latitude = geo_data.get('latitude')
        event.longitude = geo_data.get('longitude')
        
        # Calculate device fingerprint
        event.device_fingerprint = calculate_device_fingerprint(
            event.user_agent,
            event.ip_address
        )
        
        event.save()
        
        # Run anomaly detection
        if event.user and event.user.organization:
            detect_anomalies_for_event.delay(event.id)
        
        logger.info(f"Processed login event {event_id}")
        
    except LoginEvent.DoesNotExist:
        logger.error(f"LoginEvent {event_id} not found")
    except Exception as e:
        logger.error(f"Error processing login event {event_id}: {e}")


@shared_task
def detect_anomalies_for_event(event_id):
    """Run anomaly detection on a login event."""
    try:
        event = LoginEvent.objects.get(id=event_id)
        
        if not event.user or not event.user.organization:
            return
        
        org = event.user.organization
        anomaly_service = AnomalyDetectionService()
        
        # Check rule-based anomalies
        active_rules = AnomalyRule.objects.filter(organization=org, active=True)
        
        anomaly_reasons = []
        risk_score = 0.0
        
        for rule in active_rules:
            is_anomaly, score, reason = anomaly_service.check_rule(event, rule)
            if is_anomaly:
                anomaly_reasons.append(reason)
                risk_score = max(risk_score, score)
                
                # Create alert if configured
                if rule.auto_create_incident:
                    Alert.objects.create(
                        organization=org,
                        title=f"Anomaly detected: {rule.name}",
                        message=f"Anomalous login from {event.ip_address} for user {event.user.username}. Reason: {reason}",
                        severity=rule.severity,
                        related_model='LoginEvent',
                        related_id=str(event.id),
                        triggered_by_rule=rule,
                    )
        
        # Update event
        if anomaly_reasons:
            event.is_anomaly = True
            event.anomaly_reasons = anomaly_reasons
            event.risk_score = risk_score
            event.save()
            
            # Broadcast alert via WebSocket
            from .consumers import broadcast_alert
            broadcast_alert(org.id, {
                'type': 'login_anomaly',
                'severity': 'high' if risk_score > 0.7 else 'medium',
                'message': f"Anomalous login detected for {event.user.username}",
                'event_id': event.id,
                'reasons': anomaly_reasons,
            })
        
        logger.info(f"Anomaly detection completed for event {event_id}: {len(anomaly_reasons)} anomalies")
        
    except LoginEvent.DoesNotExist:
        logger.error(f"LoginEvent {event_id} not found")
    except Exception as e:
        logger.error(f"Error detecting anomalies for event {event_id}: {e}")


@shared_task
def train_anomaly_detection_model():
    """Train ML model for anomaly detection (weekly task)."""
    from core.models import Organization
    
    logger.info("Starting anomaly detection model training")
    
    for org in Organization.objects.filter(is_active=True):
        try:
            service = AnomalyDetectionService()
            service.train_isolation_forest(org.id)
            logger.info(f"Trained anomaly model for organization {org.name}")
        except Exception as e:
            logger.error(f"Error training model for {org.name}: {e}")
    
    logger.info("Anomaly detection model training completed")
