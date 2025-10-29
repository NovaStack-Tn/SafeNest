"""
Serializers for incident models.
"""
import hashlib
from rest_framework import serializers
from .models import Incident, IncidentEvent, Evidence, IncidentCategory, IncidentResolution


class IncidentCategorySerializer(serializers.ModelSerializer):
    incident_count = serializers.IntegerField(source='incidents.count', read_only=True)
    
    class Meta:
        model = IncidentCategory
        fields = [
            'id', 'organization', 'name', 'description',
            'color', 'icon', 'severity_default', 'is_active',
            'created_at', 'incident_count'
        ]
        read_only_fields = ['created_at']


class IncidentResolutionSerializer(serializers.ModelSerializer):
    resolved_by_name = serializers.CharField(source='resolved_by.get_full_name', read_only=True)
    
    class Meta:
        model = IncidentResolution
        fields = [
            'id', 'incident', 'resolution_type', 'summary',
            'actions_taken', 'root_cause', 'preventive_measures',
            'related_incidents', 'resolved_by', 'resolved_by_name',
            'resolved_at', 'time_to_detect', 'time_to_resolve', 'metadata'
        ]
        read_only_fields = ['resolved_at']


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
        read_only_fields = ['file_hash', 'file_size', 'file_name', 'uploaded_at']
    
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
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    event_count = serializers.IntegerField(source='events.count', read_only=True)
    evidence_count = serializers.IntegerField(source='evidence.count', read_only=True)
    has_resolution = serializers.SerializerMethodField()
    
    class Meta:
        model = Incident
        fields = [
            'id', 'organization', 'title', 'description',
            'incident_type', 'category', 'category_name', 'category_color',
            'severity', 'status',
            'assignee', 'assignee_name', 'created_by', 'created_by_name',
            'opened_at', 'closed_at', 'updated_at',
            'tags', 'metadata', 'event_count', 'evidence_count',
            'ai_generated', 'ai_confidence', 'extracted_entities', 'has_resolution'
        ]
        read_only_fields = ['opened_at', 'updated_at', 'ai_generated', 'ai_confidence', 'extracted_entities']
    
    def get_has_resolution(self, obj):
        return hasattr(obj, 'resolution')


class IncidentDetailSerializer(IncidentSerializer):
    """Detailed serializer with related events and evidence."""
    events = IncidentEventSerializer(many=True, read_only=True)
    evidence = EvidenceSerializer(many=True, read_only=True)
    resolution = IncidentResolutionSerializer(read_only=True)
    
    class Meta(IncidentSerializer.Meta):
        fields = IncidentSerializer.Meta.fields + ['events', 'evidence', 'resolution']


class IncidentCreateSerializer(serializers.ModelSerializer):
    use_ai_classification = serializers.BooleanField(write_only=True, default=False)
    
    class Meta:
        model = Incident
        fields = [
            'organization', 'title', 'description',
            'incident_type', 'category', 'severity', 'assignee',
            'tags', 'metadata', 'use_ai_classification'
        ]
    
    def create(self, validated_data):
        use_ai = validated_data.pop('use_ai_classification', False)
        
        if use_ai:
            from .ai_service import IncidentAIService
            
            # Classify severity if not provided or requested
            title = validated_data.get('title', '')
            description = validated_data.get('description', '')
            
            if not validated_data.get('severity'):
                severity, confidence = IncidentAIService.classify_severity(title, description)
                validated_data['severity'] = severity
                validated_data['ai_confidence'] = confidence
            
            # Extract entities
            entities = IncidentAIService.extract_entities(description)
            validated_data['extracted_entities'] = entities
            
            # Suggest category if not provided
            if not validated_data.get('category'):
                org = validated_data.get('organization')
                if org:
                    categories = list(org.incident_categories.filter(is_active=True).values_list('name', flat=True))
                    if categories:
                        suggested = IncidentAIService.suggest_category(title, description, categories)
                        if suggested:
                            cat = org.incident_categories.filter(name=suggested).first()
                            if cat:
                                validated_data['category'] = cat
        
        return super().create(validated_data)


class AutoIncidentCreateSerializer(serializers.Serializer):
    """Serializer for auto-creating incidents from alerts."""
    alert_id = serializers.CharField()
    alert_type = serializers.CharField()
    title = serializers.CharField()
    message = serializers.CharField()
    severity = serializers.CharField(required=False)
    timestamp = serializers.DateTimeField(required=False)
    metadata = serializers.JSONField(required=False, default=dict)
    organization_id = serializers.IntegerField()
    
    def create(self, validated_data):
        from .ai_service import IncidentAIService
        from .models import Incident
        from core.models import Organization
        
        org_id = validated_data.pop('organization_id')
        organization = Organization.objects.get(id=org_id)
        
        # Use AI to generate incident data
        alert_data = {
            'id': validated_data.get('alert_id'),
            'type': validated_data.get('alert_type'),
            'title': validated_data.get('title'),
            'message': validated_data.get('message'),
            'severity': validated_data.get('severity'),
            'timestamp': validated_data.get('timestamp'),
        }
        
        incident_data = IncidentAIService.auto_create_from_alert(alert_data)
        incident_data['organization'] = organization
        
        # Create the incident
        incident = Incident.objects.create(**incident_data)
        
        return incident
