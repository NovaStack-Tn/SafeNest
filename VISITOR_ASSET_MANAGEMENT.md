# Visitor & Asset Management System

## Overview
Comprehensive visitor and asset management module with AI-powered features using **Google Gemini 2.5 Flash** for intelligent visitor pre-registration, access level suggestions, visit duration prediction, and risk analysis.

## Models

### 1. **Visitor**
Tracks visitors, guests, contractors, vendors, and delivery personnel.

**Fields:**
- **Basic Info**: `first_name`, `last_name`, `email`, `phone`, `company`, `visitor_type`
- **Identification**: `id_type`, `id_number`, `photo`
- **Visit Details**: `purpose`, `host`, `department`, `status`
- **Schedule**: `expected_arrival`, `expected_departure`, `actual_arrival`, `actual_departure`
- **AI Fields**: `ai_extracted`, `ai_confidence`, `ai_suggested_access_level`, `ai_predicted_duration`, `extracted_data`
- **Additional**: `notes`, `emergency_contact`, `emergency_phone`, `vehicle_plate`

**Status Choices:**
- `pre_registered`, `checked_in`, `checked_out`, `cancelled`, `blacklisted`

**Visitor Types:**
- `guest`, `contractor`, `vendor`, `delivery`, `maintenance`, `emergency`, `other`

---

### 2. **VisitorPass**
Temporary access credentials for visitors (QR codes, NFC, biometric, PIN).

**Fields:**
- **Pass Info**: `pass_type`, `pass_code` (unique), `status`
- **Access Control**: `access_level`, `allowed_areas`, `access_points` (M2M with AccessPoint)
- **Validity**: `valid_from`, `valid_until`, `times_used`, `last_used`, `max_uses`
- **Revocation**: `revoked_by`, `revoked_at`, `revocation_reason`

**Pass Types:**
- `qr_code`, `nfc`, `biometric`, `pin`, `digital`

---

### 3. **Asset**
Equipment, devices, vehicles, and inventory items.

**Fields:**
- **Basic**: `name`, `asset_type`, `asset_tag` (unique), `serial_number`
- **Details**: `description`, `manufacturer`, `model`, `specifications` (JSON)
- **Financial**: `purchase_date`, `purchase_price`, `warranty_expiry`
- **Status**: `status`, `condition`, `location`
- **Assignment**: `current_assignee`, `assigned_at`
- **Media**: `image`, `notes`

**Asset Types:**
- `laptop`, `desktop`, `mobile`, `tablet`, `vehicle`, `equipment`, `tool`, `key`, `camera`, `other`

**Status:**
- `available`, `assigned`, `in_use`, `maintenance`, `retired`, `lost`, `damaged`

---

### 4. **AssetAssignment**
Track who has what asset and for how long.

**Fields:**
- `asset`, `assignee`, `assigned_by`, `assigned_at`
- `expected_return`, `actual_return`
- `status`, `condition_on_assignment`, `condition_on_return`
- `assignment_notes`, `return_notes`

---

### 5. **MovementLog**
Track asset check-in/out and visitor movements.

**Fields:**
- `movement_type`, `timestamp`
- `asset`, `visitor`, `user`
- `from_location`, `to_location`, `access_point`
- `verified_by`, `verification_method`
- `notes`, `metadata` (JSON for GPS, device info)

**Movement Types:**
- `asset_checkout`, `asset_checkin`, `visitor_checkin`, `visitor_checkout`, `location_transfer`, `zone_entry`, `zone_exit`

---

## AI Service (Gemini 2.5 Flash)

### **VisitorAIService** (`visitors/ai_service.py`)

#### 1. **extract_visitor_info(text, source_type)**
Extracts visitor information from emails, forms, or messages.

**Input:**
- `text`: Raw email/form content
- `source_type`: `'email'`, `'form'`, or `'message'`

**Output:**
```json
{
  "success": true,
  "extracted_data": {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "company": "ABC Corp",
    "visitor_type": "contractor",
    "purpose": "HVAC maintenance",
    "expected_arrival": "2024-10-30T14:00:00",
    "expected_departure": "2024-10-30T17:00:00"
  },
  "confidence": 0.85
}
```

---

#### 2. **suggest_access_level(visitor_data)**
AI-powered access level recommendations based on visitor type, purpose, and context.

**Available Access Levels:**
- `escorted_only` - Must be escorted at all times
- `common_areas` - Lobby, reception, common areas only
- `department_restricted` - Specific department only
- `floor_restricted` - Specific floor
- `building_restricted` - Specific building
- `limited_general` - Limited general access
- `general` - General visitor access

**Output:**
```json
{
  "success": true,
  "suggestion": {
    "suggested_access_level": "department_restricted",
    "confidence": 0.9,
    "reasoning": "Contractor on scheduled maintenance work",
    "recommended_zones": ["maintenance_area", "mechanical_room"],
    "restrictions": ["No access to data center"],
    "requires_escort": false
  }
}
```

---

#### 3. **predict_visit_duration(visitor_data)**
Predicts visit duration based on visitor type and purpose.

