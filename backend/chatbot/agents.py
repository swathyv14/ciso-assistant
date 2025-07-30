import os
import json
import logging
from typing import Dict, List, Any, Optional
from django.conf import settings
from django.urls import reverse
import requests

try:
    from google.adk.agents import LlmAgent
    from google.adk.tools import FunctionTool
    from google.genai import Client as GenAIClient
    ADK_AVAILABLE = True
except ImportError:
    # Fallback for when Google ADK is not available
    ADK_AVAILABLE = False
    LlmAgent = None
    FunctionTool = None
    GenAIClient = None

logger = logging.getLogger(__name__)


class CISOAssistantAPITool:
    """
    Tool for making API calls to CISO Assistant endpoints.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000/api"):
        self.base_url = base_url
        
    def make_api_call(self, endpoint: str, method: str = "GET", params: Dict = None, data: Dict = None) -> Dict:
        """
        Make an API call to CISO Assistant.
        
        Args:
            endpoint: API endpoint (e.g., "/frameworks", "/risk-scenarios")
            method: HTTP method (GET, POST, PUT, DELETE)
            params: Query parameters
            data: Request body data
            
        Returns:
            API response as dictionary
        """
        try:
            url = f"{self.base_url}{endpoint}"
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params or {},
                json=data
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"API call failed with status {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            logger.error(f"API call failed: {str(e)}")
            return {"error": f"API call failed: {str(e)}"}


class CISOAssistantAgent:
    """
    Main CISO Assistant chatbot agent using Google ADK.
    """
    
    def __init__(self):
        self.api_tool = CISOAssistantAPITool()
        self.client = None
        self.agent = None
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the Google ADK agent with CISO Assistant context."""
        if not ADK_AVAILABLE:
            logger.warning("Google ADK not available. Using fallback mode.")
            self.agent = None
            return

        try:
            # Initialize Google GenAI client
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                logger.warning("GOOGLE_API_KEY not set. Agent will use fallback mode.")
                self.agent = None
                return

            self.client = GenAIClient(api_key=api_key)

            # Create function tools for CISO Assistant API
            api_tools = self._create_api_tools()

            # System prompt with CISO Assistant context
            system_prompt = self._get_system_prompt()

            # Create the LLM agent
            self.agent = LlmAgent(
                model_id="gemini-2.0-flash-exp",
                client=self.client,
                system_instruction=system_prompt,
                tools=api_tools
            )

        except Exception as e:
            logger.error(f"Failed to initialize agent: {str(e)}")
            self.agent = None
    
    def _create_api_tools(self) -> List:
        """Create function tools for CISO Assistant API endpoints."""
        if not ADK_AVAILABLE or not FunctionTool:
            return []

        def get_frameworks(query: str = "") -> str:
            """Get information about available frameworks in CISO Assistant."""
            params = {"search": query} if query else {}
            result = self.api_tool.make_api_call("/frameworks", params=params)
            return json.dumps(result, indent=2)
        
        def get_risk_scenarios(query: str = "") -> str:
            """Get information about risk scenarios in CISO Assistant."""
            params = {"search": query} if query else {}
            result = self.api_tool.make_api_call("/risk-scenarios", params=params)
            return json.dumps(result, indent=2)
        
        def get_assets(query: str = "") -> str:
            """Get information about assets in CISO Assistant."""
            params = {"search": query} if query else {}
            result = self.api_tool.make_api_call("/assets", params=params)
            return json.dumps(result, indent=2)
        
        def get_compliance_assessments(query: str = "") -> str:
            """Get information about compliance assessments in CISO Assistant."""
            params = {"search": query} if query else {}
            result = self.api_tool.make_api_call("/compliance-assessments", params=params)
            return json.dumps(result, indent=2)
        
        def get_applied_controls(query: str = "") -> str:
            """Get information about applied controls in CISO Assistant."""
            params = {"search": query} if query else {}
            result = self.api_tool.make_api_call("/applied-controls", params=params)
            return json.dumps(result, indent=2)
        
        def get_users(query: str = "") -> str:
            """Get information about users in CISO Assistant."""
            params = {"search": query} if query else {}
            result = self.api_tool.make_api_call("/users", params=params)
            return json.dumps(result, indent=2)
        
        def get_folders(query: str = "") -> str:
            """Get information about folders/domains in CISO Assistant."""
            params = {"search": query} if query else {}
            result = self.api_tool.make_api_call("/folders", params=params)
            return json.dumps(result, indent=2)
        
        # Create function tools
        tools = [
            FunctionTool(get_frameworks),
            FunctionTool(get_risk_scenarios),
            FunctionTool(get_assets),
            FunctionTool(get_compliance_assessments),
            FunctionTool(get_applied_controls),
            FunctionTool(get_users),
            FunctionTool(get_folders),
        ]
        
        return tools
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the CISO Assistant agent."""
        return """
You are the CISO Assistant AI chatbot, an expert assistant for the CISO Assistant platform - a comprehensive cybersecurity governance, risk, and compliance (GRC) tool.

Your role is to help users understand and navigate CISO Assistant's features, answer questions about cybersecurity concepts, and assist with platform-specific tasks.

Key areas you can help with:
1. **Platform Navigation**: Guide users through CISO Assistant's interface and features
2. **Risk Management**: Explain risk scenarios, assessments, and mitigation strategies
3. **Compliance**: Help with compliance assessments, frameworks, and requirements
4. **Asset Management**: Assist with asset inventory and security objectives
5. **Controls**: Explain applied controls, reference controls, and implementation
6. **Frameworks**: Provide information about security frameworks (ISO 27001, NIST, etc.)
7. **Users & Permissions**: Help with user management and role assignments
8. **Reporting**: Assist with generating reports and analytics

