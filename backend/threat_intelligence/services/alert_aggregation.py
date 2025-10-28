"""
Intelligent Alert Aggregation Service
De-duplicates similar alerts, correlates related alerts, and reduces alert fatigue
"""
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Q
from difflib import SequenceMatcher
import logging

from ..models import Alert, Threat

logger = logging.getLogger(__name__)


class AlertAggregationService:
    """
    Smart alert aggregation to reduce alert fatigue
    """
    
    def __init__(self, similarity_threshold=0.8):
        """
        Initialize alert aggregation service
        
        Args:
            similarity_threshold: Minimum similarity to consider alerts as duplicates (0-1)
        """
        self.similarity_threshold = similarity_threshold
    
    def deduplicate_alerts(self, organization_id, time_window_minutes=60, max_alerts=100):
        """
        De-duplicate similar alerts within a time window
        
        Args:
            organization_id: Organization ID
            time_window_minutes: Time window for de-duplication
            max_alerts: Maximum number of alerts to process
        
        Returns:
            dict: De-duplication results
        """
        try:
            start_time = timezone.now() - timedelta(minutes=time_window_minutes)
            
            # Get recent unprocessed alerts
            alerts = Alert.objects.filter(
                organization_id=organization_id,
                triggered_at__gte=start_time,
                status='new',
                is_aggregated=False
            ).order_by('-triggered_at')[:max_alerts]
            
            if alerts.count() == 0:
                return {
                    'status': 'success',
                    'message': 'No alerts to deduplicate',
                    'deduplicated_count': 0
                }
            
            # Group similar alerts
            alert_groups = []
            processed_ids = set()
            
            for alert in alerts:
                if alert.id in processed_ids:
                    continue
                
                # Find similar alerts
                similar_alerts = self._find_similar_alerts(
                    alert, alerts, processed_ids
                )
                
                if similar_alerts:
                    alert_groups.append({
                        'primary': alert,
                        'duplicates': similar_alerts
                    })
                    processed_ids.add(alert.id)
                    for sim_alert in similar_alerts:
                        processed_ids.add(sim_alert.id)
            
            # Aggregate similar alerts
            aggregated_count = 0
            for group in alert_groups:
                if len(group['duplicates']) > 0:
                    self._aggregate_alert_group(group['primary'], group['duplicates'])
                    aggregated_count += len(group['duplicates'])
            
            return {
                'status': 'success',
                'alerts_processed': alerts.count(),
                'groups_created': len(alert_groups),
                'alerts_aggregated': aggregated_count,
                'reduction_percentage': round(
                    (aggregated_count / alerts.count()) * 100, 2
                ) if alerts.count() > 0 else 0
            }
        
        except Exception as e:
            logger.error(f"Error de-duplicating alerts: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def correlate_alerts_to_incidents(self, organization_id, time_window_hours=24):
        """
        Correlate related alerts into incidents
        
        Args:
            organization_id: Organization ID
            time_window_hours: Time window for correlation
        
        Returns:
            dict: Correlation results
        """
        try:
            start_time = timezone.now() - timedelta(hours=time_window_hours)
            
            # Get recent alerts
            alerts = Alert.objects.filter(
                organization_id=organization_id,
                triggered_at__gte=start_time,
                status__in=['new', 'acknowledged']
            )
            
            if alerts.count() < 2:
                return {
                    'status': 'success',
                    'message': 'Not enough alerts for correlation',
                    'incidents_created': 0
                }
            
            # Group alerts by correlation factors
            incident_groups = self._correlate_by_factors(alerts)
            
            # Create threats for correlated incidents
            threats_created = []
            for group in incident_groups:
                if len(group['alerts']) >= 3:  # Minimum 3 alerts for incident
                    threat = self._create_incident_from_alerts(group)
                    if threat:
                        threats_created.append(threat)
            
            return {
                'status': 'success',
                'alerts_analyzed': alerts.count(),
                'correlation_groups': len(incident_groups),
                'incidents_created': len(threats_created),
                'incidents': [
                    {
                        'id': t.id,
                        'title': t.title,
                        'severity': t.severity,
                        'alert_count': t.alerts.count()
                    }
                    for t in threats_created
                ]
            }
        
        except Exception as e:
            logger.error(f"Error correlating alerts: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def apply_smart_filtering(self, organization_id, confidence_threshold=0.7):
        """
        Apply intelligent filtering to reduce low-confidence alerts
        
        Args:
            organization_id: Organization ID
            confidence_threshold: Minimum confidence score to keep alert
        
        Returns:
            dict: Filtering results
        """
        try:
            # Get low-confidence alerts
            low_confidence_alerts = Alert.objects.filter(
                organization_id=organization_id,
                status='new',
                confidence_score__lt=confidence_threshold
            )
            
            suppressed_count = 0
            for alert in low_confidence_alerts:
                # Check if it's likely a false positive
                if self._is_likely_false_positive(alert):
                    alert.status = 'false_positive'
                    alert.save()
                    suppressed_count += 1
                else:
                    # Lower severity instead of suppressing
                    if alert.severity in ['critical', 'high']:
                        alert.severity = 'medium'
                        alert.save()
            
            return {
                'status': 'success',
                'alerts_reviewed': low_confidence_alerts.count(),
                'alerts_suppressed': suppressed_count,
                'alerts_downgraded': low_confidence_alerts.count() - suppressed_count
            }
        
        except Exception as e:
            logger.error(f"Error applying smart filtering: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def route_alerts_by_priority(self, organization_id):
        """
        Route alerts to appropriate teams based on priority and type
        
        Args:
            organization_id: Organization ID
        
        Returns:
            dict: Routing results
        """
        try:
            from core.models import User
            
            # Get unassigned high-priority alerts
            high_priority_alerts = Alert.objects.filter(
                organization_id=organization_id,
                status='new',
                severity__in=['critical', 'high'],
                assigned_to__isnull=True
            )
            
            # Get available security officers
            security_officers = User.objects.filter(
                organization_id=organization_id,
                role__name='sec_officer',
                is_active=True
            )
            
            if security_officers.count() == 0:
                return {
                    'status': 'warning',
                    'message': 'No security officers available for assignment'
                }
            
            # Round-robin assignment
            assigned_count = 0
            officer_index = 0
            
            for alert in high_priority_alerts:
                officer = security_officers[officer_index % security_officers.count()]
                alert.assigned_to = officer
                alert.status = 'acknowledged'
                alert.save()
                
                assigned_count += 1
                officer_index += 1
            
            return {
                'status': 'success',
                'alerts_routed': assigned_count,
                'security_officers': security_officers.count(),
                'routing_method': 'round_robin'
            }
        
        except Exception as e:
            logger.error(f"Error routing alerts: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def generate_alert_summary(self, organization_id, time_range_hours=24):
        """
        Generate a summary of alerts for reporting
        
        Args:
            organization_id: Organization ID
            time_range_hours: Time range for summary
        
        Returns:
            dict: Alert summary
        """
        try:
            start_time = timezone.now() - timedelta(hours=time_range_hours)
            
            alerts = Alert.objects.filter(
                organization_id=organization_id,
                triggered_at__gte=start_time
            )
            
            # Count by severity
            severity_counts = alerts.values('severity').annotate(
                count=Count('id')
            )
            
            # Count by type
            type_counts = alerts.values('alert_type').annotate(
                count=Count('id')
            )
            
            # Count by status
            status_counts = alerts.values('status').annotate(
                count=Count('id')
            )
            
            # Calculate metrics
            total_alerts = alerts.count()
            resolved_alerts = alerts.filter(status='resolved').count()
            false_positives = alerts.filter(status='false_positive').count()
            
            resolution_rate = (resolved_alerts / total_alerts * 100) if total_alerts > 0 else 0
            false_positive_rate = (false_positives / total_alerts * 100) if total_alerts > 0 else 0
            
            return {
                'status': 'success',
                'period_hours': time_range_hours,
                'total_alerts': total_alerts,
                'by_severity': {item['severity']: item['count'] for item in severity_counts},
                'by_type': {item['alert_type']: item['count'] for item in type_counts},
                'by_status': {item['status']: item['count'] for item in status_counts},
                'metrics': {
                    'resolution_rate': round(resolution_rate, 2),
                    'false_positive_rate': round(false_positive_rate, 2),
                    'pending_alerts': alerts.filter(status='new').count()
                }
            }
        
        except Exception as e:
            logger.error(f"Error generating alert summary: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    # Helper methods
    def _find_similar_alerts(self, alert, all_alerts, processed_ids):
        """Find alerts similar to the given alert"""
        similar = []
        
        for other_alert in all_alerts:
            if other_alert.id in processed_ids or other_alert.id == alert.id:
                continue
            
            # Check similarity
            if self._calculate_alert_similarity(alert, other_alert) >= self.similarity_threshold:
                similar.append(other_alert)
        
        return similar
    
    def _calculate_alert_similarity(self, alert1, alert2):
        """Calculate similarity score between two alerts"""
        score = 0.0
        
        # Same alert type (40% weight)
        if alert1.alert_type == alert2.alert_type:
            score += 0.4
        
        # Same severity (20% weight)
        if alert1.severity == alert2.severity:
            score += 0.2
        
        # Same user (20% weight)
        if alert1.user_id and alert1.user_id == alert2.user_id:
            score += 0.2
        
        # Same access point (10% weight)
        if alert1.access_point_id and alert1.access_point_id == alert2.access_point_id:
            score += 0.1
        
        # Similar title (10% weight)
        title_similarity = SequenceMatcher(None, alert1.title, alert2.title).ratio()
        score += title_similarity * 0.1
        
        return score
    
    def _aggregate_alert_group(self, primary_alert, duplicate_alerts):
        """Aggregate duplicate alerts into a primary alert"""
        try:
            primary_alert.is_aggregated = True
            primary_alert.aggregation_count = len(duplicate_alerts) + 1
            primary_alert.save()
            
            # Mark duplicates as aggregated
            for dup_alert in duplicate_alerts:
                dup_alert.is_aggregated = True
                dup_alert.parent_alert = primary_alert
                dup_alert.status = 'suppressed'
                dup_alert.save()
        
        except Exception as e:
            logger.error(f"Error aggregating alert group: {str(e)}")
    
    def _correlate_by_factors(self, alerts):
        """Correlate alerts by common factors"""
        groups = []
        processed_ids = set()
        
        for alert in alerts:
            if alert.id in processed_ids:
                continue
            
            # Find related alerts
            related = [alert]
            
            for other_alert in alerts:
                if other_alert.id in processed_ids or other_alert.id == alert.id:
                    continue
                
                # Check correlation factors
                if self._are_alerts_correlated(alert, other_alert):
                    related.append(other_alert)
                    processed_ids.add(other_alert.id)
            
            if len(related) >= 2:
                groups.append({
                    'alerts': related,
                    'correlation_factor': self._determine_correlation_factor(related)
                })
            
            processed_ids.add(alert.id)
        
        return groups
    
    def _are_alerts_correlated(self, alert1, alert2):
        """Check if two alerts are correlated"""
        # Same user within time window
        if alert1.user_id and alert1.user_id == alert2.user_id:
            time_diff = abs((alert1.triggered_at - alert2.triggered_at).total_seconds())
            if time_diff <= 3600:  # Within 1 hour
                return True
        
        # Same access point
        if alert1.access_point_id and alert1.access_point_id == alert2.access_point_id:
            return True
        
        # Related threat types
        related_types = {
            'unauthorized_access': ['failed_login', 'suspicious_activity'],
            'anomaly_detected': ['suspicious_activity', 'pattern_match']
        }
        
        if alert1.alert_type in related_types:
            if alert2.alert_type in related_types[alert1.alert_type]:
                return True
        
        return False
    
    def _determine_correlation_factor(self, alerts):
        """Determine what correlates the alerts"""
        # Check user correlation
        user_ids = [a.user_id for a in alerts if a.user_id]
        if len(set(user_ids)) == 1 and user_ids:
            return 'same_user'
        
        # Check access point correlation
        ap_ids = [a.access_point_id for a in alerts if a.access_point_id]
        if len(set(ap_ids)) == 1 and ap_ids:
            return 'same_access_point'
        
        # Check time-based correlation
        return 'temporal'
    
    def _create_incident_from_alerts(self, group):
        """Create a threat incident from correlated alerts"""
        try:
            alerts = group['alerts']
            primary_alert = alerts[0]
            
            # Determine incident severity
            severities = [a.severity for a in alerts]
            if 'critical' in severities:
                severity = 'critical'
            elif 'high' in severities:
                severity = 'high'
            else:
                severity = 'medium'
            
            # Create threat
            threat = Threat.objects.create(
                organization=primary_alert.organization,
                title=f"Correlated Incident: {primary_alert.alert_type}",
                description=f"Incident created from {len(alerts)} correlated alerts",
                threat_type='suspicious_activity',
                severity=severity,
                source='alert_correlation',
                confidence_score=0.8
            )
            
            # Link alerts to threat
            for alert in alerts:
                alert.threat = threat
                alert.status = 'investigating'
                alert.save()
            
            return threat
        
        except Exception as e:
            logger.error(f"Error creating incident from alerts: {str(e)}")
            return None
    
    def _is_likely_false_positive(self, alert):
        """Determine if an alert is likely a false positive"""
        # Check historical pattern
        similar_alerts = Alert.objects.filter(
            organization=alert.organization,
            alert_type=alert.alert_type,
            user=alert.user
        ).order_by('-triggered_at')[:10]
        
        false_positive_count = similar_alerts.filter(status='false_positive').count()
        
        # If >60% of similar alerts were false positives
        if similar_alerts.count() > 0:
            fp_rate = false_positive_count / similar_alerts.count()
            if fp_rate > 0.6:
                return True
        
        # Low confidence and low severity
        if alert.confidence_score < 0.5 and alert.severity in ['low', 'info']:
            return True
        
        return False
