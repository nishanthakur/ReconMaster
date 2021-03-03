import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reconMaster.settings')

app = Celery('reconMaster')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()