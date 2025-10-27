# SafeNest - Local Windows Setup Guide

## 🪟 Running SafeNest Locally on Windows

**Good news!** SafeNest can run **100% locally on Windows** without Docker or WSL. However, you have 3 options depending on your preference.

---

## 📊 Option Comparison

| Feature | Local Windows | Docker | WSL2 |
|---------|--------------|--------|------|
| Setup Complexity | Medium | Easy | Medium |
| Performance | ⚡ Best | Good | Very Good |
| Development Experience | ⭐ Best | Good | Very Good |
| Production-like | ❌ | ✅ | ✅ |
| Debugging | ⭐ Easiest | Medium | Easy |
| Resource Usage | Low | Higher | Medium |

---

## ✅ Option 1: Pure Local Windows Setup (Recommended for Development)

### Step 1: Install Dependencies

#### 1.1 Python 3.11+
```powershell
# Download from python.org or use winget
winget install Python.Python.3.11
python --version  # Verify
```

#### 1.2 PostgreSQL 16 with pgvector
```powershell
# Download PostgreSQL 16 installer from:
# https://www.enterprisedb.com/downloads/postgres-postgresql-downloads

# After installation, install pgvector extension:
# Option A: Download from GitHub releases
# https://github.com/pgvector/pgvector/releases
# Extract to C:\Program Files\PostgreSQL\16\lib and share\extension

# Option B: Use pre-built Windows binary
# Download pgvector Windows DLL and place in PostgreSQL directories
```

**Quick pgvector Setup:**
```powershell
# Download pgvector for Windows
Invoke-WebRequest -Uri "https://github.com/pgvector/pgvector/releases/download/v0.5.1/pgvector-v0.5.1-windows-x64-postgres16.zip" -OutFile pgvector.zip
Expand-Archive pgvector.zip -DestinationPath pgvector
# Copy files to PostgreSQL directories (adjust path as needed)
Copy-Item pgvector\lib\* "C:\Program Files\PostgreSQL\16\lib\"
Copy-Item pgvector\share\* "C:\Program Files\PostgreSQL\16\share\extension\"
```

#### 1.3 Redis for Windows
```powershell
# Option A: Use Memurai (Redis-compatible for Windows)
winget install Memurai.Memurai-Developer

# Option B: Use WSL2 Redis (lightweight)
wsl --install
# Then in WSL: sudo apt install redis-server

# Option C: Use Redis Docker container only
docker run -d -p 6379:6379 redis:7-alpine
```

#### 1.4 MinIO (Optional for local dev)
```powershell
# Option A: Use MinIO Windows binary
# Download from https://min.io/download
# Or run with Docker:
docker run -d -p 9000:9000 -p 9001:9001 minio/minio server /data --console-address ":9001"

# Option B: Skip MinIO for development, use Django FileSystemStorage
# Set in .env: USE_MINIO=False
```

---

### Step 2: Setup SafeNest Backend

```powershell
# Navigate to backend
cd C:\Users\nihed\Desktop\SafeNest\backend

# Create virtual environment
python -m venv venv

# Activate venv
.\venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

**⚠️ If you encounter compilation errors with InsightFace:**
```powershell
# Install Visual C++ Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
# OR install via winget:
winget install Microsoft.VisualStudio.2022.BuildTools

# Select "Desktop development with C++"
```

---

### Step 3: Configure Database

```powershell
# Start PostgreSQL service (if not auto-started)
# Windows Services: Press Win+R, type "services.msc"
# Find "postgresql-x64-16" and start it

# Create database
# Open Command Prompt as Admin or use pgAdmin
psql -U postgres
```

```sql
-- In psql:
CREATE DATABASE safenest;
CREATE USER safenest WITH PASSWORD 'safenest';
ALTER USER safenest CREATEDB;
GRANT ALL PRIVILEGES ON DATABASE safenest TO safenest;

-- Connect to safenest database
\c safenest

