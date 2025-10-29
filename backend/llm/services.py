"""
LLM service with Google Gemini integration and tool calling.
"""
import logging
import json
from typing import List, Dict, Any
from django.conf import settings
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Configure Gemini
if hasattr(settings, 'GEMINI_API_KEY'):
    genai.configure(api_key=settings.GEMINI_API_KEY)


class LLMService:
    """Service for interacting with Google Gemini LLM."""
    
    def __init__(self):
        self.model = 'models/gemini-2.5-flash'
    
    def _convert_tools_to_gemini_format(self, openai_tools: List[Dict]) -> List[Dict]:
        """Convert OpenAI tool format to Gemini function declarations."""
        import google.generativeai as genai
        
        function_declarations = []
        for tool in openai_tools:
            if tool.get('type') == 'function':
                func = tool['function']
                
                # Create FunctionDeclaration using genai types
                function_declarations.append(
                    genai.types.FunctionDeclaration(
                        name=func['name'],
                        description=func['description'],
                        parameters=func.get('parameters', {})
                    )
                )
        
        return function_declarations
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Get chat completion from Google Gemini.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: List of tool definitions for function calling (OpenAI format)
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
        
        Returns:
            Response dict with message and optional tool calls
        """
        try:
            # Separate system prompt from conversation
            system_prompt = None
            conversation_messages = []
            
            for msg in messages:
                if msg['role'] == 'system':
                    system_prompt = msg['content']
                else:
                    conversation_messages.append(msg)
            
            # Build Gemini chat history
            history = []
            for msg in conversation_messages[:-1]:  # Exclude last user message
                role = 'user' if msg['role'] == 'user' else 'model'
                history.append({
                    'role': role,
                    'parts': [msg['content']]
                })
            
            # Get last user message
            last_message = conversation_messages[-1]['content'] if conversation_messages else ''
            
            # Create model with optional tools
            model_kwargs = {
                'model_name': self.model,
            }
            
            if system_prompt:
                model_kwargs['system_instruction'] = system_prompt
            
            if tools:
                # Convert OpenAI tools to Gemini format
                gemini_tools = self._convert_tools_to_gemini_format(tools)
                model_kwargs['tools'] = gemini_tools
            
            model = genai.GenerativeModel(**model_kwargs)
            
            # Start chat with history
            chat = model.start_chat(history=history)
            
            # Send message
            response = chat.send_message(
                last_message,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
            )
            
            result = {
                'content': '',
                'role': 'assistant',
                'tool_calls': []
            }
            
            # Check for function calls in response
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    # Check if part has text
                    if hasattr(part, 'text') and part.text:
                        result['content'] = part.text
                    
                    # Check if part has function call
                    if hasattr(part, 'function_call') and part.function_call:
                        func_call = part.function_call
                        # Convert Gemini function call to OpenAI format
                        args_dict = {}
                        if func_call.args:
                            args_dict = dict(func_call.args)
                        
                        result['tool_calls'].append({
                            'id': f'call_{func_call.name}',
                            'name': func_call.name,
                            'arguments': args_dict
                        })
            
            return result
        
        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            import traceback
            traceback.print_exc()
            return {
                'content': f"Error: {str(e)}",
                'role': 'assistant',
                'tool_calls': []
            }
    
    def create_embedding(self, text: str) -> List[float]:
        """
        Create embedding vector for text using Gemini.
        
        Args:
            text: Text to embed
        
        Returns:
            Embedding vector (768-dim for Gemini embeddings)
        """
        try:
            result = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Error creating embedding: {e}")
            return []


class AssistantBotService:
    """SafeNest Assistant Bot - helps users navigate and explain incidents."""
    
    def __init__(self, organization_id, user_id):
        self.llm = LLMService()
        self.organization_id = organization_id
        self.user_id = user_id
        self.tools = self._get_tools()
    
    def _get_tools(self) -> List[Dict]:
        """Define available tools for assistant."""
        return [
            {
                'type': 'function',
                'function': {
                    'name': 'search_logs',
                    'description': 'Search login events and alerts by query and time range. If no specific query is provided, returns all events in the time range.',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'query': {
                                'type': 'string',
                                'description': 'Search query for logs (optional, use empty string for all events)'
                            },
                            'time_range': {
                                'type': 'string',
                                'enum': ['1h', '24h', '7d', '30d'],
                                'description': 'Time range to search'
                            },
                            'event_type': {
                                'type': 'string',
                                'enum': ['login', 'alert', 'incident', 'all'],
                                'description': 'Type of events to search'
                            }
                        },
                        'required': []
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'create_incident',
                    'description': 'Create a new security incident',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'title': {'type': 'string'},
                            'description': {'type': 'string'},
                            'severity': {
                                'type': 'string',
                                'enum': ['low', 'medium', 'high', 'critical']
                            },
                            'incident_type': {
                                'type': 'string',
                                'enum': ['unauthorized_access', 'data_breach', 'anomalous_login', 'policy_violation', 'suspicious_activity', 'other']
                            }
                        },
                        'required': ['title', 'severity']
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'get_incident',
                    'description': 'Get details of an incident by ID',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'incident_id': {'type': 'integer'}
                        },
                        'required': ['incident_id']
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'who_is',
                    'description': 'Look up a person by name in face identities',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'label': {'type': 'string', 'description': 'Person name or label'}
                        },
                        'required': ['label']
                    }
                }
            },
            {
                'type': 'function',
                'function': {
                    'name': 'show_camera',
                    'description': 'Get recent detections from a camera',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'camera_id': {'type': 'integer'}
                        },
                        'required': ['camera_id']
                    }
                }
            }
        ]
    
    def get_system_prompt(self) -> str:
        """Get system prompt for assistant."""
        return """You are SafeNest Assistant, an AI security assistant. 

