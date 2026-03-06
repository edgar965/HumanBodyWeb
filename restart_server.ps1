# Restart Django development server
# Stops and starts the server on port 8081

Write-Host "Restarting Django server..." -ForegroundColor Cyan

# Stop server
& "$PSScriptRoot\stop_server.ps1"

# Wait a moment
Start-Sleep -Seconds 1

# Start server
& "$PSScriptRoot\start_server.ps1"
