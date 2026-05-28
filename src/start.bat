@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "BACKEND_DIR=%SCRIPT_DIR%backend"
set "FRONTEND_DIR=%SCRIPT_DIR%frontend"

if not exist "%BACKEND_DIR%\main.py" (
    echo Backend entrypoint not found: "%BACKEND_DIR%\main.py"
    exit /b 1
)

if not exist "%FRONTEND_DIR%\package.json" (
    echo Frontend package file not found: "%FRONTEND_DIR%\package.json"
    exit /b 1
)

echo Starting backend on http://127.0.0.1:8000 ...
start "Market Dashboard Backend" /D "%BACKEND_DIR%" cmd /k "uvicorn main:app --host 127.0.0.1 --port 8000"

echo Starting frontend on http://127.0.0.1:5173 ...
start "Market Dashboard Frontend" /D "%FRONTEND_DIR%" cmd /k "npm run dev"

echo Startup commands were opened in separate command windows.
