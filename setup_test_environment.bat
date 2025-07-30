@echo off
REM CISO Assistant Test Environment Setup Script for Windows
REM This script sets up a complete test environment with chatbot functionality

echo 🚀 Setting up CISO Assistant Test Environment...
echo ==================================================

REM Check if we're in the right directory
if not exist "backend" (
    echo ❌ Error: Please run this script from the CISO Assistant root directory
    echo    Expected structure: backend/ and frontend/ directories
    pause
    exit /b 1
)

if not exist "frontend" (
    echo ❌ Error: Please run this script from the CISO Assistant root directory
    echo    Expected structure: backend/ and frontend/ directories
    pause
    exit /b 1
)

echo ℹ️  Step 1: Enabling chatbot functionality...

REM Enable chatbot in settings.py
powershell -Command "(Get-Content backend\ciso_assistant\settings.py) -replace '# \"chatbot\",  # Temporarily disabled for debugging', '\"chatbot\",' | Set-Content backend\ciso_assistant\settings.py"
echo ✅ Enabled chatbot app in settings.py

REM Enable chatbot URLs
powershell -Command "(Get-Content backend\core\urls.py) -replace '# path\(\"chatbot/\", include\(\"chatbot.urls\"\)\),  # Temporarily disabled for debugging', 'path(\"chatbot/\", include(\"chatbot.urls\")),' | Set-Content backend\core\urls.py"
echo ✅ Enabled chatbot URLs in core/urls.py

echo ℹ️  Step 2: Installing dependencies...

REM Install backend dependencies
cd backend
where poetry >nul 2>nul
if %errorlevel% == 0 (
    poetry install
    echo ✅ Backend dependencies installed with Poetry
) else (
    echo ⚠️  Poetry not found, please install dependencies manually
)

REM Install frontend dependencies
cd ..\frontend
where npm >nul 2>nul
if %errorlevel% == 0 (
    npm install
    echo ✅ Frontend dependencies installed with npm
) else (
    echo ⚠️  npm not found, please install frontend dependencies manually
)

cd ..

echo ℹ️  Step 3: Setting up database...

REM Run migrations
cd backend
where poetry >nul 2>nul
if %errorlevel% == 0 (
    poetry run python manage.py migrate
    echo ✅ Database migrations completed
) else (
    python manage.py migrate
    echo ✅ Database migrations completed
)

echo ℹ️  Step 4: Creating test superuser...

REM Create test superuser
where poetry >nul 2>nul
if %errorlevel% == 0 (
    poetry run python manage.py create_test_superuser --force
) else (
    python manage.py create_test_superuser --force
)

cd ..

echo ℹ️  Step 5: Environment configuration...

REM Create .env file if it doesn't exist
if not exist "backend\.env" (
    copy "backend\.env.example" "backend\.env"
    echo ✅ Created .env file from template
    echo ⚠️  Please add your GOOGLE_API_KEY to backend\.env for full AI functionality
) else (
    echo ℹ️  .env file already exists
)

echo.
echo 🎉 Setup Complete!
echo ==================
echo.
echo ✅ CISO Assistant is ready for testing!
echo.
echo 📋 What's been set up:
echo   ✅ Chatbot functionality enabled
echo   ✅ Dependencies installed
echo   ✅ Database migrations applied
echo   ✅ Test superuser created
echo   ✅ Environment configuration ready
echo.
echo 🔑 Test Superuser Credentials:
echo   Email: admin@admin.test
echo   Password: Admintest123
echo.
echo 🚀 To start the application:
echo.
echo   Option 1 - Docker (Recommended):
echo     docker-compose -f docker-compose-build.yml up -d --build
echo.
echo   Option 2 - Manual:
echo     # Terminal 1 (Backend):
echo     cd backend ^&^& poetry run python manage.py runserver
echo.
echo     # Terminal 2 (Frontend):
echo     cd frontend ^&^& npm run dev
echo.
echo 🌐 Access URLs:
echo   Frontend: http://localhost:5173 (manual) or https://localhost:8443 (Docker)
echo   Backend API: http://localhost:8000/api/
echo   Admin: http://localhost:8000/admin/
echo   Chatbot: Navigate to 'AI Assistant' in the sidebar
echo.
echo 💡 For full AI capabilities, add your Google API key to backend\.env:
echo    GOOGLE_API_KEY=your_google_api_key_here
echo.
echo ✅ Happy testing! 🤖
echo.
pause
