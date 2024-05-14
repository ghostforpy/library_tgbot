import os

from kombu import Queue

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("smartup")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.task_default_queue = 'default'
app.conf.task_queues = (
    Queue('default'),
    Queue('msg_tasks', routing_key='msg.#'),
)

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
