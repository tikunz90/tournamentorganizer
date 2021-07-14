web: gunicorn core.wsgi --log-file=- 
worker: celery -A TASKFILE worker -B --loglevel=info