Your role:
- Help users navigate the SafeNest security platform
- Explain security incidents and alerts
- Answer questions about login events and anomalies
- Recommend actions when high-risk events appear
- Be concise and cite specific IDs and timestamps

When you detect high-risk security events, recommend opening an incident.
Always provide actionable insights."""
    
    def chat(self, user_message: str, conversation_history: List[Dict] = None) -> Dict:
        """
        Process user message and return response.
        
        Args:
            user_message: User's message
            conversation_history: Previous messages in conversation
        
        Returns:
            Response dict with content and optional tool results
        """
        if conversation_history is None:
            conversation_history = []
        
        # Build messages
        messages = [
            {'role': 'system', 'content': self.get_system_prompt()}
        ]
        messages.extend(conversation_history)
        messages.append({'role': 'user', 'content': user_message})
        
        # Get LLM response
        response = self.llm.chat_completion(messages, tools=self.tools)
        
        # Execute tool calls if any
        tool_results = []
        final_content = response['content']
        
        if response['tool_calls']:
            # Execute all tools
            for tool_call in response['tool_calls']:
                result = self._execute_tool(tool_call['name'], tool_call['arguments'])
                tool_results.append({
                    'tool': tool_call['name'],
                    'result': result
                })
            
            # Send tool results back to get natural language response
            messages.append({'role': 'assistant', 'content': response['content'] or 'Using tools...'})
            
            # Format tool results for the model
            tool_results_text = "Tool Results:\n"
            for tr in tool_results:
                tool_results_text += f"\n{tr['tool']}:\n{json.dumps(tr['result'], indent=2)}\n"
            
            messages.append({'role': 'user', 'content': f"{tool_results_text}\n\nPlease summarize these results in a clear, conversational way for the user."})
            
            # Get final natural language response
            final_response = self.llm.chat_completion(messages, tools=None)
            final_content = final_response['content']
        
        return {
            'content': final_content,
            'tool_results': tool_results
        }
    
    def _execute_tool(self, tool_name: str, arguments: Dict) -> Any:
        """Execute a tool and return result."""
        from .tools import SafeNestTools
        tools = SafeNestTools(self.organization_id, self.user_id)
        
        if tool_name == 'search_logs':
            return tools.search_logs(**arguments)
        elif tool_name == 'create_incident':
            return tools.create_incident(**arguments)
        elif tool_name == 'get_incident':
            return tools.get_incident(**arguments)
        elif tool_name == 'who_is':
            return tools.who_is(**arguments)
        elif tool_name == 'show_camera':
            return tools.show_camera(**arguments)
        else:
            return {'error': f'Unknown tool: {tool_name}'}


class RecommendationBotService:
    """Recommendation Bot - suggests security policies and rules."""
    
    def __init__(self, organization_id):
        self.llm = LLMService()
        self.organization_id = organization_id
    
    def generate_recommendations(self) -> List[Dict]:
        """
        Analyze recent security events and generate recommendations.
        
        Returns:
            List of recommendation dicts
        """
        from security.models import Alert, AnomalyRule
        from incidents.models import Incident
        from datetime import timedelta
        from django.utils import timezone
        
        # Get recent data
        since = timezone.now() - timedelta(days=7)
        recent_alerts = Alert.objects.filter(
            organization_id=self.organization_id,
            created_at__gte=since
        ).count()
        
        recent_incidents = Incident.objects.filter(
            organization_id=self.organization_id,
            opened_at__gte=since
        ).values('incident_type', 'severity').distinct()
        
        active_rules = AnomalyRule.objects.filter(
            organization_id=self.organization_id,
            active=True
        ).count()
        
        # Build context
        context = f"""