**Output:**
```json
{
  "success": true,
  "prediction": {
    "predicted_duration_minutes": 180,
    "confidence": 0.8,
    "reasoning": "HVAC maintenance typically takes 2-4 hours",
    "suggested_departure_buffer": 30
  }
}
```

---

#### 4. **auto_fill_visitor_form(partial_data, context)**
Auto-completes missing visitor form fields using AI inference.

**Output:**
```json
{
  "success": true,
  "suggestions": {
    "visitor_type": {
      "value": "contractor",
      "confidence": 0.85,
      "reasoning": "Purpose involves repair work"
    },
    "department": {
      "value": "Facilities",
      "confidence": 0.75,
      "reasoning": "HVAC maintenance is facilities department"
    }
  }
}
```

---

#### 5. **analyze_visitor_risk(visitor_data, historical_data)**
Security risk assessment for visitors.

**Output:**
```json
{
  "success": true,
  "analysis": {
    "risk_level": "low",
    "risk_score": 0.2,
    "risk_factors": [],
    "recommendations": ["Standard visitor protocol"],
    "requires_additional_verification": false,
    "suggested_mitigations": []
  }
}
```

---

## API Endpoints

### **Visitors** (`/api/visitors/visitors/`)

#### Standard CRUD:
- `GET /api/visitors/visitors/` - List all visitors
- `POST /api/visitors/visitors/` - Create visitor
- `GET /api/visitors/visitors/{id}/` - Retrieve visitor
- `PATCH /api/visitors/visitors/{id}/` - Update visitor
- `DELETE /api/visitors/visitors/{id}/` - Delete visitor

#### AI Endpoints:
- `POST /api/visitors/visitors/ai-extract/` - Extract info from text
- `POST /api/visitors/visitors/ai-suggest-access/` - Get access level suggestions
- `POST /api/visitors/visitors/ai-predict-duration/` - Predict visit duration
- `POST /api/visitors/visitors/ai-autofill/` - Auto-fill form fields
- `POST /api/visitors/visitors/{id}/analyze-risk/` - Analyze visitor risk

#### Custom Actions:
- `POST /api/visitors/visitors/{id}/checkin/` - Check in visitor
- `POST /api/visitors/visitors/{id}/checkout/` - Check out visitor
- `GET /api/visitors/visitors/current/` - Currently checked-in visitors
- `GET /api/visitors/visitors/overdue/` - Overdue visitors
- `GET /api/visitors/visitors/stats/` - Visitor statistics

---

### **Visitor Passes** (`/api/visitors/visitor-passes/`)

#### Standard CRUD + Custom Actions:
- `POST /api/visitors/visitor-passes/{id}/activate/` - Activate pass
- `POST /api/visitors/visitor-passes/{id}/revoke/` - Revoke pass
- `POST /api/visitors/visitor-passes/{id}/use/` - Record pass usage

---

### **Assets** (`/api/visitors/assets/`)

#### Standard CRUD:
- Full CRUD operations available

#### Custom Actions:
- `GET /api/visitors/assets/available/` - Available assets
- `GET /api/visitors/assets/assigned/` - Assigned assets
- `POST /api/visitors/assets/{id}/assign/` - Assign asset to user
- `POST /api/visitors/assets/{id}/return_asset/` - Return assigned asset
- `GET /api/visitors/assets/stats/` - Asset statistics

---

### **Asset Assignments** (`/api/visitors/asset-assignments/`)

#### Standard CRUD + Filters:
- `GET /api/visitors/asset-assignments/active/` - Active assignments
- `GET /api/visitors/asset-assignments/overdue/` - Overdue assignments

---

### **Movement Logs** (`/api/visitors/movements/`)

#### Read-Only Operations:
- `GET /api/visitors/movements/` - All movements
- `GET /api/visitors/movements/recent/` - Last 24 hours

---

## Usage Examples

### 1. AI-Powered Visitor Pre-Registration

```python
# Extract visitor info from email
import requests

email_text = """
Subject: Visitor Pre-Registration

Hi,

John Doe from ABC Corp will be visiting tomorrow at 2 PM for HVAC maintenance.
Phone: +1234567890
Email: john.doe@abccorp.com
Expected to finish around 5 PM.

Thanks
"""

response = requests.post(
    'http://localhost:8000/api/visitors/visitors/ai-extract/',
    json={
        'text': email_text,
        'source_type': 'email'
    },
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)

extracted_data = response.json()['extracted_data']

# Create visitor with AI-extracted data
visitor_data = {
    **extracted_data,
    'ai_extracted': True,
    'ai_confidence': extracted_data.get('confidence')
}

visitor = requests.post(
    'http://localhost:8000/api/visitors/visitors/',
    json=visitor_data,
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)
```

---

### 2. Get AI Access Level Suggestion

```python
response = requests.post(
    'http://localhost:8000/api/visitors/visitors/ai-suggest-access/',
    json={
        'visitor_type': 'contractor',
        'purpose': 'HVAC maintenance',
        'company': 'ABC Corp',
        'department': 'Facilities'
    },
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)

suggestion = response.json()['suggestion']
# Use suggested_access_level when creating visitor pass
```

