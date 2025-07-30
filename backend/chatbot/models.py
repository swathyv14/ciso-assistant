from django.db import models
from django.contrib.auth import get_user_model
from core.base_models import AbstractBaseModel
import uuid

User = get_user_model()


class ChatSession(AbstractBaseModel):
    """
    Represents a chat session between a user and the CISO Assistant chatbot.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=200, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Chat Session {self.id} - {self.user.email}"

    def save(self, *args, **kwargs):
        if not self.title and self.messages.exists():
            # Set title based on first message
            first_message = self.messages.filter(role='user').first()
            if first_message:
                self.title = first_message.content[:50] + "..." if len(first_message.content) > 50 else first_message.content
        super().save(*args, **kwargs)


class ChatMessage(AbstractBaseModel):
    """
    Represents individual messages in a chat session.
    """
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)  # Store additional info like API calls made, etc.

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


class ChatFile(AbstractBaseModel):
    """
    Represents files uploaded during chat sessions for processing.
    """
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='chatbot_files/')
    original_filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50)
    processed = models.BooleanField(default=False)
    processing_result = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"File: {self.original_filename} - Session {self.session.id}"
