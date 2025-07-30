from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatSessionViewSet, ChatMessageViewSet, ChatbotViewSet

router = DefaultRouter()
router.register(r'sessions', ChatSessionViewSet, basename='chat-sessions')
router.register(r'messages', ChatMessageViewSet, basename='chat-messages')
router.register(r'bot', ChatbotViewSet, basename='chatbot')

urlpatterns = [
    path('', include(router.urls)),
]
