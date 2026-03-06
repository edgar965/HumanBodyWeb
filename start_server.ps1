# Start Django development server
# Runs on port 8081 with Daphne ASGI server

Write-Host "Starting Django server on port 8081..." -ForegroundColor Cyan

$pythonPath = "python"
$managePy = "A:/3DTools/HumanBodyWeb/manage.py"
$workDir = "A:/3DTools/HumanBodyWeb"

# Check if server is already running
$existing = Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object {
    $_.CommandLine -match 'manage\.py.*runserver.*8081'
}

if ($existing) {
    Write-Host "Django server already running (PID: $($existing.ProcessId))" -ForegroundColor Yellow
    exit 0
}

# Start server in hidden window
Start-Process $pythonPath `
    -ArgumentList $managePy, 'runserver', '8081' `
    -WorkingDirectory $workDir `
    -WindowStyle Hidden

Write-Host "Waiting for server to start..." -ForegroundColor Cyan
Start-Sleep -Seconds 3

# Verify server is responding
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8081/" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "Django server started successfully on http://localhost:8081/" -ForegroundColor Green
    }
} catch {
    Write-Host "Warning: Server may not be fully ready yet" -ForegroundColor Yellow
    Write-Host "Check manually: http://localhost:8081/" -ForegroundColor Yellow
}