-- Enable pgvector extension
CREATE EXTENSION vector;

-- Verify
\dx  -- Should show vector extension
\q
```

---

### Step 4: Configure Environment

```powershell
# Your .env is already created, update these values:
```

Edit `backend\.env`:
```bash
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-change-this
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Windows local PostgreSQL)
POSTGRES_DB=safenest
POSTGRES_USER=safenest
POSTGRES_PASSWORD=safenest
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis (Memurai or WSL)
REDIS_HOST=localhost
REDIS_PORT=6379

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0

# MinIO (if using Docker) or set USE_MINIO=False
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
USE_MINIO=False  # For local dev without MinIO

# OpenAI (REQUIRED for LLM features)
OPENAI_API_KEY=sk-your-actual-openai-key-here
OPENAI_MODEL=gpt-4-turbo-preview

# InsightFace
INSIGHTFACE_MODEL_NAME=buffalo_l
INSIGHTFACE_SIMILARITY_THRESHOLD=0.4
```

---

### Step 5: Run Migrations

```powershell
# Activate venv if not already
.\venv\Scripts\Activate.ps1

# Run migrations
python manage.py migrate

# Initialize with sample data
python init_db.py

# Create superuser (optional, init_db.py creates admin/admin123)
python manage.py createsuperuser
```

---

### Step 6: Download InsightFace Models

```powershell
# Models will auto-download on first use, or manually:
python
```

```python
import insightface
from insightface.app import FaceAnalysis

app = FaceAnalysis(name='buffalo_l')
app.prepare(ctx_id=-1)  # Use CPU (-1) or GPU (0)
print("Models downloaded successfully!")
exit()
```

Models will be in: `C:\Users\<YourName>\.insightface\models\buffalo_l\`

---

### Step 7: Start Services (4 Terminals)

#### Terminal 1: Django Server
```powershell
cd C:\Users\nihed\Desktop\SafeNest\backend
.\venv\Scripts\Activate.ps1
python manage.py runserver
```
Access: http://localhost:8000/api/

#### Terminal 2: Celery Worker
```powershell
cd C:\Users\nihed\Desktop\SafeNest\backend
.\venv\Scripts\Activate.ps1

# Windows-specific: Use eventlet or gevent pool
pip install eventlet
celery -A safenest worker -l info -P eventlet
```

#### Terminal 3: Celery Beat (Scheduled Tasks)
```powershell
cd C:\Users\nihed\Desktop\SafeNest\backend
.\venv\Scripts\Activate.ps1
celery -A safenest beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

#### Terminal 4: Django Channels (WebSocket)
```powershell
cd C:\Users\nihed\Desktop\SafeNest\backend
.\venv\Scripts\Activate.ps1
daphne -b 0.0.0.0 -p 8000 safenest.asgi:application
```

**Note**: You only need Terminal 1 for basic testing. Terminals 2-4 are for AI features and real-time alerts.

---

## 🐳 Option 2: Docker (Easiest, Production-like)

**Perfect if you want everything to "just work":**

```powershell
# Prerequisites: Docker Desktop for Windows
winget install Docker.DockerDesktop

# Start Docker Desktop, then:
cd C:\Users\nihed\Desktop\SafeNest

# Copy and edit .env (you already did this)
# Make sure OPENAI_API_KEY is set

# Start everything
docker-compose up -d

# Initialize database
docker-compose exec backend python manage.py migrate
docker-compose exec backend python init_db.py

# View logs
docker-compose logs -f backend

# Access
# API: http://localhost:8000/api/
# Admin: http://localhost:8000/admin/ (admin/admin123)
```

**Pros**:
- ✅ Zero dependency installation
- ✅ Production-like environment
- ✅ Easy to reset/restart
- ✅ Includes PostgreSQL, Redis, MinIO automatically

**Cons**:
- ❌ Higher resource usage
- ❌ Slower file watching for development
- ❌ Slightly harder to debug

---

