#!/usr/bin/env python3
"""
Script to test and verify superuser login credentials for CISO Assistant.
Run this script to troubleshoot login issues.
"""

import os
import sys
import django
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ciso_assistant.settings')
django.setup()

from django.contrib.auth import get_user_model, authenticate
from django.contrib.sessions.models import Session
from django.utils import timezone

User = get_user_model()

def test_superuser_login():
    """Test superuser login and provide troubleshooting information."""
    
    print("🔍 CISO Assistant Superuser Login Test")
    print("=" * 50)
    
    email = "admin@admin.test"
    password = "Admintest123"
    
    print(f"Testing credentials:")
    print(f"  Email: {email}")
    print(f"  Password: {password}")
    print()
    
    # Check if user exists
    try:
        user = User.objects.get(email=email)
        print("✅ User found in database")
        print(f"   ID: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   First name: {user.first_name}")
        print(f"   Last name: {user.last_name}")
        print(f"   Is superuser: {user.is_superuser}")
        print(f"   Is staff: {getattr(user, 'is_staff', 'N/A')}")
        print(f"   Is active: {user.is_active}")
        print(f"   Date joined: {user.date_joined}")
        print(f"   Last login: {user.last_login}")
        print()
        
    except User.DoesNotExist:
        print("❌ User not found in database")
        print("\nAvailable users:")
        for u in User.objects.all()[:10]:
            print(f"   - {u.email} (superuser: {u.is_superuser})")
        return False
    
    # Test authentication
    print("🔐 Testing authentication...")
    auth_user = authenticate(email=email, password=password)
    
    if auth_user:
        print("✅ Authentication successful!")
        print(f"   Authenticated user: {auth_user.email}")
        print(f"   Is superuser: {auth_user.is_superuser}")
    else:
        print("❌ Authentication failed!")
        print("\nPossible issues:")
        print("   1. Incorrect password")
        print("   2. User is not active")
        print("   3. Authentication backend issues")
        
        # Try to reset password
        print("\n🔧 Attempting to reset password...")
        user.set_password(password)
        user.save()
        print("✅ Password reset completed")
        
        # Test again
        auth_user = authenticate(email=email, password=password)
        if auth_user:
            print("✅ Authentication now works after password reset!")
        else:
            print("❌ Authentication still failing after password reset")
        
        return False
    
    # Check active sessions
    print("\n📊 Session information:")
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    print(f"   Active sessions: {active_sessions.count()}")
    
    # Test login URL
    print("\n🌐 Login URLs to try:")
    print("   Django Admin: http://localhost:8000/admin/")
    print("   CISO Assistant: http://localhost:8000/login/")
    print("   Docker (if using): https://localhost:8443/login/")
    
    print("\n💡 Troubleshooting tips:")
    print("   1. Make sure the backend server is running")
    print("   2. Clear browser cache and cookies")
    print("   3. Try incognito/private browsing mode")
    print("   4. Check browser developer console for errors")
    print("   5. Verify the correct URL (http vs https, port number)")
    
    print("\n🎯 Next steps:")
    print("   1. Start the backend server:")
    print("      cd backend && poetry run python manage.py runserver")
    print("   2. Open browser to: http://localhost:8000/admin/")
    print("   3. Login with:")
    print(f"      Email: {email}")
    print(f"      Password: {password}")
    
    return True

if __name__ == "__main__":
    try:
        success = test_superuser_login()
        if success:
            print("\n🎉 Superuser test completed successfully!")
        else:
            print("\n⚠️  Issues found. Please check the output above.")
    except Exception as e:
        print(f"\n❌ Error running test: {str(e)}")
        print("\nMake sure you're running this from the CISO Assistant root directory")
        print("and that the backend dependencies are installed.")
