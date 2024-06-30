@echo off
cd /d %~dp0

start python app.py

timeout /t 1 /nobreak
start http://localhost/admin
start http://localhost/

pause

