import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')
#app.conf.update(BROKER_URL=os.environ['REDIS_URL'],
#                CELERY_RESULT_BACKEND=os.environ['REDIS_URL'])

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)



@app.task
def debug_task(message):
    print('DEBUG: ' + message)

debug_task.delay('CELERY is RUNNING')