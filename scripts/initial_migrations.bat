cd /D "C:\beachhandball_app"
call venv_beach\Scripts\activate.bat
python manage.py makemigrations beach_handball
python manage.py migrate beach_handball