---

### 3. Check In/Out Visitors

```python
# Check in
requests.post(
    f'http://localhost:8000/api/visitors/visitors/{visitor_id}/checkin/',
    json={'verification_method': 'qr_code'},
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)

# Check out
requests.post(
    f'http://localhost:8000/api/visitors/visitors/{visitor_id}/checkout/',
    json={'verification_method': 'manual'},
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)
```

---

### 4. Asset Assignment Workflow

```python
# Assign asset
response = requests.post(
    f'http://localhost:8000/api/visitors/assets/{asset_id}/assign/',
    json={
        'assignee': user_id,
        'expected_return': '2024-11-01T17:00:00Z',
        'notes': 'For project work'
    },
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)

# Return asset
requests.post(
    f'http://localhost:8000/api/visitors/assets/{asset_id}/return_asset/',
    json={
        'condition': 'good',
        'notes': 'Returned in good condition'
    },
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)
```

---

## Configuration

### Requirements
- **Google Gemini API Key**: Set `GEMINI_API_KEY` in `.env`
- **Package**: `google-generativeai>=0.8.0` (already in requirements.txt)
- **Model**: `models/gemini-2.5-flash`

### Settings
```python
# backend/safenest/settings.py
INSTALLED_APPS = [
    ...
    'visitors',  # Visitor & Asset Management
    ...
]
```

### URLs
```python
# backend/safenest/urls.py
urlpatterns = [
    ...
    path('api/visitors/', include('visitors.urls')),
    ...
]
```

---

## Key Features

### ✅ Visitor Management
- Pre-registration with AI extraction
- Check-in/out tracking
- Visitor passes (QR, NFC, biometric, PIN)
- Access level management
- Overdue visitor alerts
- Visit history and analytics

### ✅ AI-Powered Features
- **Smart extraction** from emails/forms
- **Auto-fill** visitor details
- **Access level suggestions** based on context
- **Duration prediction** for planning
- **Risk analysis** for security

### ✅ Asset Management
- Complete asset inventory
- Assignment tracking
- Check-in/out workflow
- Warranty tracking
- Condition monitoring
- Location tracking

### ✅ Movement Logging
- Visitor movements
- Asset movements
- Access point integration
- Verification tracking
- Audit trail

---

## Database Schema

### Indexes
- `visitors_visitor_status_expected_arrival_idx`
- `visitors_visitor_organization_status_idx`
- `visitors_asset_asset_tag_idx`
- `visitors_asset_status_asset_type_idx`
- `visitors_movementlog_movement_type_timestamp_idx`

### Relationships
- **Visitor** → **VisitorPass** (1:N)
- **VisitorPass** → **AccessPoint** (M2M)
- **Asset** → **AssetAssignment** (1:N)
- **Asset/Visitor/User** → **MovementLog** (1:N)
- All models → **Organization** (Multi-tenant)

---

## Admin Interface

All models are registered in Django admin with:
- Advanced filtering
- Search functionality
- Organized fieldsets
- Read-only fields for timestamps and computed values
- Organization-level data isolation

---

## Testing

Run migrations:
```bash
cd backend
python manage.py makemigrations visitors
python manage.py migrate visitors
```

Create test data:
```bash
python manage.py shell
from visitors.models import *
from core.models import Organization, User

# Create test visitor
org = Organization.objects.first()
visitor = Visitor.objects.create(
    first_name='John',
    last_name='Doe',
    email='john@example.com',
    visitor_type='contractor',
    purpose='HVAC maintenance',
    expected_arrival='2024-10-30T14:00:00Z',
    expected_departure='2024-10-30T17:00:00Z',
    organization=org
)
```

---

## Next Steps

### Frontend Implementation (React + TypeScript)
1. **Visitors Page** - List, search, filter visitors
2. **Visitor Detail Modal** - View/edit visitor info
3. **AI Pre-Registration Form** - Paste email/text, auto-extract
4. **Check-In/Out Interface** - QR scanner, manual entry
5. **Assets Page** - Asset inventory and assignments
6. **Movement History** - Timeline view of movements
7. **Visitor Pass Generator** - QR code generation
8. **Dashboard Widgets** - Current visitors, overdue alerts, stats

### Additional Features
1. **Email notifications** for visitor arrivals
2. **SMS alerts** for hosts
3. **Badge printing** integration
4. **Photo capture** at check-in
5. **Visitor self-registration** portal
6. **Mobile app** for visitor check-in
7. **Integration with access control** hardware

---

## Summary

✅ **5 Models Created**: Visitor, VisitorPass, Asset, AssetAssignment, MovementLog  
✅ **AI Service**: Google Gemini 2.5 Flash integration for smart visitor management  
✅ **REST API**: Complete CRUD + 15+ custom endpoints  
✅ **Admin Interface**: Full Django admin configuration  
✅ **Migrations**: Applied successfully  
✅ **Multi-tenant**: Organization-level isolation  
✅ **Audit Trail**: Complete movement and assignment tracking  

The visitor and asset management system is now fully operational with AI-powered features! 🚀
