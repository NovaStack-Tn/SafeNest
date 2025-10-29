from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Threat, Alert, RiskAssessment, ThreatIndicator, Watchlist

User = get_user_model()


class UserMinimalSerializer(serializers.ModelSerializer):
    """Minimal user info for nested serialization"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id', 'username', 'email']


class ThreatSerializer(serializers.ModelSerializer):
    assigned_to_details = UserMinimalSerializer(source='assigned_to', read_only=True)
    created_by_details = UserMinimalSerializer(source='created_by', read_only=True)
    alert_count = serializers.SerializerMethodField()
    indicator_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Threat
        fields = [
            'id', 'organization', 'title', 'description', 'threat_type', 
            'severity', 'status', 'source', 'tags', 'metadata',
            'ai_analyzed', 'ai_confidence', 'ai_suggested_severity', 'ai_analysis',
            'assigned_to', 'assigned_to_details', 'created_by', 'created_by_details',
            'first_detected', 'last_activity', 'created_at', 'updated_at',
            'alert_count', 'indicator_count'
        ]
        read_only_fields = ['id', 'organization', 'created_at', 'updated_at', 
                           'ai_analyzed', 'ai_confidence', 'ai_suggested_severity', 'ai_analysis']
    
    def get_alert_count(self, obj):
        return obj.alerts.count()
    
    def get_indicator_count(self, obj):
        return obj.indicators.count()
    
    def create(self, validated_data):
        validated_data['organization'] = self.context['request'].user.organization
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class AlertSerializer(serializers.ModelSerializer):
    acknowledged_by_details = UserMinimalSerializer(source='acknowledged_by', read_only=True)
    resolved_by_details = UserMinimalSerializer(source='resolved_by', read_only=True)
    threat_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Alert
        fields = [
            'id', 'organization', 'title', 'description', 'alert_type',
            'severity', 'status', 'source', 'tags', 'metadata',
            'threat', 'threat_details', 'related_user',
            'acknowledged_by', 'acknowledged_by_details', 'acknowledged_at',
            'resolved_by', 'resolved_by_details', 'resolved_at', 'resolution_notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'organization', 'created_at', 'updated_at',
                           'acknowledged_by', 'acknowledged_at', 'resolved_by', 'resolved_at']
    
    def get_threat_details(self, obj):
        if obj.threat:
            return {
                'id': obj.threat.id,
                'title': obj.threat.title,
                'severity': obj.threat.severity
            }
        return None
    
    def create(self, validated_data):
        validated_data['organization'] = self.context['request'].user.organization
        return super().create(validated_data)


class RiskAssessmentSerializer(serializers.ModelSerializer):
    assessed_by_details = UserMinimalSerializer(source='assessed_by', read_only=True)
    threat_details = serializers.SerializerMethodField()
    
    class Meta:
        model = RiskAssessment
        fields = [
            'id', 'organization', 'threat', 'threat_details',
            'risk_level', 'likelihood', 'impact',
            'vulnerability_analysis', 'impact_analysis', 'mitigation_strategy', 'residual_risk',
            'estimated_cost', 'required_resources', 'timeline',
            'ai_generated', 'ai_confidence', 'ai_recommendations',
            'assessed_by', 'assessed_by_details', 'review_date', 'next_review_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'organization', 'created_at', 'updated_at',
                           'ai_generated', 'ai_confidence', 'ai_recommendations']
    
    def get_threat_details(self, obj):
        return {
            'id': obj.threat.id,
            'title': obj.threat.title,
            'severity': obj.threat.severity,
            'status': obj.threat.status
        }
    
    def create(self, validated_data):
        validated_data['organization'] = self.context['request'].user.organization
        validated_data['assessed_by'] = self.context['request'].user
        return super().create(validated_data)


class ThreatIndicatorSerializer(serializers.ModelSerializer):
    added_by_details = UserMinimalSerializer(source='added_by', read_only=True)
    threat_details = serializers.SerializerMethodField()
    
    class Meta:
        model = ThreatIndicator
        fields = [
            'id', 'organization', 'threat', 'threat_details',
            'indicator_type', 'value', 'description', 'confidence',
            'source', 'first_seen', 'last_seen', 'occurrence_count',
            'is_active', 'is_false_positive', 'tags', 'metadata',
            'action_taken', 'added_by', 'added_by_details',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'organization', 'created_at', 'updated_at']
    
    def get_threat_details(self, obj):
        if obj.threat:
            return {
                'id': obj.threat.id,
                'title': obj.threat.title,
                'severity': obj.threat.severity
            }
        return None
    
    def create(self, validated_data):
        validated_data['organization'] = self.context['request'].user.organization
        validated_data['added_by'] = self.context['request'].user
        return super().create(validated_data)


class WatchlistSerializer(serializers.ModelSerializer):
    added_by_details = UserMinimalSerializer(source='added_by', read_only=True)
    threat_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Watchlist
        fields = [
            'id', 'organization', 'threat', 'threat_details',
            'watchlist_type', 'subject_name', 'subject_id', 'description',
            'risk_level', 'reason', 'attributes',
            'alert_on_detection', 'auto_notify', 'action_instructions',
            'is_active', 'detection_count', 'last_detected',
            'added_by', 'added_by_details', 'notes', 'expiry_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'organization', 'created_at', 'updated_at', 'detection_count']
    
    def get_threat_details(self, obj):
        if obj.threat:
            return {
                'id': obj.threat.id,
                'title': obj.threat.title,
                'severity': obj.threat.severity
            }
        return None
    
    def create(self, validated_data):
        validated_data['organization'] = self.context['request'].user.organization
        validated_data['added_by'] = self.context['request'].user
        return super().create(validated_data)
