# SafeNest Backend - Render Deployment Guide

This guide will help you deploy the SafeNest Django backend to Render with PostgreSQL, Redis, Celery workers, and all AI features.

## 📋 Prerequisites

1. **Render Account**: Sign up at [render.com](https://render.com)
2. **GitHub Repository**: Push your code to GitHub
3. **API Keys**:
   - Google Gemini API Key (Get from [Google AI Studio](https://makersuite.google.com/app/apikey))
   - OpenAI API Key (Optional, for legacy features)

## 🚀 Deployment Options

### Option 1: Deploy with render.yaml (Recommended)

This method uses Infrastructure as Code to deploy everything at once.

#### Steps:

1. **Push Code to GitHub**
   ```bash
   git add .
   git commit -m "Add Render deployment configuration"
   git push origin main
   ```

2. **Connect to Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click **"New +"** → **"Blueprint"**
   - Connect your GitHub repository
   - Select the repository containing SafeNest
   - Render will automatically detect `render.yaml`

3. **Configure Environment Variables**
   
   Render will create these services:
   - `safenest-db` (PostgreSQL 16 with pgvector)
   - `safenest-redis` (Redis for Celery & Channels)
   - `safenest-backend` (Django web service)
   - `safenest-celery-worker` (Background tasks)
   - `safenest-celery-beat` (Scheduled tasks)

   **Set these environment variables in the Render dashboard:**
   
   | Variable | Value | Notes |
   |----------|-------|-------|
   | `ALLOWED_HOSTS` | `your-app-name.onrender.com` | Replace with your actual Render URL |
   | `CORS_ALLOWED_ORIGINS` | `https://your-frontend.vercel.app` | Your frontend URL(s) |
   | `GEMINI_API_KEY` | `your-gemini-api-key` | **REQUIRED** for AI features |
   | `OPENAI_API_KEY` | `your-openai-api-key` | Optional |
   | `MINIO_ENDPOINT` | S3 endpoint | Optional, for file storage |
   | `MINIO_ACCESS_KEY` | S3 access key | Optional |
   | `MINIO_SECRET_KEY` | S3 secret key | Optional |

4. **Deploy**
   - Click **"Apply"**
   - Render will create all services and deploy automatically
   - Wait 5-10 minutes for the build to complete

5. **Enable pgvector Extension**
   
   After deployment, connect to your database:
   ```bash
   # In Render Dashboard → safenest-db → Connect → External Connection
   psql -h <HOST> -U safenest safenest
   ```
   
   Run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

---

### Option 2: Manual Deployment

If you prefer to create services manually:

#### 1. Create PostgreSQL Database

- Go to Render Dashboard → **New +** → **PostgreSQL**
- Name: `safenest-db`
- Database: `safenest`
- User: `safenest`
- Plan: Free or Starter
- PostgreSQL Version: **16**
- Create Database

After creation:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

#### 2. Create Redis Instance

- Render Dashboard → **New +** → **Redis**
- Name: `safenest-redis`
- Plan: Free
- Create Redis

#### 3. Create Web Service

- Render Dashboard → **New +** → **Web Service**
- Connect your GitHub repository
- Configuration:
  - **Name**: `safenest-backend`
  - **Root Directory**: `backend`
  - **Environment**: `Python 3`
  - **Build Command**: `./build.sh`
  - **Start Command**: `gunicorn safenest.wsgi:application`
  - **Plan**: Free or Starter

#### 4. Configure Environment Variables

In the web service environment variables:

```bash
# Auto-configured by Render (don't set manually)
DATABASE_URL=<auto-filled>
REDIS_URL=<auto-filled>

# Required - Set these manually
DJANGO_SECRET_KEY=<generate-random-key>
DEBUG=False
ALLOWED_HOSTS=safenest-backend.onrender.com
CORS_ALLOWED_ORIGINS=https://your-frontend.com
GEMINI_API_KEY=your-gemini-api-key

# Optional
OPENAI_API_KEY=your-openai-key
MINIO_ENDPOINT=your-s3-endpoint
MINIO_ACCESS_KEY=your-s3-key
MINIO_SECRET_KEY=your-s3-secret
```

#### 5. Create Celery Worker

- Render Dashboard → **New +** → **Background Worker**
- Connect same repository
- Configuration:
  - **Name**: `safenest-celery-worker`
  - **Root Directory**: `backend`
  - **Build Command**: `pip install -r requirements.txt`
  - **Start Command**: `celery -A safenest worker --loglevel=info`
  
Environment Variables:
```bash
DATABASE_URL=<same-as-web-service>
CELERY_BROKER_URL=<redis-url>
GEMINI_API_KEY=<same-as-web-service>
```

#### 6. Create Celery Beat (Optional)

For scheduled tasks:
- Render Dashboard → **New +** → **Background Worker**
- Name: `safenest-celery-beat`
- Start Command: `celery -A safenest beat --loglevel=info`
- Same environment variables as worker

---

## 🔧 Post-Deployment Setup

### 1. Create Superuser

Superuser is created automatically during deployment! Just set the password in Render Dashboard:

**Go to**: Dashboard → `safenest-backend` → Environment

**Set this variable**:
- `DJANGO_SUPERUSER_PASSWORD` = `your-secure-password`

The superuser will be created with:
- **Username**: `admin`
- **Email**: `admin@safenest.com`
- **Password**: Whatever you set in `DJANGO_SUPERUSER_PASSWORD`

> **Note**: On free plan, shell access is disabled. The build script automatically creates the superuser using environment variables.

### 2. Verify Deployment

Test these endpoints:
- `https://your-app.onrender.com/admin/` - Django Admin
- `https://your-app.onrender.com/api/` - API Root

### 3. Configure Frontend

Update your frontend `.env` file:
```bash
VITE_API_URL=https://your-app.onrender.com
VITE_WS_URL=wss://your-app.onrender.com
```

---

## 📊 Service Architecture

```
┌─────────────────────┐
│  safenest-backend   │  ← Web Service (Django + Gunicorn)
│  Port: 10000        │
└──────────┬──────────┘
           │
    ┌──────┴──────┐
    │             │
┌───▼──────┐  ┌──▼───────────┐
│ safenest │  │ safenest-    │
│ -db      │  │ redis        │
│ (PG 16)  │  │              │
└──────────┘  └──┬───────────┘
                 │
        ┌────────┴────────┐
        │                 │
   ┌────▼─────┐    ┌─────▼─────┐
   │ celery-  │    │ celery-   │
   │ worker   │    │ beat      │
   └──────────┘    └───────────┘
```

---

## 🔍 Troubleshooting

### Build Fails

**Error**: `ModuleNotFoundError: No module named 'dj_database_url'`
- **Solution**: Ensure `requirements.txt` includes `dj-database-url==2.1.0`

**Error**: `Permission denied: ./build.sh`
- **Solution**: Make build.sh executable:
  ```bash
  chmod +x backend/build.sh
  git add backend/build.sh
  git commit -m "Make build.sh executable"
  git push
  ```

### Database Connection Error

**Error**: `django.db.utils.OperationalError: FATAL: password authentication failed`
- **Solution**: Verify `DATABASE_URL` is set correctly (auto-filled by Render)

### pgvector Extension Missing

**Error**: `django.db.utils.ProgrammingError: type "vector" does not exist`
- **Solution**: Connect to database and run:
  ```sql
  CREATE EXTENSION IF NOT EXISTS vector;
  ```

### Redis Connection Error

**Error**: `Error 111 connecting to localhost:6379. Connection refused.`
- **Solution**: Set `REDIS_URL` environment variable (auto-filled by Render)

### Static Files Not Loading

**Error**: 404 on static files
- **Solution**: Verify WhiteNoise is in `MIDDLEWARE` and run:
  ```bash
  python manage.py collectstatic --no-input
  ```

### Celery Worker Not Processing Tasks

- **Check**: Worker logs in Render Dashboard
- **Verify**: `CELERY_BROKER_URL` is set correctly
- **Ensure**: `DEBUG=False` (eager mode disabled in production)

---

## 💰 Cost Estimate

### Free Tier (750 hours/month per service)
- PostgreSQL: **Free** (1GB storage, 97 connections)
- Redis: **Free** (25MB, no eviction)
- Web Service: **Free** (512MB RAM, sleeps after 15min inactivity)
- 2 Workers: **Free** (512MB RAM each)

**Total**: **$0/month** (with free tier)

### Paid Plan (For production)
- PostgreSQL Starter: **$7/month** (256MB RAM, no sleep)
- Redis: **$10/month** (100MB)
- Web Service Starter: **$7/month** (512MB RAM, no sleep)
- Workers: **$7/month each**

**Total**: ~**$38-45/month** (with basic paid tiers)

---

## 🎯 Production Checklist

- [ ] Set strong `DJANGO_SECRET_KEY`
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Set `CORS_ALLOWED_ORIGINS` with frontend URL
- [ ] Add `GEMINI_API_KEY` for AI features
- [ ] Enable pgvector extension
- [ ] Create superuser account
- [ ] Test all API endpoints
- [ ] Configure custom domain (optional)
- [ ] Set up monitoring/alerts
- [ ] Configure backups (database)

---

## 📚 Additional Resources

- [Render Django Deployment Guide](https://render.com/docs/deploy-django)
- [Django Production Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [Celery Best Practices](https://docs.celeryproject.org/en/stable/userguide/tasks.html#best-practices)
- [pgvector Documentation](https://github.com/pgvector/pgvector)

---

## 🆘 Support

If you encounter issues:
1. Check Render service logs in the dashboard
2. Review this guide's troubleshooting section
3. Check Django logs: `https://your-app.onrender.com/admin/`
4. Verify environment variables are set correctly

---

## 🔄 Updating Your Deployment

To deploy updates:
```bash
git add .
git commit -m "Your update message"
git push origin main
```

Render will automatically rebuild and redeploy.

For zero-downtime deployments, consider:
- Using Render's paid plans
- Implementing database migrations carefully
- Using feature flags for major changes

---

**🎉 Congratulations! Your SafeNest backend is now deployed on Render!**
