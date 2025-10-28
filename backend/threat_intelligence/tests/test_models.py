"""
Unit Tests for Threat Intelligence Models
"""
import pytest
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from core.models import Organization, User
from access_control.models import AccessPoint
from threat_intelligence.models import (
    Threat,
    Alert,
    RiskAssessment,
    ThreatIndicator,
    Watchlist,
    ThreatFeed,
    ThreatHuntingQuery
)


@pytest.mark.django_db
class TestThreatModel(TestCase):
    """Test cases for Threat model"""
    
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
    
    def test_create_threat(self):
        """Test creating a threat"""
        threat = Threat.objects.create(
            organization=self.org,
            title="Test Threat",
            description="This is a test threat",
            threat_type="malware",
            severity="high",
            status="new",
            risk_score=75.5,
            confidence_score=0.85,
            source="test_system",
            created_by=self.user
        )
        
        assert threat.id is not None
        assert threat.title == "Test Threat"
        assert threat.severity == "high"
        assert threat.risk_score == 75.5
        assert str(threat) == "[HIGH] Test Threat"
    
    def test_threat_status_choices(self):
        """Test threat status choices"""
        threat = Threat.objects.create(
            organization=self.org,
            title="Status Test",
            description="Testing status",
            threat_type="phishing",
            severity="medium",
            source="manual",
            created_by=self.user
        )
        
        valid_statuses = ['new', 'investigating', 'confirmed', 'mitigated', 'resolved', 'false_positive']
        for status in valid_statuses:
            threat.status = status
            threat.save()
            threat.refresh_from_db()
            assert threat.status == status


@pytest.mark.django_db
class TestAlertModel(TestCase):
    """Test cases for Alert model"""
    
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
    
    def test_create_alert(self):
        """Test creating an alert"""
        alert = Alert.objects.create(
            organization=self.org,
            title="Test Alert",
            description="This is a test alert",
            alert_type="anomaly_detected",
            severity="high",
            detection_method="isolation_forest",
            confidence_score=0.92
        )
        
        assert alert.id is not None
        assert alert.title == "Test Alert"
        assert alert.severity == "high"
        assert alert.confidence_score == 0.92
        assert str(alert) == "[HIGH] Test Alert"
    
    def test_alert_aggregation(self):
        """Test alert aggregation"""
        parent_alert = Alert.objects.create(
            organization=self.org,
            title="Parent Alert",
            description="Main alert",
            alert_type="suspicious_activity",
            severity="medium",
            detection_method="ml_model"
        )
        
        child_alert = Alert.objects.create(
            organization=self.org,
            title="Child Alert",
            description="Duplicate alert",
            alert_type="suspicious_activity",
            severity="medium",
            detection_method="ml_model",
            is_aggregated=True,
            parent_alert=parent_alert
        )
        
        assert child_alert.parent_alert == parent_alert
        assert child_alert.is_aggregated is True


@pytest.mark.django_db
class TestRiskAssessmentModel(TestCase):
    """Test cases for RiskAssessment model"""
    
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
    
    def test_create_risk_assessment(self):
        """Test creating a risk assessment"""
        assessment = RiskAssessment.objects.create(
            organization=self.org,
            title="User Risk Assessment",
            description="Testing risk assessment",
            assessment_type="user",
            risk_level="high",
            risk_score=78.3,
            likelihood=0.75,
            impact=0.85,
            subject_user=self.user,
            assessed_by=self.user,
            assessment_method="threat_scoring_ai"
        )
        
        assert assessment.id is not None
        assert assessment.risk_level == "high"
        assert assessment.risk_score == 78.3
        assert assessment.subject_user == self.user
        assert str(assessment) == "[HIGH] User Risk Assessment"


