@echo off
echo Building frontend...
cd frontend
call npm run build
if errorlevel 1 (
    echo Frontend build failed.
    pause
    exit /b 1
)
cd ..

echo.
echo Starting server at http://localhost:8000
cd backend
python run.py
