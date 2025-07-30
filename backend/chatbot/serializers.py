from rest_framework import serializers
from core.serializers import BaseModelSerializer
from .models import ChatSession, ChatMessage, ChatFile


class ChatMessageSerializer(BaseModelSerializer):
    """
    Serializer for chat messages.
    """
    class Meta:
        model = ChatMessage
        fields = ['id', 'role', 'content', 'metadata', 'created_at']
        read_only_fields = ['id', 'created_at']


class ChatFileSerializer(BaseModelSerializer):
    """
    Serializer for chat files.
    """
    class Meta:
        model = ChatFile
        fields = ['id', 'file', 'original_filename', 'file_type', 'processed', 'processing_result', 'created_at']
        read_only_fields = ['id', 'processed', 'processing_result', 'created_at']


class ChatSessionSerializer(BaseModelSerializer):
    """
    Serializer for chat sessions with messages.
    """
    messages = ChatMessageSerializer(many=True, read_only=True)
    files = ChatFileSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatSession
        fields = ['id', 'title', 'is_active', 'messages', 'files', 'message_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_message_count(self, obj):
        return obj.messages.count()


class ChatSessionListSerializer(BaseModelSerializer):
    """
    Simplified serializer for listing chat sessions.
    """
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatSession
        fields = ['id', 'title', 'is_active', 'message_count', 'last_message', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_message_count(self, obj):
        return obj.messages.count()
    
    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return {
                'role': last_msg.role,
                'content': last_msg.content[:100] + "..." if len(last_msg.content) > 100 else last_msg.content,
                'created_at': last_msg.created_at
            }
        return None


class ChatMessageCreateSerializer(serializers.Serializer):
    """
    Serializer for creating new chat messages and getting responses.
    """
    message = serializers.CharField(max_length=10000)
    session_id = serializers.UUIDField(required=False)
    files = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        allow_empty=True
    )
    
    def validate_message(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message cannot be empty.")
        return value.strip()
