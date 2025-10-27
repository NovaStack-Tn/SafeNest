"""
Celery tasks for LLM processing.
"""
import logging
from celery import shared_task
from .models import RAGDocument
from .services import LLMService, AnalysisBotService

logger = logging.getLogger(__name__)


@shared_task
def index_security_events_for_rag():
    """Index security events for RAG (nightly task)."""
    from security.models import Alert, LoginEvent
    from incidents.models import Incident
    from faces.models import FaceDetection
    from core.models import Organization
    from datetime import timedelta
    from django.utils import timezone
    
    logger.info("Starting RAG indexing task")
    llm_service = LLMService()
    
    # Index last 24 hours
    since = timezone.now() - timedelta(days=1)
    
    for org in Organization.objects.filter(is_active=True):
        try:
            indexed_count = 0
            
            # Index alerts
            alerts = Alert.objects.filter(
                organization=org,
                created_at__gte=since
            )
            
            for alert in alerts:
                content = f"Alert: {alert.title}\n{alert.message}\nSeverity: {alert.severity}\nStatus: {alert.status}"
                embedding = llm_service.create_embedding(content)
                
                if embedding:
                    RAGDocument.objects.update_or_create(
                        document_type='alert',
                        document_id=str(alert.id),
                        defaults={
                            'organization': org,
                            'content': content,
                            'embedding': embedding,
                            'metadata': {
                                'severity': alert.severity,
                                'created_at': alert.created_at.isoformat()
                            }
                        }
                    )
                    indexed_count += 1
            
            # Index incidents
            incidents = Incident.objects.filter(
                organization=org,
                opened_at__gte=since
            )
            
            for incident in incidents:
                content = f"Incident: {incident.title}\n{incident.description}\nType: {incident.incident_type}\nSeverity: {incident.severity}"
                embedding = llm_service.create_embedding(content)
                
                if embedding:
                    RAGDocument.objects.update_or_create(
                        document_type='incident',
                        document_id=str(incident.id),
                        defaults={
                            'organization': org,
                            'content': content,
                            'embedding': embedding,
                            'metadata': {
                                'severity': incident.severity,
                                'type': incident.incident_type,
                                'opened_at': incident.opened_at.isoformat()
                            }
                        }
                    )
                    indexed_count += 1
            
            logger.info(f"Indexed {indexed_count} documents for {org.name}")
            
        except Exception as e:
            logger.error(f"Error indexing for {org.name}: {e}")
    
    logger.info("RAG indexing task completed")


@shared_task
def generate_weekly_security_analysis():
    """Generate weekly security analysis for all organizations."""
    from core.models import Organization
    
    logger.info("Starting weekly security analysis generation")
    
    for org in Organization.objects.filter(is_active=True):
        try:
            analysis_service = AnalysisBotService(org.id)
            report = analysis_service.generate_weekly_analysis()
            
            # Could save report or send via email
            logger.info(f"Generated analysis for {org.name}: {len(report)} chars")
            
        except Exception as e:
            logger.error(f"Error generating analysis for {org.name}: {e}")
    
    logger.info("Weekly analysis generation completed")
