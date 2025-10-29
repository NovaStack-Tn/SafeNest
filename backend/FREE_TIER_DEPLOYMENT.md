# 🆓 Render Free Tier Deployment Guide

This guide is specifically for deploying SafeNest on Render's **FREE plan** (no shell access).

## ⚠️ Free Tier Limitations

- **No Shell Access**: Can't run `python manage.py` commands manually
- **Service Sleeps**: After 15 minutes of inactivity (30s wake time)
- **Limited Resources**: 512MB RAM, 0.1 CPU
- **750 hours/month**: Shared across all free services

## ✅ Automated Solutions

### 1. Automatic Superuser Creation

The build script automatically creates a superuser using environment variables.

**Set in Render Dashboard → safenest-backend → Environment**:
```
DJANGO_SUPERUSER_PASSWORD=YourSecurePassword123!
```

**Default credentials**:
- Username: `admin`
- Email: `admin@safenest.com`
- Password: Whatever you set above

### 2. Automatic Migrations

Migrations run automatically during build:
```bash
python manage.py migrate
```

### 3. Automatic Static Files Collection

Static files are collected automatically:
```bash
python manage.py collectstatic --no-input
```

## 📝 Required Environment Variables

Set these in **Render Dashboard → safenest-backend → Environment**:

| Variable | Example | Required |
|----------|---------|----------|
| `ALLOWED_HOSTS` | `safenest-backend-fx9f.onrender.com` | ✅ Yes |
| `DJANGO_SUPERUSER_PASSWORD` | `YourPassword123!` | ✅ Yes |
| `GEMINI_API_KEY` | `AIza...` | ✅ Yes |
| `CORS_ALLOWED_ORIGINS` | `https://your-app.vercel.app` | ✅ Yes |

## 🚀 Quick Start

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Add Render deployment config with auto superuser"
git push origin main
```

### Step 2: Deploy on Render
1. Go to [Render Dashboard](https://dashboard.render.com)
2. **New +** → **Blueprint**
3. Connect your GitHub repo
4. Click **Apply**

### Step 3: Set Environment Variables
In Render Dashboard → `safenest-backend` → **Environment**:
```
ALLOWED_HOSTS=safenest-backend-fx9f.onrender.com
DJANGO_SUPERUSER_PASSWORD=YourSecurePassword123!
GEMINI_API_KEY=your-gemini-api-key
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

### Step 4: Wait for Build (~5-10 minutes)
Monitor the build logs. Look for:
```
✓ Static files collected
✓ Migrations applied
✓ Superuser "admin" created successfully
```

### Step 5: Enable pgvector

**Connect to database**:
```bash
# Get connection string from Render Dashboard → safenest-db
psql postgresql://safenest:password@host/safenest
```

**Run**:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

### Step 6: Test Your Deployment

**Health Check** (no auth):
```
https://safenest-backend-fx9f.onrender.com/api/health/
```

**Admin Panel**:
```
https://safenest-backend-fx9f.onrender.com/admin/
Username: admin
Password: Your DJANGO_SUPERUSER_PASSWORD
```

**Get JWT Token**:
```bash
curl -X POST https://safenest-backend-fx9f.onrender.com/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"YourPassword123!"}'
```

## 🔍 Troubleshooting Free Tier

### Build Fails: Permission Denied
**Error**: `./build.sh: Permission denied`

**Fix**:
```bash
git update-index --chmod=+x backend/build.sh
git commit -m "Make build.sh executable"
git push
```

### Service Keeps Sleeping
**Issue**: First request takes 30 seconds

**Solutions**:
- Use external uptime monitor (UptimeRobot, Cronitor - free)
- Upgrade to Starter plan ($7/month for 24/7)

### Out of Memory
**Error**: Service crashes with OOM

**Fix**:
- Disable Celery workers on free tier (or upgrade)
- Reduce concurrent processes

### Can't Access Shell
**Issue**: Need to run commands

**Solutions**:
- All commands run automatically via `build.sh`
- Create custom management commands
- Upgrade to paid plan for shell access

## 📊 Services on Free Tier

| Service | Status | Notes |
|---------|--------|-------|
| **safenest-db** (PostgreSQL) | ✅ Free | 1GB storage, never sleeps |
| **safenest-redis** (Redis) | ✅ Free | 25MB, never sleeps |
| **safenest-backend** (Web) | ✅ Free | Sleeps after 15min |
| **safenest-celery-worker** | ⚠️ Optional | Uses extra free hours |
| **safenest-celery-beat** | ⚠️ Optional | Uses extra free hours |

**Total Free Hours**: 750/month shared across all services

## 💡 Tips for Free Tier

1. **Disable unused services** to save free hours
2. **Use external cron** for scheduled tasks instead of Celery Beat
3. **Keep database backups** (Render doesn't backup free DBs)
4. **Monitor uptime** with free services
5. **Upgrade critical services** to paid ($7/month each)

## 🎯 When to Upgrade

Consider paid plan if:
- ❌ 30-second wake time is unacceptable
- ❌ Need shell access for debugging
- ❌ Running out of 750 free hours
- ❌ Need better performance (more RAM/CPU)
- ❌ Need automated backups

**Cost**: ~$7-14/month for web service + DB

## 📚 Additional Resources

- [Render Free Tier Docs](https://render.com/docs/free)
- [Django Production Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [Full Deployment Guide](../RENDER_DEPLOYMENT_GUIDE.md)

---

**🎉 Your SafeNest backend is now running on Render's free tier!**

No shell access needed - everything runs automatically during build.