@pytest.mark.django_db
class TestThreatIndicatorModel(TestCase):
    """Test cases for ThreatIndicator model"""
    
    def setUp(self):
        """Set up test data"""
        self.org = Organization.objects.create(
            name="Test Org",
            slug="test-org"
        )
    
    def test_create_threat_indicator(self):
        """Test creating a threat indicator"""
        indicator = ThreatIndicator.objects.create(
            organization=self.org,
            indicator_type="ip_address",
            indicator_value="192.168.1.100",
            description="Suspicious IP address",
            severity="medium",
            status="active",
            confidence_score=0.88,
            source="external_feed"
        )
        
        assert indicator.id is not None
        assert indicator.indicator_type == "ip_address"
        assert indicator.indicator_value == "192.168.1.100"
        assert indicator.times_detected == 1
    
    def test_indicator_expiration(self):
        """Test indicator expiration"""
        future_date = timezone.now() + timedelta(days=30)
        past_date = timezone.now() - timedelta(days=1)
        
        # Future expiration
        indicator1 = ThreatIndicator.objects.create(
            organization=self.org,
            indicator_type="domain",
            indicator_value="malicious.com",
            description="Malicious domain",
            severity="high",
            expires_at=future_date,
            source="manual"
        )
        
        # Past expiration
        indicator2 = ThreatIndicator.objects.create(
            organization=self.org,
            indicator_type="domain",
            indicator_value="old-threat.com",
            description="Old threat",
            severity="low",
            status="expired",
            expires_at=past_date,
            source="manual"
        )
        
        assert indicator1.status == "active"
        assert indicator2.status == "expired"


@pytest.mark.django_db
class TestWatchlistModel(TestCase):
    """Test cases for Watchlist model"""
    
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
    
    def test_create_watchlist_entry(self):
        """Test creating a watchlist entry"""
        entry = Watchlist.objects.create(
            organization=self.org,
            watchlist_type="person",
            name="Suspicious Person",
            description="Known threat actor",
            threat_level="high",
            subject_identifier="suspect@example.com",
            reason="Previous security incident",
            alert_on_detection=True,
            added_by=self.user
        )
        
        assert entry.id is not None
        assert entry.name == "Suspicious Person"
        assert entry.threat_level == "high"
        assert entry.alert_on_detection is True
        assert entry.times_detected == 0
    
    def test_watchlist_detection_update(self):
        """Test updating watchlist detection"""
        entry = Watchlist.objects.create(
            organization=self.org,
            watchlist_type="vehicle",
            name="Suspicious Vehicle",
            description="Stolen vehicle",
            threat_level="critical",
            subject_identifier="ABC-1234",
            reason="Reported stolen",
            added_by=self.user
        )
        
        # Simulate detection
        entry.times_detected += 1
        entry.last_detected_at = timezone.now()
        entry.last_detected_location = "Main Gate"
        entry.save()
        
        assert entry.times_detected == 1
        assert entry.last_detected_location == "Main Gate"
        assert entry.last_detected_at is not None


@pytest.mark.django_db
class TestThreatFeedModel(TestCase):
    """Test cases for ThreatFeed model"""
    
    def setUp(self):
        """Set up test data"""
        self.org = Organization.objects.create(
            name="Test Org",
            slug="test-org"
        )
    
    def test_create_threat_feed(self):
        """Test creating a threat feed"""
        feed = ThreatFeed.objects.create(
            organization=self.org,
            name="AlienVault OTX",
            feed_type="alienvault",
            description="AlienVault Open Threat Exchange",
            api_url="https://otx.alienvault.com/api/v1/",
            api_key="test_api_key",
            update_frequency=3600,
            auto_import=True,
            trust_score=0.85
        )
        
        assert feed.id is not None
        assert feed.name == "AlienVault OTX"
        assert feed.status == "active"
        assert feed.update_frequency == 3600
        assert feed.total_indicators_imported == 0


@pytest.mark.django_db
class TestThreatHuntingQueryModel(TestCase):
    """Test cases for ThreatHuntingQuery model"""
    
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
    
    def test_create_hunting_query(self):
        """Test creating a threat hunting query"""
        query = ThreatHuntingQuery.objects.create(
            organization=self.org,
            name="Failed Login Hunt",
            description="Hunt for failed login attempts",
            query_text="Show me all failed logins from China",
            query_type="natural_language",
            hypothesis="Possible brute force attack from foreign IPs",
            is_public=False,
            created_by=self.user
        )
        
        assert query.id is not None
        assert query.name == "Failed Login Hunt"
        assert query.times_executed == 0
        assert query.is_public is False
    
    def test_query_execution_tracking(self):
        """Test tracking query execution"""
        query = ThreatHuntingQuery.objects.create(
            organization=self.org,
            name="Test Query",
            description="Test query",
            query_text="Test",
            query_type="sql",
            created_by=self.user
        )
        
        # Simulate execution
        query.times_executed += 1
        query.last_executed_at = timezone.now()
        query.last_result_count = 42
        query.save()
        
        assert query.times_executed == 1
        assert query.last_result_count == 42
        assert query.last_executed_at is not None
