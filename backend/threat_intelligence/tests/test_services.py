"""
Unit Tests for Threat Intelligence AI Services
"""
import pytest
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from unittest.mock import Mock, patch

from core.models import Organization, User
from access_control.models import AccessPoint, AccessLog
from threat_intelligence.models import Threat, Alert, ThreatIndicator
from threat_intelligence.services import (
    AnomalyDetectionService,
    ThreatScoringService,
    PredictiveThreatAnalytics,
    AlertAggregationService,
    ThreatHuntingAssistant
)


@pytest.mark.django_db
class TestAnomalyDetectionService(TestCase):
    """Test cases for Anomaly Detection Service"""
    
    def setUp(self):
        """Set up test data"""
        self.org = Organization.objects.create(
            name="Test Org",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            organization=self.org
        )
        self.access_point = AccessPoint.objects.create(
            organization=self.org,
            name="Main Door",
            point_type="door",
            location="Building A",
            hardware_id="AP001"
        )
        self.service = AnomalyDetectionService(contamination=0.1)
    
    def test_service_initialization(self):
        """Test service initialization"""
        assert self.service.contamination == 0.1
        assert self.service.scaler is not None
    
    def test_detect_user_anomalies_insufficient_data(self):
        """Test anomaly detection with insufficient data"""
        result = self.service.detect_user_behavior_anomalies(
            user_id=self.user.id,
            time_range_days=30
        )
        
        assert result['status'] == 'insufficient_data'
        assert 'message' in result
    
    def test_detect_user_anomalies_with_data(self):
        """Test anomaly detection with sufficient data"""
        # Create sample access logs
        for i in range(20):
            AccessLog.objects.create(
                organization=self.org,
                access_point=self.access_point,
                user=self.user,
                event_type='entry',
                is_granted=True,
                timestamp=timezone.now() - timedelta(hours=i)
            )
        
        result = self.service.detect_user_behavior_anomalies(
            user_id=self.user.id,
            time_range_days=7
        )
        
        assert result['status'] == 'success'
        assert 'total_logs_analyzed' in result
        assert result['total_logs_analyzed'] == 20


@pytest.mark.django_db
class TestThreatScoringService(TestCase):
    """Test cases for Threat Scoring Service"""
    
    def setUp(self):
        """Set up test data"""
        self.org = Organization.objects.create(
            name="Test Org",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            organization=self.org
        )
        self.access_point = AccessPoint.objects.create(
            organization=self.org,
            name="Main Door",
            point_type="door",
            location="Building A",
            hardware_id="AP001"
        )
        self.service = ThreatScoringService()
    
    def test_calculate_user_risk_score(self):
        """Test user risk score calculation"""
        result = self.service.calculate_user_risk_score(
            user_id=self.user.id,
            time_range_days=30
        )
        
        assert result['status'] == 'success'
        assert 'risk_score' in result
        assert 0 <= result['risk_score'] <= 100
        assert 'risk_level' in result
        assert 'contributing_factors' in result
        assert 'recommendations' in result
    
    def test_calculate_access_point_risk_score(self):
        """Test access point risk score calculation"""
        # Create some access logs
        for i in range(10):
            AccessLog.objects.create(
                organization=self.org,
                access_point=self.access_point,
                user=self.user,
                event_type='entry',
                is_granted=(i % 2 == 0),  # Half granted, half denied
                timestamp=timezone.now() - timedelta(hours=i)
            )
        
        result = self.service.calculate_access_point_risk_score(
            access_point_id=self.access_point.id,
            time_range_days=7
        )
        
        assert result['status'] == 'success'
        assert 'risk_score' in result
        assert 'contributing_factors' in result
        assert 'statistics' in result
    
    def test_determine_risk_level(self):
        """Test risk level determination"""
        assert self.service._determine_risk_level(85) == 'critical'
        assert self.service._determine_risk_level(65) == 'severe'
        assert self.service._determine_risk_level(45) == 'high'
        assert self.service._determine_risk_level(25) == 'moderate'
        assert self.service._determine_risk_level(15) == 'low'
        assert self.service._determine_risk_level(5) == 'minimal'


@pytest.mark.django_db
class TestPredictiveThreatAnalytics(TestCase):
    """Test cases for Predictive Threat Analytics"""
    
    def setUp(self):
        """Set up test data"""
        self.org = Organization.objects.create(
            name="Test Org",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            organization=self.org
        )
        self.service = PredictiveThreatAnalytics()
    
    def test_forecast_threats_insufficient_data(self):
        """Test threat forecasting with insufficient data"""
        result = self.service.forecast_threat_trends(
            organization_id=self.org.id,
            forecast_days=7,
            historical_days=30
        )
        
        assert result['status'] == 'insufficient_data'
    
    def test_forecast_threats_with_data(self):
        """Test threat forecasting with sufficient data"""
        # Create sample threats
        for i in range(15):
            Threat.objects.create(
                organization=self.org,
                title=f"Threat {i}",
                description="Test threat",
                threat_type="malware",
                severity="medium",
                source="test",
                created_by=self.user,
                first_detected_at=timezone.now() - timedelta(days=i)
            )
        
        result = self.service.forecast_threat_trends(
            organization_id=self.org.id,
            forecast_days=7,
            historical_days=30
        )
        
        assert result['status'] == 'success'
        assert 'forecast' in result
        assert 'trend' in result
    
    def test_identify_emerging_patterns(self):
        """Test emerging pattern identification"""
        result = self.service.identify_emerging_patterns(
            organization_id=self.org.id,
            time_range_days=30
        )
        
        assert result['status'] == 'success'
        assert 'emerging_threat_types' in result
        assert 'timing_patterns' in result


