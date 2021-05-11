@echo off
echo Installing MySQL Server. Please wait...

msiexec /i "mysql-installer-community-8.0.19.0.msi" /qn

echo Configurating MySQL Server...

"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqlinstanceconfig.exe" 
-i -q ServiceName=MySQL RootPassword=mysql ServerType=DEVELOPER 
DatabaseType=MYISAM Port=3306 Charset=utf8
echo Installation was successfully