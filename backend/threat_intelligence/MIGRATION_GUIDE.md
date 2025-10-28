# Threat Intelligence Migration Guide

## Steps to Create and Apply Migrations

### 1. Activate Virtual Environment
First, activate your Python virtual environment:

```bash
# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies
Ensure all dependencies are installed:

```bash
pip install -r requirements.txt
```

### 3. Create Migrations
Generate migration files for the threat_intelligence app:

```bash
python manage.py makemigrations threat_intelligence
```

This will create migration files in `backend/threat_intelligence/migrations/` directory.

### 4. Review Migrations
Check the generated migration files to ensure they are correct:

```bash
python manage.py showmigrations threat_intelligence
```

### 5. Apply Migrations
Apply the migrations to your database:

```bash
python manage.py migrate threat_intelligence
```

### 6. Verify Database Tables
The following tables should be created:

- `threat_intelligence_threat` - Main threats table
- `threat_intelligence_alert` - Security alerts table
- `threat_intelligence_riskassessment` - Risk assessments table
- `threat_intelligence_threatindicator` - Threat indicators (IOCs) table
- `threat_intelligence_watchlist` - Watchlist entries table
- `threat_intelligence_threatfeed` - External threat feed configurations
- `threat_intelligence_threathuntingquery` - Saved threat hunting queries

Plus several many-to-many relationship tables.

### 7. Create Superuser (if not already done)
```bash
python manage.py createsuperuser
```

### 8. Test the Installation
Start the development server:

```bash
python manage.py runserver
```

Then access:
- Admin: http://localhost:8000/admin/
- API: http://localhost:8000/api/threat-intelligence/

## API Endpoints

### CRUD Endpoints
- `/api/threat-intelligence/threats/` - Threat management
- `/api/threat-intelligence/alerts/` - Alert management
- `/api/threat-intelligence/risk-assessments/` - Risk assessments
- `/api/threat-intelligence/indicators/` - Threat indicators
- `/api/threat-intelligence/watchlist/` - Watchlist management
- `/api/threat-intelligence/feeds/` - Threat feeds
- `/api/threat-intelligence/hunting-queries/` - Threat hunting queries

### AI Service Endpoints
- `/api/threat-intelligence/ai/anomaly-detection/detect_user_anomalies/`
- `/api/threat-intelligence/ai/anomaly-detection/detect_login_anomalies/`
- `/api/threat-intelligence/ai/anomaly-detection/detect_traffic_anomalies/`
- `/api/threat-intelligence/ai/threat-scoring/calculate_risk/`
- `/api/threat-intelligence/ai/threat-scoring/update_dynamic_levels/`
- `/api/threat-intelligence/ai/predictive-analytics/forecast_threats/`
- `/api/threat-intelligence/ai/predictive-analytics/emerging_patterns/`
- `/api/threat-intelligence/ai/predictive-analytics/predict_attack_vectors/`
- `/api/threat-intelligence/ai/alert-aggregation/deduplicate/`
- `/api/threat-intelligence/ai/alert-aggregation/correlate/`
- `/api/threat-intelligence/ai/alert-aggregation/smart_filter/`
- `/api/threat-intelligence/ai/threat-hunting/query/`
- `/api/threat-intelligence/ai/threat-hunting/suggest_hypotheses/`
- `/api/threat-intelligence/ai/threat-hunting/generate_report/`

## Celery Tasks Setup

### 1. Start Redis (if not running)
```bash
redis-server
```

### 2. Start Celery Worker
```bash
celery -A safenest worker -l info
```

### 3. Start Celery Beat (for scheduled tasks)
```bash
celery -A safenest beat -l info
```

## Testing

Run the test suite:
```bash
pytest backend/threat_intelligence/tests/
```

## Troubleshooting

### Migration Errors
If you encounter migration errors:

```bash
# Reset migrations (CAUTION: This will delete data)
python manage.py migrate threat_intelligence zero
python manage.py makemigrations threat_intelligence
python manage.py migrate threat_intelligence
```

### Import Errors
If you see import errors, ensure:
1. Virtual environment is activated
2. All dependencies are installed
3. PYTHONPATH includes the backend directory

### Database Connection Errors
Check your `.env` file has correct database settings:
```
POSTGRES_DB=safenest
POSTGRES_USER=safenest
POSTGRES_PASSWORD=safenest
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

## Next Steps

1. Configure Celery Beat schedule in `safenest/celery.py`
2. Set up external threat feed integrations
3. Configure alert notification channels
4. Customize threat scoring weights
5. Train ML models with historical data
