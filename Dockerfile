FROM python:3.6

ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    ssh \
    autossh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the private key file and set permissions
# Assuming the private key file is named id_rsa and located in the same directory as your Dockerfile
COPY id_rsa /root/.ssh/id_rsa
RUN chmod 600 /root/.ssh/id_rsa

# Add the private key to the SSH agent
RUN eval $(ssh-agent -s) && ssh-add /root/.ssh/id_rsa

# Copy application files
COPY manage.py gunicorn-cfg.py requirements.txt .env ./
COPY beachhandball_app beachhandball_app
COPY authentication authentication
COPY core core

# Install Python dependencies
RUN pip install -r requirements.txt

# Run Django management commands
# -o StrictHostKeyChecking=noRUN python manage.py makemigrations
#RUN python manage.py migrate
#RUN python manage.py collectstatic --noinput

# Expose the port your app runs on
EXPOSE 8080

# Command to run the SSH tunnel and the application
#CMD autossh -M 0 -N -L 3307:127.0.0.1:3306 root@38.242.148.70 & \
#    gunicorn --config gunicorn-cfg.py core.wsgi

    # Start SSH tunnel in the background (adjust the tunnel setup as needed)
CMD autossh -M 0 -N -o StrictHostKeyChecking=no -L 3307:127.0.0.1:3306 root@38.242.148.70 & \
  python manage.py makemigrations && \
  python manage.py migrate && \
  python manage.py collectstatic --noinput && \
  gunicorn --config gunicorn-cfg.py core.wsgi
