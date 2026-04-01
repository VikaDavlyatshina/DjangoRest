import os

from celery import Celery
from celery.schedules import crontab

# Устанавливаем настройки Django по умолчанию
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.

# Загружаем настройки из Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

