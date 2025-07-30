import asyncio
import logging
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.contrib.auth import get_user_model
from core.views import BaseModelViewSet
from .models import ChatSession, ChatMessage, ChatFile
from .serializers import (
    ChatSessionSerializer,
    ChatSessionListSerializer,
    ChatMessageSerializer,
    ChatMessageCreateSerializer,
    ChatFileSerializer
)
from .agents import get_agent

User = get_user_model()
logger = logging.getLogger(__name__)


class ChatSessionViewSet(BaseModelViewSet):
    """
    ViewSet for managing chat sessions.
    """
    model = ChatSession
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return ChatSessionListSerializer
        return ChatSessionSerializer

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive a chat session."""
        session = self.get_object()
        session.is_active = False
        session.save()
        return Response({'status': 'session archived'})

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restore an archived chat session."""
        session = self.get_object()
        session.is_active = True
        session.save()
        return Response({'status': 'session restored'})


class ChatMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing chat messages.
    """
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        session_id = self.request.query_params.get('session_id')
        if session_id:
            return ChatMessage.objects.filter(
                session_id=session_id,
                session__user=self.request.user
            )
        return ChatMessage.objects.filter(session__user=self.request.user)


class ChatbotViewSet(viewsets.ViewSet):
    """
    Main chatbot interaction viewset.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    @action(detail=False, methods=['post'])
    def chat(self, request):
        """
        Main chat endpoint for sending messages and getting responses.
        """
        serializer = ChatMessageCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_message = serializer.validated_data['message']
            session_id = serializer.validated_data.get('session_id')
            files = serializer.validated_data.get('files', [])

            # Get or create chat session
            if session_id:
                try:
                    session = ChatSession.objects.get(id=session_id, user=request.user)
                except ChatSession.DoesNotExist:
                    return Response(
                        {'error': 'Chat session not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                session = ChatSession.objects.create(user=request.user)

            # Save user message
            user_msg = ChatMessage.objects.create(
                session=session,
                role='user',
                content=user_message
            )

            # Process uploaded files if any
            file_results = []
            if files:
                agent = get_agent()
                for file in files:
                    chat_file = ChatFile.objects.create(
                        session=session,
                        file=file,
                        original_filename=file.name,
                        file_type=file.name.split('.')[-1] if '.' in file.name else 'unknown'
                    )

                    # Process the file
                    processing_result = agent.process_file(chat_file.file.path, chat_file.file_type)
                    chat_file.processing_result = processing_result
                    chat_file.processed = True
                    chat_file.save()

                    file_results.append(processing_result)

            # Get conversation context
            recent_messages = session.messages.order_by('-created_at')[:10]
            context = {
                'history': [
                    {'role': msg.role, 'content': msg.content}
                    for msg in reversed(recent_messages)
                ],
                'files': file_results
            }

            # Get agent response
            agent = get_agent()

            # Run async method in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                agent_response = loop.run_until_complete(
                    agent.process_message(user_message, context)
                )
            finally:
                loop.close()

            # Save agent response
            assistant_msg = ChatMessage.objects.create(
                session=session,
                role='assistant',
                content=agent_response,
                metadata={'files_processed': len(file_results)}
            )

            # Update session title if it's the first exchange
            if not session.title:
                session.title = user_message[:50] + "..." if len(user_message) > 50 else user_message
                session.save()

            return Response({
                'session_id': str(session.id),
                'user_message': ChatMessageSerializer(user_msg).data,
                'assistant_response': ChatMessageSerializer(assistant_msg).data,
                'files_processed': len(file_results)
            })

        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            return Response(
                {'error': f'An error occurred while processing your message: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def health(self, request):
        """
        Health check endpoint for the chatbot service.
        """
        try:
            agent = get_agent()
            return Response({
                'status': 'healthy',
                'agent_initialized': agent is not None,
                'message': 'Chatbot service is running'
            })
        except Exception as e:
            return Response({
                'status': 'unhealthy',
                'error': str(e)
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    @action(detail=False, methods=['get'])
    def capabilities(self, request):
        """
        Get chatbot capabilities and available features.
        """
        return Response({
            'capabilities': [
                'Answer questions about CISO Assistant features',
                'Provide cybersecurity guidance',
                'Help with risk management',
                'Assist with compliance assessments',
                'Explain security frameworks',
                'Process uploaded documents',
                'Access CISO Assistant data via API'
            ],
            'supported_file_types': ['pdf', 'docx', 'txt', 'xlsx', 'csv'],
            'api_endpoints': [
                '/frameworks',
                '/risk-scenarios',
                '/assets',
                '/compliance-assessments',
                '/applied-controls',
                '/users',
                '/folders'
            ]
        })
