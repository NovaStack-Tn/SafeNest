"""
Serializers for LLM models.
"""
from rest_framework import serializers
from .models import ChatSession, Message, PromptTemplate


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'session', 'role', 'content', 'tool_name', 'tool_args', 'tool_result', 'timestamp']
        read_only_fields = ['timestamp']


class ChatSessionSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    message_count = serializers.IntegerField(source='messages.count', read_only=True)
    
    class Meta:
        model = ChatSession
        fields = ['id', 'organization', 'user', 'user_name', 'bot_type', 'title', 'message_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ChatSessionDetailSerializer(ChatSessionSerializer):
    """Detailed serializer with messages."""
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta(ChatSessionSerializer.Meta):
        fields = ChatSessionSerializer.Meta.fields + ['messages']


class PromptTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptTemplate
        fields = ['id', 'name', 'purpose', 'template_text', 'variables', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ChatMessageSerializer(serializers.Serializer):
    """Serializer for chat request."""
    session_id = serializers.IntegerField(required=False)
    message = serializers.CharField()
    bot_type = serializers.ChoiceField(choices=['assistant', 'recommendation', 'analysis'], default='assistant')
