"""
Serializers for incident models.
"""
import hashlib
from rest_framework import serializers
from .models import Incident, IncidentEvent, Evidence


class IncidentEventSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source='actor.get_full_name', read_only=True)
    
    class Meta:
        model = IncidentEvent
        fields = [
            'id', 'incident', 'action', 'description',
            'actor', 'actor_name', 'metadata', 'timestamp'
        ]
        read_only_fields = ['timestamp']


class EvidenceSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Evidence
        fields = [
            'id', 'incident', 'file', 'file_url', 'file_name',
            'file_size', 'file_hash', 'kind', 'description',
            'uploaded_by', 'uploaded_by_name', 'uploaded_at', 'metadata'
        ]
        read_only_fields = ['file_hash', 'file_size', 'uploaded_at']
    
    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None
    
    def create(self, validated_data):
        """Calculate file hash and size on upload."""
        file_obj = validated_data.get('file')
        if file_obj:
            # Calculate SHA-256 hash
            hash_sha256 = hashlib.sha256()
            for chunk in file_obj.chunks():
                hash_sha256.update(chunk)
            validated_data['file_hash'] = hash_sha256.hexdigest()
            validated_data['file_size'] = file_obj.size
            validated_data['file_name'] = file_obj.name
        
        return super().create(validated_data)


class IncidentSerializer(serializers.ModelSerializer):
    assignee_name = serializers.CharField(source='assignee.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    event_count = serializers.IntegerField(source='events.count', read_only=True)
    evidence_count = serializers.IntegerField(source='evidence.count', read_only=True)
    
    class Meta:
        model = Incident
        fields = [
            'id', 'organization', 'title', 'description',
            'incident_type', 'severity', 'status',
            'assignee', 'assignee_name', 'created_by', 'created_by_name',
            'opened_at', 'closed_at', 'updated_at',
            'tags', 'metadata', 'event_count', 'evidence_count'
        ]
        read_only_fields = ['opened_at', 'updated_at']


class IncidentDetailSerializer(IncidentSerializer):
    """Detailed serializer with related events and evidence."""
    events = IncidentEventSerializer(many=True, read_only=True)
    evidence = EvidenceSerializer(many=True, read_only=True)
    
    class Meta(IncidentSerializer.Meta):
        fields = IncidentSerializer.Meta.fields + ['events', 'evidence']


class IncidentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incident
        fields = [
            'organization', 'title', 'description',
            'incident_type', 'severity', 'assignee', 'tags', 'metadata'
        ]
