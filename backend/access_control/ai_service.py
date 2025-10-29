"""
AI-Powered Access Control Analytics and Anomaly Detection
"""
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Avg, Q
from collections import Counter
import json

logger = logging.getLogger(__name__)


class AccessAnomalyDetector:
    """
    AI-powered anomaly detection for access control patterns
    """
    
    def __init__(self, organization):
        self.organization = organization
    
    def analyze_user_access(self, user, access_log):
        """
        Analyze a single access event and detect anomalies
        Returns: (is_anomaly, anomaly_type, severity, confidence, description)
        """
        anomalies = []
        
        # Check unusual time access
        time_anomaly = self._check_unusual_time(user, access_log)
        if time_anomaly:
            anomalies.append(time_anomaly)
        
        # Check unusual location
        location_anomaly = self._check_unusual_location(user, access_log)
        if location_anomaly:
            anomalies.append(location_anomaly)
        
        # Check rapid sequential access
        rapid_anomaly = self._check_rapid_sequence(user, access_log)
        if rapid_anomaly:
            anomalies.append(rapid_anomaly)
        
        # Check simultaneous access
        simultaneous_anomaly = self._check_simultaneous_access(user, access_log)
        if simultaneous_anomaly:
            anomalies.append(simultaneous_anomaly)
        
        # Check pattern break
        pattern_anomaly = self._check_pattern_break(user, access_log)
        if pattern_anomaly:
            anomalies.append(pattern_anomaly)
        
        # Return highest severity anomaly
        if anomalies:
            anomalies.sort(key=lambda x: x['confidence'], reverse=True)
            return anomalies[0]
        
        return None
    
    def _check_unusual_time(self, user, access_log):
        """Check if access time is unusual for this user"""
        from .models import AccessLog
        
        # Get user's historical access times
        thirty_days_ago = timezone.now() - timedelta(days=30)
        historical_logs = AccessLog.objects.filter(
            user=user,
            organization=self.organization,
            timestamp__gte=thirty_days_ago,
            is_granted=True
        ).exclude(id=access_log.id)
        
        if historical_logs.count() < 5:
            return None  # Not enough data
        
        # Get hour distribution
        access_hour = access_log.timestamp.hour
        hour_counts = Counter([log.timestamp.hour for log in historical_logs])
        total_accesses = sum(hour_counts.values())
        
        # Calculate probability of this hour
        hour_probability = hour_counts.get(access_hour, 0) / total_accesses
        
        # If this hour is rare (< 5% of accesses), flag it
        if hour_probability < 0.05:
            confidence = 1 - hour_probability
            severity = 'high' if hour_probability < 0.01 else 'medium'
            
            return {
                'type': 'unusual_time',
                'severity': severity,
                'confidence': min(confidence, 1.0),
                'description': f"Access at {access_log.timestamp.strftime('%H:%M')} is unusual. User typically accesses at different times.",
                'baseline': {
                    'common_hours': [hour for hour, count in hour_counts.most_common(3)],
                    'total_samples': total_accesses
                },
                'detected': {
                    'hour': access_hour,
                    'probability': hour_probability
                }
            }
        
        return None
    
    def _check_unusual_location(self, user, access_log):
        """Check if access location is unusual for this user"""
        from .models import AccessLog
        
        thirty_days_ago = timezone.now() - timedelta(days=30)
        historical_logs = AccessLog.objects.filter(
            user=user,
            organization=self.organization,
            timestamp__gte=thirty_days_ago,
            is_granted=True
        ).exclude(id=access_log.id)
        
        if historical_logs.count() < 5:
            return None
        
        # Get location distribution
        location_counts = Counter([log.access_point_id for log in historical_logs])
        total_accesses = sum(location_counts.values())
        
        current_location = access_log.access_point_id
        location_probability = location_counts.get(current_location, 0) / total_accesses
        
        # If this location is very rare (< 2% of accesses), flag it
        if location_probability < 0.02:
            confidence = 1 - location_probability
            severity = 'high' if location_probability == 0 else 'medium'
            
            return {
                'type': 'unusual_location',
                'severity': severity,
                'confidence': min(confidence, 1.0),
                'description': f"Access to {access_log.access_point.name} is unusual. User rarely visits this location.",
                'baseline': {
                    'common_locations': [loc for loc, count in location_counts.most_common(3)],
                    'total_samples': total_accesses
                },
                'detected': {
                    'location_id': current_location,
                    'probability': location_probability
                }
            }
        
        return None
    
    def _check_rapid_sequence(self, user, access_log):
        """Check for rapid sequential accesses"""
        from .models import AccessLog
        
        # Check for accesses within last 5 minutes
        five_minutes_ago = access_log.timestamp - timedelta(minutes=5)
        recent_accesses = AccessLog.objects.filter(
            user=user,
            organization=self.organization,
            timestamp__gte=five_minutes_ago,
            timestamp__lt=access_log.timestamp,
            is_granted=True
        ).count()
        
        if recent_accesses >= 3:
            return {
                'type': 'rapid_sequence',
                'severity': 'medium',
                'confidence': min(recent_accesses / 5.0, 1.0),
                'description': f"User accessed {recent_accesses + 1} points in 5 minutes. Possible badge sharing or security breach.",
                'baseline': {'normal_interval': '> 5 minutes'},
                'detected': {'accesses_in_5min': recent_accesses + 1}
            }
        
        return None
    
    def _check_simultaneous_access(self, user, access_log):
        """Check for physically impossible simultaneous access"""
        from .models import AccessLog
        
        # Check for accesses within last 2 minutes at different locations
        two_minutes_ago = access_log.timestamp - timedelta(minutes=2)
        recent_different_location = AccessLog.objects.filter(
            user=user,
            organization=self.organization,
            timestamp__gte=two_minutes_ago,
            timestamp__lt=access_log.timestamp,
            is_granted=True
        ).exclude(access_point=access_log.access_point).first()
        
        if recent_different_location:
            return {
                'type': 'simultaneous',
                'severity': 'critical',
                'confidence': 0.95,
                'description': f"User accessed different locations within 2 minutes. Possible badge sharing or cloning.",
                'baseline': {'normal_interval': '> 2 minutes'},
                'detected': {
                    'location_1': recent_different_location.access_point.name,
                    'location_2': access_log.access_point.name,
                    'time_diff_seconds': (access_log.timestamp - recent_different_location.timestamp).seconds
                }
            }
        
        return None
    
    def _check_pattern_break(self, user, access_log):
        """Check for significant breaks from normal patterns"""
        from .models import AccessLog
        
        # Get day of week pattern
        thirty_days_ago = timezone.now() - timedelta(days=30)
        historical_logs = AccessLog.objects.filter(
            user=user,
            organization=self.organization,
            timestamp__gte=thirty_days_ago,
            is_granted=True
        ).exclude(id=access_log.id)
        
        if historical_logs.count() < 10:
            return None
        
        # Get day of week distribution
        day_counts = Counter([log.timestamp.weekday() for log in historical_logs])
        total_days = sum(day_counts.values())
        
        current_day = access_log.timestamp.weekday()
        day_probability = day_counts.get(current_day, 0) / total_days
        
        # Weekend access when user never works weekends
        if current_day in [5, 6] and day_probability < 0.05:
            return {
                'type': 'pattern_break',
                'severity': 'medium',
                'confidence': 0.7,
                'description': f"Weekend access is unusual. User rarely works on weekends.",
                'baseline': {
                    'typical_days': [day for day, count in day_counts.most_common(3)]
                },
                'detected': {'day': current_day}
            }
        
        return None
    
    def get_user_behavior_profile(self, user):
        """Generate a behavioral profile for a user"""
        from .models import AccessLog
        
        thirty_days_ago = timezone.now() - timedelta(days=30)
        logs = AccessLog.objects.filter(
            user=user,
            organization=self.organization,
            timestamp__gte=thirty_days_ago,
            is_granted=True
        )
        
        if logs.count() < 5:
            return None
        
        # Analyze patterns
        hour_distribution = Counter([log.timestamp.hour for log in logs])
        location_distribution = Counter([log.access_point.name for log in logs])
        day_distribution = Counter([log.timestamp.weekday() for log in logs])
        
        return {
            'user_id': user.id,
            'username': user.username,
            'sample_size': logs.count(),
            'date_range': {
                'from': thirty_days_ago.isoformat(),
                'to': timezone.now().isoformat()
            },
            'common_hours': [hour for hour, _ in hour_distribution.most_common(5)],
            'common_locations': [loc for loc, _ in location_distribution.most_common(5)],
            'common_days': [day for day, _ in day_distribution.most_common()],
            'avg_daily_accesses': logs.count() / 30,
            'weekend_access_rate': sum(1 for log in logs if log.timestamp.weekday() in [5, 6]) / logs.count()
        }


