# 🚀 Render Deployment Quick Checklist

## Pre-Deployment

- [ ] **Push to GitHub**
  ```bash
  git add .
  git commit -m "Add Render deployment configuration"
  git push origin main
  ```

- [ ] **Get API Keys**
  - [ ] Google Gemini API Key from [Google AI Studio](https://makersuite.google.com/app/apikey)
  - [ ] OpenAI API Key (optional)

## Render Setup

- [ ] **Create Render Account** at [render.com](https://render.com)

- [ ] **Deploy with Blueprint**
  1. Dashboard → **New +** → **Blueprint**
  2. Connect GitHub repository
  3. Select SafeNest repository
  4. Wait for auto-detection of `render.yaml`
  5. Click **Apply**

## Environment Variables to Set

Navigate to: Dashboard → safenest-backend → Environment

### Required Variables
- [ ] `ALLOWED_HOSTS` = `your-app-name.onrender.com`
- [ ] `GEMINI_API_KEY` = `your-gemini-api-key`

### Recommended Variables
- [ ] `CORS_ALLOWED_ORIGINS` = `https://your-frontend-url.com`
- [ ] `OPENAI_API_KEY` = `your-openai-key` (optional)

### Optional (for file storage)
- [ ] `MINIO_ENDPOINT`
- [ ] `MINIO_ACCESS_KEY`
- [ ] `MINIO_SECRET_KEY`

## Post-Deployment

- [ ] **Enable pgvector Extension**
  ```bash
  # Connect to database from Render dashboard
  psql -h <HOST> -U safenest safenest
  CREATE EXTENSION IF NOT EXISTS vector;
  \q
  ```

- [ ] **Create Superuser**
  ```bash
  # In Render: safenest-backend → Shell
  python manage.py createsuperuser
  ```

- [ ] **Test Endpoints**
  - [ ] `https://your-app.onrender.com/api/health/`
  - [ ] `https://your-app.onrender.com/admin/`
  - [ ] `https://your-app.onrender.com/api/`

- [ ] **Update Frontend Environment**
  ```bash
  # In your frontend .env
  VITE_API_URL=https://your-app.onrender.com
  VITE_WS_URL=wss://your-app.onrender.com
  ```

## Verification

- [ ] All 5 services are **Live** (green status)
  - safenest-db
  - safenest-redis
  - safenest-backend
  - safenest-celery-worker
  - safenest-celery-beat

- [ ] No build errors in logs
- [ ] Database migrations completed
- [ ] Static files collected
- [ ] Health check returns 200 OK

## Troubleshooting

If deployment fails, check:
1. **Build logs** in Render dashboard
2. **Environment variables** are set correctly
3. **build.sh** has execute permissions
4. **Database connection** (DATABASE_URL auto-set)
5. **Redis connection** (REDIS_URL auto-set)

## Cost

- **Free Tier**: $0/month (all services free, web sleeps after 15min)
- **Starter Tier**: ~$38-45/month (no sleep, better performance)

## Support

📖 Full guide: See `RENDER_DEPLOYMENT_GUIDE.md`
🆘 Issues? Check service logs in Render dashboard

---

**Note**: Free tier services sleep after 15 minutes of inactivity. First request after sleep takes ~30 seconds to wake up. Upgrade to Starter plan for 24/7 availability.