Recent Security Data (Last 7 Days):
- Total Alerts: {recent_alerts}
- Recent Incidents: {recent_incidents.count()}
- Active Anomaly Rules: {active_rules}

Incident Types:
{json.dumps(list(recent_incidents), indent=2)}
"""
        
        prompt = f"""Based on the following security data, provide 3-5 actionable recommendations to improve security posture:

{context}

For each recommendation:
1. Identify the security gap
2. Suggest a specific rule or policy
3. Provide implementation parameters

Format as JSON array with keys: title, description, rule_type, config"""
        
        messages = [
            {'role': 'system', 'content': 'You are a security expert providing actionable recommendations.'},
            {'role': 'user', 'content': prompt}
        ]
        
        response = self.llm.chat_completion(messages, temperature=0.3)
        
        try:
            recommendations = json.loads(response['content'])
            return recommendations
        except:
            return [{'title': 'Analysis Complete', 'description': response['content']}]


class AnalysisBotService:
    """Analysis Bot - generates security posture summaries using RAG."""
    
    def __init__(self, organization_id):
        self.llm = LLMService()
        self.organization_id = organization_id
    
    def generate_weekly_analysis(self) -> str:
        """Generate weekly security analysis report."""
        from security.models import LoginEvent, Alert
        from incidents.models import Incident
        from faces.models import FaceDetection
        from datetime import timedelta
        from django.utils import timezone
        from django.db.models import Count, Q
        
        since = timezone.now() - timedelta(days=7)
        
        # Gather statistics
        login_stats = {
            'total': LoginEvent.objects.filter(user__organization_id=self.organization_id, timestamp__gte=since).count(),
            'failed': LoginEvent.objects.filter(user__organization_id=self.organization_id, timestamp__gte=since, success=False).count(),
            'anomalies': LoginEvent.objects.filter(user__organization_id=self.organization_id, timestamp__gte=since, is_anomaly=True).count(),
        }
        
        alert_stats = Alert.objects.filter(
            organization_id=self.organization_id,
            created_at__gte=since
        ).values('severity').annotate(count=Count('id'))
        
        incident_stats = Incident.objects.filter(
            organization_id=self.organization_id,
            opened_at__gte=since
        ).values('severity', 'status').annotate(count=Count('id'))
        
        face_stats = {
            'detections': FaceDetection.objects.filter(camera__organization_id=self.organization_id, timestamp__gte=since).count(),
            'matches': FaceDetection.objects.filter(camera__organization_id=self.organization_id, timestamp__gte=since, is_match=True).count(),
        }
        
        # Build context
        context = f"""
WEEKLY SECURITY REPORT (Last 7 Days)

Login Activity:
- Total Logins: {login_stats['total']}
- Failed Logins: {login_stats['failed']}
- Anomalous Logins: {login_stats['anomalies']}

Alerts by Severity:
{json.dumps(list(alert_stats), indent=2)}

Incidents:
{json.dumps(list(incident_stats), indent=2)}

Face Recognition:
- Total Detections: {face_stats['detections']}
- Matched Identities: {face_stats['matches']}
"""
        
        prompt = f"""Generate an executive security summary based on this data:

{context}

Include:
1. Overall security posture assessment
2. Key trends and hotspots
3. Areas requiring attention
4. Positive developments

Be concise and actionable."""
        
        messages = [
            {'role': 'system', 'content': 'You are a security analyst creating executive reports.'},
            {'role': 'user', 'content': prompt}
        ]
        
        response = self.llm.chat_completion(messages, temperature=0.5, max_tokens=1500)
        
        return response['content']
