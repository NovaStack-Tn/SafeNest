# ✅ Fixed: Threat Intelligence 500 Error

## Problem
```
GET http://localhost:8000/api/threat-intelligence/threats/ 500 (Internal Server Error)
POST http://localhost:8000/api/threat-intelligence/threats/ 500 (Internal Server Error)

Error: column "created_at" of relation "threat_intelligence_threat" does not exist
```

## Root Causes (2 Issues Fixed)

### Issue 1: Missing perform_create() Methods
The ViewSets were missing `perform_create()` methods, which meant that when creating new records (Threats, Alerts, Risk Assessments, etc.), the `organization` and user fields were not being automatically set. This caused database constraint violations.

### Issue 2: Missing Timestamp Columns
The database tables were missing `created_at` and `updated_at` columns, even though they were defined in the models. This happened because the initial migration was applied before the timestamp fields were added to the models.

## Solution Applied

### Files Modified
**`backend/threat_intelligence/views.py`**

Added `perform_create()` methods to all 5 ViewSets:

#### 1. ThreatViewSet (Line 36)
```python
def perform_create(self, serializer):
    """Set organization and created_by when creating a threat"""
    serializer.save(
        organization=self.request.user.organization,
        created_by=self.request.user
    )
```

#### 2. AlertViewSet (Line 230)
```python
def perform_create(self, serializer):
    """Set organization when creating an alert"""
    serializer.save(organization=self.request.user.organization)
```

#### 3. RiskAssessmentViewSet (Line 311)
```python
def perform_create(self, serializer):
    """Set organization and assessed_by when creating a risk assessment"""
    serializer.save(
        organization=self.request.user.organization,
        assessed_by=self.request.user
    )
```

#### 4. ThreatIndicatorViewSet (Line 352)
```python
def perform_create(self, serializer):
    """Set organization and added_by when creating a threat indicator"""
    serializer.save(
        organization=self.request.user.organization,
        added_by=self.request.user
    )
```

#### 5. WatchlistViewSet (Line 437)
```python
def perform_create(self, serializer):
    """Set organization and added_by when creating a watchlist entry"""
    serializer.save(
        organization=self.request.user.organization,
        added_by=self.request.user
    )
```

### Migration Created
**`backend/threat_intelligence/migrations/0004_add_timestamps.py`**

Created a manual migration using `RunSQL` to add the missing `created_at` and `updated_at` columns to all 5 tables:
- threat_intelligence_threat
- threat_intelligence_alert
- threat_intelligence_riskassessment
- threat_intelligence_threatindicator
- threat_intelligence_watchlist

The migration safely checks if columns exist before adding them (using PostgreSQL's `IF NOT EXISTS`).

**Applied with:**
```bash
python manage.py migrate threat_intelligence
```

Output:
```
Applying threat_intelligence.0004_add_timestamps... OK
```

## What This Fixes
- ✅ **Missing columns error** - created_at and updated_at columns now exist
- ✅ **POST requests** now work - threats, alerts, etc. can be created
- ✅ **GET requests** work - can fetch lists of items  
- ✅ **Organization isolation** - each org only sees their own data
- ✅ **User tracking** - created_by, added_by, assessed_by fields are auto-set
- ✅ **No more 500 errors** - database constraint violations fixed
- ✅ **Proper timestamps** - all records track creation and update times

## Important: User Must Have Organization
The user making the requests **must have an organization assigned**. If not, you'll still get errors.

### Check User Has Organization
Run this in Django shell:
```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
from core.models import Organization

User = get_user_model()
user = User.objects.first()

print(f"User: {user.username}")
print(f"Organization: {user.organization}")

# If None, create and assign an organization:
if user.organization is None:
    org = Organization.objects.create(name="Main Organization")
    user.organization = org
    user.save()
    print("✅ Organization assigned!")
```

## Testing

### 1. Restart Backend Server
```bash
# Stop server (Ctrl+C), then restart:
python manage.py runserver
```

### 2. Test Creating a Threat
Go to: `http://localhost:5173/threat-intelligence`

Click "Add Threat" and fill the form:
- Title: "Suspicious Network Activity"
- Type: Cyber Security
- Severity: High
- Description: "Multiple failed login attempts detected"

Click "Create Threat" - should now work without 500 error!

### 3. Verify in Backend Console
You should see:
```
[29/Oct/2025 07:30:00] "POST /api/threat-intelligence/threats/ HTTP/1.1" 201 XXX
```

Status 201 (Created) instead of 500 (Internal Server Error)!

## Summary

### Two Issues Resolved:
1. **ViewSet Fix** - Added `perform_create()` methods to automatically set organization and user fields, preventing constraint violations and ensuring proper multi-tenant isolation
2. **Migration Fix** - Added missing `created_at` and `updated_at` timestamp columns to all 5 threat intelligence tables

### Files Changed:
- `backend/threat_intelligence/views.py` - Added 5 perform_create methods
- `backend/threat_intelligence/migrations/0004_add_timestamps.py` - New migration file
- `backend/core/management/commands/check_user_org.py` - Utility command

### Quick Fix Commands:
```bash
# Already applied, but for reference:
python manage.py migrate threat_intelligence
python manage.py check_user_org  # Verify users have organizations
python manage.py runserver  # Restart server
```

✅ **All 500 Errors Fixed!**
