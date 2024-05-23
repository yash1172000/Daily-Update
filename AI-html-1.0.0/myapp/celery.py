from celery import Celery
from celery.schedules import crontab
from django.conf import settings

app = Celery('myapp')
app.config_from_object('django.conf:settings')

# Schedule the management command to run every day at midnight
app.conf.beat_schedule = {
    'cleanup-workspace': {
        'task': 'myapp.tasks.cleanup_workspace',
        'schedule': crontab(minute=0, hour=0),  # Run at midnight every day
    },
}

@app.task
def cleanup_workspace():
    from django.core.management import call_command
    call_command('cleanup_workspace')
