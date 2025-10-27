# SafeNest Quick Start Guide

## Prerequisites
- Docker & Docker Compose installed
- OpenAI API Key (get from https://platform.openai.com/api-keys)

## 🚀 Option 1: Docker (Recommended)

### 1. Configure Environment
```bash
cd SafeNest/backend
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Start Everything
```bash
docker-compose up -d
```

This starts PostgreSQL, Redis, MinIO, Django, and Celery workers.

### 3. Create Admin User
```bash
docker-compose exec backend python manage.py createsuperuser
```

### 4. Access the Platform
- **API**: http://localhost:8000/api/
- **Admin**: http://localhost:8000/admin/
- **API Docs**: http://localhost:8000/api/schema/swagger-ui/

## 🛠️ Option 2: Local Development

### 1. Setup Backend
```bash
cd SafeNest/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
```

### 2. Start Database (Docker)
```bash
docker run -d --name safenest-pg \
  -e POSTGRES_DB=safenest \
  -e POSTGRES_USER=safenest \
  -e POSTGRES_PASSWORD=safenest \
  -p 5432:5432 \
  pgvector/pgvector:pg16

docker run -d --name safenest-redis \
  -p 6379:6379 \
  redis:7-alpine
```

### 3. Run Migrations
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4. Start Services (4 terminals)
```bash
# Terminal 1: Django
python manage.py runserver

# Terminal 2: Celery Worker
celery -A safenest worker -l info

# Terminal 3: Celery Beat
celery -A safenest beat -l info

# Terminal 4: Optional - Channels (for WebSocket)
daphne -b 0.0.0.0 -p 8000 safenest.asgi:application
```

## 📝 First Steps After Setup

### 1. Login to Admin
Go to http://localhost:8000/admin/ and login with your superuser credentials.

### 2. Create an Organization
```python
# Admin panel: Core > Organizations > Add
Name: "My Company"
Slug: "my-company"
```

### 3. Create Users with Roles
```python
# Admin panel: Core > Users > Add
Username: security_officer
Organization: My Company
Role: Security Officer
```

### 4. Configure Anomaly Rules
```python
# Admin panel: Security > Anomaly Rules > Add
Name: "After Hours Login"
Rule Type: Time-based
Config: {"allowed_hours": [9,10,11,12,13,14,15,16,17]}
```

### 5. Test Face Recognition

**Create Face Identity:**
```bash
curl -X POST http://localhost:8000/api/faces/identities/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "organization": 1,
    "person_label": "John Doe",
    "person_meta": {"employee_id": "EMP001"}
  }'
```

**Upload Photos for Enrollment:**
```bash
curl -X POST http://localhost:8000/api/faces/identities/1/enroll/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "images=@photo1.jpg" \
  -F "images=@photo2.jpg" \
  -F "images=@photo3.jpg"
```

**Detect Faces in Image:**
```bash
curl -X POST http://localhost:8000/api/faces/detections/detect/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "image=@test_image.jpg" \
  -F "camera_id=1"
```

### 6. Chat with AI Assistant

**Get JWT Token:**
```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'
```

**Chat:**
```bash
curl -X POST http://localhost:8000/api/llm/api/chat/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me all high-risk events from the last 24 hours",
    "bot_type": "assistant"
  }'
```

## 🔍 Testing the System

### Create Test Data
```bash
# Access Django shell
python manage.py shell

# Create test login events
from security.models import LoginEvent
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.first()

LoginEvent.objects.create(
    user=user,
    username=user.username,
    success=True,
    ip_address="192.168.1.100",
    country_code="US",
    country_name="United States",
    user_agent="Mozilla/5.0..."
)
```

### View Dashboard Stats
```bash
curl http://localhost:8000/api/dashboard/stats/?range=7d \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Monitor Real-time Alerts (WebSocket)
```javascript
// In browser console or WebSocket client
const ws = new WebSocket('ws://localhost:8000/ws/alerts/');
ws.onmessage = (event) => {
    console.log('Alert:', JSON.parse(event.data));
};
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Check what's using port 8000
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or use different port
python manage.py runserver 8001
```

### Database Connection Error
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Restart container
docker restart safenest-pg

# Check logs
docker logs safenest-pg
```

### Celery Worker Not Starting
```bash
# Check Redis connection
redis-cli ping

# Check environment
echo $CELERY_BROKER_URL

# Start with verbose logging
celery -A safenest worker -l debug
```

### InsightFace Model Download Issues
```bash
# Manually download models
cd ~/.insightface/models
wget https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip
unzip buffalo_l.zip
```

## 📚 Next Steps

1. **Read the full README.md** for detailed API documentation
2. **Explore the Admin Panel** to understand all features
3. **Test face recognition** with your photos
4. **Configure anomaly rules** for your use case
5. **Integrate with frontend** or build custom UI
6. **Deploy to production** following security checklist

## 🆘 Getting Help

- Check logs: `docker-compose logs backend`
- Django logs: `backend/logs/safenest.log`
- Database logs: `docker logs safenest-postgres`
- Celery logs: `docker logs safenest-celery-worker`

## 🎯 Demo Scenario

Try this end-to-end flow:

1. **Simulate anomalous login** from unusual country
2. **System creates alert** automatically
3. **View alert in dashboard** API
4. **Ask AI assistant**: "What happened in the last hour?"
5. **AI creates incident** based on findings
6. **Upload face** and test recognition
7. **View all activity** in real-time WebSocket feed

---

**You're all set! 🎉** Start building amazing security features with SafeNest!
