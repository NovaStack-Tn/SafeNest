"""
Serializers for security models.
"""
from rest_framework import serializers
from .models import LoginEvent, AnomalyRule, Alert


class LoginEventSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = LoginEvent
        fields = [
            'id', 'user', 'user_name', 'username', 'success',
            'ip_address', 'country_code', 'country_name', 'city',
            'latitude', 'longitude', 'user_agent', 'device_type',
            'browser', 'os', 'device_fingerprint', 'risk_score',
            'is_anomaly', 'anomaly_reasons', 'timestamp', 'metadata'
        ]
        read_only_fields = ['timestamp']


class AnomalyRuleSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = AnomalyRule
        fields = [
            'id', 'organization', 'name', 'rule_type', 'description',
            'config', 'threshold', 'severity', 'active',
            'auto_create_incident', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class AlertSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    rule_name = serializers.CharField(source='triggered_by_rule.name', read_only=True)
    
    class Meta:
        model = Alert
        fields = [
            'id', 'organization', 'title', 'message', 'severity', 'status',
            'related_model', 'related_id', 'triggered_by_rule', 'rule_name',
            'assigned_to', 'assigned_to_name', 'created_by', 'created_by_name',
            'created_at', 'updated_at', 'resolved_at', 'metadata'
        ]
        read_only_fields = ['created_at', 'updated_at']


class AlertCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = [
            'organization', 'title', 'message', 'severity',
            'related_model', 'related_id', 'metadata'
        ]
