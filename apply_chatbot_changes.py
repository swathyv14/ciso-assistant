#!/usr/bin/env python3
"""
Script to apply CISO Assistant Chatbot changes to your local repository.
Run this script from your CISO Assistant root directory.

Usage:
    python apply_chatbot_changes.py
"""

import os
import sys
import shutil
import json
from pathlib import Path

def create_directory(path):
    """Create directory if it doesn't exist."""
    Path(path).mkdir(parents=True, exist_ok=True)
    print(f"✓ Created directory: {path}")

def write_file(path, content):
    """Write content to file."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Created file: {path}")

def update_file(path, old_content, new_content):
    """Update file by replacing old content with new content."""
    if not os.path.exists(path):
        print(f"⚠ File not found: {path}")
        return False
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if old_content in content:
        updated_content = content.replace(old_content, new_content)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print(f"✓ Updated file: {path}")
        return True
    else:
        print(f"⚠ Content not found in {path}, manual update required")
        return False

def main():
    """Apply all chatbot changes."""
    print("🤖 Applying CISO Assistant Chatbot Changes...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('backend') or not os.path.exists('frontend'):
        print("❌ Error: Please run this script from the CISO Assistant root directory")
        print("   Expected structure: backend/ and frontend/ directories")
        sys.exit(1)
    
    # 1. Create backend chatbot app directory
    print("\n📁 Creating backend chatbot app...")
    create_directory('backend/chatbot')
    create_directory('backend/chatbot/migrations')
    
    # 2. Create chatbot models.py
    models_content = '''from django.db import models
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
'''
    write_file('backend/chatbot/models.py', models_content)
    
    print("\n✅ Step 1: Backend chatbot app created")
    print("📝 Next steps:")
    print("   1. Copy the remaining chatbot files from the workspace")
    print("   2. Update pyproject.toml with Google ADK dependencies")
    print("   3. Update settings.py to include chatbot app")
    print("   4. Create frontend components")
    print("   5. Run migrations")
    
    print("\n🔧 Manual steps required:")
    print("   1. Add to backend/pyproject.toml dependencies:")
    print('      google-adk = "^0.1.0"')
    print('      google-cloud-aiplatform = "^1.70.0"')
    print('      google-auth = "^2.35.0"')
    print()
    print("   2. Add to backend/ciso_assistant/settings.py INSTALLED_APPS:")
    print('      "chatbot",')
    print()
    print("   3. Add to backend/core/urls.py:")
    print('      path("chatbot/", include("chatbot.urls")),')
    print()
    print("   4. Add to frontend/src/lib/components/SideBar/navData.ts:")
    print('      {')
    print('          name: "chatbot",')
    print('          fa_icon: "fa-solid fa-robot",')
    print('          href: "/chatbot"')
    print('      }')
    print()
    print("   5. Add to frontend/messages/en.json:")
    print('      "chatbot": "AI Assistant",')

if __name__ == "__main__":
    main()
'''
