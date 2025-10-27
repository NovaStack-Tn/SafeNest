"""
Celery configuration for SafeNest project.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safenest.settings')

app = Celery('safenest')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Periodic tasks
app.conf.beat_schedule = {
    'index-security-events-nightly': {
        'task': 'llm.tasks.index_security_events_for_rag',
        'schedule': crontab(hour=2, minute=0),  # 2 AM daily
    },
    'cleanup-old-frames': {
        'task': 'faces.tasks.cleanup_old_face_detections',
        'schedule': crontab(hour=3, minute=0),  # 3 AM daily
    },
    'train-anomaly-model': {
        'task': 'security.tasks.train_anomaly_detection_model',
        'schedule': crontab(hour=4, minute=0, day_of_week=1),  # Monday 4 AM
    },
    'generate-weekly-analysis': {
        'task': 'llm.tasks.generate_weekly_security_analysis',
        'schedule': crontab(hour=8, minute=0, day_of_week=1),  # Monday 8 AM
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
