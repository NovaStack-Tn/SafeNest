"""
Threat Intelligence Management Serializers
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Threat,
    Alert,
    RiskAssessment,
    ThreatIndicator,
    Watchlist,
    ThreatFeed,
    ThreatHuntingQuery
)
from access_control.models import AccessPoint

User = get_user_model()


class ThreatSerializer(serializers.ModelSerializer):
    """Serializer for Threat model"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    related_user_names = serializers.SerializerMethodField()
    related_access_point_names = serializers.SerializerMethodField()
    
    class Meta:
        model = Threat
        fields = [
            'id', 'organization', 'title', 'description', 'threat_type',
            'severity', 'status', 'risk_score', 'confidence_score',
            'source', 'external_ref', 'assigned_to', 'assigned_to_name',
            'created_by', 'created_by_name', 'related_users', 'related_user_names',
            'related_access_points', 'related_access_point_names',
            'latitude', 'longitude', 'location_name', 'tags', 'metadata',
            'attack_vector', 'impact_analysis', 'first_detected_at',
            'last_seen_at', 'resolved_at'
        ]
        read_only_fields = ['first_detected_at', 'last_seen_at']
    
    def get_related_user_names(self, obj):
        return [user.get_full_name() for user in obj.related_users.all()]
    
    def get_related_access_point_names(self, obj):
        return [ap.name for ap in obj.related_access_points.all()]


class ThreatListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for threat lists"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Threat
        fields = [
            'id', 'title', 'threat_type', 'severity', 'status',
            'risk_score', 'created_by_name', 'first_detected_at'
        ]


