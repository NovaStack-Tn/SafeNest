"""
LLM service with OpenAI integration and tool calling.
"""
import logging
import json
from typing import List, Dict, Any
from django.conf import settings
import openai

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with OpenAI LLM."""
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Get chat completion from OpenAI.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: List of tool definitions for function calling
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
        
        Returns:
            Response dict with message and optional tool calls
        """
        try:
            kwargs = {
                'model': self.model,
                'messages': messages,
                'temperature': temperature,
                'max_tokens': max_tokens,
            }
            
            if tools:
                kwargs['tools'] = tools
                kwargs['tool_choice'] = 'auto'
            
            response = openai.chat.completions.create(**kwargs)
            
            message = response.choices[0].message
            
            result = {
                'content': message.content,
                'role': message.role,
                'tool_calls': []
            }
            
            # Extract tool calls if present
            if hasattr(message, 'tool_calls') and message.tool_calls:
                for tool_call in message.tool_calls:
                    result['tool_calls'].append({
                        'id': tool_call.id,
                        'name': tool_call.function.name,
                        'arguments': json.loads(tool_call.function.arguments)
                    })
            
            return result
            
        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            return {
                'content': f"Error: {str(e)}",
                'role': 'assistant',
                'tool_calls': []
            }
    
    def create_embedding(self, text: str) -> List[float]:
        """
        Create embedding vector for text using OpenAI.
        
        Args:
            text: Text to embed
        
        Returns:
            Embedding vector (1536-dim for ada-002)
        """
        try:
            response = openai.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
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
                    'description': 'Search login events and alerts by query and time range',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'query': {
                                'type': 'string',
                                'description': 'Search query for logs'
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
                        'required': ['query']
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
        if response['tool_calls']:
            for tool_call in response['tool_calls']:
                result = self._execute_tool(tool_call['name'], tool_call['arguments'])
                tool_results.append({
                    'tool': tool_call['name'],
                    'result': result
                })
        
        return {
            'content': response['content'],
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