@pytest.mark.django_db
class TestAlertAggregationService(TestCase):
    """Test cases for Alert Aggregation Service"""
    
    def setUp(self):
        """Set up test data"""
        self.org = Organization.objects.create(
            name="Test Org",
            slug="test-org"
        )
        self.service = AlertAggregationService(similarity_threshold=0.8)
    
    def test_service_initialization(self):
        """Test service initialization"""
        assert self.service.similarity_threshold == 0.8
    
    def test_deduplicate_alerts_no_data(self):
        """Test alert deduplication with no alerts"""
        result = self.service.deduplicate_alerts(
            organization_id=self.org.id,
            time_window_minutes=60
        )
        
        assert result['status'] == 'success'
        assert result['deduplicated_count'] == 0
    
    def test_deduplicate_alerts_with_data(self):
        """Test alert deduplication with similar alerts"""
        # Create similar alerts
        for i in range(5):
            Alert.objects.create(
                organization=self.org,
                title="Suspicious Activity Detected",
                description="Repeated failed login attempts",
                alert_type="failed_login",
                severity="medium",
                detection_method="rule_engine",
                triggered_at=timezone.now() - timedelta(minutes=i)
            )
        
        result = self.service.deduplicate_alerts(
            organization_id=self.org.id,
            time_window_minutes=60
        )
        
        assert result['status'] == 'success'
        assert 'alerts_processed' in result
    
    def test_calculate_alert_similarity(self):
        """Test alert similarity calculation"""
        alert1 = Alert.objects.create(
            organization=self.org,
            title="Test Alert 1",
            description="Test",
            alert_type="anomaly_detected",
            severity="high",
            detection_method="ml"
        )
        
        alert2 = Alert.objects.create(
            organization=self.org,
            title="Test Alert 2",
            description="Test",
            alert_type="anomaly_detected",
            severity="high",
            detection_method="ml"
        )
        
        similarity = self.service._calculate_alert_similarity(alert1, alert2)
        
        assert 0 <= similarity <= 1
        assert similarity > 0.5  # Should be similar


@pytest.mark.django_db
class TestThreatHuntingAssistant(TestCase):
    """Test cases for Threat Hunting Assistant"""
    
    def setUp(self):
        """Set up test data"""
        self.org = Organization.objects.create(
            name="Test Org",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            organization=self.org
        )
        self.assistant = ThreatHuntingAssistant()
    
    def test_parse_query_intent(self):
        """Test query intent parsing"""
        assert self.assistant._parse_query_intent(
            "Show me failed logins"
        ) == 'failed_logins'
        
        assert self.assistant._parse_query_intent(
            "Find unusual access patterns"
        ) == 'unusual_access'
        
        assert self.assistant._parse_query_intent(
            "Show threats by location"
        ) == 'threats_by_location'
    
    def test_execute_natural_language_query(self):
        """Test natural language query execution"""
        result = self.assistant.execute_natural_language_query(
            organization_id=self.org.id,
            query_text="Show me recent incidents",
            created_by=self.user
        )
        
        assert result['status'] == 'success'
        assert 'query' in result
        assert 'intent' in result
        assert 'results' in result
    
    def test_suggest_hypotheses(self):
        """Test hypothesis suggestion"""
        result = self.assistant.suggest_hunting_hypotheses(
            organization_id=self.org.id,
            time_range_days=7
        )
        
        assert result['status'] == 'success'
        assert 'hypotheses' in result
        assert isinstance(result['hypotheses'], list)
    
    def test_generate_threat_report(self):
        """Test threat report generation"""
        result = self.assistant.generate_threat_report(
            organization_id=self.org.id,
            report_type='summary',
            time_range_days=7
        )
        
        assert result['status'] == 'success'
        assert 'report' in result
        assert 'summary' in result['report']
    
    def test_extract_time_range(self):
        """Test time range extraction from queries"""
        assert self.assistant._extract_time_range("show data from today") == 1
        assert self.assistant._extract_time_range("last week") == 7
        assert self.assistant._extract_time_range("past month") == 30
        assert self.assistant._extract_time_range("show me data") == 7  # default


@pytest.mark.django_db
class TestServiceIntegration(TestCase):
    """Integration tests for multiple services"""
    
    def setUp(self):
        """Set up test data"""
        self.org = Organization.objects.create(
            name="Test Org",
            slug="test-org"
        )
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            organization=self.org
        )
    
    def test_end_to_end_threat_detection(self):
        """Test end-to-end threat detection workflow"""
        # 1. Create threat
        threat = Threat.objects.create(
            organization=self.org,
            title="Suspicious Activity",
            description="Multiple failed login attempts",
            threat_type="unauthorized_access",
            severity="high",
            source="anomaly_detection",
            created_by=self.user
        )
        
        # 2. Create related alert
        alert = Alert.objects.create(
            organization=self.org,
            title="Failed Login Alert",
            description="Multiple failed logins detected",
            alert_type="failed_login",
            severity="high",
            threat=threat,
            user=self.user,
            detection_method="ml_model",
            confidence_score=0.89
        )
        
        # 3. Calculate risk score
        scoring_service = ThreatScoringService()
        risk_result = scoring_service.calculate_user_risk_score(
            user_id=self.user.id
        )
        
        # 4. Create threat indicator
        indicator = ThreatIndicator.objects.create(
            organization=self.org,
            indicator_type="email",
            indicator_value=self.user.email,
            description="User involved in security incident",
            severity="medium",
            threat=threat,
            source="incident_response"
        )
        
        # Verify workflow
        assert threat.id is not None
        assert alert.threat == threat
        assert risk_result['status'] == 'success'
        assert indicator.threat == threat
        assert Alert.objects.filter(threat=threat).count() == 1
