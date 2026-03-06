@echo off
REM Stop Django server
echo Stopping Django server on port 8081...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8081 ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul

REM Wait a moment
timeout /t 2 /nobreak >nul

REM Start Django server
echo Starting Django server...
start /B python manage.py runserver 8081

echo Server restarted.
