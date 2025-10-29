"""
AI Service for Visitor Management using Google Gemini 2.5 Flash
Provides intelligent visitor pre-registration, information extraction, and predictions
"""

import google.generativeai as genai
from django.conf import settings
from datetime import datetime, timedelta
import json
import re
from typing import Dict, Any, Optional, List


class VisitorAIService:
    """AI-powered visitor management service using Gemini 2.5 Flash"""
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    def extract_visitor_info(self, text: str, source_type: str = 'email') -> Dict[str, Any]:
        """
        Extract visitor information from email, form, or text using Gemini
        
        Args:
            text: Raw text from email, form submission, or other source
            source_type: Type of source ('email', 'form', 'message')
        
        Returns:
            Dict with extracted visitor information and confidence score
        """
        prompt = f"""
You are an AI assistant that extracts visitor information from {source_type} content.
Extract the following information from the text below and return ONLY a valid JSON object.

Required fields (extract if available):
- first_name: Visitor's first name
- last_name: Visitor's last name
- email: Email address
- phone: Phone number (format: +1234567890)
- company: Company/organization name
- visitor_type: One of [guest, contractor, vendor, delivery, maintenance, emergency, other]
- purpose: Purpose of visit
- expected_arrival: Expected arrival date/time (ISO 8601 format)
- expected_departure: Expected departure date/time (ISO 8601 format)
- department: Department to visit
- host_name: Name of person they're visiting
- id_type: Type of ID (passport, driver_license, national_id, etc.)
- id_number: ID number if mentioned
- vehicle_plate: Vehicle license plate if mentioned
- emergency_contact: Emergency contact name
- emergency_phone: Emergency contact phone
- notes: Any additional relevant information

Additional context:
- If arrival/departure times are relative (e.g., "tomorrow at 2pm", "next Monday"), convert to ISO 8601 format based on current date: {datetime.now().isoformat()}
- If only date is mentioned, assume 9 AM for arrival and 5 PM for departure
- Infer visitor_type from context (e.g., "delivery" if mentions package, "contractor" if mentions work/project)
- Extract any security-relevant details into notes

Return a JSON object with extracted fields and a "confidence" score (0.0-1.0) indicating extraction quality.
Set "confidence" to 0.0 if information is missing or unclear.

Text to analyze:
{text}

Return ONLY the JSON object, no additional text or explanation.
"""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Clean up response - remove markdown code blocks if present
            result_text = self._clean_json_response(result_text)
            
            # Parse JSON
            extracted_data = json.loads(result_text)
            
            # Validate and clean the data
            cleaned_data = self._validate_extracted_data(extracted_data)
            
            return {
                'success': True,
                'extracted_data': cleaned_data,
                'confidence': extracted_data.get('confidence', 0.5),
                'raw_response': result_text
            }
            
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f'Failed to parse AI response as JSON: {str(e)}',
                'raw_response': result_text if 'result_text' in locals() else None
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'AI extraction failed: {str(e)}',
                'raw_response': None
            }
    
    def suggest_access_level(self, visitor_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Suggest appropriate access level based on visitor information
        
        Args:
            visitor_data: Dictionary containing visitor information
        
        Returns:
            Dict with suggested access level and reasoning
        """
        prompt = f"""
You are a security AI that suggests access levels for visitors.

Visitor Information:
- Type: {visitor_data.get('visitor_type', 'unknown')}
- Purpose: {visitor_data.get('purpose', 'Not specified')}
- Company: {visitor_data.get('company', 'Not specified')}
- Department: {visitor_data.get('department', 'Not specified')}
- Duration: {visitor_data.get('expected_duration', 'Not specified')}

Available access levels (from most to least restrictive):
1. "escorted_only" - Must be escorted at all times
2. "common_areas" - Access to lobby, reception, common areas only
3. "department_restricted" - Access to specific department only
4. "floor_restricted" - Access to specific floor
5. "building_restricted" - Access to specific building
6. "limited_general" - Limited general access with some restrictions
7. "general" - General visitor access

Consider:
- Delivery/vendor personnel typically need "escorted_only" or "common_areas"
- Contractors on long-term projects may need "department_restricted"
- Guests visiting employees usually need "common_areas" or "department_restricted"
- Emergency services may need "limited_general"
- Unknown/unverified visitors should get "escorted_only"

Return ONLY a JSON object with:
{{
    "suggested_access_level": "level_name",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation",
    "recommended_zones": ["zone1", "zone2"],
    "restrictions": ["restriction1", "restriction2"],
    "requires_escort": true/false
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = self._clean_json_response(response.text.strip())
            suggestion = json.loads(result_text)
            
            return {
                'success': True,
                'suggestion': suggestion
            }
            
        except Exception as e:
            # Fallback to rule-based suggestion
            return self._fallback_access_level_suggestion(visitor_data)
    
    def predict_visit_duration(self, visitor_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict visit duration based on visitor information and historical patterns
        
        Args:
            visitor_data: Dictionary containing visitor information
        
        Returns:
            Dict with predicted duration in minutes and confidence
        """
        prompt = f"""
You are an AI that predicts visitor visit durations based on context.

Visitor Information:
- Type: {visitor_data.get('visitor_type', 'unknown')}
- Purpose: {visitor_data.get('purpose', 'Not specified')}
- Company: {visitor_data.get('company', 'Not specified')}

Typical durations:
- Delivery: 15-30 minutes
- Job interview: 60-90 minutes
- Business meeting: 60-120 minutes
- Contractor work: 240-480 minutes (4-8 hours)
- Maintenance: 120-240 minutes
- Guest/social visit: 30-120 minutes
- Vendor consultation: 90-180 minutes

Based on the purpose and type, predict the visit duration.

Return ONLY a JSON object:
{{
    "predicted_duration_minutes": integer,
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation",
    "suggested_departure_buffer": integer (extra minutes to add for safety)
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = self._clean_json_response(response.text.strip())
            prediction = json.loads(result_text)
            
            return {
                'success': True,
                'prediction': prediction
            }
            
        except Exception as e:
            # Fallback to rule-based prediction
            return self._fallback_duration_prediction(visitor_data)
    
    def auto_fill_visitor_form(self, partial_data: Dict[str, Any], context: str = "") -> Dict[str, Any]:
        """
        Auto-fill missing visitor form fields using AI inference
        
        Args:
            partial_data: Partially filled visitor data
            context: Additional context or notes
        
        Returns:
            Dict with suggested values for missing fields
        """
        prompt = f"""
You are an AI assistant helping to complete a visitor registration form.

Partially filled data:
{json.dumps(partial_data, indent=2)}

Additional context:
{context}

Based on the provided information, suggest reasonable values for missing fields.
Consider:
- If purpose involves "interview", likely visitor_type is "guest"
- If purpose involves "repair" or "installation", likely "contractor" or "maintenance"
- If company is a delivery service (FedEx, UPS, DHL), likely "delivery"
- Infer department from purpose if possible
- Suggest typical visit duration based on purpose

Return ONLY a JSON object with suggested fields:
{{
    "suggested_fields": {{
        "field_name": {{
            "value": "suggested_value",
            "confidence": 0.0-1.0,
            "reasoning": "why this was suggested"
        }}
    }}
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = self._clean_json_response(response.text.strip())
            suggestions = json.loads(result_text)
            
            return {
                'success': True,
                'suggestions': suggestions.get('suggested_fields', {})
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Auto-fill failed: {str(e)}',
                'suggestions': {}
            }
    
    def analyze_visitor_risk(self, visitor_data: Dict[str, Any], historical_data: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Analyze potential security risks associated with a visitor
        
        Args:
            visitor_data: Current visitor information
            historical_data: Optional historical visitor data
        
        Returns:
            Dict with risk assessment and recommendations
        """
        history_summary = ""
        if historical_data:
            history_summary = f"\nHistorical visits: {len(historical_data)} previous visits"
        
        prompt = f"""
You are a security AI analyzing visitor risk factors.

Visitor Information:
{json.dumps(visitor_data, indent=2)}
{history_summary}

Risk factors to consider:
- Unknown/unverified company
- Vague or suspicious purpose
- No host assigned
- Unusual visit timing (late night, weekends)
- First-time visitor with high access requests
- Incomplete information
- Pattern anomalies (if historical data available)

Return ONLY a JSON object:
{{
    "risk_level": "low|medium|high",
    "risk_score": 0.0-1.0,
    "risk_factors": ["factor1", "factor2"],
    "recommendations": ["recommendation1", "recommendation2"],
    "requires_additional_verification": true/false,
    "suggested_mitigations": ["mitigation1", "mitigation2"]
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = self._clean_json_response(response.text.strip())
            analysis = json.loads(result_text)
            
            return {
                'success': True,
                'analysis': analysis
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Risk analysis failed: {str(e)}',
                'analysis': {
                    'risk_level': 'medium',
                    'risk_score': 0.5,
                    'risk_factors': ['Unable to complete AI analysis'],
                    'recommendations': ['Manual review recommended']
                }
            }
    
    # Helper methods
    
    def _clean_json_response(self, text: str) -> str:
        """Remove markdown code blocks and clean JSON response"""
        # Remove markdown code blocks
        text = re.sub(r'^```json\s*', '', text)
        text = re.sub(r'^```\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        return text.strip()
    
    def _validate_extracted_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean extracted visitor data"""
        cleaned = {}
        
        # String fields
        string_fields = ['first_name', 'last_name', 'email', 'phone', 'company', 
                        'visitor_type', 'purpose', 'department', 'host_name',
                        'id_type', 'id_number', 'vehicle_plate', 'emergency_contact',
                        'emergency_phone', 'notes']
        
        for field in string_fields:
            if field in data and data[field]:
                cleaned[field] = str(data[field]).strip()
        
        # Datetime fields
        for field in ['expected_arrival', 'expected_departure']:
            if field in data and data[field]:
                try:
                    # Validate ISO format
                    datetime.fromisoformat(data[field].replace('Z', '+00:00'))
                    cleaned[field] = data[field]
                except:
                    pass
        
        # Confidence score
        if 'confidence' in data:
            try:
                confidence = float(data['confidence'])
                cleaned['confidence'] = max(0.0, min(1.0, confidence))
            except:
                cleaned['confidence'] = 0.5
        
        return cleaned
    
    def _fallback_access_level_suggestion(self, visitor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Rule-based fallback for access level suggestion"""
        visitor_type = visitor_data.get('visitor_type', 'guest')
        
        access_mapping = {
            'delivery': 'escorted_only',
            'vendor': 'common_areas',
            'contractor': 'department_restricted',
            'guest': 'common_areas',
            'maintenance': 'department_restricted',
            'emergency': 'limited_general',
            'other': 'escorted_only'
        }
        
        suggested_level = access_mapping.get(visitor_type, 'escorted_only')
        
        return {
            'success': True,
            'suggestion': {
                'suggested_access_level': suggested_level,
                'confidence': 0.6,
                'reasoning': f'Rule-based suggestion for {visitor_type} visitor',
                'recommended_zones': ['reception', 'lobby'],
                'restrictions': ['No unescorted access'],
                'requires_escort': visitor_type in ['delivery', 'other']
            }
        }
    
    def _fallback_duration_prediction(self, visitor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Rule-based fallback for duration prediction"""
        visitor_type = visitor_data.get('visitor_type', 'guest')
        
        duration_mapping = {
            'delivery': 20,
            'vendor': 90,
            'contractor': 240,
            'guest': 60,
            'maintenance': 180,
            'emergency': 120,
            'other': 60
        }
        
        predicted_minutes = duration_mapping.get(visitor_type, 60)
        
        return {
            'success': True,
            'prediction': {
                'predicted_duration_minutes': predicted_minutes,
                'confidence': 0.6,
                'reasoning': f'Standard duration for {visitor_type} visits',
                'suggested_departure_buffer': 30
            }
        }
