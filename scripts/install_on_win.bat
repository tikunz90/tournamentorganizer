rem @echo off
echo Start installing Beachhandball Tournament Organizer...
set root=C:\beachhandball_app\
if exist "C:\beachhandball_app\" rd /s /q "C:\beachhandball_app"
if not exist "C:\beachhandball_app\" mkdir C:\beachhandball_app
chdir /D %root%
pause
echo Create virtual environment...
pip install wheel
pip install virtualenv
virtualenv "C:\beachhandball_app\venv_beach"

echo Clone from Gitlab...
git init     
git remote add origin https://gitlab.com/beachhandball/beach_handball.git   
git fetch     
git checkout -t origin/master -f

echo Start venv...
call "C:\beachhandball_app\venv_beach\Scripts\activate.bat"
echo Start installing requirements
pip install -r requirements.txt

echo Start installing MysqlConnector
pip install ext_installer\mysqlclient-1.4.6-cp38-cp38-win32.whl

echo Initial migrations
call "C:\beachhandball_app\scripts\initial_migrations.bat"

echo FINISHED installing Beachhandball Tournament Organizer
pause