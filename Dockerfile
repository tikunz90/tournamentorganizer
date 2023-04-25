FROM python:3.6

ENV PYTHONUNBUFFERED 1

COPY manage.py gunicorn-cfg.py requirements.txt .env ./
COPY beachhandball_app beachhandball_app
COPY authentication authentication
COPY core core

RUN pip install -r requirements.txt

RUN python manage.py makemigrations
RUN python manage.py migrate

EXPOSE 8080
CMD ["gunicorn", "--config", "gunicorn-cfg.py", "core.wsgi"]
