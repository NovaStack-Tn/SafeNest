"""
Gemini AI service for Access Control insights and recommendations
"""
import logging
import json
from django.conf import settings
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Configure Gemini API
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)


class GeminiAccessControlService:
    """Service for generating AI-powered insights using Gemini"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
        self.enabled = bool(settings.GEMINI_API_KEY)
    
    def _get_fallback_suggestions(self, stats_data):
        """Generate basic suggestions when Gemini API is unavailable"""
        suggestions = []
        
        # High denial rate
        if stats_data.get('today_denied', 0) > 10:
            suggestions.append({
                'title': 'High Access Denial Rate',
                'description': f"{stats_data.get('today_denied', 0)} denials today. Review access permissions and schedules to reduce friction.",
                'priority': 'high',
                'category': 'security',
                'icon': 'shield'
            })
        
        # Anomalies detected
        if stats_data.get('today_anomalies', 0) > 0:
            suggestions.append({
                'title': 'Security Anomalies Detected',
                'description': f"{stats_data.get('today_anomalies', 0)} unusual patterns flagged. Investigate late-night access and pattern breaks.",
                'priority': 'high',
                'category': 'security',
                'icon': 'zap'
            })
        
        # Traffic optimization
        if stats_data.get('today_logs', 0) > 200:
            suggestions.append({
                'title': 'Peak Traffic Optimization',
                'description': 'High traffic volume detected. Consider adding additional entry points during rush hours (8-9 AM).',
                'priority': 'medium',
                'category': 'efficiency',
                'icon': 'clock'
            })
        
        # Default suggestion if none apply
        if not suggestions:
            suggestions.append({
                'title': 'System Operating Normally',
                'description': 'No critical issues detected. Continue monitoring access patterns for anomalies.',
                'priority': 'low',
                'category': 'operations',
                'icon': 'shield'
            })
        
        return suggestions
    
    def generate_access_point_suggestions(self, stats_data):
        """
        Generate optimization suggestions for access points based on stats.
        
        Args:
            stats_data: Dictionary with access points stats, denials, anomalies
        
        Returns:
            List of suggestion dictionaries
        """
        if not self.enabled:
            return self._get_fallback_suggestions(stats_data)
        
        try:
            # Prepare context for Gemini
            prompt = f"""
You are a security and operations AI assistant for an access control system.

Analyze this data and provide 3-5 actionable recommendations to improve security and efficiency:

**Access Points Statistics:**
- Total Access Points: {stats_data.get('total_access_points', 0)}
- Active Points: {stats_data.get('active_points', 0)}
- Today's Accesses: {stats_data.get('today_logs', 0)}
- Today's Denials: {stats_data.get('today_denied', 0)}
- Today's Anomalies: {stats_data.get('today_anomalies', 0)}

**Top Access Points (by traffic):**
{json.dumps(stats_data.get('top_access_points', [])[:5], indent=2)}

**Hourly Distribution:**
{json.dumps(stats_data.get('access_by_hour', {}), indent=2)}

Provide recommendations in JSON format:
{{
  "suggestions": [
    {{
      "title": "Brief title",
      "description": "Detailed recommendation",
      "priority": "high|medium|low",
      "category": "security|operations|efficiency",
      "icon": "shield|clock|users|zap"
    }}
  ]
}}

