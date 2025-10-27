"""
Anomaly detection service using rule-based and ML approaches.
"""
import logging
import pickle
from datetime import timedelta
from django.utils import timezone
from django.core.cache import cache
from sklearn.ensemble import IsolationForest
import numpy as np
from .models import LoginEvent, AnomalyRule

logger = logging.getLogger(__name__)


class AnomalyDetectionService:
    """Service for detecting anomalous login behavior."""
    
    def __init__(self):
        self.isolation_forest_cache_key = 'anomaly_model_org_{}'
    
    def check_rule(self, event, rule):
        """Check if event matches an anomaly rule."""
        if rule.rule_type == 'time':
            return self._check_time_rule(event, rule)
        elif rule.rule_type == 'geo':
            return self._check_geo_rule(event, rule)
        elif rule.rule_type == 'device':
            return self._check_device_rule(event, rule)
        elif rule.rule_type == 'velocity':
            return self._check_velocity_rule(event, rule)
        elif rule.rule_type == 'frequency':
            return self._check_frequency_rule(event, rule)
        elif rule.rule_type == 'ml':
            return self._check_ml_rule(event, rule)
        
        return False, 0.0, ''
    
    def _check_time_rule(self, event, rule):
        """Check if login is outside normal hours."""
        config = rule.config
        allowed_hours = config.get('allowed_hours', [9, 10, 11, 12, 13, 14, 15, 16, 17])
        
        hour = event.timestamp.hour
        if hour not in allowed_hours:
            return True, 0.6, f"Login at unusual hour: {hour}"
        
        return False, 0.0, ''
    
    def _check_geo_rule(self, event, rule):
        """Check if login is from disallowed country."""
        config = rule.config
        allowed_countries = config.get('allowed_countries', [])
        blocked_countries = config.get('blocked_countries', [])
        
        if allowed_countries and event.country_code not in allowed_countries:
            return True, 0.8, f"Login from non-whitelisted country: {event.country_name}"
        
        if blocked_countries and event.country_code in blocked_countries:
            return True, 0.9, f"Login from blocked country: {event.country_name}"
        
        return False, 0.0, ''
    
    def _check_device_rule(self, event, rule):
        """Check if device is new or unusual."""
        if not event.user:
            return False, 0.0, ''
        
        # Check if device fingerprint has been seen before
        previous_devices = LoginEvent.objects.filter(
            user=event.user,
            success=True,
            timestamp__lt=event.timestamp
        ).values_list('device_fingerprint', flat=True).distinct()
        
        if event.device_fingerprint not in previous_devices:
            return True, 0.5, "Login from new device"
        
        return False, 0.0, ''
    
    def _check_velocity_rule(self, event, rule):
        """Check for impossible travel (velocity too high)."""
        if not event.user or not event.latitude or not event.longitude:
            return False, 0.0, ''
        
        # Get last login event
        last_event = LoginEvent.objects.filter(
            user=event.user,
            success=True,
            timestamp__lt=event.timestamp,
            latitude__isnull=False,
            longitude__isnull=False
        ).order_by('-timestamp').first()
        
        if not last_event:
            return False, 0.0, ''
        
        from .utils import calculate_travel_velocity
        velocity = calculate_travel_velocity(last_event, event)
        
        # Max reasonable velocity is ~900 km/h (commercial flight)
        max_velocity = rule.config.get('max_velocity_kmh', 900)
        
        if velocity and velocity > max_velocity:
            return True, 0.9, f"Impossible travel: {velocity:.0f} km/h"
        
        return False, 0.0, ''
    
    def _check_frequency_rule(self, event, rule):
        """Check for too many login attempts."""
        if not event.user:
            return False, 0.0, ''
        
        # Count recent login attempts
        time_window = rule.config.get('time_window_minutes', 60)
        max_attempts = rule.config.get('max_attempts', 10)
        
        since = timezone.now() - timedelta(minutes=time_window)
        recent_count = LoginEvent.objects.filter(
            user=event.user,
            timestamp__gte=since
        ).count()
        
        if recent_count > max_attempts:
            return True, 0.7, f"Too many login attempts: {recent_count} in {time_window}min"
        
        return False, 0.0, ''
    
    def _check_ml_rule(self, event, rule):
        """Use ML model to detect anomalies."""
        if not event.user:
            return False, 0.0, ''
        
        org_id = event.user.organization_id
        model = self._get_isolation_forest_model(org_id)
        
        if not model:
            return False, 0.0, ''
        
        # Extract features
        features = self._extract_features(event)
        if not features:
            return False, 0.0, ''
        
        # Predict (-1 for anomaly, 1 for normal)
        prediction = model.predict([features])[0]
        score = model.score_samples([features])[0]
        
        if prediction == -1:
            return True, abs(score), "ML model detected anomaly"
        
        return False, 0.0, ''
    
    def _extract_features(self, event):
        """Extract numerical features for ML model."""
        try:
            return [
                event.timestamp.hour,
                event.timestamp.weekday(),
                float(hash(event.country_code) % 1000) / 1000,  # Normalize country code
                float(hash(event.device_fingerprint) % 1000) / 1000,  # Normalize device
                1.0 if event.success else 0.0,
            ]
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            return None
    
    def train_isolation_forest(self, org_id):
        """Train Isolation Forest model for an organization."""
        from django.conf import settings
        
        # Get training data (last 90 days)
        since = timezone.now() - timedelta(days=90)
        events = LoginEvent.objects.filter(
            user__organization_id=org_id,
            timestamp__gte=since
        ).select_related('user')
        
        if events.count() < 100:
            logger.warning(f"Insufficient data for org {org_id}: {events.count()} events")
            return None
        
        # Extract features
        features = []
        for event in events:
            f = self._extract_features(event)
            if f:
                features.append(f)
        
        if len(features) < 100:
            return None
        
        # Train model
        contamination = settings.ANOMALY_ISOLATION_FOREST_CONTAMINATION
        model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        model.fit(features)
        
        # Cache model
        cache_key = self.isolation_forest_cache_key.format(org_id)
        cache.set(cache_key, pickle.dumps(model), timeout=60*60*24*7)  # 7 days
        
        logger.info(f"Trained Isolation Forest for org {org_id} with {len(features)} samples")
        return model
    
    def _get_isolation_forest_model(self, org_id):
        """Get cached ML model."""
        cache_key = self.isolation_forest_cache_key.format(org_id)
        model_bytes = cache.get(cache_key)
        
        if model_bytes:
            return pickle.loads(model_bytes)
        
        return None
