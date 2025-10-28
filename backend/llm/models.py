"""
LLM models: ChatSession, Message, PromptTemplate
"""
from django.db import models
from django.contrib.auth import get_user_model
# Temporarily disabled - install pgvector extension first
# from pgvector.django import VectorField
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class ChatSession(models.Model):
    """Chat session with AI assistant."""
    BOT_TYPE_CHOICES = [
        ('assistant', 'General Assistant'),
        ('recommendation', 'Recommendation Bot'),
        ('analysis', 'Analysis Bot'),
    ]
    
    organization = models.ForeignKey(
        'core.Organization',
        on_delete=models.CASCADE,
        related_name='chat_sessions'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_sessions'
    )
    bot_type = models.CharField(max_length=20, choices=BOT_TYPE_CHOICES, default='assistant')
    title = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['-updated_at']),
            models.Index(fields=['organization', 'user', '-updated_at']),
        ]
        verbose_name = _('Chat Session')
        verbose_name_plural = _('Chat Sessions')
    
    def __str__(self):
        return f"{self.title or f'Session {self.id}'} - {self.user.username}"


class Message(models.Model):
    """Message in a chat session."""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('tool', 'Tool'),
        ('system', 'System'),
    ]
    
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    
    # Tool call data
    tool_name = models.CharField(max_length=100, blank=True)
    tool_args = models.JSONField(default=dict, blank=True)
    tool_result = models.JSONField(default=dict, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['session', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}"


class PromptTemplate(models.Model):
    """Reusable prompt templates."""
    name = models.CharField(max_length=255, unique=True)
    purpose = models.CharField(max_length=255)
    template_text = models.TextField(help_text="Use {variable} for placeholders")
    variables = models.JSONField(
        default=list,
        help_text="List of required variable names"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def render(self, **kwargs):
        """Render template with variables."""
        return self.template_text.format(**kwargs)


class RAGDocument(models.Model):
    """Documents for RAG (Retrieval Augmented Generation)."""
    organization = models.ForeignKey(
        'core.Organization',
        on_delete=models.CASCADE,
        related_name='rag_documents'
    )
    document_type = models.CharField(max_length=50)  # 'alert', 'incident', 'login_event'
    document_id = models.CharField(max_length=255)
    content = models.TextField()
    # Temporarily using TextField - will change to VectorField after pgvector installation
    embedding = models.TextField(help_text="Document embedding vector (temp: install pgvector)")
    
    metadata = models.JSONField(default=dict, blank=True)
    indexed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-indexed_at']
        indexes = [
            models.Index(fields=['organization', 'document_type']),
        ]
        unique_together = ['document_type', 'document_id']
    
    def __str__(self):
        return f"{self.document_type}:{self.document_id}"
