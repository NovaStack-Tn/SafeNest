"""
Threat AI Analysis Service
Provides AI-powered threat analysis, action planning, and mitigation suggestions
Uses Google Gemini 2.5 Flash via centralized LLM service
"""
import logging
from typing import Dict, List, Any
from django.utils import timezone

from llm.services import LLMService
from ..models import Threat

logger = logging.getLogger(__name__)


class ThreatAIAnalysisService:
    """
    AI-powered threat analysis using Google Gemini 2.5 Flash
    """
    
    def __init__(self):
        """Initialize the AI analysis service"""
        self.llm = LLMService()
    
    def analyze_threat(self, threat: Threat) -> Dict[str, Any]:
        """
        Perform comprehensive AI analysis of a threat
        
        Args:
            threat: Threat instance to analyze
        
        Returns:
            dict: Analysis results with insights and recommendations
        """
        try:
            # Prepare threat context
            threat_context = self._prepare_threat_context(threat)
            
            # Create analysis prompt
            prompt = f"""Analyze this security threat and provide detailed insights:

**Threat Details:**
- Title: {threat.title}
- Type: {threat.get_threat_type_display()}
- Severity: {threat.get_severity_display()}
- Status: {threat.get_status_display()}
- Description: {threat.description}
- Risk Score: {threat.risk_score}/100
- Confidence: {threat.confidence_score * 100}%
- Source: {threat.source}
{f"- External Reference: {threat.external_ref}" if threat.external_ref else ""}
{f"- Location: {threat.location_name}" if threat.location_name else ""}
{f"- Attack Vector: {threat.attack_vector}" if threat.attack_vector else ""}
{f"- Tags: {', '.join(threat.tags)}" if threat.tags else ""}

**Analysis Required:**
1. Threat Assessment - Evaluate the actual risk and potential impact
2. Root Cause Analysis - Identify likely causes and attack vectors
3. Affected Systems - Determine what systems/users are at risk
4. Business Impact - Assess potential business consequences
5. Related Threats - Identify patterns or connections to known threats
6. Immediate Actions - List urgent actions needed
7. Confidence Level - Rate your analysis confidence (0-100%)

Provide a comprehensive JSON response."""

            # Get AI analysis
            response = self.llm.generate_completion(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.3
            )
            
            analysis = {
                'status': 'success',
                'threat_id': threat.id,
                'threat_title': threat.title,
                'analysis': response,
                'analyzed_at': timezone.now().isoformat(),
                'ai_model': 'gemini-2.5-flash'
            }
            
            logger.info(f"AI analysis completed for threat {threat.id}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing threat {threat.id}: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'threat_id': threat.id
            }
    
    def generate_action_plan(self, threat: Threat) -> Dict[str, Any]:
        """
        Generate AI-powered action plan for threat response
        
        Args:
            threat: Threat instance
        
        Returns:
            dict: Structured action plan with prioritized steps
        """
        try:
            prompt = f"""Generate a detailed action plan to respond to this security threat:

**Threat:**
- Title: {threat.title}
- Type: {threat.get_threat_type_display()}
- Severity: {threat.get_severity_display()}
- Description: {threat.description}
- Risk Score: {threat.risk_score}/100

**Action Plan Required:**
Generate a comprehensive, prioritized action plan with the following sections:

1. **Immediate Actions (0-1 hour):**
   - Critical steps to contain the threat
   - Emergency response procedures
   
2. **Short-term Actions (1-24 hours):**
   - Investigation steps
   - Evidence collection
   - Stakeholder notification
   
3. **Medium-term Actions (1-7 days):**
   - Remediation activities
   - Security improvements
   - Monitoring enhancements
   
4. **Long-term Actions (1-4 weeks):**
   - Preventive measures
   - Policy updates
   - Training requirements

5. **Resource Requirements:**
   - Personnel needed
   - Tools/technologies required
   - Budget considerations

6. **Success Metrics:**
   - How to measure response effectiveness
   - Key performance indicators

Provide specific, actionable steps with estimated timeframes and responsible parties."""

            response = self.llm.generate_completion(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.4
            )
            
            action_plan = {
                'status': 'success',
                'threat_id': threat.id,
                'threat_title': threat.title,
                'threat_severity': threat.severity,
                'action_plan': response,
                'generated_at': timezone.now().isoformat(),
                'ai_model': 'gemini-2.5-flash'
            }
            
            logger.info(f"Action plan generated for threat {threat.id}")
            return action_plan
            
        except Exception as e:
            logger.error(f"Error generating action plan for threat {threat.id}: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'threat_id': threat.id
            }
    
    def suggest_mitigation(self, threat: Threat) -> Dict[str, Any]:
        """
        Generate AI-powered mitigation suggestions
        
        Args:
            threat: Threat instance
        
        Returns:
            dict: Mitigation strategies and recommendations
        """
        try:
            prompt = f"""Provide comprehensive mitigation strategies for this security threat:

**Threat:**
- Title: {threat.title}
- Type: {threat.get_threat_type_display()}
- Severity: {threat.get_severity_display()}
- Description: {threat.description}
- Risk Score: {threat.risk_score}/100
{f"- Attack Vector: {threat.attack_vector}" if threat.attack_vector else ""}

**Mitigation Strategies Required:**

1. **Technical Controls:**
   - Network security measures
   - Access control improvements
   - Encryption/authentication enhancements
   - Monitoring and detection rules

2. **Procedural Controls:**
   - Process improvements
   - Policy updates
   - Incident response procedures
   - Communication protocols

3. **Administrative Controls:**
   - User training needs
   - Awareness campaigns
   - Role-based access reviews
   - Compliance requirements

4. **Preventive Measures:**
   - How to prevent recurrence
   - Vulnerability remediation
   - Security hardening
   - Patch management

5. **Compensating Controls:**
   - Alternative security measures
   - Temporary safeguards
   - Risk acceptance strategies

6. **Implementation Priority:**
   - Quick wins (immediate impact, low effort)
   - High-value (high impact, medium effort)
   - Strategic (long-term, high effort)

7. **Cost-Benefit Analysis:**
   - Estimated implementation costs
   - Risk reduction value
   - ROI considerations

Provide specific, implementable recommendations with technical details where applicable."""

            response = self.llm.generate_completion(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.3
            )
            
            mitigation = {
                'status': 'success',
                'threat_id': threat.id,
                'threat_title': threat.title,
                'threat_severity': threat.severity,
                'mitigation_strategies': response,
                'generated_at': timezone.now().isoformat(),
                'ai_model': 'gemini-2.5-flash'
            }
            
            logger.info(f"Mitigation suggestions generated for threat {threat.id}")
            return mitigation
            
        except Exception as e:
            logger.error(f"Error generating mitigation for threat {threat.id}: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'threat_id': threat.id
            }
    
    def bulk_analyze_threats(self, queryset, limit: int = 10) -> Dict[str, Any]:
        """
        Analyze multiple threats and identify patterns
        
        Args:
            queryset: QuerySet of threats to analyze
            limit: Maximum number of threats to analyze
        
        Returns:
            dict: Bulk analysis results with patterns and trends
        """
        try:
            threats = queryset.filter(status__in=['new', 'investigating'])[:limit]
            
            if threats.count() == 0:
                return {
                    'status': 'success',
                    'message': 'No threats to analyze',
                    'analyzed_count': 0
                }
            
            # Prepare threat summaries
            threat_summaries = []
            for threat in threats:
                threat_summaries.append({
                    'id': threat.id,
                    'title': threat.title,
                    'type': threat.get_threat_type_display(),
                    'severity': threat.get_severity_display(),
                    'risk_score': threat.risk_score,
                    'description': threat.description[:200] + '...' if len(threat.description) > 200 else threat.description,
                    'detected_at': threat.first_detected_at.isoformat()
                })
            
            prompt = f"""Analyze these {len(threat_summaries)} security threats and identify patterns:

**Threats:**
{self._format_threats_for_analysis(threat_summaries)}

**Analysis Required:**

1. **Pattern Identification:**
   - Common attack vectors
   - Related threat types
   - Temporal patterns (timing, frequency)
   - Geographic patterns (if applicable)

2. **Threat Clustering:**
   - Group related threats
   - Identify potential campaigns
   - Detect coordinated attacks

3. **Risk Prioritization:**
   - Rank threats by actual risk (not just severity)
   - Identify which threats need immediate attention
   - Suggest investigation order

4. **Common Root Causes:**
   - Shared vulnerabilities
   - Systemic weaknesses
   - Configuration issues

5. **Recommended Actions:**
   - Bulk mitigation strategies
   - Process improvements
   - Security enhancements

6. **Trend Analysis:**
   - Increasing/decreasing threat types
   - Emerging attack patterns
   - Effectiveness of current controls

Provide actionable insights for the security team."""

            response = self.llm.generate_completion(
                prompt=prompt,
                max_tokens=2500,
                temperature=0.3
            )
            
            bulk_analysis = {
                'status': 'success',
                'analyzed_count': len(threat_summaries),
                'threats_analyzed': [t['id'] for t in threat_summaries],
                'analysis': response,
                'analyzed_at': timezone.now().isoformat(),
                'ai_model': 'gemini-2.5-flash'
            }
            
            logger.info(f"Bulk analysis completed for {len(threat_summaries)} threats")
            return bulk_analysis
            
        except Exception as e:
            logger.error(f"Error in bulk threat analysis: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'analyzed_count': 0
            }
    
    def _prepare_threat_context(self, threat: Threat) -> str:
        """Prepare threat context for AI analysis"""
        context = f"""
Threat ID: {threat.id}
Title: {threat.title}
Type: {threat.get_threat_type_display()}
Severity: {threat.get_severity_display()}
Status: {threat.get_status_display()}
Risk Score: {threat.risk_score}
Confidence: {threat.confidence_score}
Source: {threat.source}
Description: {threat.description}
"""
        return context.strip()
    
    def _format_threats_for_analysis(self, threat_summaries: List[Dict]) -> str:
        """Format threat summaries for AI analysis"""
        formatted = []
        for i, threat in enumerate(threat_summaries, 1):
            formatted.append(f"""
{i}. [{threat['severity']}] {threat['title']}
   - Type: {threat['type']}
   - Risk Score: {threat['risk_score']}/100
   - Detected: {threat['detected_at']}
   - Description: {threat['description']}
""")
        return '\n'.join(formatted)
