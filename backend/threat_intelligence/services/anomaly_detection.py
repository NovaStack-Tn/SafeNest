"""
Anomaly Detection Engine using ML techniques
Detects behavioral anomalies, login pattern anomalies, and network traffic anomalies
"""
import numpy as np
import pandas as pd
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Q
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import logging

from access_control.models import AccessLog
from core.models import AuditLog, User
from ..models import Alert, Threat

logger = logging.getLogger(__name__)


class AnomalyDetectionService:
    """
    ML-based anomaly detection service using Isolation Forest and other algorithms
    """
    
    def __init__(self, contamination=0.1):
        """
        Initialize the anomaly detection service
        
        Args:
            contamination: Expected proportion of outliers (default 0.1 = 10%)
        """
        self.contamination = contamination
        self.scaler = StandardScaler()
    
    def detect_user_behavior_anomalies(self, user_id, time_range_days=30):
        """
        Detect anomalous behavior patterns for a specific user
        
        Args:
            user_id: User ID to analyze
            time_range_days: Number of days to analyze
        
        Returns:
            dict: Anomaly detection results
        """
        try:
            user = User.objects.get(id=user_id)
            start_date = timezone.now() - timedelta(days=time_range_days)
            
            # Get user's access logs
            access_logs = AccessLog.objects.filter(
                user=user,
                timestamp__gte=start_date
            ).order_by('timestamp')
            
            if access_logs.count() < 10:
                return {
                    'status': 'insufficient_data',
                    'message': 'Not enough data for anomaly detection',
                    'anomalies': []
                }
            
            # Extract features
            features = self._extract_access_features(access_logs)
            
            if len(features) == 0:
                return {
                    'status': 'no_features',
                    'message': 'Could not extract features',
                    'anomalies': []
                }
            
            # Train Isolation Forest
            X = features[['hour', 'day_of_week', 'access_count', 'failed_attempts']]
            X_scaled = self.scaler.fit_transform(X)
            
            iso_forest = IsolationForest(
                contamination=self.contamination,
                random_state=42
            )
            predictions = iso_forest.fit_predict(X_scaled)
            anomaly_scores = iso_forest.score_samples(X_scaled)
            
            # Identify anomalies
            anomalies = []
            for idx, (pred, score) in enumerate(zip(predictions, anomaly_scores)):
                if pred == -1:  # Anomaly detected
                    log = access_logs[idx]
                    anomalies.append({
                        'timestamp': log.timestamp,
                        'access_point': log.access_point.name,
                        'anomaly_score': float(abs(score)),
                        'reason': self._determine_anomaly_reason(log, features.iloc[idx]),
                        'confidence': float(min(abs(score) * 100, 100))
                    })
            
            # Create alerts for significant anomalies
            for anomaly in anomalies:
                if anomaly['confidence'] > 70:
                    self._create_anomaly_alert(user, anomaly)
            
            return {
                'status': 'success',
                'user_id': user_id,
                'total_logs_analyzed': access_logs.count(),
                'anomalies_detected': len(anomalies),
                'anomalies': anomalies
            }
        
        except User.DoesNotExist:
            return {'status': 'error', 'message': 'User not found'}
        except Exception as e:
            logger.error(f"Error in user behavior anomaly detection: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def detect_login_pattern_anomalies(self, organization_id, time_range_days=30):
        """
        Detect anomalous login patterns across the organization
        
        Args:
            organization_id: Organization ID
            time_range_days: Number of days to analyze
        
        Returns:
            dict: Anomaly detection results
        """
        try:
            start_date = timezone.now() - timedelta(days=time_range_days)
            
            # Get all login audit logs
            login_logs = AuditLog.objects.filter(
                organization_id=organization_id,
                action='login',
                timestamp__gte=start_date
            ).select_related('user')
            
            if login_logs.count() < 20:
                return {
                    'status': 'insufficient_data',
                    'message': 'Not enough login data',
                    'anomalies': []
                }
            
            # Group by user and extract features
            user_login_patterns = {}
            for log in login_logs:
                if log.user_id not in user_login_patterns:
                    user_login_patterns[log.user_id] = []
                
                user_login_patterns[log.user_id].append({
                    'timestamp': log.timestamp,
                    'hour': log.timestamp.hour,
                    'day_of_week': log.timestamp.weekday(),
                    'ip_address': log.ip_address
                })
            
            # Detect anomalies for each user
            all_anomalies = []
            for user_id, patterns in user_login_patterns.items():
                if len(patterns) < 5:
                    continue
                
                anomalies = self._detect_time_based_anomalies(user_id, patterns)
                all_anomalies.extend(anomalies)
            
            return {
                'status': 'success',
                'organization_id': organization_id,
                'users_analyzed': len(user_login_patterns),
                'total_anomalies': len(all_anomalies),
                'anomalies': all_anomalies
            }
        
        except Exception as e:
            logger.error(f"Error in login pattern anomaly detection: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def detect_network_traffic_anomalies(self, access_point_id, time_range_days=7):
        """
        Detect anomalous access patterns at a specific access point
        
        Args:
            access_point_id: Access point ID to analyze
            time_range_days: Number of days to analyze
        
        Returns:
            dict: Anomaly detection results
        """
        try:
            start_date = timezone.now() - timedelta(days=time_range_days)
            
            # Get access logs for the access point
            access_logs = AccessLog.objects.filter(
                access_point_id=access_point_id,
                timestamp__gte=start_date
            ).order_by('timestamp')
            
            if access_logs.count() < 50:
                return {
                    'status': 'insufficient_data',
                    'message': 'Not enough traffic data',
                    'anomalies': []
                }
            
            # Create time-series features
            df = pd.DataFrame(list(access_logs.values(
                'timestamp', 'is_granted', 'user_id', 'is_anomaly'
            )))
            
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            
            # Resample by hour
            hourly_stats = df.resample('H').agg({
                'is_granted': ['count', 'sum'],
                'user_id': 'nunique'
            })
            
            hourly_stats.columns = ['total_attempts', 'granted', 'unique_users']
            hourly_stats['denied'] = hourly_stats['total_attempts'] - hourly_stats['granted']
            hourly_stats['denial_rate'] = hourly_stats['denied'] / hourly_stats['total_attempts']
            hourly_stats.fillna(0, inplace=True)
            
            # Detect anomalies in traffic patterns
            if len(hourly_stats) > 0:
                X = hourly_stats[['total_attempts', 'unique_users', 'denial_rate']].values
                X_scaled = self.scaler.fit_transform(X)
                
                iso_forest = IsolationForest(contamination=self.contamination, random_state=42)
                predictions = iso_forest.fit_predict(X_scaled)
                
                anomalies = []
                for idx, pred in enumerate(predictions):
                    if pred == -1:
                        timestamp = hourly_stats.index[idx]
                        stats = hourly_stats.iloc[idx]
                        anomalies.append({
                            'timestamp': timestamp.isoformat(),
                            'total_attempts': int(stats['total_attempts']),
                            'unique_users': int(stats['unique_users']),
                            'denial_rate': float(stats['denial_rate']),
                            'reason': self._determine_traffic_anomaly_reason(stats)
                        })
                
                return {
                    'status': 'success',
                    'access_point_id': access_point_id,
                    'time_periods_analyzed': len(hourly_stats),
                    'anomalies_detected': len(anomalies),
                    'anomalies': anomalies
                }
            
            return {
                'status': 'no_data',
                'message': 'No traffic data available',
                'anomalies': []
            }
        
        except Exception as e:
            logger.error(f"Error in network traffic anomaly detection: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def detect_time_series_anomalies(self, organization_id, metric='access_count', time_range_days=30):
        """
        Detect anomalies in time-series data using statistical methods
        
        Args:
            organization_id: Organization ID
            metric: Metric to analyze ('access_count', 'alert_count', 'threat_count')
            time_range_days: Number of days to analyze
        
        Returns:
            dict: Anomaly detection results
        """
        try:
            start_date = timezone.now() - timedelta(days=time_range_days)
            
            # Get time-series data based on metric
            if metric == 'access_count':
                data = AccessLog.objects.filter(
                    organization_id=organization_id,
                    timestamp__gte=start_date
                ).extra({'date': "date(timestamp)"}).values('date').annotate(
                    count=Count('id')
                ).order_by('date')
            elif metric == 'alert_count':
                data = Alert.objects.filter(
                    organization_id=organization_id,
                    triggered_at__gte=start_date
                ).extra({'date': "date(triggered_at)"}).values('date').annotate(
                    count=Count('id')
                ).order_by('date')
            elif metric == 'threat_count':
                data = Threat.objects.filter(
                    organization_id=organization_id,
                    first_detected_at__gte=start_date
                ).extra({'date': "date(first_detected_at)"}).values('date').annotate(
                    count=Count('id')
                ).order_by('date')
            else:
                return {'status': 'error', 'message': 'Invalid metric'}
            
            if len(data) < 7:
                return {
                    'status': 'insufficient_data',
                    'message': 'Not enough time-series data',
                    'anomalies': []
                }
            
            # Convert to pandas DataFrame
            df = pd.DataFrame(list(data))
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            # Calculate moving average and standard deviation
            df['rolling_mean'] = df['count'].rolling(window=7, min_periods=1).mean()
            df['rolling_std'] = df['count'].rolling(window=7, min_periods=1).std()
            
            # Detect anomalies using z-score
            df['z_score'] = (df['count'] - df['rolling_mean']) / (df['rolling_std'] + 1e-6)
            df['is_anomaly'] = np.abs(df['z_score']) > 2.5
            
            anomalies = []
            for idx, row in df[df['is_anomaly']].iterrows():
                anomalies.append({
                    'date': idx.isoformat(),
                    'value': int(row['count']),
                    'expected_range': [
                        float(row['rolling_mean'] - 2 * row['rolling_std']),
                        float(row['rolling_mean'] + 2 * row['rolling_std'])
                    ],
                    'z_score': float(row['z_score']),
                    'severity': 'high' if abs(row['z_score']) > 3 else 'medium'
                })
            
            return {
                'status': 'success',
                'metric': metric,
                'days_analyzed': len(df),
                'anomalies_detected': len(anomalies),
                'anomalies': anomalies
            }
        
        except Exception as e:
            logger.error(f"Error in time-series anomaly detection: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    # Helper methods
    def _extract_access_features(self, access_logs):
        """Extract features from access logs for ML"""
        features = []
        for log in access_logs:
            features.append({
                'hour': log.timestamp.hour,
                'day_of_week': log.timestamp.weekday(),
                'access_count': 1,
                'failed_attempts': 0 if log.is_granted else 1
            })
        return pd.DataFrame(features)
    
    def _determine_anomaly_reason(self, log, features):
        """Determine the reason for an anomaly"""
        reasons = []
        if features['hour'] < 6 or features['hour'] > 22:
            reasons.append('unusual_time')
        if not log.is_granted:
            reasons.append('access_denied')
        if log.is_tailgating:
            reasons.append('tailgating')
        return reasons if reasons else ['pattern_deviation']
    
    def _determine_traffic_anomaly_reason(self, stats):
        """Determine reason for traffic anomaly"""
        if stats['denial_rate'] > 0.5:
            return 'high_denial_rate'
        elif stats['total_attempts'] > stats['total_attempts'].mean() * 3:
            return 'unusual_high_traffic'
        elif stats['unique_users'] > stats['unique_users'].mean() * 2:
            return 'unusual_user_count'
        else:
            return 'pattern_deviation'
    
    def _detect_time_based_anomalies(self, user_id, patterns):
        """Detect time-based anomalies in login patterns"""
        anomalies = []
        
        # Calculate typical login hours
        hours = [p['hour'] for p in patterns]
        mean_hour = np.mean(hours)
        std_hour = np.std(hours)
        
        for pattern in patterns[-5:]:  # Check last 5 logins
            if abs(pattern['hour'] - mean_hour) > 2 * std_hour:
                anomalies.append({
                    'user_id': user_id,
                    'timestamp': pattern['timestamp'],
                    'reason': 'unusual_login_time',
                    'typical_hour': float(mean_hour),
                    'actual_hour': pattern['hour']
                })
        
        return anomalies
    
    def _create_anomaly_alert(self, user, anomaly):
        """Create an alert for detected anomaly"""
        try:
            Alert.objects.create(
                organization=user.organization,
                title=f"Anomalous behavior detected for {user.get_full_name()}",
                description=f"Unusual access pattern detected. Reason: {', '.join(anomaly['reason'])}",
                alert_type='anomaly_detected',
                severity='high' if anomaly['confidence'] > 85 else 'medium',
                user=user,
                detection_method='isolation_forest',
                confidence_score=anomaly['confidence'] / 100,
                context={
                    'anomaly_score': anomaly['anomaly_score'],
                    'timestamp': anomaly['timestamp'].isoformat(),
                    'access_point': anomaly['access_point']
                }
            )
        except Exception as e:
            logger.error(f"Error creating anomaly alert: {str(e)}")
