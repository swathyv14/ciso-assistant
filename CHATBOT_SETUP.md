# CISO Assistant AI Chatbot Setup Guide

This guide will help you set up and configure the AI chatbot feature in CISO Assistant.

## Overview

The CISO Assistant AI Chatbot is an intelligent assistant that can:
- Answer questions about CISO Assistant features and functionality
- Provide cybersecurity guidance and best practices
- Help with risk management and compliance tasks
- Process uploaded documents (PDF, Word, Excel, CSV, TXT)
- Access and query your CISO Assistant data via API calls
- Assist with framework implementation and assessment workflows

## Architecture

The chatbot is built using:
- **Backend**: Django REST API with Google ADK (Agent Development Kit) integration
- **Frontend**: Svelte components with real-time chat interface
- **AI Engine**: Google Gemini LLM with custom tools for CISO Assistant API access
- **File Processing**: Support for document upload and analysis

## Prerequisites

1. **Python 3.11+** (for backend)
2. **Node.js 18+** (for frontend)
3. **Google Cloud Account** with API access
4. **Google API Key** for Gemini access

## Setup Instructions

### 1. Backend Setup

#### Install Dependencies
```bash
cd backend
poetry install
```

#### Configure Environment Variables
Create a `.env` file in the backend directory:
```bash
cp .env.example .env
```

Edit the `.env` file and add your Google API key:
```env
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CLOUD_PROJECT=your_project_id_here  # Optional
```

#### Run Database Migrations
```bash
poetry run python manage.py migrate
```

### 2. Google Cloud Setup

#### Get Google API Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Vertex AI API
   - Generative AI API
4. Go to "APIs & Services" > "Credentials"
5. Click "Create Credentials" > "API Key"
6. Copy the API key and add it to your `.env` file

#### Configure Authentication (Optional)
For production deployments, consider using service account authentication:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
```

### 3. Frontend Setup

The frontend components are already integrated. No additional setup required.

### 4. Testing the Setup

#### Start the Backend Server
```bash
cd backend
poetry run python manage.py runserver
```

#### Start the Frontend Server
```bash
cd frontend
npm run dev
```

#### Access the Chatbot
1. Open CISO Assistant in your browser
2. Log in with your credentials
3. Navigate to the "AI Assistant" menu item in the sidebar
4. Start a new conversation!

## API Endpoints

The chatbot exposes the following API endpoints:

- `GET /api/chatbot/sessions/` - List chat sessions
- `POST /api/chatbot/sessions/` - Create new chat session
- `GET /api/chatbot/messages/` - Get messages for a session
- `POST /api/chatbot/bot/chat/` - Send message and get AI response
- `GET /api/chatbot/bot/health/` - Check chatbot health
- `GET /api/chatbot/bot/capabilities/` - Get chatbot capabilities

## Features

### 1. Conversational Interface
- Real-time chat with AI assistant
- Message history and session management
- File upload support for document analysis

### 2. CISO Assistant Integration
The chatbot can access and query:
- Frameworks and compliance standards
- Risk scenarios and assessments
- Assets and security controls
- Users and organizational structure
- Compliance assessments and audits

### 3. File Processing
Supported file types:
- PDF documents
- Word documents (.docx, .doc)
- Excel spreadsheets (.xlsx, .xls)
- CSV files
- Plain text files (.txt)

### 4. Intelligent Responses
- Context-aware conversations
- Cybersecurity expertise
- CISO Assistant feature guidance
- Best practice recommendations

## Troubleshooting

### Common Issues

#### 1. "Google ADK not available" Error
- Ensure Google ADK is properly installed: `poetry show google-adk`
- Check your Python version (3.11+ required)
- Verify all dependencies are installed

#### 2. "API Key not set" Warning
- Check your `.env` file contains `GOOGLE_API_KEY`
- Ensure the API key is valid and has proper permissions
- Verify the Generative AI API is enabled in Google Cloud

#### 3. "Agent initialization failed" Error
- Check your internet connection
- Verify Google Cloud project settings
- Ensure API quotas are not exceeded

#### 4. File Upload Issues
- Check file size limits (10MB max)
- Verify supported file types
- Ensure proper file permissions

### Fallback Mode

If Google ADK is not available or configured, the chatbot will run in fallback mode with:
- Basic keyword-based responses
- Direct API data retrieval
- Limited AI capabilities
- Manual data formatting

## Configuration Options

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google Gemini API key | Yes |
| `GOOGLE_CLOUD_PROJECT` | Google Cloud project ID | No |
| `GOOGLE_APPLICATION_CREDENTIALS` | Service account key path | No |

### Customization

You can customize the chatbot by modifying:
- `backend/chatbot/agents.py` - AI agent configuration and tools
- `backend/chatbot/models.py` - Database models
- `frontend/src/lib/components/Chatbot/` - UI components

## Security Considerations

1. **API Key Security**: Store API keys securely and never commit them to version control
2. **User Permissions**: The chatbot respects CISO Assistant's user permissions and RBAC
3. **Data Privacy**: Conversations are stored locally and not sent to external services except for AI processing
4. **File Security**: Uploaded files are processed securely and can be configured for automatic cleanup

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the CISO Assistant documentation
3. Check Google ADK documentation: https://google.github.io/adk-docs/
4. Open an issue in the CISO Assistant repository

## License

This chatbot feature is part of CISO Assistant and follows the same licensing terms.