class AccessPredictor:
    """
    Predict access patterns and suggest improvements
    """
    
    def __init__(self, organization):
        self.organization = organization
    
    def predict_busy_hours(self):
        """Predict busy hours for access points"""
        from .models import AccessLog
        
        seven_days_ago = timezone.now() - timedelta(days=7)
        logs = AccessLog.objects.filter(
            organization=self.organization,
            timestamp__gte=seven_days_ago,
            is_granted=True
        )
        
        hour_counts = Counter([log.timestamp.hour for log in logs])
        total = sum(hour_counts.values())
        
        predictions = []
        for hour, count in hour_counts.most_common():
            percentage = (count / total) * 100
            if percentage > 5:  # Only show significant hours
                predictions.append({
                    'hour': hour,
                    'time_range': f"{hour:02d}:00 - {hour:02d}:59",
                    'access_count': count,
                    'percentage': round(percentage, 1),
                    'load_level': 'high' if percentage > 15 else 'medium' if percentage > 8 else 'normal'
                })
        
        return predictions
    
    def suggest_access_optimizations(self):
        """Suggest improvements for access control"""
        from .models import AccessLog, AccessPoint
        
        suggestions = []
        
        # Find bottleneck access points
        seven_days_ago = timezone.now() - timedelta(days=7)
        busy_points = AccessLog.objects.filter(
            organization=self.organization,
            timestamp__gte=seven_days_ago
        ).values('access_point__name').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        for point in busy_points:
            if point['count'] > 100:  # Arbitrary threshold
                suggestions.append({
                    'type': 'high_traffic',
                    'priority': 'medium',
                    'access_point': point['access_point__name'],
                    'access_count': point['count'],
                    'suggestion': f"Consider adding an additional access point or implementing scheduled access to reduce congestion."
                })
        
        # Find denied access patterns
        denied_logs = AccessLog.objects.filter(
            organization=self.organization,
            timestamp__gte=seven_days_ago,
            is_granted=False
        )
        
        if denied_logs.count() > 50:
            common_reasons = denied_logs.values('denial_reason').annotate(
                count=Count('id')
            ).order_by('-count')
            
            for reason in common_reasons:
                suggestions.append({
                    'type': 'access_denial',
                    'priority': 'high',
                    'denial_reason': reason['denial_reason'],
                    'count': reason['count'],
                    'suggestion': f"Review and adjust access permissions to reduce {reason['denial_reason']} denials."
                })
        
        return suggestions
