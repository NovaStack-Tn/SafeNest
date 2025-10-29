"""
AI-powered threat analysis service using Google Gemini 2.5 Flash
"""
import json
import re
from django.conf import settings
import google.generativeai as genai

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)


def clean_json_response(text):
    """Extract and clean JSON from Gemini response"""
    # Remove markdown code blocks
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    text = text.strip()
    
    # Try to find JSON object
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        text = json_match.group()
    
    return text


def analyze_threat(threat_description, threat_type=None, source=None):
    """
    Analyze a threat and provide severity assessment, classification, and recommendations
    
    Args:
        threat_description (str): Description of the threat
        threat_type (str, optional): Type of threat
        source (str, optional): Where threat was identified
    
    Returns:
        dict: Analysis including severity, confidence, recommendations
    """
    try:
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        prompt = f"""Analyze this security threat and provide a comprehensive assessment in JSON format:

Threat Description: {threat_description}
{f'Threat Type: {threat_type}' if threat_type else ''}
{f'Source: {source}' if source else ''}

Provide a JSON response with:
{{
    "severity": "critical|high|medium|low|info",
    "confidence": 0.0-1.0,
    "threat_type": "physical|cyber|insider|terrorism|fraud|data_breach|social_engineering|other",
    "attack_vectors": ["list of potential attack vectors"],
    "potential_impact": "detailed impact analysis",
    "indicators": ["key indicators or IOCs"],
    "recommended_actions": ["immediate actions to take"],
    "risk_factors": ["factors that increase risk"],
    "analysis_summary": "brief summary"
}}

Be specific and actionable in your recommendations."""

        response = model.generate_content(prompt)
        cleaned_text = clean_json_response(response.text)
        analysis = json.loads(cleaned_text)
        
        return {
            'success': True,
            'analysis': analysis
        }
        
    except json.JSONDecodeError as e:
        return {
            'success': False,
            'error': f'Failed to parse AI response: {str(e)}',
            'raw_response': response.text if 'response' in locals() else None
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def generate_risk_assessment(threat_title, threat_description, threat_type):
    """
    Generate comprehensive risk assessment for a threat
    
    Args:
        threat_title (str): Title of the threat
        threat_description (str): Description
        threat_type (str): Type of threat
    
    Returns:
        dict: Risk assessment including likelihood, impact, and mitigation strategies
    """
    try:
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        prompt = f"""Generate a comprehensive risk assessment for this security threat in JSON format:

Title: {threat_title}
Description: {threat_description}
Type: {threat_type}

Provide a JSON response with:
{{
    "risk_level": "critical|high|medium|low|negligible",
    "likelihood": "certain|likely|possible|unlikely|rare",
    "impact": "catastrophic|severe|moderate|minor|insignificant",
    "confidence": 0.0-1.0,
    "vulnerability_analysis": "what makes the organization vulnerable",
    "impact_analysis": "what could happen if exploited",
    "mitigation_strategy": "how to reduce or eliminate the risk",
    "residual_risk": "risk remaining after mitigation",
    "estimated_cost_range": "cost estimate to mitigate (e.g., $5000-$10000)",
    "timeline": "recommended timeline for mitigation",
    "required_resources": "resources needed",
    "recommendations": ["specific actionable recommendations"]
}}

Be thorough and specific in your analysis."""

        response = model.generate_content(prompt)
        cleaned_text = clean_json_response(response.text)
        assessment = json.loads(cleaned_text)
        
        return {
            'success': True,
            'assessment': assessment
        }
        
    except json.JSONDecodeError as e:
        return {
            'success': False,
            'error': f'Failed to parse AI response: {str(e)}',
            'raw_response': response.text if 'response' in locals() else None
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def extract_threat_indicators(description, metadata=None):
    """
    Extract Indicators of Compromise (IOCs) from threat description
    
    Args:
        description (str): Threat description
        metadata (dict, optional): Additional metadata
    
    Returns:
        dict: Extracted indicators with types and confidence levels
    """
    try:
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        prompt = f"""Extract Indicators of Compromise (IOCs) and suspicious patterns from this threat description:

Description: {description}
{f'Additional Context: {json.dumps(metadata)}' if metadata else ''}

Provide a JSON response with an array of indicators:
{{
    "indicators": [
        {{
            "type": "ip_address|domain|url|file_hash|email|username|phone|license_plate|device_id|pattern",
            "value": "the actual indicator value",
            "confidence": "high|medium|low",
            "description": "context about this indicator",
            "first_seen": "approximate timestamp or 'unknown'",
            "tags": ["relevant tags"]
        }}
    ],
    "patterns": ["behavioral patterns observed"],
    "summary": "brief summary of extracted indicators"
}}

Extract all relevant IOCs you can identify."""

        response = model.generate_content(prompt)
        cleaned_text = clean_json_response(response.text)
        result = json.loads(cleaned_text)
        
        return {
            'success': True,
            'indicators': result.get('indicators', []),
            'patterns': result.get('patterns', []),
            'summary': result.get('summary', '')
        }
        
    except json.JSONDecodeError as e:
        return {
            'success': False,
            'error': f'Failed to parse AI response: {str(e)}',
            'raw_response': response.text if 'response' in locals() else None
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def analyze_watchlist_subject(subject_name, subject_type, reason, attributes=None):
    """
    Analyze a watchlist subject and provide risk assessment
    
    Args:
        subject_name (str): Name/identifier of subject
        subject_type (str): Type of subject (person, vehicle, etc.)
        reason (str): Reason for watchlist
        attributes (dict, optional): Additional attributes
    
    Returns:
        dict: Risk analysis and monitoring recommendations
    """
    try:
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        prompt = f"""Analyze this watchlist subject and provide risk assessment in JSON format:

Subject: {subject_name}
Type: {subject_type}
Reason for Watchlist: {reason}
{f'Additional Attributes: {json.dumps(attributes)}' if attributes else ''}

Provide a JSON response with:
{{
    "risk_level": "critical|high|medium|low|monitor",
    "confidence": 0.0-1.0,
    "threat_assessment": "detailed threat assessment",
    "monitoring_recommendations": ["specific monitoring actions"],
    "alert_triggers": ["conditions that should trigger alerts"],
    "action_instructions": "what to do if subject is detected",
    "related_threats": ["potential related threats or connections"],
    "recommended_expiry": "recommended watchlist duration (e.g., '90 days', 'indefinite')"
}}

Be specific about monitoring requirements."""

        response = model.generate_content(prompt)
        cleaned_text = clean_json_response(response.text)
        analysis = json.loads(cleaned_text)
        
        return {
            'success': True,
            'analysis': analysis
        }
        
    except json.JSONDecodeError as e:
        return {
            'success': False,
            'error': f'Failed to parse AI response: {str(e)}',
            'raw_response': response.text if 'response' in locals() else None
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def correlate_threats(threat_descriptions):
    """
    Analyze multiple threats to identify patterns and connections
    
    Args:
        threat_descriptions (list): List of threat descriptions
    
    Returns:
        dict: Correlation analysis including patterns and recommendations
    """
    try:
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        threats_text = "\n\n".join([f"Threat {i+1}: {desc}" for i, desc in enumerate(threat_descriptions)])
        
        prompt = f"""Analyze these security threats and identify correlations, patterns, and connections:

{threats_text}

Provide a JSON response with:
{{
    "correlation_found": true|false,
    "confidence": 0.0-1.0,
    "common_patterns": ["identified patterns across threats"],
    "potential_campaign": "description if threats appear coordinated",
    "shared_indicators": ["IOCs or patterns shared across threats"],
    "threat_actors": ["potential threat actors if identifiable"],
    "recommended_actions": ["prioritized actions based on correlation"],
    "risk_escalation": "whether combined threats increase risk level",
    "analysis_summary": "summary of correlation analysis"
}}

Look for connections and patterns that might not be obvious."""

        response = model.generate_content(prompt)
        cleaned_text = clean_json_response(response.text)
        correlation = json.loads(cleaned_text)
        
        return {
            'success': True,
            'correlation': correlation
        }
        
    except json.JSONDecodeError as e:
        return {
            'success': False,
            'error': f'Failed to parse AI response: {str(e)}',
            'raw_response': response.text if 'response' in locals() else None
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def generate_threat_report(threats_data, time_period):
    """
    Generate comprehensive threat intelligence report
    
    Args:
        threats_data (list): List of threat data dictionaries
        time_period (str): Time period for report (e.g., "last 7 days")
    
    Returns:
        dict: Comprehensive threat report
    """
    try:
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        threats_summary = "\n".join([
            f"- {t.get('title')} ({t.get('severity')}, {t.get('status')})"
            for t in threats_data[:20]  # Limit to avoid token limits
        ])
        
        prompt = f"""Generate a comprehensive threat intelligence report for the {time_period}:

Threats Summary:
{threats_summary}

Total Threats: {len(threats_data)}

Provide a JSON response with:
{{
    "executive_summary": "high-level summary for executives",
    "threat_landscape": "overall threat landscape assessment",
    "key_findings": ["critical findings"],
    "trends": ["observed trends"],
    "top_threats": ["most critical threats"],
    "recommendations": ["strategic recommendations"],
    "metrics": {{
        "critical_count": 0,
        "high_count": 0,
        "resolved_count": 0,
        "avg_response_time": "estimate"
    }},
    "forecast": "threat forecast for next period"
}}

Provide actionable intelligence."""

        response = model.generate_content(prompt)
        cleaned_text = clean_json_response(response.text)
        report = json.loads(cleaned_text)
        
        return {
            'success': True,
            'report': report
        }
        
    except json.JSONDecodeError as e:
        return {
            'success': False,
            'error': f'Failed to parse AI response: {str(e)}',
            'raw_response': response.text if 'response' in locals() else None
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
