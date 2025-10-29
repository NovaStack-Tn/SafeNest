# 🔧 Fix 500 Internal Server Error

## The Problem
```
GET http://localhost:8000/api/threat-intelligence/threats/ 500 (Internal Server Error)
POST http://localhost:8000/api/threat-intelligence/threats/ 500 (Internal Server Error)
```

**Root Cause:** The database tables for `threat_intelligence` app don't exist yet. Migrations need to be run.

---

## 🚀 Quick Fix (Follow These Steps)

### **Step 1: Stop Backend Server**
Press `Ctrl + C` in the terminal running Django

### **Step 2: Run Migrations**
```bash
cd backend

# Make migrations (create migration files)
python manage.py makemigrations threat_intelligence

# Apply migrations (create database tables)
python manage.py migrate threat_intelligence

# Apply all migrations
python manage.py migrate
```

### **Step 3: Verify Tables Created**
```bash
# Check if tables exist
python manage.py dbshell

# In the database shell:
\dt threat_intelligence*

# You should see:
# - threat_intelligence_threat
# - threat_intelligence_alert
# - threat_intelligence_riskassessment
# - threat_intelligence_threatindicator
# - threat_intelligence_watchlist

# Exit database shell
\q
```

### **Step 4: Check User Has Organization**
```bash
python manage.py shell

# In Python shell:
from django.contrib.auth import get_user_model
User = get_user_model()

# Check your user
user = User.objects.first()
print(f"User: {user.username}")
print(f"Organization: {user.organization}")

# If organization is None, create one:
if user.organization is None:
    from core.models import Organization
    org = Organization.objects.create(name="Default Organization")
    user.organization = org
    user.save()
    print(f"✅ Organization created and assigned!")

# Exit Python shell
exit()
```

### **Step 5: Restart Backend**
```bash
python manage.py runserver
```

### **Step 6: Test in Browser**
1. Refresh frontend: `Ctrl + Shift + R`
2. Go to `/threat-intelligence`
3. Click "Add First Threat"
4. Fill form and submit
5. ✅ Should work now!

---

## 🔍 Detailed Troubleshooting

### **Check Backend Console**
Look for error messages in the terminal running Django:
- **"no such table"** → Migrations not run
- **"organization_id cannot be NULL"** → User has no organization
- **"connection refused"** → Database not running

### **Common Errors & Solutions**

#### Error: "no such table: threat_intelligence_threat"
**Solution:** Run migrations
```bash
python manage.py migrate threat_intelligence
```

#### Error: "NOT NULL constraint failed: threat_intelligence_threat.organization_id"
**Solution:** Ensure user has organization
```bash
python manage.py shell
from django.contrib.auth import get_user_model
from core.models import Organization
User = get_user_model()

# Get your user
user = User.objects.get(username='your_username')

# Create/assign organization
org, created = Organization.objects.get_or_create(name="Main Organization")
user.organization = org
user.save()
```

#### Error: "relation 'threat_intelligence_threat' does not exist"
**Solution:** PostgreSQL needs migrations
```bash
python manage.py makemigrations threat_intelligence
python manage.py migrate threat_intelligence
```

---

## 📝 Migration Files Check

### **Expected Migration File:**
`backend/threat_intelligence/migrations/0001_initial.py`

If this file doesn't exist:
```bash
cd backend
python manage.py makemigrations threat_intelligence
```

You should see:
```
Migrations for 'threat_intelligence':
  threat_intelligence/migrations/0001_initial.py
    - Create model Alert
    - Create model RiskAssessment
    - Create model Threat
    - Create model ThreatIndicator
    - Create model Watchlist
```

Then apply:
```bash
python manage.py migrate threat_intelligence
```

You should see:
```
Running migrations:
  Applying threat_intelligence.0001_initial... OK
```

---

## 🧪 Test Database Connection

### **Quick Database Test:**
```bash
cd backend
python manage.py dbshell
```

If this fails, check database configuration in `backend/safenest/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

## ✅ Verification Steps

After running migrations, verify everything works:

### **1. Check Tables Exist:**
```bash
python manage.py dbshell
\dt threat_intelligence*
\q
```

### **2. Check Django Admin:**
1. Go to: `http://localhost:8000/admin`
2. Login with superuser
3. Look for "Threat Intelligence" section
4. Should see: Threats, Alerts, Risk Assessments, Indicators, Watchlists

### **3. Test API Endpoints:**
```bash
# Test GET (should return empty list, not 500)
curl http://localhost:8000/api/threat-intelligence/threats/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Should return: {"results": []}
```

### **4. Test Frontend:**
1. Open: `http://localhost:5173/threat-intelligence`
2. Should see "No Threats Found" (not error)
3. Click "Add First Threat"
4. Modal opens
5. Fill form and submit
6. ✅ Threat created!

---

## 🐛 Still Getting 500 Error?

### **Check Django Logs:**
Look at the terminal running `python manage.py runserver` for detailed error:

```
Internal Server Error: /api/threat-intelligence/threats/
Traceback (most recent call last):
  ... (error details here)
```

### **Enable Debug Mode:**
In `backend/safenest/settings.py`:
```python
DEBUG = True
```

Restart server and try again. You'll see detailed error in browser.

### **Check User Authentication:**
```bash
python manage.py shell

from django.contrib.auth import get_user_model
User = get_user_model()

# Check user exists
user = User.objects.filter(username='your_username').first()
print(f"User found: {user}")
print(f"Has organization: {user.organization if user else 'N/A'}")
```

---

## 🎯 Complete Setup Script

Run all commands at once:

```bash
# Navigate to backend
cd backend

# Make migrations
python manage.py makemigrations threat_intelligence

# Apply migrations
python manage.py migrate

# Create superuser (if needed)
python manage.py createsuperuser

# Start server
python manage.py runserver
```

---

## 📊 Expected Output

### **After Migrations:**
```
Operations to perform:
  Apply all migrations: threat_intelligence
Running migrations:
  Applying threat_intelligence.0001_initial... OK
```

### **After First Request:**
```
[29/Oct/2025 07:05:00] "GET /api/threat-intelligence/threats/ HTTP/1.1" 200 45
```
(Status 200, not 500!)

---

## 🎉 Success Indicators

✅ **No 500 errors in console**  
✅ **Tables visible in database**  
✅ **Django admin shows Threat Intelligence models**  
✅ **API returns empty list, not error**  
✅ **Frontend loads without errors**  
✅ **Can create threats through modal**  
✅ **Backend logs show 200 status codes**

---

## 💡 Pro Tip

Always run migrations after:
- Creating a new Django app
- Adding new models
- Modifying existing models
- Pulling code with model changes

**Command to remember:**
```bash
python manage.py makemigrations && python manage.py migrate
```

---

**After following these steps, the 500 errors should be gone!** ✅
