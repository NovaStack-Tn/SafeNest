"""
Predictive Threat Analytics Service
Forecasts threat trends, identifies emerging patterns, and predicts attack vectors
"""
import numpy as np
import pandas as pd
from datetime import timedelta, datetime
from django.utils import timezone
from django.db.models import Count, Q
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import logging

from ..models import Threat, Alert, ThreatIndicator
from access_control.models import AccessLog

logger = logging.getLogger(__name__)


class PredictiveThreatAnalytics:
    """
    ML-based predictive analytics for threat forecasting
    """
    
    def forecast_threat_trends(self, organization_id, threat_type=None, 
                               forecast_days=7, historical_days=30):
        """
        Forecast threat trends for the next N days
        
        Args:
            organization_id: Organization ID
            threat_type: Optional specific threat type to forecast
            forecast_days: Number of days to forecast
            historical_days: Historical data window
        
        Returns:
            dict: Forecast results with predictions
        """
        try:
            start_date = timezone.now() - timedelta(days=historical_days)
            
            # Get historical threat data
            threats_query = Threat.objects.filter(
                organization_id=organization_id,
                first_detected_at__gte=start_date
            )
            
            if threat_type:
                threats_query = threats_query.filter(threat_type=threat_type)
            
            # Aggregate by date
            daily_counts = threats_query.extra(
                {'date': "date(first_detected_at)"}
            ).values('date').annotate(
                count=Count('id')
            ).order_by('date')
            
            if len(daily_counts) < 7:
                return {
                    'status': 'insufficient_data',
                    'message': 'Not enough historical data for forecasting'
                }
            
            # Convert to DataFrame
            df = pd.DataFrame(list(daily_counts))
            df['date'] = pd.to_datetime(df['date'])
            
            # Prepare data for forecasting
            df['days_from_start'] = (df['date'] - df['date'].min()).dt.days
            X = df[['days_from_start']].values
            y = df['count'].values
            
            # Fit polynomial regression model (degree 2 for trend detection)
            poly_features = PolynomialFeatures(degree=2)
            X_poly = poly_features.fit_transform(X)
            
            model = LinearRegression()
            model.fit(X_poly, y)
            
            # Generate future dates for prediction
            last_day = df['days_from_start'].max()
            future_days = np.array([[last_day + i] for i in range(1, forecast_days + 1)])
            future_days_poly = poly_features.transform(future_days)
            
            # Make predictions
            predictions = model.predict(future_days_poly)
            predictions = np.maximum(predictions, 0)  # No negative predictions
            
            # Calculate confidence intervals
            residuals = y - model.predict(X_poly)
            std_error = np.std(residuals)
            
            # Generate forecast data
            forecast_data = []
            for i, pred in enumerate(predictions):
                forecast_date = timezone.now().date() + timedelta(days=i+1)
                forecast_data.append({
                    'date': forecast_date.isoformat(),
                    'predicted_count': int(round(pred)),
                    'confidence_lower': max(int(round(pred - 1.96 * std_error)), 0),
                    'confidence_upper': int(round(pred + 1.96 * std_error))
                })
            
            # Calculate trend
            trend = 'increasing' if predictions[-1] > predictions[0] else 'decreasing'
            trend_magnitude = abs(predictions[-1] - predictions[0]) / (predictions[0] + 1)
            
            return {
                'status': 'success',
                'threat_type': threat_type or 'all',
                'historical_days': historical_days,
                'forecast_days': forecast_days,
                'trend': trend,
                'trend_magnitude': round(float(trend_magnitude), 2),
                'current_daily_average': round(float(y.mean()), 2),
                'predicted_daily_average': round(float(predictions.mean()), 2),
                'forecast': forecast_data
            }
        
        except Exception as e:
            logger.error(f"Error forecasting threat trends: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def identify_emerging_patterns(self, organization_id, time_range_days=30):
        """
        Identify emerging threat patterns using pattern recognition
        
        Args:
            organization_id: Organization ID
            time_range_days: Analysis window
        
        Returns:
            dict: Identified patterns
        """
        try:
            start_date = timezone.now() - timedelta(days=time_range_days)
            
            # Analyze threat type distribution over time
            threats = Threat.objects.filter(
                organization_id=organization_id,
                first_detected_at__gte=start_date
            )
            
            # Group by threat type and week
            threat_type_trends = {}
            for threat in threats:
                week = threat.first_detected_at.isocalendar()[1]
                threat_type = threat.threat_type
                
                if threat_type not in threat_type_trends:
                    threat_type_trends[threat_type] = {}
                
                threat_type_trends[threat_type][week] = \
                    threat_type_trends[threat_type].get(week, 0) + 1
            
            # Identify emerging patterns (increasing trends)
            emerging_patterns = []
            for threat_type, weekly_counts in threat_type_trends.items():
                if len(weekly_counts) >= 2:
                    weeks = sorted(weekly_counts.keys())
                    counts = [weekly_counts[w] for w in weeks]
                    
                    # Calculate simple trend
                    if len(counts) >= 2:
                        recent_avg = np.mean(counts[-2:])
                        early_avg = np.mean(counts[:2])
                        
                        if recent_avg > early_avg * 1.5:  # 50% increase
                            growth_rate = ((recent_avg - early_avg) / early_avg) * 100
                            emerging_patterns.append({
                                'threat_type': threat_type,
                                'growth_rate': round(float(growth_rate), 2),
                                'recent_count': int(recent_avg),
                                'severity': self._assess_pattern_severity(growth_rate, recent_avg)
                            })
            
            # Analyze attack timing patterns
            timing_patterns = self._analyze_timing_patterns(threats)
            
            # Analyze target patterns
            target_patterns = self._analyze_target_patterns(threats)
            
            return {
                'status': 'success',
                'analysis_period_days': time_range_days,
                'emerging_threat_types': emerging_patterns,
                'timing_patterns': timing_patterns,
                'target_patterns': target_patterns,
                'total_threats_analyzed': threats.count()
            }
        
        except Exception as e:
            logger.error(f"Error identifying emerging patterns: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def predict_attack_vectors(self, organization_id, time_range_days=60):
        """
        Predict likely attack vectors based on historical data
        
        Args:
            organization_id: Organization ID
            time_range_days: Historical analysis window
        
        Returns:
            dict: Predicted attack vectors with probabilities
        """
        try:
            start_date = timezone.now() - timedelta(days=time_range_days)
            
            # Get historical threats and alerts
            threats = Threat.objects.filter(
                organization_id=organization_id,
                first_detected_at__gte=start_date
            )
            
            alerts = Alert.objects.filter(
                organization_id=organization_id,
                triggered_at__gte=start_date
            )
            
            # Analyze attack vectors from threat metadata
            attack_vectors = {}
            for threat in threats:
                vectors = threat.attack_vector
                if isinstance(vectors, dict):
                    for vector_type, details in vectors.items():
                        if vector_type not in attack_vectors:
                            attack_vectors[vector_type] = {
                                'count': 0,
                                'severity_sum': 0,
                                'recent_count': 0
                            }
                        
                        attack_vectors[vector_type]['count'] += 1
                        
                        # Weight recent threats more heavily
                        days_ago = (timezone.now() - threat.first_detected_at).days
                        if days_ago <= 7:
                            attack_vectors[vector_type]['recent_count'] += 1
                        
                        # Add severity weight
                        severity_weights = {
                            'critical': 4, 'high': 3, 'medium': 2, 'low': 1
                        }
                        attack_vectors[vector_type]['severity_sum'] += \
                            severity_weights.get(threat.severity, 1)
            
            # Calculate risk probability for each vector
            total_threats = threats.count()
            predictions = []
            
            for vector, stats in attack_vectors.items():
                # Base probability on historical frequency
                base_probability = stats['count'] / total_threats if total_threats > 0 else 0
                
                # Adjust for recency (recent = higher probability)
                recency_factor = 1 + (stats['recent_count'] / stats['count'])
                
                # Adjust for severity
                severity_factor = stats['severity_sum'] / stats['count']
                
                # Combined probability
                probability = min(base_probability * recency_factor * (severity_factor / 2), 1.0)
                
                predictions.append({
                    'attack_vector': vector,
                    'probability': round(float(probability), 3),
                    'historical_occurrences': stats['count'],
                    'recent_occurrences': stats['recent_count'],
                    'risk_level': self._assess_vector_risk(probability)
                })
            
            # Sort by probability
            predictions.sort(key=lambda x: x['probability'], reverse=True)
            
            return {
                'status': 'success',
                'analysis_period_days': time_range_days,
                'total_threats_analyzed': total_threats,
                'predicted_vectors': predictions[:10],  # Top 10
                'recommendations': self._generate_vector_recommendations(predictions[:3])
            }
        
        except Exception as e:
            logger.error(f"Error predicting attack vectors: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def analyze_seasonal_patterns(self, organization_id, months=12):
        """
        Analyze seasonal threat patterns over multiple months
        
        Args:
            organization_id: Organization ID
            months: Number of months to analyze
        
        Returns:
            dict: Seasonal pattern analysis
        """
        try:
            start_date = timezone.now() - timedelta(days=months * 30)
            
            threats = Threat.objects.filter(
                organization_id=organization_id,
                first_detected_at__gte=start_date
            )
            
            # Analyze by day of week
            day_of_week_counts = [0] * 7
            for threat in threats:
                day = threat.first_detected_at.weekday()
                day_of_week_counts[day] += 1
            
            # Analyze by hour of day
            hour_counts = [0] * 24
            for threat in threats:
                hour = threat.first_detected_at.hour
                hour_counts[hour] += 1
            
            # Analyze by month
            month_counts = {}
            for threat in threats:
                month = threat.first_detected_at.month
                month_counts[month] = month_counts.get(month, 0) + 1
            
            # Identify peak times
            peak_day = day_of_week_counts.index(max(day_of_week_counts))
            peak_hour = hour_counts.index(max(hour_counts))
            peak_month = max(month_counts, key=month_counts.get) if month_counts else None
            
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            return {
                'status': 'success',
                'analysis_months': months,
                'total_threats': threats.count(),
                'peak_day_of_week': day_names[peak_day],
                'peak_hour': peak_hour,
                'peak_month': peak_month,
                'day_distribution': {day_names[i]: count for i, count in enumerate(day_of_week_counts)},
                'hour_distribution': {str(i): count for i, count in enumerate(hour_counts)},
                'month_distribution': month_counts
            }
        
        except Exception as e:
            logger.error(f"Error analyzing seasonal patterns: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    # Helper methods
    def _assess_pattern_severity(self, growth_rate, count):
        """Assess severity of emerging pattern"""
        if growth_rate > 200 and count > 10:
            return 'critical'
        elif growth_rate > 100 and count > 5:
            return 'high'
        elif growth_rate > 50:
            return 'medium'
        else:
            return 'low'
    
    def _analyze_timing_patterns(self, threats):
        """Analyze timing patterns in threats"""
        if threats.count() == 0:
            return {}
        
        # Analyze time of day distribution
        time_buckets = {'morning': 0, 'afternoon': 0, 'evening': 0, 'night': 0}
        
        for threat in threats:
            hour = threat.first_detected_at.hour
            if 6 <= hour < 12:
                time_buckets['morning'] += 1
            elif 12 <= hour < 18:
                time_buckets['afternoon'] += 1
            elif 18 <= hour < 24:
                time_buckets['evening'] += 1
            else:
                time_buckets['night'] += 1
        
        # Find peak period
        peak_period = max(time_buckets, key=time_buckets.get)
        
        return {
            'distribution': time_buckets,
            'peak_period': peak_period,
            'off_hours_percentage': round(
                (time_buckets['night'] / threats.count()) * 100, 2
            )
        }
    
    def _analyze_target_patterns(self, threats):
        """Analyze target patterns in threats"""
        # Analyze most targeted users
        user_targets = {}
        for threat in threats:
            for user in threat.related_users.all():
                user_targets[user.id] = user_targets.get(user.id, 0) + 1
        
        # Get top 5 targets
        top_targets = sorted(user_targets.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_unique_targets': len(user_targets),
            'top_5_targeted_users': [
                {'user_id': uid, 'threat_count': count} 
                for uid, count in top_targets
            ]
        }
    
    def _assess_vector_risk(self, probability):
        """Assess risk level based on probability"""
        if probability >= 0.7:
            return 'critical'
        elif probability >= 0.5:
            return 'high'
        elif probability >= 0.3:
            return 'medium'
        else:
            return 'low'
    
    def _generate_vector_recommendations(self, top_vectors):
        """Generate recommendations based on predicted vectors"""
        recommendations = []
        
        for vector in top_vectors:
            if vector['probability'] > 0.6:
                recommendations.append(
                    f"High risk of {vector['attack_vector']} - implement additional controls"
                )
        
        if not recommendations:
            recommendations.append("Continue monitoring for emerging threats")
        
        return recommendations
