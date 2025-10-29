# 🛡️ Threat Intelligence Management System

## Overview

Complete threat intelligence management system for SafeNest with AI-powered analysis using Google Gemini 2.5 Flash.

## Features

### 1. **Threat Management**
- Track and manage security threats
- AI-powered threat analysis and severity assessment
- Automatic indicator extraction
- AI-generated risk assessments
- Status tracking (new, investigating, confirmed, mitigated, resolved)
- Assignment and ownership management

### 2. **Alert Management**
- System-generated security alerts
- Alert acknowledgment and resolution workflows
- Alert-to-threat linking
- Real-time notifications
- Alert statistics and analytics

### 3. **Risk Assessments**
- Comprehensive risk analysis framework
- Likelihood and impact assessment
- AI-generated mitigation strategies
- Cost estimation for mitigation
- Review scheduling and tracking

### 4. **Threat Indicators (IOCs)**
- Track Indicators of Compromise
- Support for multiple indicator types:
  - IP addresses
  - Domains and URLs
  - File hashes
  - Email addresses
  - Usernames
  - Phone numbers
  - License plates
  - Device IDs
  - Behavioral patterns
- Confidence scoring
- False positive marking
- Occurrence tracking

### 5. **Watchlist Management**
- Monitor persons, vehicles, and entities of interest
- Risk level classification
- Detection tracking
- Automated alerting
- Expiry management

## Backend Structure

### Models

#### Threat
```python
- organization: FK to Organization
- title: CharField(255)
- description: TextField
- threat_type: Choice (physical, cyber, insider, terrorism, fraud, data_breach, social_engineering, other)
- severity: Choice (critical, high, medium, low, info)
- status: Choice (new, investigating, confirmed, mitigated, resolved, false_positive)
- source: CharField (where identified)
- tags: JSONField
- metadata: JSONField
- ai_analyzed: Boolean
- ai_confidence: Float
- ai_suggested_severity: CharField
- ai_analysis: JSONField
- assigned_to: FK to User
- created_by: FK to User
- first_detected: DateTimeField
- last_activity: DateTimeField
```

#### Alert
```python
- organization: FK to Organization
- title: CharField(255)
- description: TextField
- alert_type: Choice (intrusion, anomaly, unauthorized_access, suspicious_activity, policy_violation, system, face_recognition, other)
- severity: Choice (critical, high, medium, low, info)
- status: Choice (new, acknowledged, investigating, resolved, dismissed)
- threat: FK to Threat (optional)
- acknowledged_by/at: FK to User, DateTimeField
- resolved_by/at: FK to User, DateTimeField
- resolution_notes: TextField
```

#### RiskAssessment
```python
- organization: FK to Organization
- threat: FK to Threat
- risk_level: Choice (critical, high, medium, low, negligible)
- likelihood: Choice (certain, likely, possible, unlikely, rare)
- impact: Choice (catastrophic, severe, moderate, minor, insignificant)
- vulnerability_analysis: TextField
- impact_analysis: TextField
- mitigation_strategy: TextField
- residual_risk: TextField
- estimated_cost: DecimalField
- required_resources: TextField
- timeline: CharField
- ai_generated: Boolean
- ai_confidence: Float
- ai_recommendations: JSONField
```

#### ThreatIndicator
```python
- organization: FK to Organization
- threat: FK to Threat (optional)
- indicator_type: Choice (ip_address, domain, url, file_hash, email, username, phone, license_plate, device_id, pattern, other)
- value: CharField(500)
- confidence: Choice (high, medium, low)
- first_seen: DateTimeField
- last_seen: DateTimeField
- occurrence_count: Integer
- is_active: Boolean
- is_false_positive: Boolean
```

#### Watchlist
```python
- organization: FK to Organization
- threat: FK to Threat (optional)
- watchlist_type: Choice (person, vehicle, organization, location, device)
- subject_name: CharField(255)
- subject_id: CharField(255)
- risk_level: Choice (critical, high, medium, low, monitor)
- reason: TextField
- attributes: JSONField (flexible for different types)
- alert_on_detection: Boolean
- auto_notify: JSONField (user IDs)
- action_instructions: TextField
- detection_count: Integer
- last_detected: DateTimeField
- expiry_date: DateField
```

### API Endpoints

#### Threats
```
GET    /api/threat-intelligence/threats/
POST   /api/threat-intelligence/threats/
GET    /api/threat-intelligence/threats/{id}/
PUT    /api/threat-intelligence/threats/{id}/
PATCH  /api/threat-intelligence/threats/{id}/
DELETE /api/threat-intelligence/threats/{id}/

POST   /api/threat-intelligence/threats/{id}/assign/
POST   /api/threat-intelligence/threats/{id}/update_status/
POST   /api/threat-intelligence/threats/{id}/ai_analyze/
POST   /api/threat-intelligence/threats/{id}/generate_risk_assessment/
POST   /api/threat-intelligence/threats/{id}/extract_indicators/
GET    /api/threat-intelligence/threats/statistics/
```

