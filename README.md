# SafeNest - Smart Access & Incident Management Platform

SafeNest is an AI-powered security platform combining face recognition, anomaly detection, incident management, and LLM-powered assistants for comprehensive security operations.

## 🚀 Features

### Core Capabilities
- **Multi-tenant Architecture** - Organizations with RBAC (Admin, Security Officer, Employee, Viewer)
- **Face Recognition** - InsightFace (ArcFace) with pgvector similarity search
- **Anomaly Detection** - Rule-based + ML (Isolation Forest) for login anomalies
- **Incident Management** - Full lifecycle tracking with evidence and timelines
- **LLM Assistants** - 3 AI bots (General Assistant, Recommendations, Analysis) with OpenAI
- **Real-time Alerts** - WebSocket notifications via Django Channels
- **Comprehensive Audit** - All actions logged for compliance

### Technical Stack
- **Backend**: Django 5, Django REST Framework, Django Channels
- **Database**: PostgreSQL 16 + pgvector
- **Queue**: Celery + Redis
- **Storage**: MinIO/S3
- **AI/ML**: InsightFace, scikit-learn, OpenAI GPT-4
- **Infrastructure**: Docker Compose

## 📋 Prerequisites

- Python 3.11+
- Docker & Docker Compose
- OpenAI API Key (for LLM features)
- 8GB+ RAM (for face recognition models)

## 🛠️ Quick Start

### 1. Clone & Setup

```bash
cd SafeNest/backend
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Start with Docker Compose

```bash
docker-compose up -d
```

This will start:
- PostgreSQL (port 5432)
- Redis (port 6379)
- MinIO (port 9000, console 9001)
- Django Backend (port 8000)
- Celery Worker
- Celery Beat

### 3. Create Superuser

```bash
docker-compose exec backend python manage.py createsuperuser
```

### 4. Access the Platform

- **API**: http://localhost:8000/api/
- **Admin**: http://localhost:8000/admin/
- **MinIO Console**: http://localhost:9001/ (minioadmin/minioadmin)

## 🔧 Local Development Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Setup Database

```bash
# Start PostgreSQL with pgvector
docker run -d --name safenest-pg \
  -e POSTGRES_DB=safenest \
  -e POSTGRES_USER=safenest \
  -e POSTGRES_PASSWORD=safenest \
  -p 5432:5432 \
  pgvector/pgvector:pg16

# Run migrations
python manage.py migrate

# Create pgvector extension
python manage.py shell
>>> from django.db import connection
>>> with connection.cursor() as cursor:
...     cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
```

### 3. Start Services

```bash
# Terminal 1: Django
python manage.py runserver

# Terminal 2: Celery Worker
celery -A safenest worker -l info

# Terminal 3: Celery Beat
celery -A safenest beat -l info

# Terminal 4: Redis (if not using Docker)
redis-server
```

## 📚 API Documentation

### Authentication

```bash
# Get JWT Token
POST /api/auth/token/
{
  "username": "admin",
  "password": "password"
}

# Response
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

# Use token in headers
Authorization: Bearer <access_token>
```

### Key Endpoints

#### Core
- `GET /api/organizations/` - List organizations
- `GET /api/users/` - List users
- `GET /api/users/me/` - Current user profile
- `GET /api/audit-logs/` - Audit trail

#### Security
- `GET /api/security/login-events/` - Login history
- `GET /api/security/login-events/anomalies/` - Anomalous logins
- `GET /api/security/alerts/` - Security alerts
- `POST /api/security/alerts/` - Create alert
- `GET /api/security/anomaly-rules/` - Anomaly rules
- `WS /ws/alerts/` - Real-time alert stream

#### Incidents
- `GET /api/incidents/incidents/` - List incidents
- `POST /api/incidents/incidents/` - Create incident
- `POST /api/incidents/incidents/{id}/assign/` - Assign incident
- `POST /api/incidents/incidents/{id}/add_comment/` - Add comment
- `POST /api/incidents/evidence/` - Upload evidence

#### Face Recognition
- `GET /api/faces/cameras/` - List cameras
- `POST /api/faces/cameras/{id}/start_stream/` - Start RTSP processing
- `GET /api/faces/identities/` - List face identities
- `POST /api/faces/identities/` - Create identity
- `POST /api/faces/identities/{id}/enroll/` - Enroll with photos
- `GET /api/faces/detections/` - List detections
- `POST /api/faces/detections/detect/` - Detect faces in image

#### LLM & AI
- `POST /api/llm/api/chat/` - Chat with assistant
- `GET /api/llm/api/recommendations/` - Get AI recommendations
- `GET /api/llm/api/weekly_analysis/` - Security analysis report
- `GET /api/llm/sessions/` - Chat sessions

#### Dashboard
- `GET /api/dashboard/stats/?range=7d` - KPI statistics
- `GET /api/dashboard/activity/` - Recent activity feed
- `GET /api/dashboard/risk-map/` - Geographic risk map

## 🤖 AI Services

### Face Recognition with InsightFace

```python
# Enroll a person
POST /api/faces/identities/
{
  "organization": 1,
  "person_label": "John Doe",
  "person_meta": {
    "employee_id": "EMP001",
    "department": "Engineering"
  }
}

