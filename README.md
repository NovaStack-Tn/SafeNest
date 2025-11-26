# 🏛️ **SafeNest – AI-Powered Security & Access Control Platform**

SafeNest is an **enterprise-grade, AI-driven security platform** combining identity management, physical access control, surveillance, threat intelligence, incident response, and anomaly detection into one unified system.

Built with **Django + React + PostgreSQL**, it integrates **InsightFace**, **Isolation Forest**, and **LLMs (GPT-4/Gemini)** to deliver intelligent, automated, real-time security operations.

---

# 🚀 **Key Features**

### 🔐 **Identity & Access Management**

* Multi-tenant architecture
* Role-based access control (Admin, Security Officer, Employee, Viewer)
* Custom user model + team management
* Full audit log of all actions
* JWT authentication

### 🏢 **Access Control**

* Access points (doors, gates, zones)
* Time-based access schedules
* Permissions & credential management
* Real-time access logging
* **AI anomaly detection**: unusual location, unusual time, badge sharing, rapid access
* Lockdown mode & tailgating detection

### 👁️ **Face Recognition & Surveillance**

* InsightFace (ArcFace 512D embeddings)
* Multi-angle enrollment (3 images)
* Real-time face detection & recognition
* RTSP camera support with Celery streaming
* Age & gender estimation
* Unknown-person alerts
* Detection history & identity matching

### 🧠 **AI Assistants (LLM)**

* 3 specialized bots:

  * **Assistant** – general help + tools
  * **Recommendation Bot** – policies & best practices
  * **Analysis Bot** – security reports
* Function-calling tools:

  * search_logs, create_incident, show_camera, who_is, get_incident
* Embeddings (pgvector) for memory & context

### 🚨 **Incident Management**

* Case lifecycle: Open → Investigating → Contained → Resolved → Closed
* Assignment workflow
* Evidence uploads (SHA-256 integrity)
* Timeline tracking
* Severity levels + audit trail

### 🛬 **Visitor & Asset Management**

* Visitor pre-registration
* **AI-powered form extraction** (Gemini)
* AI suggestions: access level, risk score, visit duration
* QR-pass generation
* Asset inventory + assignment
* Movement logs + background check workflow
* NDA & watchlist support

### 🔍 **Threat Intelligence**

* Threat catalog with severity, indicators & analysis
* AI-powered:

  * threat severity
  * IOC extraction (IPs, domains, emails, hashes)
  * risk assessments
* Alerts & watchlist management
* Multi-step workflow UI

### 🔒 **Security Monitoring**

* Login event tracking
* **ML anomaly detection (Isolation Forest)**
* Impossible travel detection
* New-device fingerprinting
* Geo-enrichment
* WebSocket real-time alerts

### 📊 **Unified Dashboard**

* KPIs for:

  * Alerts
  * Incidents
  * Access logs
  * Face detections
  * Login anomalies
* Time-range filtering
* Recent activity feed

---

# 🧰 **Tech Stack**

### **Backend**

* Django 5 + Django REST Framework
* Django Channels (WebSockets)
* PostgreSQL + pgvector
* Redis + Celery workers
* MinIO (S3 storage)
* Gunicorn + Daphne
* Docker & Docker Compose

### **Frontend**

* React 18 + TypeScript
* Vite
* TailwindCSS
* Zustand (state)
* React Query (data fetching)
* React Router

### **AI / ML**

* InsightFace (face recognition)
* scikit-learn (Isolation Forest anomaly detection)
* Gemini / GPT-4 LLM integration
* OpenCV (image processing)

---

# 📦 **Installation (Docker Compose)**

```bash
cd SafeNest/backend
cp .env.example .env
# Add your API keys (OPENAI_API_KEY or GEMINI_API_KEY)

docker-compose up -d
```

### Services Started

* Django API → [http://localhost:8000](http://localhost:8000)
* PostgreSQL (5432)
* Redis (6379)
* MinIO (9000/9001)
* Celery worker + beat

### Create Superuser

```bash
docker-compose exec backend python manage.py createsuperuser
```

---

# 🔧 **Local Development**

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Database (pgvector)

```bash
docker run -d --name safenest-pg \
  -e POSTGRES_DB=safenest \
  -e POSTGRES_USER=safenest \
  -e POSTGRES_PASSWORD=safenest \
  -p 5432:5432 \
  pgvector/pgvector:pg16
```

### Start Services

```bash
python manage.py runserver          # Backend
celery -A safenest worker -l info   # Worker
celery -A safenest beat -l info     # Scheduler
redis-server                        # Optional local Redis
```

---

# 📚 **API Overview**

### Authentication

`POST /api/auth/token/` – JWT login

### Core

* `/api/organizations/`
* `/api/users/`
* `/api/audit-logs/`

### Access Control

* `/api/access-control/access-points/`
* `/api/access-control/access-logs/`
* `/api/access-control/schedules/`

### Face Recognition

* `/api/faces/cameras/`
* `/api/faces/identities/`
* `/api/faces/detections/detect/`

### Security

* `/api/security/login-events/`
* `/api/security/anomaly-rules/`
* `/api/security/alerts/`
* `WS /ws/alerts/`

### Incidents

* `/api/incidents/incidents/`
* `/api/incidents/{id}/assign/`
* `/api/incidents/{id}/add_comment/`

### Threat Intelligence

* `/api/threat-intelligence/threats/`
* `/api/threat-intelligence/threats/{id}/ai_analyze/`

### LLM Assistants

* `/api/llm/api/chat/`
* `/api/llm/sessions/`

---

# 🤖 **AI Features**

### InsightFace (Face Recognition)

* Multi-angle enrollment
* 512D vectors
* Cosine similarity matching
* Real-time camera processing

### ML Anomaly Detection

* Time anomalies
* Location anomalies
* Device anomalies
* Behavioral ML detection (Isolation Forest)

### LLM Assistant Tools

* Search logs
* Create incidents
* Show camera detections
* Identify people
* Generate reports

---

# 📊 **Celery Scheduled Tasks**

* Login enrichment
* Anomaly detection
* Face enrollment processing
* RTSP camera monitoring
* RAG indexing
* Cleanup (daily)
* ML retraining (weekly)

---

# 🔐 **Security & Compliance**

* Multi-tenant data isolation
* PII-safe embeddings (no raw face images stored)
* SHA-256 evidence hashing
* Full audit logs
* RBAC enforcement
* Configurable data retention

---

# 🏗️ **Architecture Diagram**

```
Browser (WebRTC/HTTP/WS)
        │
        ▼
Django ASGI (DRF + Channels)
        │
 ┌──────┼───────────────┬───────────┐
 ▼      ▼               ▼           ▼
PostgreSQL       Redis        MinIO      Celery Workers
(pgvector)
```

---

# 🧪 **Testing**

```bash
pytest
pytest --cov=. --cov-report=html
```

---

# 📦 **Production Notes**

* Use HTTPS
* Rotate secret keys
* Restrict CORS
* Enable backups
* Configure monitoring (Grafana/Prometheus)
* Tune anomaly rule thresholds

---

# 🤝 **Contributing**

* Follow Django/React best practices
* Write tests for new features
* Format using Black

---

# 📄 **License**

Proprietary – All Rights Reserved

---

# 🆘 **Support**

* Open a GitHub Issue
* Check backend logs:

```bash
docker-compose logs backend
```

---
Built with ❤️ for modern security operations
