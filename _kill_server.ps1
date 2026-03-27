Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
  Where-Object { $_.CommandLine -match 'manage\.py.*runserver.*4040' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force; Write-Host "Killed PID $($_.ProcessId)" }
