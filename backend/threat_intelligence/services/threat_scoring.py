"""
Threat Scoring AI Service
Calculates risk scores for users, locations, events, and access points
"""
import numpy as np
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Avg, Q
import logging

from access_control.models import AccessLog, AccessPoint, AccessAnomaly
from core.models import User
from ..models import Threat, Alert, RiskAssessment, ThreatIndicator

logger = logging.getLogger(__name__)


class ThreatScoringService:
    """
    AI-powered threat scoring service for dynamic risk assessment
    """
    
    # Weight factors for different risk components
    WEIGHTS = {
        'historical_incidents': 0.25,
        'recent_anomalies': 0.30,
        'access_violations': 0.20,
        'threat_indicators': 0.15,
        'behavior_pattern': 0.10
    }
    
    def calculate_user_risk_score(self, user_id, time_range_days=30):
        """
        Calculate comprehensive risk score for a user
        
        Args:
            user_id: User ID to score
            time_range_days: Time window for analysis
        
        Returns:
            dict: Risk assessment results
        """
        try:
            user = User.objects.get(id=user_id)
            start_date = timezone.now() - timedelta(days=time_range_days)
            
            # Calculate individual risk components
            historical_score = self._calculate_historical_incident_score(user, start_date)
            anomaly_score = self._calculate_anomaly_score(user, start_date)
            violation_score = self._calculate_violation_score(user, start_date)
            indicator_score = self._calculate_threat_indicator_score(user)
            behavior_score = self._calculate_behavior_pattern_score(user, start_date)
            
            # Calculate weighted composite score
            risk_score = (
                historical_score * self.WEIGHTS['historical_incidents'] +
                anomaly_score * self.WEIGHTS['recent_anomalies'] +
                violation_score * self.WEIGHTS['access_violations'] +
                indicator_score * self.WEIGHTS['threat_indicators'] +
                behavior_score * self.WEIGHTS['behavior_pattern']
            )
            
            # Normalize to 0-100 scale
            risk_score = min(max(risk_score, 0), 100)
            
            # Determine risk level
            risk_level = self._determine_risk_level(risk_score)
            
            # Generate recommendations
            recommendations = self._generate_user_recommendations(
                user, risk_score, {
                    'historical': historical_score,
                    'anomaly': anomaly_score,
                    'violation': violation_score,
                    'indicator': indicator_score,
                    'behavior': behavior_score
                }
            )
            
            # Create or update risk assessment
            self._create_risk_assessment(
                user=user,
                assessment_type='user',
                risk_score=risk_score,
                risk_level=risk_level,
                recommendations=recommendations
            )
            
            return {
                'status': 'success',
                'user_id': user_id,
                'risk_score': round(risk_score, 2),
                'risk_level': risk_level,
                'contributing_factors': {
                    'historical_incidents': round(historical_score, 2),
                    'recent_anomalies': round(anomaly_score, 2),
                    'access_violations': round(violation_score, 2),
                    'threat_indicators': round(indicator_score, 2),
                    'behavior_pattern': round(behavior_score, 2)
                },
                'recommendations': recommendations
            }
        
        except User.DoesNotExist:
            return {'status': 'error', 'message': 'User not found'}
        except Exception as e:
            logger.error(f"Error calculating user risk score: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def calculate_access_point_risk_score(self, access_point_id, time_range_days=30):
        """
        Calculate risk score for an access point
        
        Args:
            access_point_id: Access point ID
            time_range_days: Time window for analysis
        
        Returns:
            dict: Risk assessment results
        """
        try:
            access_point = AccessPoint.objects.get(id=access_point_id)
            start_date = timezone.now() - timedelta(days=time_range_days)
            
            # Get access statistics
            total_attempts = AccessLog.objects.filter(
                access_point=access_point,
                timestamp__gte=start_date
            ).count()
            
            denied_attempts = AccessLog.objects.filter(
                access_point=access_point,
                timestamp__gte=start_date,
                is_granted=False
            ).count()
            
            anomalous_attempts = AccessLog.objects.filter(
                access_point=access_point,
                timestamp__gte=start_date,
                is_anomaly=True
            ).count()
            
            # Get threats related to this access point
            related_threats = Threat.objects.filter(
                related_access_points=access_point,
                first_detected_at__gte=start_date
            ).count()
            
            # Calculate component scores
            denial_rate = denied_attempts / total_attempts if total_attempts > 0 else 0
            anomaly_rate = anomalous_attempts / total_attempts if total_attempts > 0 else 0
            
            denial_score = min(denial_rate * 100, 100)
            anomaly_score = min(anomaly_rate * 150, 100)
            threat_score = min(related_threats * 20, 100)
            
            # Physical security score
            physical_score = 0
            if not access_point.is_secure:
                physical_score += 40
            if access_point.status != 'active':
                physical_score += 30
            if access_point.lockdown_enabled:
                physical_score += 20
            
            # Composite risk score
            risk_score = (
                denial_score * 0.30 +
                anomaly_score * 0.30 +
                threat_score * 0.25 +
                physical_score * 0.15
            )
            
            risk_score = min(max(risk_score, 0), 100)
            risk_level = self._determine_risk_level(risk_score)
            
            # Generate recommendations
            recommendations = self._generate_access_point_recommendations(
                access_point, risk_score, {
                    'denial_rate': denial_rate,
                    'anomaly_rate': anomaly_rate,
                    'related_threats': related_threats
                }
            )
            
            # Create risk assessment
            self._create_risk_assessment(
                access_point=access_point,
                assessment_type='access_point',
                risk_score=risk_score,
                risk_level=risk_level,
                recommendations=recommendations
            )
            
            return {
                'status': 'success',
                'access_point_id': access_point_id,
                'risk_score': round(risk_score, 2),
                'risk_level': risk_level,
                'contributing_factors': {
                    'denial_rate': round(denial_rate * 100, 2),
                    'anomaly_rate': round(anomaly_rate * 100, 2),
                    'related_threats': related_threats,
                    'physical_security': round(physical_score, 2)
                },
                'recommendations': recommendations,
                'statistics': {
                    'total_attempts': total_attempts,
                    'denied_attempts': denied_attempts,
                    'anomalous_attempts': anomalous_attempts
                }
            }
        
        except AccessPoint.DoesNotExist:
            return {'status': 'error', 'message': 'Access point not found'}
        except Exception as e:
            logger.error(f"Error calculating access point risk score: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def calculate_location_risk_score(self, organization_id, location_name, time_range_days=30):
        """
        Calculate risk score for a physical location
        
        Args:
            organization_id: Organization ID
            location_name: Location name
            time_range_days: Time window for analysis
        
        Returns:
            dict: Risk assessment results
        """
        try:
            start_date = timezone.now() - timedelta(days=time_range_days)
            
            # Get all access points at this location
            access_points = AccessPoint.objects.filter(
                organization_id=organization_id,
                location__icontains=location_name
            )
            
            if not access_points.exists():
                return {'status': 'error', 'message': 'Location not found'}
            
            # Aggregate statistics across all access points
            total_score = 0
            for ap in access_points:
                result = self.calculate_access_point_risk_score(ap.id, time_range_days)
                if result['status'] == 'success':
                    total_score += result['risk_score']
            
            # Average risk score
            avg_risk_score = total_score / access_points.count()
            risk_level = self._determine_risk_level(avg_risk_score)
            
            # Get threats at this location
            threats = Threat.objects.filter(
                organization_id=organization_id,
                location_name__icontains=location_name,
                first_detected_at__gte=start_date
            )
            
            return {
                'status': 'success',
                'location': location_name,
                'risk_score': round(avg_risk_score, 2),
                'risk_level': risk_level,
                'access_points_analyzed': access_points.count(),
                'active_threats': threats.filter(status__in=['new', 'investigating']).count(),
                'total_threats': threats.count()
            }
        
        except Exception as e:
            logger.error(f"Error calculating location risk score: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def update_dynamic_threat_levels(self, organization_id):
        """
        Update threat levels across the organization dynamically
        
        Args:
            organization_id: Organization ID
        
        Returns:
            dict: Update results
        """
        try:
            updated_users = []
            updated_access_points = []
            
            # Update user risk scores
            users = User.objects.filter(organization_id=organization_id, is_active=True)
            for user in users:
                result = self.calculate_user_risk_score(user.id)
                if result['status'] == 'success' and result['risk_score'] > 60:
                    updated_users.append({
                        'user_id': user.id,
                        'username': user.username,
                        'risk_score': result['risk_score'],
                        'risk_level': result['risk_level']
                    })
            
            # Update access point risk scores
            access_points = AccessPoint.objects.filter(organization_id=organization_id, status='active')
            for ap in access_points:
                result = self.calculate_access_point_risk_score(ap.id)
                if result['status'] == 'success' and result['risk_score'] > 60:
                    updated_access_points.append({
                        'access_point_id': ap.id,
                        'name': ap.name,
                        'risk_score': result['risk_score'],
                        'risk_level': result['risk_level']
                    })
            
            return {
                'status': 'success',
                'high_risk_users': updated_users,
                'high_risk_access_points': updated_access_points,
                'total_users_analyzed': users.count(),
                'total_access_points_analyzed': access_points.count()
            }
        
        except Exception as e:
            logger.error(f"Error updating dynamic threat levels: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    # Helper methods
    def _calculate_historical_incident_score(self, user, start_date):
        """Calculate score based on historical incidents"""
        threats = Threat.objects.filter(
            related_users=user,
            first_detected_at__gte=start_date
        )
        
        score = 0
        for threat in threats:
            if threat.severity == 'critical':
                score += 25
            elif threat.severity == 'high':
                score += 15
            elif threat.severity == 'medium':
                score += 8
            else:
                score += 3
        
        return min(score, 100)
    
    def _calculate_anomaly_score(self, user, start_date):
        """Calculate score based on recent anomalies"""
        anomalies = AccessAnomaly.objects.filter(
            user=user,
            detected_at__gte=start_date,
            is_false_positive=False
        )
        
        score = 0
        for anomaly in anomalies:
            if anomaly.severity == 'critical':
                score += 20
            elif anomaly.severity == 'high':
                score += 12
            elif anomaly.severity == 'medium':
                score += 6
            else:
                score += 2
        
        return min(score, 100)
    
    def _calculate_violation_score(self, user, start_date):
        """Calculate score based on access violations"""
        denied_attempts = AccessLog.objects.filter(
            user=user,
            timestamp__gte=start_date,
            is_granted=False
        ).count()
        
        return min(denied_attempts * 5, 100)
    
    def _calculate_threat_indicator_score(self, user):
        """Calculate score based on threat indicators"""
        indicators = ThreatIndicator.objects.filter(
            Q(indicator_value__icontains=user.email) |
            Q(indicator_value__icontains=user.username),
            status='active'
        )
        
        score = indicators.count() * 30
        return min(score, 100)
    
    def _calculate_behavior_pattern_score(self, user, start_date):
        """Calculate score based on behavior patterns"""
        access_logs = AccessLog.objects.filter(
            user=user,
            timestamp__gte=start_date
        )
        
        if access_logs.count() == 0:
            return 0
        
        # Check for suspicious patterns
        score = 0
        
        # Failed login attempts
        failed_attempts = access_logs.filter(is_granted=False).count()
        if failed_attempts > 10:
            score += 30
        elif failed_attempts > 5:
            score += 15
        
        # Off-hours access
        off_hours_count = access_logs.filter(
            Q(timestamp__hour__lt=6) | Q(timestamp__hour__gt=22)
        ).count()
        
        off_hours_rate = off_hours_count / access_logs.count()
        if off_hours_rate > 0.5:
            score += 25
        
        return min(score, 100)
    
    def _determine_risk_level(self, risk_score):
        """Determine categorical risk level from numerical score"""
        if risk_score >= 80:
            return 'critical'
        elif risk_score >= 60:
            return 'severe'
        elif risk_score >= 40:
            return 'high'
        elif risk_score >= 20:
            return 'moderate'
        elif risk_score >= 10:
            return 'low'
        else:
            return 'minimal'
    
    def _generate_user_recommendations(self, user, risk_score, factors):
        """Generate actionable recommendations for user risk"""
        recommendations = []
        
        if risk_score > 70:
            recommendations.append("Immediate security review required")
            recommendations.append("Consider temporary access restriction")
        
        if factors['anomaly'] > 50:
            recommendations.append("Investigate recent anomalous behavior patterns")
        
        if factors['violation'] > 40:
            recommendations.append("Review and reinforce access policies with user")
        
        if factors['indicator'] > 30:
            recommendations.append("User associated with known threat indicators - investigate immediately")
        
        if factors['behavior'] > 50:
            recommendations.append("Unusual behavior detected - schedule security interview")
        
        if not recommendations:
            recommendations.append("Continue monitoring user activity")
        
        return recommendations
    
    def _generate_access_point_recommendations(self, access_point, risk_score, factors):
        """Generate recommendations for access point security"""
        recommendations = []
        
        if risk_score > 70:
            recommendations.append("Consider temporary lockdown or enhanced monitoring")
        
        if factors['denial_rate'] > 0.3:
            recommendations.append("High denial rate detected - review access permissions")
        
        if factors['anomaly_rate'] > 0.2:
            recommendations.append("Increase monitoring frequency and alert sensitivity")
        
        if factors['related_threats'] > 5:
            recommendations.append("Multiple threats detected - conduct security audit")
        
        if not access_point.is_secure:
            recommendations.append("Physical security compromised - immediate inspection required")
        
        if not recommendations:
            recommendations.append("Maintain current security measures")
        
        return recommendations
    
    def _create_risk_assessment(self, assessment_type, risk_score, risk_level, 
                                recommendations, user=None, access_point=None):
        """Create or update risk assessment record"""
        try:
            organization = user.organization if user else access_point.organization
            
            # Create title
            if user:
                title = f"User Risk Assessment: {user.get_full_name()}"
            elif access_point:
                title = f"Access Point Risk Assessment: {access_point.name}"
            else:
                title = "Risk Assessment"
            
            # Calculate likelihood and impact
            likelihood = min(risk_score / 100, 1.0)
            impact = min(risk_score / 80, 1.0)
            
            RiskAssessment.objects.create(
                organization=organization,
                title=title,
                description=f"Automated risk assessment with score {risk_score:.2f}",
                assessment_type=assessment_type,
                risk_level=risk_level,
                risk_score=risk_score,
                likelihood=likelihood,
                impact=impact,
                subject_user=user,
                subject_access_point=access_point,
                assessment_method='threat_scoring_ai',
                mitigation_recommendations=recommendations
            )
        
        except Exception as e:
            logger.error(f"Error creating risk assessment: {str(e)}")
