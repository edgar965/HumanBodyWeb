Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
  Where-Object { $_.CommandLine -match 'manage\.py.*runserver.*8081' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force; Write-Host "Killed PID $($_.ProcessId)" }
Start-Sleep -Seconds 1
Start-Process python -ArgumentList 'A:/3DTools/HumanBodyWeb/manage.py','runserver','8081' -WorkingDirectory 'A:/3DTools/HumanBodyWeb' -WindowStyle Hidden
Write-Host "Server restarted on port 8081"
