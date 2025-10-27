"""
URL routing for LLM app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ChatSessionViewSet, MessageViewSet, PromptTemplateViewSet, LLMAPIViewSet
)

router = DefaultRouter()
router.register(r'sessions', ChatSessionViewSet, basename='chat-session')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'templates', PromptTemplateViewSet, basename='prompt-template')
router.register(r'api', LLMAPIViewSet, basename='llm-api')

urlpatterns = [
    path('', include(router.urls)),
]
