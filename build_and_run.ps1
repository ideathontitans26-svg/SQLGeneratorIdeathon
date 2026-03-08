# Build frontend and run the full application
Write-Host "Building frontend..."
Push-Location frontend
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "Frontend build failed."
    Pop-Location
    exit 1
}
Pop-Location

Write-Host ""
Write-Host "Starting server at http://localhost:8000"
Push-Location backend
python run.py
Pop-Location