## 🐧 Option 3: WSL2 (Best of Both Worlds)

**Ubuntu on Windows with native Linux performance:**

```powershell
# Install WSL2
wsl --install
# Restart computer

# Open WSL2
wsl

# In WSL2 Ubuntu:
cd /mnt/c/Users/nihed/Desktop/SafeNest/backend

# Install Python, PostgreSQL, Redis
sudo apt update
sudo apt install python3.11 python3.11-venv postgresql-16 redis-server

# Follow Linux setup from README.md
# Everything runs natively with Linux performance
```

**Pros**:
- ✅ Native Linux performance
- ✅ Easier dependency installation
- ✅ Production-like environment
- ✅ Can still use Windows editors

**Cons**:
- ❌ Requires WSL2 setup
- ❌ File system bridging can be slow

---

## 🎯 Recommendation

### For Development (Day-to-day coding):
**✅ Option 1: Pure Local Windows**
- Best debugging experience
- Fast file changes
- Direct access to Python debugger
- No overhead

### For Testing (Production-like):
**✅ Option 2: Docker Compose**
- Fastest setup
- Matches production
- Easy reset

### For Performance + Development:
**✅ Option 3: WSL2**
- Near-native Linux speed
- Best of both worlds
- Easier package management

---

## 🔧 Quick PowerShell Setup Script

I'll create an automated setup script for you:

```powershell
# Save as setup-local.ps1
# Run with: .\setup-local.ps1
```

---

## ⚠️ Common Windows Issues

### 1. Celery on Windows
Celery doesn't fully support Windows. Solutions:
- ✅ Use `-P eventlet` pool: `celery -A safenest worker -P eventlet`
- ✅ Use `-P solo` for single process: `celery -A safenest worker -P solo`
- ✅ Run Celery in Docker/WSL only
- ✅ Use Windows Subsystem for Linux

### 2. PostgreSQL Permission Issues
```powershell
# Run Command Prompt as Administrator
# Or adjust pg_hba.conf to allow password auth
```

### 3. Redis on Windows
```powershell
# Memurai is the easiest: https://www.memurai.com/
# Or use Docker for Redis only:
docker run -d -p 6379:6379 redis:7-alpine
```

### 4. InsightFace Build Errors
```powershell
# Install Visual C++ Build Tools
winget install Microsoft.VisualStudio.2022.BuildTools
# Select "Desktop development with C++"
```

### 5. Long Path Issues
```powershell
# Enable long paths in Windows
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1
```

---

## 🚀 Hybrid Approach (Recommended)

**Best setup for Windows developers:**

1. **Run Django + development locally** (fast iteration)
2. **Run services in Docker** (PostgreSQL, Redis, MinIO)
3. **Optional: Celery in WSL** (if needed)

```powershell
# Start only services with Docker
docker run -d --name safenest-pg -p 5432:5432 -e POSTGRES_PASSWORD=safenest pgvector/pgvector:pg16
docker run -d --name safenest-redis -p 6379:6379 redis:7-alpine
docker run -d --name safenest-minio -p 9000:9000 -p 9001:9001 minio/minio server /data --console-address ":9001"

# Run Django locally
cd backend
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

This gives you:
- ✅ Fast Django development
- ✅ Easy database/Redis management
- ✅ No complex Windows service configuration
- ✅ Best of both worlds

---

## 📝 Summary

**Answer to your question:**
- ✅ **YES, SafeNest runs perfectly on local Windows** without Docker/WSL
- ✅ Docker is **optional** but makes setup easier
- ✅ WSL2 is **optional** but gives better Celery support
- ✅ **Hybrid approach** (Docker for services, local for Django) is most practical

Choose based on:
- **Quick test?** → Docker
- **Heavy development?** → Local Windows + Docker services
- **Need Celery?** → WSL2 or Docker
- **Just API/CRUD?** → Pure local Windows works perfectly

**My recommendation for you:** Start with local Windows + Docker services (hybrid approach) 🎯