# Upload photos and enroll
POST /api/faces/identities/1/enroll/
FormData: images=[file1.jpg, file2.jpg, file3.jpg]

# Detect and recognize faces
POST /api/faces/detections/detect/
FormData: image=frame.jpg, camera_id=1
```

### LLM Assistant Chat

```python
# Start chat
POST /api/llm/api/chat/
{
  "message": "Show me high-risk events from yesterday",
  "bot_type": "assistant"
}

# Response
{
  "session_id": 123,
  "message": "Found 3 high-risk events...",
  "tool_results": [
    {
      "tool": "search_logs",
      "result": {...}
    }
  ]
}
```

### Available LLM Tools

The assistant can call these functions:
- `search_logs(query, time_range, event_type)` - Search login events/alerts
- `create_incident(title, severity, description)` - Create incidents
- `get_incident(incident_id)` - Get incident details
- `who_is(label)` - Look up face identities
- `show_camera(camera_id)` - Get camera detections

## 🔐 Security & Compliance

### RBAC Permissions
- **Admin**: Full access to all features
- **Security Officer**: View/manage incidents, alerts, configure rules
- **Employee**: Limited view access
- **Viewer**: Read-only access

### Data Privacy
- Per-organization data isolation
- Configurable face retention policies
- Consent tracking
- PII handling in embeddings (vectors stored, not raw faces)

### Audit Trail
All administrative actions are logged with:
- User, timestamp, IP address
- Action type (create/update/delete)
- Changed fields
- User agent

## 📊 Monitoring

### Celery Tasks
- `process_login_event` - Enrich and analyze logins
- `detect_anomalies_for_event` - Run anomaly detection
- `enroll_face_identity` - Process face enrollment
- `detect_faces_in_image` - Face detection & recognition
- `process_rtsp_stream` - Continuous camera monitoring
- `index_security_events_for_rag` - Build RAG knowledge base (nightly)
- `cleanup_old_face_detections` - Data retention (daily)
- `train_anomaly_detection_model` - ML model training (weekly)

### Health Checks
```bash
# Database
curl http://localhost:8000/admin/

# Redis
redis-cli ping

# Celery
celery -A safenest inspect active
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific app tests
pytest core/tests/
pytest security/tests/
pytest faces/tests/

# With coverage
pytest --cov=. --cov-report=html
```

## 📦 Production Deployment

### Environment Variables

Required for production:
```bash
DJANGO_SECRET_KEY=<strong-random-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
OPENAI_API_KEY=sk-...
POSTGRES_PASSWORD=<strong-password>
MINIO_SECRET_KEY=<strong-password>
```

### Security Checklist
- [ ] Change all default passwords
- [ ] Set strong SECRET_KEY
- [ ] Configure HTTPS/TLS
- [ ] Set up proper CORS origins
- [ ] Configure email backend
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Enable database backups
- [ ] Review anomaly rule thresholds
- [ ] Test face recognition accuracy
- [ ] Configure retention policies

## 📖 Architecture

```
┌─────────────┐
│   Browser   │
│  (WebRTC)   │
└──────┬──────┘
       │ HTTP/WebSocket
       ▼
┌─────────────────────────────────┐
│   Django (ASGI/Daphne)          │
│   - REST API (DRF)              │
│   - WebSocket (Channels)        │
│   - Admin Panel                 │
└────────┬────────────────────────┘
         │
    ┌────┴─────┬──────────┬────────┐
    ▼          ▼          ▼        ▼
┌────────┐ ┌────────┐ ┌──────┐ ┌───────┐
│ PostgreSQL│ │ Redis  │ │MinIO │ │Celery │
│ +pgvector│ │        │ │      │ │Workers│
└──────────┘ └────────┘ └──────┘ └───────┘
```

## 🤝 Contributing

1. Follow Django/Python best practices
2. Write tests for new features
3. Document API changes
4. Use Black for code formatting

## 📄 License

Proprietary - All Rights Reserved

## 🆘 Support

For issues and questions:
- Create GitHub issues
- Check logs: `docker-compose logs backend`
- Review Django logs in `logs/safenest.log`

## 🎯 MVP Scope (2-3 Weeks)

**Week 1**: Core + Security + Incidents
- ✅ Multi-tenant auth & RBAC
- ✅ Login event capture
- ✅ Anomaly rules & alerts
- ✅ Incident CRUD

**Week 2**: Faces + Real-time
- ✅ Face enrollment & recognition
- ✅ Camera integration
- ✅ WebSocket alerts
- ✅ Dashboard v1

**Week 3**: LLM + Polish
- ✅ Assistant bot with tools
- ✅ Recommendations & analysis
- ✅ Demo scenarios
- ✅ Documentation

**Stretch Goals**:
- RTSP live streaming
- Advanced ML anomaly models
- Mobile app
- Browser-based WebRTC capture

---

**Built with ❤️ for modern security operations**