Focus on:
1. Security improvements (high denials, anomalies, unusual patterns)
2. Operational efficiency (bottlenecks, peak hours, capacity)
3. Cost optimization (underutilized points, redundancy)
"""
            
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Extract JSON from response
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            
            result = json.loads(text)
            suggestions = result.get('suggestions', [])
            
            logger.info(f"Generated {len(suggestions)} suggestions via Gemini")
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating Gemini suggestions: {e}")
            return self._get_fallback_suggestions(stats_data)
    
    def _get_fallback_alerts(self, logs_data, anomalies_data):
        """Generate basic alerts when Gemini API is unavailable"""
        alerts = []
        
        anomaly_count = len([log for log in logs_data if log.get('is_anomaly')])
        denied_count = len([log for log in logs_data if not log.get('is_granted')])
        
        # Critical: Multiple anomalies
        if anomaly_count >= 3:
            alerts.append({
                'title': 'Multiple Anomalies Detected',
                'message': f'{anomaly_count} unusual access patterns detected in recent activity',
                'severity': 'critical',
                'action': 'Review anomaly logs immediately and investigate suspicious access patterns',
                'affected_count': anomaly_count
            })
        
        # High: Unusual access denials
        if denied_count > 15:
            alerts.append({
                'title': 'High Access Denial Rate',
                'message': f'{denied_count} access attempts denied - possible security probing or permission issues',
                'severity': 'high',
                'action': 'Review denied access logs and verify user permissions are up to date',
                'affected_count': denied_count
            })
        
        # Medium: Pattern changes
        if anomaly_count > 0 and anomaly_count < 3:
            alerts.append({
                'title': 'Unusual Access Pattern',
                'message': 'Off-hours or unusual location access detected',
                'severity': 'medium',
                'action': 'Monitor user activity and verify business justification',
                'affected_count': anomaly_count
            })
        
        # Default if no alerts
        if not alerts:
            alerts.append({
                'title': 'No Critical Issues',
                'message': 'Access control system operating within normal parameters',
                'severity': 'low',
                'action': 'Continue routine monitoring',
                'affected_count': 0
            })
        
        return alerts
    
    def generate_security_alerts(self, logs_data, anomalies_data):
        """
        Generate AI-powered security alerts based on recent activity.
        
        Args:
            logs_data: Recent access logs
            anomalies_data: Recent anomalies
        
        Returns:
            List of alert dictionaries
        """
        if not self.enabled:
            return self._get_fallback_alerts(logs_data, anomalies_data)
        
        try:
            prompt = f"""
You are a security AI assistant analyzing access control events.

Analyze these recent events and anomalies, then generate security alerts:

**Recent Access Logs (last 24h):**
- Total Events: {len(logs_data)}
- Granted: {sum(1 for log in logs_data if log.get('is_granted'))}
- Denied: {sum(1 for log in logs_data if not log.get('is_granted'))}
- Flagged by AI: {sum(1 for log in logs_data if log.get('is_anomaly'))}

**Anomaly Summary:**
{json.dumps(anomalies_data[:10], indent=2)}

Generate 2-4 critical security alerts in JSON format:
{{
  "alerts": [
    {{
      "title": "Alert title",
      "message": "Detailed alert message",
      "severity": "critical|high|medium|low",
      "action": "Recommended action to take",
      "affected_count": 0
    }}
  ]
}}

Focus on:
1. Unusual patterns (late night access, weekend activity)
2. Security threats (rapid attempts, simultaneous access)
3. System issues (high denial rates, failed authentications)
4. Insider risk indicators
"""
            
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Extract JSON
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            
            result = json.loads(text)
            alerts = result.get('alerts', [])
            
            logger.info(f"Generated {len(alerts)} security alerts via Gemini")
            return alerts
            
        except Exception as e:
            logger.error(f"Error generating Gemini alerts: {e}")
            return self._get_fallback_alerts(logs_data, anomalies_data)
    
    def generate_daily_report(self, summary_data):
        """
        Generate executive daily report.
        
        Args:
            summary_data: Complete day's statistics
        
        Returns:
            Dictionary with report sections
        """
        if not self.enabled:
            return {
                "summary": "Gemini AI not configured",
                "highlights": [],
                "recommendations": []
            }
        
        try:
            prompt = f"""
You are an executive assistant generating a daily access control report.

**Daily Statistics:**
{json.dumps(summary_data, indent=2)}

Generate a professional daily report in JSON format:
{{
  "summary": "2-3 sentence executive summary",
  "highlights": [
    "Key highlight 1",
    "Key highlight 2",
    "Key highlight 3"
  ],
  "concerns": [
    "Security concern if any"
  ],
  "recommendations": [
    "Action recommendation 1",
    "Action recommendation 2"
  ],
  "metrics": {{
    "trend": "improving|stable|concerning",
    "efficiency_score": 85
  }}
}}

Be concise, professional, and actionable.
"""
            
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Extract JSON
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            
            result = json.loads(text)
            
            logger.info("Generated daily report via Gemini")
            return result
            
        except Exception as e:
            logger.error(f"Error generating Gemini report: {e}")
            return {
                "summary": "Error generating report",
                "highlights": [],
                "recommendations": []
            }


# Singleton instance
_service = None

def get_gemini_service():
    """Get or create Gemini service singleton"""
    global _service
    if _service is None:
        _service = GeminiAccessControlService()
    return _service
