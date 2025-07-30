# PowerShell script to apply CISO Assistant Chatbot changes
# Run this from your CISO Assistant root directory

Write-Host "🤖 Applying CISO Assistant Chatbot Changes..." -ForegroundColor Green
Write-Host "=" * 50

# Check if we're in the right directory
if (-not (Test-Path "backend") -or -not (Test-Path "frontend")) {
    Write-Host "❌ Error: Please run this script from the CISO Assistant root directory" -ForegroundColor Red
    Write-Host "   Expected structure: backend/ and frontend/ directories" -ForegroundColor Red
    exit 1
}

# Function to create directory
function New-DirectoryIfNotExists {
    param($Path)
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
        Write-Host "✓ Created directory: $Path" -ForegroundColor Green
    }
}

# Function to create file
function New-FileWithContent {
    param($Path, $Content)
    $dir = Split-Path $Path -Parent
    if ($dir -and -not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    Set-Content -Path $Path -Value $Content -Encoding UTF8
    Write-Host "✓ Created file: $Path" -ForegroundColor Green
}

Write-Host "`n📁 Creating backend chatbot app..." -ForegroundColor Yellow

# Create backend directories
New-DirectoryIfNotExists "backend\chatbot"
New-DirectoryIfNotExists "backend\chatbot\migrations"

# Create __init__.py
New-FileWithContent "backend\chatbot\__init__.py" ""

# Create apps.py
$appsContent = @"
from django.apps import AppConfig


class ChatbotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chatbot'
"@
New-FileWithContent "backend\chatbot\apps.py" $appsContent

# Create admin.py
$adminContent = @"
from django.contrib import admin

# Register your models here.
"@
New-FileWithContent "backend\chatbot\admin.py" $adminContent

# Create tests.py
$testsContent = @"
from django.test import TestCase

# Create your tests here.
"@
New-FileWithContent "backend\chatbot\tests.py" $testsContent

# Create models.py
$modelsContent = @"
from django.db import models
from django.contrib.auth import get_user_model
from core.base_models import AbstractBaseModel
import uuid

User = get_user_model()


class ChatSession(AbstractBaseModel):
    """"""
    Represents a chat session between a user and the CISO Assistant chatbot.
    """"""
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
    """"""
    Represents individual messages in a chat session.
    """"""
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
    """"""
    Represents files uploaded during chat sessions for processing.
    """"""
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='chatbot_files/')
    original_filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50)
    processed = models.BooleanField(default=False)
    processing_result = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"File: {self.original_filename} - Session {self.session.id}"
"@
New-FileWithContent "backend\chatbot\models.py" $modelsContent

Write-Host "`n✅ Backend chatbot app structure created!" -ForegroundColor Green

Write-Host "`n📝 MANUAL STEPS REQUIRED:" -ForegroundColor Yellow
Write-Host "1. Add Google ADK dependencies to backend/pyproject.toml:" -ForegroundColor Cyan
Write-Host '   google-adk = "^0.1.0"' -ForegroundColor White
Write-Host '   google-cloud-aiplatform = "^1.70.0"' -ForegroundColor White
Write-Host '   google-auth = "^2.35.0"' -ForegroundColor White

Write-Host "`n2. Add chatbot to backend/ciso_assistant/settings.py INSTALLED_APPS:" -ForegroundColor Cyan
Write-Host '   "chatbot",' -ForegroundColor White

Write-Host "`n3. Add chatbot URLs to backend/core/urls.py:" -ForegroundColor Cyan
Write-Host '   path("chatbot/", include("chatbot.urls")),' -ForegroundColor White

Write-Host "`n4. Install dependencies:" -ForegroundColor Cyan
Write-Host "   cd backend" -ForegroundColor White
Write-Host "   poetry add google-adk google-cloud-aiplatform google-auth" -ForegroundColor White

Write-Host "`n5. Run migrations:" -ForegroundColor Cyan
Write-Host "   poetry run python manage.py makemigrations chatbot" -ForegroundColor White
Write-Host "   poetry run python manage.py migrate" -ForegroundColor White

Write-Host "`n🎯 After completing these steps, you'll need to:" -ForegroundColor Yellow
Write-Host "   - Copy the remaining chatbot files (views.py, serializers.py, agents.py, urls.py)" -ForegroundColor White
Write-Host "   - Create frontend components" -ForegroundColor White
Write-Host "   - Update navigation and translations" -ForegroundColor White

Write-Host "`n📧 Contact me for the complete file contents!" -ForegroundColor Green
