@echo off
setlocal
cd /d "%~dp0"

echo === Trizen Photo Sharing Platform ===
echo.

where python >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Python was not found on PATH. Install Python 3.12+ first.
  pause
  exit /b 1
)

python -c "import uvicorn" >nul 2>&1
if errorlevel 1 (
  echo [INFO] Installing backend dependencies...
  python -m pip install -r backend\requirements.txt
  if errorlevel 1 (
    echo [ERROR] Backend dependency install failed. See output above.
    pause
    exit /b 1
  )
)

where npm >nul 2>&1
if errorlevel 1 (
  echo [ERROR] npm was not found on PATH. Install Node.js LTS first.
  pause
  exit /b 1
)

echo [1/2] Starting backend  - http://localhost:8000  (docs: /docs)
start "Trizen Backend" /d "%~dp0backend" cmd /k python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

if not exist "frontend\node_modules" (
  echo [2/2] First run: installing frontend dependencies - this takes a few minutes...
  pushd frontend
  call npm install
  if errorlevel 1 (
    echo [ERROR] npm install failed. See output above.
    popd
    pause
    exit /b 1
  )
  popd
) else (
  echo [2/2] Frontend dependencies found, skipping install.
)

echo Starting frontend - http://localhost:3000
start "Trizen Frontend" /d "%~dp0frontend" cmd /k call npm start

echo.
echo Backend:    http://localhost:8000  (API docs: http://localhost:8000/docs)
echo Frontend:   http://localhost:3000
echo Galleries:  http://localhost:3000/gallery/<slug> + PIN