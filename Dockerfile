FROM python:3.6

ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    ssh \
    autossh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY id_rsa /root/.ssh/id_rsa
RUN chmod 600 /root/.ssh/id_rsa

RUN eval $(ssh-agent -s) && ssh-add /root/.ssh/id_rsa


COPY manage.py gunicorn-cfg.py requirements.txt .env ./
COPY beachhandball_app beachhandball_app
COPY authentication authentication
COPY core core

RUN pip install -r requirements.txt

#RUN python manage.py makemigrations
#RUN python manage.py migrate
#RUN python manage.py collectstatic

EXPOSE 8080
#CMD ["gunicorn", "--config", "gunicorn-cfg.py", "core.wsgi"]

CMD autossh -M 0 -N -o StrictHostKeyChecking=no -L 127.0.0.1:3307:127.0.0.1:3306 root@38.242.148.70 & \
    #python manage.py makemigrations && \
    #python manage.py migrate && \
    python manage.py collectstatic --noinput && \
    gunicorn --config gunicorn-cfg.py core.wsgi