#### Alerts
```
GET    /api/threat-intelligence/alerts/
POST   /api/threat-intelligence/alerts/
GET    /api/threat-intelligence/alerts/{id}/
PUT    /api/threat-intelligence/alerts/{id}/
PATCH  /api/threat-intelligence/alerts/{id}/
DELETE /api/threat-intelligence/alerts/{id}/

POST   /api/threat-intelligence/alerts/{id}/acknowledge/
POST   /api/threat-intelligence/alerts/{id}/resolve/
POST   /api/threat-intelligence/alerts/{id}/dismiss/
GET    /api/threat-intelligence/alerts/statistics/
```

#### Risk Assessments
```
GET    /api/threat-intelligence/risk-assessments/
POST   /api/threat-intelligence/risk-assessments/
GET    /api/threat-intelligence/risk-assessments/{id}/
PUT    /api/threat-intelligence/risk-assessments/{id}/
PATCH  /api/threat-intelligence/risk-assessments/{id}/
DELETE /api/threat-intelligence/risk-assessments/{id}/
GET    /api/threat-intelligence/risk-assessments/statistics/
```

#### Threat Indicators
```
GET    /api/threat-intelligence/indicators/
POST   /api/threat-intelligence/indicators/
GET    /api/threat-intelligence/indicators/{id}/
PUT    /api/threat-intelligence/indicators/{id}/
PATCH  /api/threat-intelligence/indicators/{id}/
DELETE /api/threat-intelligence/indicators/{id}/

POST   /api/threat-intelligence/indicators/{id}/mark_false_positive/
POST   /api/threat-intelligence/indicators/{id}/increment_occurrence/
POST   /api/threat-intelligence/indicators/search/
GET    /api/threat-intelligence/indicators/statistics/
```

#### Watchlist
```
GET    /api/threat-intelligence/watchlists/
POST   /api/threat-intelligence/watchlists/
GET    /api/threat-intelligence/watchlists/{id}/
PUT    /api/threat-intelligence/watchlists/{id}/
PATCH  /api/threat-intelligence/watchlists/{id}/
DELETE /api/threat-intelligence/watchlists/{id}/

POST   /api/threat-intelligence/watchlists/{id}/record_detection/
POST   /api/threat-intelligence/watchlists/{id}/deactivate/
POST   /api/threat-intelligence/watchlists/search_subject/
GET    /api/threat-intelligence/watchlists/statistics/
```

## AI Services (Gemini 2.5 Flash)

### `analyze_threat(threat_description, threat_type, source)`
Analyzes a threat and provides:
- Severity assessment
- Confidence score
- Attack vectors
- Potential impact
- Key indicators
- Recommended actions
- Risk factors

### `generate_risk_assessment(threat_title, threat_description, threat_type)`
Generates comprehensive risk assessment:
- Risk level (critical to negligible)
- Likelihood assessment
- Impact analysis
- Vulnerability analysis
- Mitigation strategies
- Cost estimation
- Timeline recommendations

### `extract_threat_indicators(description, metadata)`
Extracts IOCs from threat description:
- IP addresses
- Domains/URLs
- File hashes
- Email addresses
- Usernames and identifiers
- Behavioral patterns
- Confidence scoring

### `analyze_watchlist_subject(subject_name, subject_type, reason, attributes)`
Analyzes watchlist subjects:
- Risk level assessment
- Threat assessment
- Monitoring recommendations
- Alert triggers
- Action instructions

### `correlate_threats(threat_descriptions)`
Identifies patterns across multiple threats:
- Common patterns
- Potential campaigns
- Shared indicators
- Threat actors
- Risk escalation analysis

### `generate_threat_report(threats_data, time_period)`
Generates comprehensive threat intelligence report:
- Executive summary
- Threat landscape analysis
- Key findings
- Trends and patterns
- Top threats
- Strategic recommendations
- Metrics and KPIs

## Frontend Features

### Main Interface
- **Statistics Dashboard**: Real-time metrics for threats, alerts, and risk levels
- **Tabbed Navigation**: 
  - Threats
  - Alerts
  - Risk Assessments
  - Threat Indicators
  - Watchlist

### Threat Cards
- Severity and status badges
- Threat type classification
- Source attribution
- Creation date
- Quick actions (View Details, AI Analyze)