When users ask questions:
- Use the available API tools to fetch current data from CISO Assistant
- Provide accurate, helpful, and contextual responses
- Explain cybersecurity concepts in clear, understandable terms
- Suggest relevant CISO Assistant features when appropriate
- If you need to access specific data, use the appropriate API tool first

Always be helpful, professional, and focused on cybersecurity best practices.
"""
    
    async def process_message(self, message: str, context: Dict = None) -> str:
        """
        Process a user message and return the agent's response.

        Args:
            message: User's message
            context: Additional context (session history, etc.)

        Returns:
            Agent's response
        """
        try:
            if not self.agent:
                # Fallback response when ADK is not available
                return self._fallback_response(message, context)

            # Add context if provided
            full_message = message
            if context and context.get('history'):
                # Include recent conversation history for context
                history_context = "\n".join([
                    f"{msg['role']}: {msg['content']}"
                    for msg in context['history'][-5:]  # Last 5 messages
                ])
                full_message = f"Previous conversation:\n{history_context}\n\nCurrent message: {message}"

            # Get response from the agent
            response = await self.agent.run(full_message)

            return response.text if hasattr(response, 'text') else str(response)

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return f"I apologize, but I encountered an error while processing your request: {str(e)}"

    def _fallback_response(self, message: str, context: Dict = None) -> str:
        """
        Provide a fallback response when Google ADK is not available.
        """
        message_lower = message.lower()

        # Basic keyword-based responses
        if any(word in message_lower for word in ['framework', 'frameworks']):
            frameworks_data = self.api_tool.make_api_call("/frameworks")
            if 'error' not in frameworks_data:
                return f"Here are the available frameworks in CISO Assistant:\n{json.dumps(frameworks_data, indent=2)}"

        elif any(word in message_lower for word in ['risk', 'risks', 'scenario']):
            risk_data = self.api_tool.make_api_call("/risk-scenarios")
            if 'error' not in risk_data:
                return f"Here are the risk scenarios in CISO Assistant:\n{json.dumps(risk_data, indent=2)}"

        elif any(word in message_lower for word in ['asset', 'assets']):
            assets_data = self.api_tool.make_api_call("/assets")
            if 'error' not in assets_data:
                return f"Here are the assets in CISO Assistant:\n{json.dumps(assets_data, indent=2)}"

        elif any(word in message_lower for word in ['compliance', 'assessment']):
            compliance_data = self.api_tool.make_api_call("/compliance-assessments")
            if 'error' not in compliance_data:
                return f"Here are the compliance assessments in CISO Assistant:\n{json.dumps(compliance_data, indent=2)}"

        elif any(word in message_lower for word in ['control', 'controls']):
            controls_data = self.api_tool.make_api_call("/applied-controls")
            if 'error' not in controls_data:
                return f"Here are the applied controls in CISO Assistant:\n{json.dumps(controls_data, indent=2)}"

        elif any(word in message_lower for word in ['user', 'users']):
            users_data = self.api_tool.make_api_call("/users")
            if 'error' not in users_data:
                return f"Here are the users in CISO Assistant:\n{json.dumps(users_data, indent=2)}"

        elif any(word in message_lower for word in ['folder', 'folders', 'domain']):
            folders_data = self.api_tool.make_api_call("/folders")
            if 'error' not in folders_data:
                return f"Here are the folders/domains in CISO Assistant:\n{json.dumps(folders_data, indent=2)}"

        elif any(word in message_lower for word in ['help', 'what', 'how']):
            return """
I'm the CISO Assistant chatbot! I can help you with:

🔍 **Information Retrieval:**
- Ask about frameworks, risk scenarios, assets, compliance assessments
- Get information about applied controls, users, and folders/domains

📊 **Platform Guidance:**
- Explain CISO Assistant features and capabilities
- Help navigate the platform
- Provide cybersecurity best practices

💡 **Examples of what you can ask:**
- "Show me available frameworks"
- "What risk scenarios do we have?"
- "List our assets"
- "Show compliance assessments"
- "What applied controls are in place?"

Note: For the best experience, please configure Google ADK with your API key.
"""

        # Default response
        return f"""
I understand you're asking about: "{message}"

I'm currently running in basic mode. I can help you access CISO Assistant data by asking about:
- Frameworks
- Risk scenarios
- Assets
- Compliance assessments
- Applied controls
- Users
- Folders/domains

For more advanced AI capabilities, please configure Google ADK with your API key.

What specific information would you like to know about?
"""
    
    def process_file(self, file_path: str, file_type: str) -> Dict:
        """
        Process uploaded files (documents, spreadsheets, etc.).
        
        Args:
            file_path: Path to the uploaded file
            file_type: Type of file (pdf, xlsx, docx, etc.)
            
        Returns:
            Processing result
        """
        try:
            # Basic file processing logic
            # This can be extended to handle different file types
            result = {
                "processed": True,
                "file_type": file_type,
                "summary": f"File {file_path} has been processed successfully.",
                "extracted_data": {}
            }
            
            # Add specific processing based on file type
            if file_type.lower() in ['pdf', 'docx', 'txt']:
                result["summary"] = "Document processed. I can help you analyze its content in relation to CISO Assistant features."
            elif file_type.lower() in ['xlsx', 'csv']:
                result["summary"] = "Spreadsheet processed. I can help you understand how to import this data into CISO Assistant."
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            return {
                "processed": False,
                "error": str(e)
            }


# Global agent instance
_agent_instance = None

def get_agent() -> CISOAssistantAgent:
    """Get or create the global agent instance."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = CISOAssistantAgent()
    return _agent_instance
