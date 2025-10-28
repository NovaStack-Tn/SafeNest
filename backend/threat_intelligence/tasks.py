"""
Celery Tasks for Threat Intelligence Background Processing
Automated threat analysis, risk scoring, and alert management
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

from .services import (
    AnomalyDetectionService,
    ThreatScoringService,
    PredictiveThreatAnalytics,
    AlertAggregationService,
    ThreatHuntingAssistant
)
from .models import Threat, Alert, ThreatFeed, RiskAssessment
from core.models import Organization, User
from access_control.models import AccessPoint

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def detect_anomalies_periodic(self, organization_id=None):
    """
    Periodic task to detect anomalies across the organization
    Runs every hour by default
    """
    try:
        logger.info("Starting periodic anomaly detection")
        
        if organization_id:
            organizations = [Organization.objects.get(id=organization_id)]
        else:
            organizations = Organization.objects.filter(is_active=True)
        
        service = AnomalyDetectionService()
        results = []
        
        for org in organizations:
            # Detect user behavior anomalies
            active_users = User.objects.filter(
                organization=org,
                is_active=True
            )
            
            for user in active_users[:50]:  # Limit to 50 users per run
                try:
                    result = service.detect_user_behavior_anomalies(
                        user_id=user.id,
                        time_range_days=7
                    )
                    if result['status'] == 'success' and result['anomalies_detected'] > 0:
                        results.append({
                            'organization': org.name,
                            'user': user.username,
                            'anomalies': result['anomalies_detected']
                        })
                except Exception as e:
                    logger.error(f"Error detecting anomalies for user {user.id}: {str(e)}")
            
            # Detect login pattern anomalies
            try:
                login_result = service.detect_login_pattern_anomalies(
                    organization_id=org.id,
                    time_range_days=7
                )
                if login_result['status'] == 'success':
                    results.append({
                        'organization': org.name,
                        'type': 'login_patterns',
                        'anomalies': login_result.get('total_anomalies', 0)
                    })
            except Exception as e:
                logger.error(f"Error detecting login anomalies for org {org.id}: {str(e)}")
        
        logger.info(f"Anomaly detection completed. Found {len(results)} anomalies")
        return {
            'status': 'success',
            'organizations_processed': len(organizations),
            'results': results
        }
    
    except Exception as exc:
        logger.error(f"Error in periodic anomaly detection: {str(exc)}")
        raise self.retry(exc=exc, countdown=300)  # Retry after 5 minutes


@shared_task(bind=True, max_retries=3)
def update_risk_scores_periodic(self, organization_id=None):
    """
    Periodic task to update risk scores for users and access points
    Runs every 6 hours by default
    """
    try:
        logger.info("Starting periodic risk score updates")
        
        if organization_id:
            organizations = [Organization.objects.get(id=organization_id)]
        else:
            organizations = Organization.objects.filter(is_active=True)
        
        service = ThreatScoringService()
        total_updated = 0
        
        for org in organizations:
            try:
                result = service.update_dynamic_threat_levels(
                    organization_id=org.id
                )
                
                if result['status'] == 'success':
                    total_updated += len(result['high_risk_users'])
                    total_updated += len(result['high_risk_access_points'])
                    
                    logger.info(
                        f"Updated risk scores for org {org.name}: "
                        f"{len(result['high_risk_users'])} users, "
                        f"{len(result['high_risk_access_points'])} access points"
                    )
            except Exception as e:
                logger.error(f"Error updating risk scores for org {org.id}: {str(e)}")
        
        return {
            'status': 'success',
            'organizations_processed': len(organizations),
            'entities_updated': total_updated
        }
    
    except Exception as exc:
        logger.error(f"Error in periodic risk score update: {str(exc)}")
        raise self.retry(exc=exc, countdown=600)  # Retry after 10 minutes


@shared_task(bind=True, max_retries=3)
def aggregate_alerts_periodic(self, organization_id=None):
    """
    Periodic task to aggregate and correlate alerts
    Runs every 30 minutes by default
    """
    try:
        logger.info("Starting periodic alert aggregation")
        
        if organization_id:
            organizations = [Organization.objects.get(id=organization_id)]
        else:
            organizations = Organization.objects.filter(is_active=True)
        
        service = AlertAggregationService()
        results = []
        
        for org in organizations:
            try:
                # De-duplicate alerts
                dedup_result = service.deduplicate_alerts(
                    organization_id=org.id,
                    time_window_minutes=60,
                    max_alerts=100
                )
                
                # Correlate alerts to incidents
                corr_result = service.correlate_alerts_to_incidents(
                    organization_id=org.id,
                    time_window_hours=24
                )
                
                # Apply smart filtering
                filter_result = service.apply_smart_filtering(
                    organization_id=org.id,
                    confidence_threshold=0.7
                )
                
                results.append({
                    'organization': org.name,
                    'deduplicated': dedup_result.get('alerts_aggregated', 0),
                    'incidents_created': corr_result.get('incidents_created', 0),
                    'filtered': filter_result.get('alerts_suppressed', 0)
                })
                
                logger.info(f"Alert aggregation for org {org.name}: {results[-1]}")
            
            except Exception as e:
                logger.error(f"Error aggregating alerts for org {org.id}: {str(e)}")
        
        return {
            'status': 'success',
            'organizations_processed': len(organizations),
            'results': results
        }
    
    except Exception as exc:
        logger.error(f"Error in periodic alert aggregation: {str(exc)}")
        raise self.retry(exc=exc, countdown=300)


@shared_task(bind=True, max_retries=3)
def sync_threat_feeds(self, feed_id=None):
    """
    Sync threat intelligence feeds
    Runs based on feed update_frequency
    """
    try:
        logger.info("Starting threat feed synchronization")
        
        if feed_id:
            feeds = [ThreatFeed.objects.get(id=feed_id)]
        else:
            # Get feeds that need syncing
            feeds = ThreatFeed.objects.filter(
                status='active',
                auto_import=True
            )
        
        synced_count = 0
        total_indicators = 0
        
        for feed in feeds:
            try:
                # Check if feed is due for sync
                if feed.last_sync_at:
                    time_since_sync = (timezone.now() - feed.last_sync_at).total_seconds()
                    if time_since_sync < feed.update_frequency:
                        continue  # Not yet time to sync
                
                # Placeholder for actual feed sync logic
                # In production, this would connect to external APIs
                logger.info(f"Syncing feed: {feed.name}")
                
                # Update feed status
                feed.last_sync_at = timezone.now()
                feed.save()
                
                synced_count += 1
                
            except Exception as e:
                logger.error(f"Error syncing feed {feed.id}: {str(e)}")
                feed.status = 'error'
                feed.last_error = str(e)
                feed.save()
        
        return {
            'status': 'success',
            'feeds_synced': synced_count,
            'indicators_imported': total_indicators
        }
    
    except Exception as exc:
        logger.error(f"Error in threat feed sync: {str(exc)}")
        raise self.retry(exc=exc, countdown=600)


@shared_task(bind=True)
def generate_daily_threat_report(self, organization_id):
    """
    Generate daily threat report for an organization
    Scheduled to run once per day
    """
    try:
        logger.info(f"Generating daily threat report for org {organization_id}")
        
        assistant = ThreatHuntingAssistant()
        result = assistant.generate_threat_report(
            organization_id=organization_id,
            report_type='executive',
            time_range_days=1
        )
        
        if result['status'] == 'success':
            # In production, this would email the report or save it
            logger.info(f"Daily report generated for org {organization_id}")
            return result['report']
        else:
            logger.error(f"Failed to generate report: {result.get('message')}")
            return None
    
    except Exception as exc:
        logger.error(f"Error generating daily report: {str(exc)}")
        return None


@shared_task(bind=True)
def forecast_threats_weekly(self, organization_id):
    """
    Generate weekly threat forecast
    Scheduled to run once per week
    """
    try:
        logger.info(f"Generating weekly threat forecast for org {organization_id}")
        
        service = PredictiveThreatAnalytics()
        
        # Forecast threat trends
        forecast_result = service.forecast_threat_trends(
            organization_id=organization_id,
            forecast_days=7,
            historical_days=30
        )
        
        # Identify emerging patterns
        patterns_result = service.identify_emerging_patterns(
            organization_id=organization_id,
            time_range_days=30
        )
        
        # Predict attack vectors
        vectors_result = service.predict_attack_vectors(
            organization_id=organization_id,
            time_range_days=60
        )
        
        return {
            'status': 'success',
            'forecast': forecast_result,
            'emerging_patterns': patterns_result,
            'predicted_vectors': vectors_result
        }
    
    except Exception as exc:
        logger.error(f"Error in weekly threat forecast: {str(exc)}")
        return None


@shared_task(bind=True)
def cleanup_old_threats(self, days_to_keep=90):
    """
    Clean up resolved threats older than specified days
    Runs monthly
    """
    try:
        logger.info(f"Cleaning up threats older than {days_to_keep} days")
        
        cutoff_date = timezone.now() - timedelta(days=days_to_keep)
        
        # Archive or delete old resolved threats
        old_threats = Threat.objects.filter(
            status='resolved',
            resolved_at__lt=cutoff_date
        )
        
        count = old_threats.count()
        # Instead of deleting, we could archive them
        # old_threats.delete()
        
        logger.info(f"Found {count} old threats to archive")
        
        return {
            'status': 'success',
            'threats_archived': count
        }
    
    except Exception as exc:
        logger.error(f"Error in threat cleanup: {str(exc)}")
        return None


@shared_task(bind=True)
def expire_old_indicators(self):
    """
    Expire threat indicators past their expiration date
    Runs daily
    """
    try:
        logger.info("Expiring old threat indicators")
        
        from .models import ThreatIndicator
        
        expired_count = ThreatIndicator.objects.filter(
            status='active',
            expires_at__lt=timezone.now()
        ).update(status='expired')
        
        logger.info(f"Expired {expired_count} threat indicators")
        
        return {
            'status': 'success',
            'indicators_expired': expired_count
        }
    
    except Exception as exc:
        logger.error(f"Error expiring indicators: {str(exc)}")
        return None


@shared_task(bind=True)
def update_watchlist_detections(self, organization_id):
    """
    Check for watchlist detections and trigger alerts
    Runs every 15 minutes
    """
    try:
        logger.info(f"Checking watchlist detections for org {organization_id}")
        
        from .models import Watchlist
        from access_control.models import AccessLog
        
        # Get active watchlist entries
        watchlist_entries = Watchlist.objects.filter(
            organization_id=organization_id,
            status='active'
        )
        
        detections = []
        
        for entry in watchlist_entries:
            # Check recent access logs for watchlist subjects
            if entry.watchlist_type == 'person' and entry.subject_user:
                recent_access = AccessLog.objects.filter(
                    user=entry.subject_user,
                    timestamp__gte=timezone.now() - timedelta(minutes=15)
                ).exists()
                
                if recent_access:
                    # Update detection count
                    entry.times_detected += 1
                    entry.last_detected_at = timezone.now()
                    entry.save()
                    
                    # Create alert if enabled
                    if entry.alert_on_detection:
                        Alert.objects.create(
                            organization_id=organization_id,
                            title=f"Watchlist Detection: {entry.name}",
                            description=f"Watchlist entry '{entry.name}' detected in access logs",
                            alert_type='suspicious_activity',
                            severity='high' if entry.threat_level == 'critical' else 'medium',
                            user=entry.subject_user,
                            detection_method='watchlist_monitoring',
                            confidence_score=0.9
                        )
                    
                    detections.append({
                        'watchlist_id': entry.id,
                        'name': entry.name,
                        'threat_level': entry.threat_level
                    })
        
        logger.info(f"Found {len(detections)} watchlist detections")
        
        return {
            'status': 'success',
            'detections': detections
        }
    
    except Exception as exc:
        logger.error(f"Error checking watchlist detections: {str(exc)}")
        return None


@shared_task(bind=True)
def calculate_organization_threat_score(self, organization_id):
    """
    Calculate overall threat score for organization
    Runs every 12 hours
    """
    try:
        logger.info(f"Calculating organization threat score for org {organization_id}")
        
        org = Organization.objects.get(id=organization_id)
        
        # Get recent threats
        recent_threats = Threat.objects.filter(
            organization=org,
            first_detected_at__gte=timezone.now() - timedelta(days=7)
        )
        
        # Calculate weighted score
        threat_score = 0
        severity_weights = {'critical': 10, 'high': 5, 'medium': 2, 'low': 1}
        
        for threat in recent_threats:
            weight = severity_weights.get(threat.severity, 1)
            threat_score += weight
        
        # Normalize to 0-100
        org_threat_score = min(threat_score, 100)
        
        # Get active alerts count
        active_alerts = Alert.objects.filter(
            organization=org,
            status__in=['new', 'acknowledged']
        ).count()
        
        # Get high-risk assessments count
        high_risk_assessments = RiskAssessment.objects.filter(
            organization=org,
            risk_level__in=['critical', 'severe', 'high'],
            is_active=True
        ).count()
        
        result = {
            'organization_id': organization_id,
            'threat_score': org_threat_score,
            'active_threats': recent_threats.count(),
            'active_alerts': active_alerts,
            'high_risk_assessments': high_risk_assessments,
            'calculated_at': timezone.now().isoformat()
        }
        
        logger.info(f"Organization threat score calculated: {org_threat_score}")
        
        return result
    
    except Exception as exc:
        logger.error(f"Error calculating org threat score: {str(exc)}")
        return None


# Task scheduling configuration (to be added to celerybeat schedule)
"""
CELERY_BEAT_SCHEDULE = {
    'detect-anomalies-hourly': {
        'task': 'threat_intelligence.tasks.detect_anomalies_periodic',
        'schedule': crontab(minute=0),  # Every hour
    },
    'update-risk-scores-6hourly': {
        'task': 'threat_intelligence.tasks.update_risk_scores_periodic',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
    },
    'aggregate-alerts-30min': {
        'task': 'threat_intelligence.tasks.aggregate_alerts_periodic',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
    'sync-threat-feeds-hourly': {
        'task': 'threat_intelligence.tasks.sync_threat_feeds',
        'schedule': crontab(minute=15),  # Every hour at :15
    },
    'expire-indicators-daily': {
        'task': 'threat_intelligence.tasks.expire_old_indicators',
        'schedule': crontab(minute=0, hour=2),  # Daily at 2 AM
    },
    'cleanup-threats-monthly': {
        'task': 'threat_intelligence.tasks.cleanup_old_threats',
        'schedule': crontab(minute=0, hour=3, day_of_month=1),  # Monthly
    },
}
"""
