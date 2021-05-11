@echo off
cd /D "C:\beachhandball_app"
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -pmysql < scripts\create_db_and_user.sql