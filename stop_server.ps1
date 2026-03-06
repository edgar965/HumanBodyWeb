# Stop Django development server
# Only kills the manage.py runserver process on port 8081

Write-Host "Stopping Django server (port 8081)..." -ForegroundColor Cyan

# Find Django server process
$processes = Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object {
    $_.CommandLine -match 'manage\.py.*runserver.*8081'
}

if ($processes) {
    foreach ($proc in $processes) {
        Write-Host "Stopping process $($proc.ProcessId): $($proc.CommandLine)" -ForegroundColor Yellow
        Stop-Process -Id $proc.ProcessId -Force
    }
    Write-Host "Django server stopped" -ForegroundColor Green
} else {
    Write-Host "No Django server found on port 8081" -ForegroundColor Yellow
}
