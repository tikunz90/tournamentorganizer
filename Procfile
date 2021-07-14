web: gunicorn core.wsgi --log-file=- 
worker: celery -A core.celery worker -B --loglevel=info
