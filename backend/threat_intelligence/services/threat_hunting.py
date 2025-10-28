"""
Threat Hunting Assistant with LLM-powered natural language queries
"""
import json
from datetime import timedelta
from django.utils import timezone
from django.db.models import Q, Count
import logging

from ..models import Threat, Alert, ThreatHuntingQuery, ThreatIndicator
from access_control.models import AccessLog
from core.models import AuditLog

logger = logging.getLogger(__name__)


class ThreatHuntingAssistant:
    """
    LLM-powered threat hunting assistant for natural language queries
    """
    
    def __init__(self):
        self.supported_queries = [
            'failed_logins',
            'unusual_access',
            'threats_by_location',
            'suspicious_users',
            'recent_incidents',
            'access_patterns'
        ]
    
    def execute_natural_language_query(self, organization_id, query_text, created_by=None):
        """
        Execute a natural language threat hunting query
        
        Args:
            organization_id: Organization ID
            query_text: Natural language query
            created_by: User executing the query
        
        Returns:
            dict: Query results
        """
        try:
            # Parse the query to determine intent
            intent = self._parse_query_intent(query_text)
            
            # Execute the appropriate query
            if intent == 'failed_logins':
                results = self._query_failed_logins(organization_id, query_text)
            elif intent == 'unusual_access':
                results = self._query_unusual_access(organization_id, query_text)
            elif intent == 'threats_by_location':
                results = self._query_threats_by_location(organization_id, query_text)
            elif intent == 'suspicious_users':
                results = self._query_suspicious_users(organization_id, query_text)
            elif intent == 'recent_incidents':
                results = self._query_recent_incidents(organization_id, query_text)
            elif intent == 'access_patterns':
                results = self._query_access_patterns(organization_id, query_text)
            else:
                results = self._execute_generic_search(organization_id, query_text)
            
            # Save query for future reference
            if created_by:
                self._save_hunting_query(
                    organization_id, query_text, intent, results, created_by
                )
            
            return {
                'status': 'success',
                'query': query_text,
                'intent': intent,
                'results': results
            }
        
        except Exception as e:
            logger.error(f"Error executing threat hunting query: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def suggest_hunting_hypotheses(self, organization_id, time_range_days=7):
        """
        Generate threat hunting hypotheses based on recent activity
        
        Args:
            organization_id: Organization ID
            time_range_days: Analysis window
        
        Returns:
            dict: Suggested hypotheses
        """
        try:
            start_date = timezone.now() - timedelta(days=time_range_days)
            
            hypotheses = []
            
            # Check for anomalous access patterns
            anomalous_access = AccessLog.objects.filter(
                organization_id=organization_id,
                timestamp__gte=start_date,
                is_anomaly=True
            ).count()
            
            if anomalous_access > 10:
                hypotheses.append({
                    'hypothesis': 'Are there unauthorized access attempts targeting specific access points?',
                    'suggested_query': 'Show me all failed access attempts in the last 7 days',
                    'rationale': f'Detected {anomalous_access} anomalous access events',
                    'priority': 'high'
                })
            
            # Check for unusual login times
            off_hours_logins = AuditLog.objects.filter(
                organization_id=organization_id,
                action='login',
                timestamp__gte=start_date
            ).filter(
                Q(timestamp__hour__lt=6) | Q(timestamp__hour__gt=22)
            ).count()
            
            if off_hours_logins > 5:
                hypotheses.append({
                    'hypothesis': 'Are there suspicious off-hours login attempts?',
                    'suggested_query': 'Show me all logins between 10 PM and 6 AM',
                    'rationale': f'Detected {off_hours_logins} off-hours login attempts',
                    'priority': 'medium'
                })
            
            # Check for threat concentration
            threats = Threat.objects.filter(
                organization_id=organization_id,
                first_detected_at__gte=start_date
            )
            
            if threats.count() > 20:
                # Check if threats are concentrated
                location_counts = threats.values('location_name').annotate(
                    count=Count('id')
                ).order_by('-count')
                
                if location_counts.exists() and location_counts[0]['count'] > 5:
                    hypotheses.append({
                        'hypothesis': f"Is there a targeted attack on {location_counts[0]['location_name']}?",
                        'suggested_query': f"Show me all threats at {location_counts[0]['location_name']}",
                        'rationale': 'High concentration of threats at specific location',
                        'priority': 'high'
                    })
            
            # Check for repeated failed attempts
            repeated_failures = AccessLog.objects.filter(
                organization_id=organization_id,
                timestamp__gte=start_date,
                is_granted=False
            ).values('user').annotate(
                count=Count('id')
            ).filter(count__gte=10)
            
            if repeated_failures.exists():
                hypotheses.append({
                    'hypothesis': 'Are there potential brute force attacks?',
                    'suggested_query': 'Show me users with more than 10 failed access attempts',
                    'rationale': f'Detected {repeated_failures.count()} users with repeated failures',
                    'priority': 'high'
                })
            
            # Check for new threat indicators
            recent_indicators = ThreatIndicator.objects.filter(
                organization_id=organization_id,
                first_seen__gte=start_date,
                status='active'
            ).count()
            
            if recent_indicators > 5:
                hypotheses.append({
                    'hypothesis': 'Are we seeing new threat indicators in our environment?',
                    'suggested_query': 'Show me all active threat indicators from the last 7 days',
                    'rationale': f'{recent_indicators} new threat indicators detected',
                    'priority': 'medium'
                })
            
            return {
                'status': 'success',
                'period_days': time_range_days,
                'hypotheses_count': len(hypotheses),
                'hypotheses': hypotheses
            }
        
        except Exception as e:
            logger.error(f"Error generating hunting hypotheses: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def generate_threat_report(self, organization_id, report_type='summary', time_range_days=7):
        """
        Generate a comprehensive threat report
        
        Args:
            organization_id: Organization ID
            report_type: Type of report ('summary', 'detailed', 'executive')
            time_range_days: Report period
        
        Returns:
            dict: Threat report
        """
        try:
            start_date = timezone.now() - timedelta(days=time_range_days)
            
            # Gather data
            threats = Threat.objects.filter(
                organization_id=organization_id,
                first_detected_at__gte=start_date
            )
            
            alerts = Alert.objects.filter(
                organization_id=organization_id,
                triggered_at__gte=start_date
            )
            
            access_logs = AccessLog.objects.filter(
                organization_id=organization_id,
                timestamp__gte=start_date
            )
            
            # Calculate metrics
            total_threats = threats.count()
            critical_threats = threats.filter(severity='critical').count()
            resolved_threats = threats.filter(status='resolved').count()
            
            total_alerts = alerts.count()
            high_severity_alerts = alerts.filter(severity__in=['critical', 'high']).count()
            
            failed_access = access_logs.filter(is_granted=False).count()
            anomalous_access = access_logs.filter(is_anomaly=True).count()
            
            # Generate report based on type
            report = {
                'report_type': report_type,
                'period_days': time_range_days,
                'generated_at': timezone.now().isoformat(),
                'summary': {
                    'total_threats': total_threats,
                    'critical_threats': critical_threats,
                    'resolved_threats': resolved_threats,
                    'resolution_rate': round(
                        (resolved_threats / total_threats * 100) if total_threats > 0 else 0, 2
                    ),
                    'total_alerts': total_alerts,
                    'high_severity_alerts': high_severity_alerts,
                    'failed_access_attempts': failed_access,
                    'anomalous_activities': anomalous_access
                }
            }
            
            if report_type in ['detailed', 'executive']:
                # Add threat breakdown
                report['threat_breakdown'] = list(
                    threats.values('threat_type').annotate(count=Count('id'))
                )
                
                # Add top threats
                report['top_threats'] = [
                    {
                        'id': t.id,
                        'title': t.title,
                        'severity': t.severity,
                        'risk_score': t.risk_score,
                        'status': t.status
                    }
                    for t in threats.order_by('-risk_score')[:10]
                ]
                
                # Add trends
                report['trends'] = self._calculate_trends(organization_id, time_range_days)
            
            if report_type == 'executive':
                # Add executive summary
                report['executive_summary'] = self._generate_executive_summary(report)
                
                # Add recommendations
                report['recommendations'] = self._generate_recommendations(
                    threats, alerts, access_logs
                )
            
            return {
                'status': 'success',
                'report': report
            }
        
        except Exception as e:
            logger.error(f"Error generating threat report: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    # Helper methods for query parsing
    def _parse_query_intent(self, query_text):
        """Parse natural language query to determine intent"""
        query_lower = query_text.lower()
        
        if any(word in query_lower for word in ['failed', 'login', 'authentication']):
            return 'failed_logins'
        elif any(word in query_lower for word in ['unusual', 'anomalous', 'strange']):
            return 'unusual_access'
        elif any(word in query_lower for word in ['location', 'place', 'where']):
            return 'threats_by_location'
        elif any(word in query_lower for word in ['suspicious', 'user', 'person']):
            return 'suspicious_users'
        elif any(word in query_lower for word in ['recent', 'latest', 'new', 'incident']):
            return 'recent_incidents'
        elif any(word in query_lower for word in ['pattern', 'behavior', 'activity']):
            return 'access_patterns'
        else:
            return 'generic'
    
    def _query_failed_logins(self, organization_id, query_text):
        """Query for failed login attempts"""
        # Extract time range from query if specified
        days = self._extract_time_range(query_text)
        start_date = timezone.now() - timedelta(days=days)
        
        failed_logins = AuditLog.objects.filter(
            organization_id=organization_id,
            action='login',
            timestamp__gte=start_date
        ).filter(
            changes__contains={'success': False}
        )
        
        # Extract country if mentioned
        country = self._extract_country(query_text)
        if country:
            failed_logins = failed_logins.filter(
                changes__contains={'country': country}
            )
        
        results = []
        for log in failed_logins[:50]:
            results.append({
                'timestamp': log.timestamp.isoformat(),
                'user': log.user.username if log.user else 'Unknown',
                'ip_address': log.ip_address,
                'details': log.changes
            })
        
        return {
            'count': failed_logins.count(),
            'items': results
        }
    
    def _query_unusual_access(self, organization_id, query_text):
        """Query for unusual access patterns"""
        days = self._extract_time_range(query_text)
        start_date = timezone.now() - timedelta(days=days)
        
        unusual_access = AccessLog.objects.filter(
            organization_id=organization_id,
            timestamp__gte=start_date,
            is_anomaly=True
        )
        
        results = []
        for log in unusual_access[:50]:
            results.append({
                'timestamp': log.timestamp.isoformat(),
                'user': log.user.username if log.user else 'Unknown',
                'access_point': log.access_point.name,
                'anomaly_score': log.anomaly_score,
                'granted': log.is_granted
            })
        
        return {
            'count': unusual_access.count(),
            'items': results
        }
    
    def _query_threats_by_location(self, organization_id, query_text):
        """Query threats by location"""
        days = self._extract_time_range(query_text)
        start_date = timezone.now() - timedelta(days=days)
        
        threats = Threat.objects.filter(
            organization_id=organization_id,
            first_detected_at__gte=start_date
        ).exclude(location_name='')
        
        # Group by location
        location_threats = threats.values('location_name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return {
            'count': threats.count(),
            'locations': list(location_threats[:20])
        }
    
    def _query_suspicious_users(self, organization_id, query_text):
        """Query for suspicious users"""
        days = self._extract_time_range(query_text)
        start_date = timezone.now() - timedelta(days=days)
        
        # Find users with multiple alerts or failed access
        from core.models import User
        
        suspicious_users = User.objects.filter(
            organization_id=organization_id,
            is_active=True
        ).annotate(
            alert_count=Count('alerts', filter=Q(alerts__triggered_at__gte=start_date)),
            failed_access=Count('access_logs', filter=Q(
                access_logs__timestamp__gte=start_date,
                access_logs__is_granted=False
            ))
        ).filter(
            Q(alert_count__gte=3) | Q(failed_access__gte=5)
        )
        
        results = []
        for user in suspicious_users[:20]:
            results.append({
                'user_id': user.id,
                'username': user.username,
                'full_name': user.get_full_name(),
                'alert_count': user.alert_count,
                'failed_access_count': user.failed_access
            })
        
        return {
            'count': suspicious_users.count(),
            'users': results
        }
    
    def _query_recent_incidents(self, organization_id, query_text):
        """Query recent incidents/threats"""
        days = self._extract_time_range(query_text)
        start_date = timezone.now() - timedelta(days=days)
        
        threats = Threat.objects.filter(
            organization_id=organization_id,
            first_detected_at__gte=start_date
        ).order_by('-first_detected_at')
        
        results = []
        for threat in threats[:50]:
            results.append({
                'id': threat.id,
                'title': threat.title,
                'threat_type': threat.threat_type,
                'severity': threat.severity,
                'status': threat.status,
                'risk_score': threat.risk_score,
                'detected_at': threat.first_detected_at.isoformat()
            })
        
        return {
            'count': threats.count(),
            'threats': results
        }
    
    def _query_access_patterns(self, organization_id, query_text):
        """Query access patterns"""
        days = self._extract_time_range(query_text)
        start_date = timezone.now() - timedelta(days=days)
        
        access_logs = AccessLog.objects.filter(
            organization_id=organization_id,
            timestamp__gte=start_date
        )
        
        # Aggregate patterns
        hourly_pattern = access_logs.extra(
            {'hour': "EXTRACT(hour FROM timestamp)"}
        ).values('hour').annotate(count=Count('id')).order_by('hour')
        
        daily_pattern = access_logs.extra(
            {'day': "EXTRACT(dow FROM timestamp)"}
        ).values('day').annotate(count=Count('id')).order_by('day')
        
        return {
            'total_access_events': access_logs.count(),
            'hourly_distribution': list(hourly_pattern),
            'daily_distribution': list(daily_pattern)
        }
    
    def _execute_generic_search(self, organization_id, query_text):
        """Execute generic search across multiple entities"""
        return {
            'message': 'Generic search executed',
            'query': query_text,
            'results': []
        }
    
    def _extract_time_range(self, query_text):
        """Extract time range from query text"""
        query_lower = query_text.lower()
        
        if 'today' in query_lower or '24 hours' in query_lower:
            return 1
        elif 'week' in query_lower or '7 days' in query_lower:
            return 7
        elif 'month' in query_lower or '30 days' in query_lower:
            return 30
        else:
            return 7  # Default to 7 days
    
    def _extract_country(self, query_text):
        """Extract country name from query"""
        # Simple country extraction (can be enhanced)
        countries = ['china', 'russia', 'usa', 'uk', 'france', 'germany']
        query_lower = query_text.lower()
        
        for country in countries:
            if country in query_lower:
                return country.upper()
        
        return None
    
    def _save_hunting_query(self, organization_id, query_text, intent, results, created_by):
        """Save threat hunting query for future reference"""
        try:
            from core.models import Organization
            
            ThreatHuntingQuery.objects.create(
                organization_id=organization_id,
                name=query_text[:100],
                description=f"Auto-generated from natural language query",
                query_text=query_text,
                query_type='natural_language',
                created_by=created_by,
                last_result_count=results.get('count', 0),
                last_executed_at=timezone.now(),
                times_executed=1
            )
        except Exception as e:
            logger.error(f"Error saving hunting query: {str(e)}")
    
    def _calculate_trends(self, organization_id, days):
        """Calculate threat trends"""
        # Placeholder for trend calculation
        return {
            'threat_trend': 'increasing',
            'alert_trend': 'stable'
        }
    
    def _generate_executive_summary(self, report):
        """Generate executive summary"""
        summary = report['summary']
        
        text = f"During the past {report['period_days']} days, "
        text += f"{summary['total_threats']} threats were detected, "
        text += f"including {summary['critical_threats']} critical threats. "
        
        if summary['resolution_rate'] > 80:
            text += "The organization has maintained a strong security posture "
            text += f"with a {summary['resolution_rate']}% threat resolution rate."
        else:
            text += f"Threat resolution rate of {summary['resolution_rate']}% "
            text += "indicates room for improvement in incident response."
        
        return text
    
    def _generate_recommendations(self, threats, alerts, access_logs):
        """Generate security recommendations"""
        recommendations = []
        
        critical_threats = threats.filter(severity='critical', status__in=['new', 'investigating'])
        if critical_threats.count() > 0:
            recommendations.append({
                'priority': 'high',
                'recommendation': f'Immediate action required on {critical_threats.count()} critical threats'
            })
        
        failed_rate = access_logs.filter(is_granted=False).count() / access_logs.count() if access_logs.count() > 0 else 0
        if failed_rate > 0.2:
            recommendations.append({
                'priority': 'medium',
                'recommendation': 'High failure rate in access attempts - review access policies'
            })
        
        return recommendations
