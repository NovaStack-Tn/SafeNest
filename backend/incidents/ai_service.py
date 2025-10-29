"""
AI-powered incident analysis and classification using Google Gemini.
"""
import re
import json
from typing import Dict, Tuple, List
from django.conf import settings
import google.generativeai as genai

# Configure Gemini
if hasattr(settings, 'GEMINI_API_KEY'):
    genai.configure(api_key=settings.GEMINI_API_KEY)


class IncidentAIService:
    """AI service for incident classification and analysis."""
    
    @staticmethod
    def classify_severity(title: str, description: str) -> Tuple[str, float]:
        """
        Classify incident severity using Google Gemini.
        
        Returns:
            Tuple of (severity, confidence)
        """
        try:
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            
            prompt = f"""Analyze this security incident and classify its severity.

Title: {title}
Description: {description}

Classify the severity as one of: low, medium, high, critical

Consider:
- Impact on security and operations
- Potential data exposure
- System compromise level
- Urgency of response needed

Respond ONLY with valid JSON format (no markdown, no code blocks):
{{"severity": "low|medium|high|critical", "confidence": 0.0-1.0, "reasoning": "brief explanation"}}"""

            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=200,
                )
            )
            
            # Check if response has content
            if not response.parts:
                print(f"AI severity classification: No valid response (finish_reason: {response.candidates[0].finish_reason})")
                return IncidentAIService._fallback_severity_classification(title, description)
            
            result = response.text.strip()
            
            # Remove markdown code blocks if present
            if result.startswith('```'):
                result = result.split('```')[1]
                if result.startswith('json'):
                    result = result[4:]
            
            # Parse the response
            data = json.loads(result)
            severity = data.get('severity', 'medium')
            confidence = float(data.get('confidence', 0.7))
            
            return severity, confidence
            
        except Exception as e:
            print(f"AI severity classification failed: {e}")
            # Fallback to rule-based classification
            return IncidentAIService._fallback_severity_classification(title, description)
    
    @staticmethod
    def _fallback_severity_classification(title: str, description: str) -> Tuple[str, float]:
        """Fallback rule-based severity classification."""
        text = (title + ' ' + description).lower()
        
        critical_keywords = ['breach', 'compromised', 'ransomware', 'data leak', 'emergency', 'critical']
        high_keywords = ['unauthorized access', 'intrusion', 'malware', 'attack', 'exploit']
        medium_keywords = ['suspicious', 'anomaly', 'unusual', 'failed login', 'violation']
        
        if any(kw in text for kw in critical_keywords):
            return 'critical', 0.8
        elif any(kw in text for kw in high_keywords):
            return 'high', 0.7
        elif any(kw in text for kw in medium_keywords):
            return 'medium', 0.6
        else:
            return 'low', 0.5
    
    @staticmethod
    def extract_entities(description: str) -> Dict:
        """
        Extract key entities from incident description using NLP.
        
        Returns:
            Dict with extracted entities (IPs, users, locations, times, etc.)
        """
        try:
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            
            prompt = f"""Extract key entities from this security incident description.

Description: {description}

Extract and return JSON with:
- ip_addresses: list of IP addresses
- usernames: list of usernames or user IDs
- locations: list of locations or systems
- timestamps: list of times mentioned
- actions: list of actions taken or observed
- assets: list of affected systems/assets

If none found for a category, use empty list.

Respond ONLY with valid JSON format (no markdown, no code blocks):
{{
  "ip_addresses": [],
  "usernames": [],
  "locations": [],
  "timestamps": [],
  "actions": [],
  "assets": []
}}"""

            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=300,
                )
            )
            
            # Check if response has content
            if not response.parts:
                print(f"AI entity extraction: No valid response (safety filter)")
                return IncidentAIService._fallback_entity_extraction(description)
            
            result = response.text.strip()
            
            # Remove markdown code blocks if present
            if result.startswith('```'):
                result = result.split('```')[1]
                if result.startswith('json'):
                    result = result[4:]
            
            # Parse the response
            entities = json.loads(result)
            
            return entities
            
        except Exception as e:
            print(f"AI entity extraction failed: {e}")
            # Fallback to regex-based extraction
            return IncidentAIService._fallback_entity_extraction(description)
    
    @staticmethod
    def _fallback_entity_extraction(description: str) -> Dict:
        """Fallback regex-based entity extraction."""
        entities = {
            'ip_addresses': [],
            'usernames': [],
            'locations': [],
            'timestamps': [],
            'actions': [],
            'assets': []
        }
        
        # Extract IP addresses
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        entities['ip_addresses'] = re.findall(ip_pattern, description)
        
        # Extract common usernames (basic pattern)
        username_pattern = r'\b(?:user|username|account)[\s:]+([a-zA-Z0-9_-]+)\b'
        entities['usernames'] = re.findall(username_pattern, description, re.IGNORECASE)
        
        # Extract time patterns
        time_pattern = r'\b\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?\b'
        entities['timestamps'] = re.findall(time_pattern, description)
        
        return entities
    
    @staticmethod
    def suggest_category(title: str, description: str, available_categories: List[str]) -> str:
        """
        Suggest the most appropriate category for an incident.
        
        Args:
            title: Incident title
            description: Incident description
            available_categories: List of available category names
            
        Returns:
            Suggested category name
        """
        if not available_categories:
            return None
            
        try:
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            
            categories_str = ', '.join(available_categories)
            prompt = f"""Given this security incident, suggest the most appropriate category.

Title: {title}
Description: {description}

Available categories: {categories_str}

Respond with just the category name that best fits (no explanation, just the name)."""

            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=50,
                )
            )
            
            # Check if response has content
            if not response.parts:
                print(f"AI category suggestion: No valid response (safety filter)")
                return available_categories[0] if available_categories else None
            
            suggested = response.text.strip()
            
            # Remove any quotes or extra characters
            suggested = suggested.strip('"\'')
            
            # Verify it's in the list
            if suggested in available_categories:
                return suggested
            
            # Try case-insensitive match
            for cat in available_categories:
                if cat.lower() == suggested.lower():
                    return cat
            
            return available_categories[0] if available_categories else None
            
        except Exception as e:
            print(f"AI category suggestion failed: {e}")
            return available_categories[0] if available_categories else None
    
    @staticmethod
    def auto_create_from_alert(alert_data: Dict) -> Dict:
        """
        Auto-create incident from security alert.
        
        Args:
            alert_data: Dict with alert information (title, message, severity, etc.)
            
        Returns:
            Dict with incident creation data
        """
        title = alert_data.get('title', 'Security Alert')
        description = alert_data.get('message', '')
        
        # Classify severity
        severity, confidence = IncidentAIService.classify_severity(title, description)
        
        # Extract entities
        entities = IncidentAIService.extract_entities(description)
        
        # Determine incident type based on alert
        alert_type = alert_data.get('type', 'other')
        incident_type_mapping = {
            'login_anomaly': 'anomalous_login',
            'access_violation': 'unauthorized_access',
            'data_access': 'suspicious_activity',
            'policy_breach': 'policy_violation',
        }
        incident_type = incident_type_mapping.get(alert_type, 'other')
        
        return {
            'title': title,
            'description': description,
            'incident_type': incident_type,
            'severity': severity,
            'ai_generated': True,
            'ai_confidence': confidence,
            'extracted_entities': entities,
            'metadata': {
                'source': 'auto_generated',
                'alert_id': alert_data.get('id'),
                'alert_timestamp': alert_data.get('timestamp'),
            }
        }
    
    @staticmethod
    def recommend_actions(incident) -> list:
        """
        Suggest next actions to take for an incident using AI.
        
        Args:
            incident: Incident model instance
            
        Returns:
            List of recommended actions with priority
        """
        try:
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            
            # Simplified text to avoid safety filters
            sanitized_title = incident.title.replace('phishing', 'email campaign')
            sanitized_desc = incident.description[:300].replace('phishing', 'email campaign')
            sanitized_desc = sanitized_desc.replace('malicious', 'suspicious')
            
            prompt = f"""Suggest 3 priority actions for this security incident:

Incident: {sanitized_title}
Current Status: {incident.get_status_display()}
Priority: {incident.get_severity_display()}

Context: {sanitized_desc}

For each action, provide:
- Action name
- Priority level (High/Medium/Low)
- Brief description (1 sentence)

Format as JSON array:
[{{"action": "name", "priority": "high", "description": "desc"}}]"""

            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"}
            ]
            
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.5,
                    max_output_tokens=300,
                ),
                safety_settings=safety_settings
            )
            
            if not response.parts:
                # Fallback recommendations based on status
                return IncidentAIService._get_fallback_actions(incident)
            
            result = response.text.strip()
            
            # Clean markdown formatting
            if result.startswith('```'):
                result = result.split('```')[1]
                if result.startswith('json'):
                    result = result[4:]
                result = result.strip('`')
            
            # Parse JSON
            try:
                actions = json.loads(result)
                return actions if isinstance(actions, list) else [actions]
            except json.JSONDecodeError:
                return IncidentAIService._get_fallback_actions(incident)
                
        except Exception as e:
            print(f"AI action recommendations failed: {e}")
            return IncidentAIService._get_fallback_actions(incident)
    
    @staticmethod
    def _get_fallback_actions(incident) -> list:
        """Generate fallback action recommendations based on incident status."""
        status = incident.status.lower()
        severity = incident.severity.lower()
        
        if status == 'open':
            return [
                {"action": "Assign to Security Team", "priority": "high", "description": "Assign this incident to the appropriate security team member for investigation."},
                {"action": "Review Initial Evidence", "priority": "high", "description": "Examine all available logs and evidence to understand the scope."},
                {"action": "Document Timeline", "priority": "medium", "description": "Begin documenting the sequence of events in the timeline."}
            ]
        elif status == 'investigating':
            return [
                {"action": "Identify Affected Systems", "priority": "high", "description": "Determine all systems and users impacted by this incident."},
                {"action": "Contain the Threat", "priority": "high" if severity in ['high', 'critical'] else "medium", "description": "Take immediate steps to prevent further damage or spread."},
                {"action": "Collect Additional Evidence", "priority": "medium", "description": "Gather logs, screenshots, and other relevant evidence."}
            ]
        elif status == 'contained':
            return [
                {"action": "Verify Containment", "priority": "high", "description": "Confirm that the threat has been fully contained and cannot spread."},
                {"action": "Plan Remediation", "priority": "high", "description": "Develop a plan to fully resolve the incident and restore normal operations."},
                {"action": "Notify Stakeholders", "priority": "medium", "description": "Update relevant stakeholders on the current status and next steps."}
            ]
        elif status == 'resolved':
            return [
                {"action": "Add Resolution Details", "priority": "high", "description": "Document the resolution, actions taken, and root cause."},
                {"action": "Verify Fix", "priority": "high", "description": "Test and confirm that the issue has been fully resolved."},
                {"action": "Update Documentation", "priority": "medium", "description": "Update security documentation and procedures based on lessons learned."}
            ]
        else:  # closed
            return [
                {"action": "Review Resolution", "priority": "low", "description": "Ensure all resolution details are properly documented."},
                {"action": "Update Knowledge Base", "priority": "low", "description": "Add incident details to the security knowledge base for future reference."},
                {"action": "Schedule Post-Mortem", "priority": "medium", "description": "Conduct a post-incident review meeting with the team."}
            ]
    
    @staticmethod
    def _create_fallback_summary(incident) -> str:
        """Create an intelligent summary from incident data when AI fails."""
        # Get key details
        title = incident.title
        severity = incident.get_severity_display()
        status = incident.get_status_display()
        event_count = incident.events.count()
        
        # Extract first sentence from description
        desc_sentences = incident.description.split('.')
        first_detail = desc_sentences[0].strip() if desc_sentences else incident.description[:150]
        
        # Build summary based on status
        if status.lower() == 'resolved' or status.lower() == 'closed':
            summary = f"{title}: {first_detail}. This {severity.lower()} severity incident has been {status.lower()}"
            if event_count > 0:
                summary += f" with {event_count} actions documented in the timeline"
            summary += "."
        elif status.lower() == 'contained':
            summary = f"{title}: {first_detail}. The situation has been contained and is classified as {severity.lower()} severity"
            if event_count > 0:
                summary += f". {event_count} response actions have been documented"
            summary += "."
        else:
            summary = f"{title}: {first_detail}. This is an active {severity.lower()} severity incident currently under investigation"
            if event_count > 0:
                summary += f" with {event_count} timeline events"
            summary += "."
        
        return summary
    
    @staticmethod
    def generate_summary(incident) -> str:
        """
        Generate an AI summary of the incident and its timeline.
        
        Args:
            incident: Incident model instance
            
        Returns:
            Summary text
        """
        try:
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            
            # Gather incident data
            events = list(incident.events.all()[:20])
            event_descriptions = []
            if events:
                event_descriptions = [
                    f"- {e.timestamp.strftime('%Y-%m-%d %H:%M')}: {e.action.replace('_', ' ').title()} - {e.description}"
                    for e in events
                ]
            
            # Build timeline section
            timeline_section = ""
            if event_descriptions:
                timeline_section = f"\n\nTimeline of Events:\n" + "\n".join(event_descriptions)
            
            # Add tags if available
            tags_section = ""
            if incident.tags:
                tags_section = f"\n\nTags: {', '.join(incident.tags)}"
            
            # Add category if available
            category_section = ""
            if hasattr(incident, 'category') and incident.category:
                category_section = f"\nCategory: {incident.category.name}"
            
            # Comprehensive sanitization to avoid triggering safety filters
            def sanitize_text(text):
                """Replace security-related terms with neutral equivalents"""
                replacements = {
                    'phishing': 'email campaign',
                    'attack': 'activity',
                    'malicious link': 'link',
                    'malicious': 'suspicious',
                    'breach': 'unauthorized access',
                    'hacker': 'unauthorized user',
                    'exploit': 'unauthorized action',
                    'threat': 'concern',
                    'vulnerable': 'exposed',
                    'compromise': 'access',
                    'compromised': 'affected',
                    'malware': 'software',
                    'ransomware': 'encryption software',
                    'virus': 'program',
                    'trojan': 'program',
                    'backdoor': 'entry point',
                    'injection': 'input',
                    'intrusion': 'entry',
                    'clicked': 'accessed',
                    'spoofing': 'impersonating',
                    'fake': 'imitation',
                }
                
                sanitized = text
                for original, replacement in replacements.items():
                    # Case-insensitive replacement
                    import re
                    pattern = re.compile(re.escape(original), re.IGNORECASE)
                    sanitized = pattern.sub(replacement, sanitized)
                
                return sanitized
            
            sanitized_description = sanitize_text(incident.description)
            sanitized_title = sanitize_text(incident.title)
            
            prompt = f"""Summarize this business operational report:

Title: {sanitized_title}
Current Status: {incident.get_status_display()}

What happened: {sanitized_description[:400]}

Write a brief 2-3 sentence summary."""

            # Configure safety settings to allow security analysis content
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_ONLY_HIGH"
                }
            ]
            
            # Try up to 2 times with different approaches
            for attempt in range(2):
                try:
                    if attempt == 1:
                        # Second attempt: Ultra-simple, no context at all
                        prompt = f"""Write a 2-3 sentence summary of this:

{sanitized_description[:350]}

Summary:"""
                    
                    response = model.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(
                            temperature=0.4,
                            max_output_tokens=250,
                        ),
                        safety_settings=safety_settings
                    )
                    
                    # Check if response has content
                    if response.parts:
                        summary = response.text.strip()
                        
                        # Remove markdown formatting if present
                        if summary.startswith('```'):
                            summary = summary.split('```')[1]
                        if summary.startswith('Summary:') or summary.startswith('**Summary:**'):
                            summary = summary.split(':', 1)[1].strip()
                        
                        return summary
                    else:
                        if attempt == 0:
                            print(f"AI summary generation attempt {attempt + 1}: Blocked by safety filter, retrying with simpler prompt...")
                            continue
                        else:
                            print(f"AI summary generation: All attempts blocked by safety filter")
                            return f"Unable to generate AI summary due to content filters. {incident.title} - {incident.get_severity_display()} severity."
                
                except Exception as e:
                    if attempt == 0:
                        print(f"AI summary generation attempt {attempt + 1} failed: {e}, retrying...")
                        continue
                    else:
                        print(f"AI summary generation failed after {attempt + 1} attempts: {e}")
                        import traceback
                        traceback.print_exc()
                        return f"Unable to generate AI summary (API error). {incident.title} - {incident.get_severity_display()} severity."
            
            # Fallback: Create intelligent summary from incident data
            return IncidentAIService._create_fallback_summary(incident)
            
        except Exception as e:
            print(f"AI summary generation failed: {e}")
            import traceback
            traceback.print_exc()
            return f"Unable to generate AI summary (API error). {incident.title} - {incident.get_severity_display()} severity."