class AlertSerializer(serializers.ModelSerializer):
    """Serializer for Alert model"""
    threat_title = serializers.CharField(source='threat.title', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    access_point_name = serializers.CharField(source='access_point.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    acknowledged_by_name = serializers.CharField(source='acknowledged_by.get_full_name', read_only=True)
    
    class Meta:
        model = Alert
        fields = [
            'id', 'organization', 'title', 'description', 'alert_type',
            'severity', 'status', 'threat', 'threat_title', 'user',
            'user_name', 'access_point', 'access_point_name',
            'detection_method', 'confidence_score', 'assigned_to',
            'assigned_to_name', 'acknowledged_by', 'acknowledged_by_name',
            'acknowledged_at', 'is_aggregated', 'parent_alert',
            'aggregation_count', 'source_data', 'context', 'tags',
            'triggered_at', 'resolved_at'
        ]
        read_only_fields = ['triggered_at']


class AlertListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for alert lists"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Alert
        fields = [
            'id', 'title', 'alert_type', 'severity', 'status',
            'user_name', 'confidence_score', 'triggered_at'
        ]


class RiskAssessmentSerializer(serializers.ModelSerializer):
    """Serializer for RiskAssessment model"""
    assessed_by_name = serializers.CharField(source='assessed_by.get_full_name', read_only=True)
    subject_user_name = serializers.CharField(source='subject_user.get_full_name', read_only=True)
    subject_access_point_name = serializers.CharField(source='subject_access_point.name', read_only=True)
    
    class Meta:
        model = RiskAssessment
        fields = [
            'id', 'organization', 'title', 'description', 'assessment_type',
            'risk_level', 'risk_score', 'likelihood', 'impact',
            'subject_user', 'subject_user_name', 'subject_access_point',
            'subject_access_point_name', 'subject_identifier',
            'risk_factors', 'vulnerabilities', 'mitigation_recommendations',
            'assessed_by', 'assessed_by_name', 'assessment_method',
            'is_active', 'valid_from', 'valid_until', 'metadata',
            'assessed_at', 'updated_at'
        ]
        read_only_fields = ['assessed_at', 'updated_at']


class RiskAssessmentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for risk assessment lists"""
    subject_user_name = serializers.CharField(source='subject_user.get_full_name', read_only=True)
    
    class Meta:
        model = RiskAssessment
        fields = [
            'id', 'title', 'assessment_type', 'risk_level', 'risk_score',
            'subject_user_name', 'is_active', 'assessed_at'
        ]


class ThreatIndicatorSerializer(serializers.ModelSerializer):
    """Serializer for ThreatIndicator model"""
    threat_title = serializers.CharField(source='threat.title', read_only=True)
    added_by_name = serializers.CharField(source='added_by.get_full_name', read_only=True)
    
    class Meta:
        model = ThreatIndicator
        fields = [
            'id', 'organization', 'indicator_type', 'indicator_value',
            'description', 'severity', 'status', 'threat', 'threat_title',
            'first_seen', 'last_seen', 'times_detected', 'confidence_score',
            'false_positive_rate', 'source', 'external_references',
            'expires_at', 'tags', 'metadata', 'added_by', 'added_by_name'
        ]
        read_only_fields = ['first_seen', 'last_seen', 'times_detected']


class ThreatIndicatorListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for threat indicator lists"""
    
    class Meta:
        model = ThreatIndicator
        fields = [
            'id', 'indicator_type', 'indicator_value', 'severity',
            'status', 'confidence_score', 'last_seen'
        ]


class WatchlistSerializer(serializers.ModelSerializer):
    """Serializer for Watchlist model"""
    subject_user_name = serializers.CharField(source='subject_user.get_full_name', read_only=True)
    added_by_name = serializers.CharField(source='added_by.get_full_name', read_only=True)
    related_threat_titles = serializers.SerializerMethodField()
    
    class Meta:
        model = Watchlist
        fields = [
            'id', 'organization', 'watchlist_type', 'name', 'description',
            'threat_level', 'status', 'subject_identifier', 'subject_user',
            'subject_user_name', 'alert_on_detection', 'auto_block',
            'times_detected', 'last_detected_at', 'last_detected_location',
            'reason', 'notes', 'related_threats', 'related_threat_titles',
            'valid_from', 'valid_until', 'added_by', 'added_by_name',
            'tags', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'times_detected']
    
    def get_related_threat_titles(self, obj):
        return [threat.title for threat in obj.related_threats.all()]


class WatchlistListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for watchlist lists"""
    
    class Meta:
        model = Watchlist
        fields = [
            'id', 'watchlist_type', 'name', 'threat_level', 'status',
            'subject_identifier', 'times_detected', 'created_at'
        ]


class ThreatFeedSerializer(serializers.ModelSerializer):
    """Serializer for ThreatFeed model"""
    
    class Meta:
        model = ThreatFeed
        fields = [
            'id', 'organization', 'name', 'feed_type', 'description',
            'api_url', 'api_key', 'authentication_method',
            'update_frequency', 'auto_import', 'trust_score', 'status',
            'last_sync_at', 'last_error', 'total_indicators_imported',
            'last_import_count', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'last_sync_at',
            'total_indicators_imported', 'last_import_count'
        ]
        extra_kwargs = {
            'api_key': {'write_only': True}
        }


class ThreatFeedListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for threat feed lists"""
    
    class Meta:
        model = ThreatFeed
        fields = [
            'id', 'name', 'feed_type', 'status', 'auto_import',
            'last_sync_at', 'total_indicators_imported'
        ]


class ThreatHuntingQuerySerializer(serializers.ModelSerializer):
    """Serializer for ThreatHuntingQuery model"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    threat_titles = serializers.SerializerMethodField()
    
    class Meta:
        model = ThreatHuntingQuery
        fields = [
            'id', 'organization', 'name', 'description', 'query_text',
            'query_type', 'hypothesis', 'expected_outcome', 'times_executed',
            'last_executed_at', 'last_result_count', 'findings',
            'threats_discovered', 'threat_titles', 'is_public',
            'created_by', 'created_by_name', 'tags', 'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'times_executed',
            'last_executed_at', 'last_result_count'
        ]
    
    def get_threat_titles(self, obj):
        return [threat.title for threat in obj.threats_discovered.all()]


class ThreatHuntingQueryListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for threat hunting query lists"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = ThreatHuntingQuery
        fields = [
            'id', 'name', 'query_type', 'times_executed',
            'created_by_name', 'is_public', 'updated_at'
        ]


# Specialized serializers for AI operations
class AnomalyDetectionInputSerializer(serializers.Serializer):
    """Input serializer for anomaly detection"""
    user_id = serializers.IntegerField(required=False)
    access_point_id = serializers.IntegerField(required=False)
    time_range_days = serializers.IntegerField(default=30)
    detection_method = serializers.ChoiceField(
        choices=['isolation_forest', 'dbscan', 'one_class_svm'],
        default='isolation_forest'
    )


class ThreatScoringInputSerializer(serializers.Serializer):
    """Input serializer for threat scoring"""
    entity_type = serializers.ChoiceField(
        choices=['user', 'access_point', 'location', 'event']
    )
    entity_id = serializers.IntegerField()
    time_range_days = serializers.IntegerField(default=30)


class ThreatScoringOutputSerializer(serializers.Serializer):
    """Output serializer for threat scoring"""
    entity_type = serializers.CharField()
    entity_id = serializers.IntegerField()
    risk_score = serializers.FloatField()
    risk_level = serializers.CharField()
    contributing_factors = serializers.JSONField()
    recommendations = serializers.ListField()


class PredictiveThreatAnalyticsInputSerializer(serializers.Serializer):
    """Input serializer for predictive threat analytics"""
    threat_type = serializers.CharField(required=False)
    prediction_days = serializers.IntegerField(default=7)
    confidence_threshold = serializers.FloatField(default=0.7)


class AlertAggregationInputSerializer(serializers.Serializer):
    """Input serializer for alert aggregation"""
    time_window_minutes = serializers.IntegerField(default=60)
    similarity_threshold = serializers.FloatField(default=0.8)
    max_alerts = serializers.IntegerField(default=100)
