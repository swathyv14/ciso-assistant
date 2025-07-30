#!/bin/bash

# CISO Assistant Test Environment Setup Script
# This script sets up a complete test environment with chatbot functionality

set -e  # Exit on any error

echo "🚀 Setting up CISO Assistant Test Environment..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    print_error "Please run this script from the CISO Assistant root directory"
    exit 1
fi

print_info "Step 1: Enabling chatbot functionality..."

# Enable chatbot in settings.py
sed -i 's/# "chatbot",  # Temporarily disabled for debugging/"chatbot",/' backend/ciso_assistant/settings.py
print_status "Enabled chatbot app in settings.py"

# Enable chatbot URLs
sed -i 's/# path("chatbot\/", include("chatbot.urls")),  # Temporarily disabled for debugging/path("chatbot\/", include("chatbot.urls")),/' backend/core/urls.py
print_status "Enabled chatbot URLs in core/urls.py"

# Enable Google ADK imports (if they exist)
if grep -q "# Temporarily disable Google ADK" backend/chatbot/agents.py; then
    sed -i 's/# Temporarily disable Google ADK to debug startup issues/# Google ADK imports enabled/' backend/chatbot/agents.py
    sed -i 's/ADK_AVAILABLE = False/# ADK_AVAILABLE = False/' backend/chatbot/agents.py
    sed -i 's/# try:/try:/' backend/chatbot/agents.py
    sed -i 's/# except ImportError:/except ImportError:/' backend/chatbot/agents.py
    print_status "Enabled Google ADK imports in agents.py"
fi

print_info "Step 2: Installing dependencies..."

# Install backend dependencies
cd backend
if command -v poetry &> /dev/null; then
    poetry install
    print_status "Backend dependencies installed with Poetry"
else
    print_warning "Poetry not found, please install dependencies manually"
fi

# Install frontend dependencies
cd ../frontend
if command -v npm &> /dev/null; then
    npm install
    print_status "Frontend dependencies installed with npm"
else
    print_warning "npm not found, please install frontend dependencies manually"
fi

cd ..

print_info "Step 3: Setting up database..."

# Run migrations
cd backend
if command -v poetry &> /dev/null; then
    poetry run python manage.py migrate
    print_status "Database migrations completed"
else
    python manage.py migrate
    print_status "Database migrations completed"
fi

print_info "Step 4: Creating test superuser..."

# Create test superuser
if command -v poetry &> /dev/null; then
    poetry run python manage.py create_test_superuser --force
else
    python manage.py create_test_superuser --force
fi

cd ..

print_info "Step 5: Environment configuration..."

# Create .env file if it doesn't exist
if [ ! -f "backend/.env" ]; then
    cp backend/.env.example backend/.env
    print_status "Created .env file from template"
    print_warning "Please add your GOOGLE_API_KEY to backend/.env for full AI functionality"
else
    print_info ".env file already exists"
fi

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
print_status "CISO Assistant is ready for testing!"
echo ""
echo "📋 What's been set up:"
echo "  ✅ Chatbot functionality enabled"
echo "  ✅ Dependencies installed"
echo "  ✅ Database migrations applied"
echo "  ✅ Test superuser created"
echo "  ✅ Environment configuration ready"
echo ""
echo "🔑 Test Superuser Credentials:"
echo "  Email: admin@admin.test"
echo "  Password: Admintest123"
echo ""
echo "🚀 To start the application:"
echo ""
echo "  Option 1 - Docker (Recommended):"
echo "    docker-compose -f docker-compose-build.yml up -d --build"
echo ""
echo "  Option 2 - Manual:"
echo "    # Terminal 1 (Backend):"
echo "    cd backend && poetry run python manage.py runserver"
echo ""
echo "    # Terminal 2 (Frontend):"
echo "    cd frontend && npm run dev"
echo ""
echo "🌐 Access URLs:"
echo "  Frontend: http://localhost:5173 (manual) or https://localhost:8443 (Docker)"
echo "  Backend API: http://localhost:8000/api/"
echo "  Admin: http://localhost:8000/admin/"
echo "  Chatbot: Navigate to 'AI Assistant' in the sidebar"
echo ""
echo "💡 For full AI capabilities, add your Google API key to backend/.env:"
echo "   GOOGLE_API_KEY=your_google_api_key_here"
echo ""
print_status "Happy testing! 🤖"
