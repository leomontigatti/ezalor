import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ezalor.settings")

app = Celery("ezalor")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.beat_schedule = {
    # Executes every two hours.
    "fetching_today_articles": {
        "name": "Fetch today articles",
        "task": "scraper.tasks.fetch_new_articles_task",
        "schedule": crontab(hour="2,5,8,11,14,17,20,23", minute=0),
    },
    # Executes every three hours.
    "auto_creating_posts": {
        "name": "Auto create posts",
        "task": "scraper.tasks.auto_create_posts_task",
        "schedule": crontab(hour="2,5,8,11,14,17,20,23", minute=30),
    },
}

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
