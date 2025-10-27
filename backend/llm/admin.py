"""
Admin configuration for LLM models.
"""
from django.contrib import admin
from .models import ChatSession, Message, PromptTemplate, RAGDocument


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ['timestamp']


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'organization', 'bot_type', 'created_at']
    list_filter = ['bot_type', 'organization', 'created_at']
    search_fields = ['title', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'role', 'content_preview', 'timestamp']
    list_filter = ['role', 'timestamp']
    readonly_fields = ['timestamp']
    
    def content_preview(self, obj):
        return obj.content[:100]
    content_preview.short_description = 'Content'


@admin.register(PromptTemplate)
class PromptTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'purpose', 'created_at']
    search_fields = ['name', 'purpose']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(RAGDocument)
class RAGDocumentAdmin(admin.ModelAdmin):
    list_display = ['document_type', 'document_id', 'organization', 'indexed_at']
    list_filter = ['document_type', 'organization', 'indexed_at']
    readonly_fields = ['indexed_at']
