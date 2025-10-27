"""
API views for LLM services.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import ChatSession, Message, PromptTemplate
from .serializers import (
    ChatSessionSerializer, ChatSessionDetailSerializer,
    MessageSerializer, PromptTemplateSerializer, ChatMessageSerializer
)
from .services import AssistantBotService, RecommendationBotService, AnalysisBotService


class ChatSessionViewSet(viewsets.ModelViewSet):
    """API endpoint for chat sessions."""
    queryset = ChatSession.objects.select_related('organization', 'user').prefetch_related('messages')
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['bot_type', 'user']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ChatSessionDetailSerializer
        return ChatSessionSerializer
    
    def get_queryset(self):
        """Filter by organization for non-admin users."""
        user = self.request.user
        queryset = super().get_queryset()
        
        if not user.is_staff and user.organization:
            queryset = queryset.filter(organization=user.organization)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set user to current user."""
        serializer.save(user=self.request.user, organization=self.request.user.organization)


class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for messages (read-only)."""
    queryset = Message.objects.select_related('session')
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['session', 'role']


class PromptTemplateViewSet(viewsets.ModelViewSet):
    """API endpoint for prompt templates."""
    queryset = PromptTemplate.objects.all()
    serializer_class = PromptTemplateSerializer
    permission_classes = [IsAuthenticated]


class LLMAPIViewSet(viewsets.ViewSet):
    """Main LLM API endpoints."""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def chat(self, request):
        """Chat with assistant bot."""
        serializer = ChatMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        if not user.organization:
            return Response(
                {'error': 'User has no organization'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        message_text = serializer.validated_data['message']
        bot_type = serializer.validated_data['bot_type']
        session_id = serializer.validated_data.get('session_id')
        
        # Get or create session
        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id, user=user)
            except ChatSession.DoesNotExist:
                return Response(
                    {'error': 'Session not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            session = ChatSession.objects.create(
                organization=user.organization,
                user=user,
                bot_type=bot_type,
                title=message_text[:50]
            )
        
        # Get conversation history
        history = [
            {'role': m.role, 'content': m.content}
            for m in session.messages.all()
        ]
        
        # Process with appropriate bot
        if bot_type == 'assistant':
            bot = AssistantBotService(user.organization.id, user.id)
            response = bot.chat(message_text, history)
        else:
            # For other bot types, use simple completion
            from .services import LLMService
            llm = LLMService()
            messages = history + [{'role': 'user', 'content': message_text}]
            llm_response = llm.chat_completion(messages)
            response = {
                'content': llm_response['content'],
                'tool_results': []
            }
        
        # Save messages
        Message.objects.create(
            session=session,
            role='user',
            content=message_text
        )
        
        assistant_message = Message.objects.create(
            session=session,
            role='assistant',
            content=response['content']
        )
        
        # Save tool results if any
        if response.get('tool_results'):
            for tool_result in response['tool_results']:
                Message.objects.create(
                    session=session,
                    role='tool',
                    tool_name=tool_result['tool'],
                    tool_result=tool_result['result'],
                    content=str(tool_result['result'])
                )
        
        return Response({
            'session_id': session.id,
            'message': response['content'],
            'tool_results': response.get('tool_results', [])
        })
    
    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        """Get security recommendations."""
        user = request.user
        if not user.organization:
            return Response(
                {'error': 'User has no organization'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        bot = RecommendationBotService(user.organization.id)
        recommendations = bot.generate_recommendations()
        
        return Response({
            'recommendations': recommendations,
            'count': len(recommendations)
        })
    
    @action(detail=False, methods=['get'])
    def weekly_analysis(self, request):
        """Get weekly security analysis."""
        user = request.user
        if not user.organization:
            return Response(
                {'error': 'User has no organization'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        bot = AnalysisBotService(user.organization.id)
        analysis = bot.generate_weekly_analysis()
        
        return Response({
            'analysis': analysis
        })
