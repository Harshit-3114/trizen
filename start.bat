@echo off
echo Starting Trizen Challenge Photo Sharing Platform...
echo.
echo Starting Backend Server...
start "" cmd /k "cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo.
echo Starting Frontend Server...
start "" cmd /k "cd frontend && npm start"
echo.
echo Both servers are starting in separate windows.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000