### Alert Management
- Color-coded severity indicators
- Status workflow (new → acknowledged → investigating → resolved)
- Bulk operations
- Alert-to-threat linking

## Configuration

### Environment Variables
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

### Settings (already configured)
```python
INSTALLED_APPS = [
    ...
    'threat_intelligence.apps.ThreatIntelligenceConfig',
]
```

### URLs (already configured)
```python
path('api/threat-intelligence/', include('threat_intelligence.urls')),
```

## Database Migration

Run migrations to create the threat intelligence tables:

```bash
cd backend
python manage.py makemigrations threat_intelligence
python manage.py migrate threat_intelligence
```

## Usage Examples

### Creating a Threat
```python
POST /api/threat-intelligence/threats/
{
  "title": "Suspicious Login Attempts",
  "description": "Multiple failed login attempts from unknown IP addresses",
  "threat_type": "cyber",
  "severity": "high",
  "source": "IDS System"
}
```

### AI-Analyzing a Threat
```python
POST /api/threat-intelligence/threats/123/ai_analyze/
```

Response includes AI analysis with severity, attack vectors, indicators, and recommendations.

### Generating Risk Assessment
```python
POST /api/threat-intelligence/threats/123/generate_risk_assessment/
```

Automatically creates a comprehensive risk assessment record with AI recommendations.

### Extracting Indicators
```python
POST /api/threat-intelligence/threats/123/extract_indicators/
```

Automatically extracts and creates ThreatIndicator records from threat description.

### Creating an Alert
```python
POST /api/threat-intelligence/alerts/
{
  "title": "Unauthorized Access Detected",
  "description": "User attempted to access restricted area",
  "alert_type": "unauthorized_access",
  "severity": "critical",
  "threat": 123
}
```

### Acknowledging an Alert
```python
POST /api/threat-intelligence/alerts/456/acknowledge/
```

### Adding to Watchlist
```python
POST /api/threat-intelligence/watchlists/
{
  "watchlist_type": "person",
  "subject_name": "John Doe",
  "subject_id": "EMP-12345",
  "risk_level": "medium",
  "reason": "Former employee with security clearance",
  "alert_on_detection": true,
  "action_instructions": "Notify security immediately"
}
```

### Searching Indicators
```python
POST /api/threat-intelligence/indicators/search/
{
  "value": "192.168.1.100"
}
```

## Multi-Tenancy

All data is automatically scoped to the user's organization:
- Organization field set automatically on creation
- Queries filtered by user's organization
- Full data isolation between organizations

## Permissions

All endpoints require authentication (`IsAuthenticated`):
- Users can only access data from their organization
- CRUD operations based on user permissions
- Assignment requires appropriate role

## Frontend Integration

The Threat Intelligence page is already integrated:
- Route: `/threat-intelligence`
- Component: `ThreatIntel.tsx`
- Navigation: Already in sidebar

## Key Benefits

✅ **Comprehensive**: Covers all aspects of threat intelligence management
✅ **AI-Powered**: Gemini 2.5 Flash for intelligent analysis
✅ **Integrated**: Links threats, alerts, assessments, and indicators
✅ **Scalable**: Multi-tenant with organization isolation
✅ **Actionable**: Clear workflows and recommendations
✅ **Real-time**: Live statistics and updates
✅ **Flexible**: JSON fields for extensibility

## Files Created/Modified

### Backend
- `backend/threat_intelligence/models.py` - 5 models
- `backend/threat_intelligence/serializers.py` - 5 serializers
- `backend/threat_intelligence/views.py` - 5 ViewSets with AI endpoints
- `backend/threat_intelligence/urls.py` - URL routing
- `backend/threat_intelligence/admin.py` - Admin interface
- `backend/threat_intelligence/ai_service.py` - AI analysis functions
- `backend/safenest/settings.py` - App registration
- `backend/safenest/urls.py` - URL inclusion

### Frontend
- `frontend/src/pages/ThreatIntel.tsx` - Complete UI with tabs

### Documentation
- `THREAT_INTELLIGENCE_GUIDE.md` - This file

## Next Steps

1. **Run Migrations**: Apply database migrations
2. **Test AI Features**: Ensure GEMINI_API_KEY is configured
3. **Create Test Data**: Add sample threats and alerts
4. **Integrate Webhooks**: Connect with existing alert systems
5. **Add Notifications**: Real-time alerts for critical threats
6. **Create Dashboards**: Add visualization for threat trends
7. **Build Reports**: Automated threat intelligence reports

## Support

For issues or questions, refer to:
- Main project documentation: `README.md`
- API documentation: Run server and visit `/admin/`
- Gemini setup: `GEMINI_SETUP.md`
