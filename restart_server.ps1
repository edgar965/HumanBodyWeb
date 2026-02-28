Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object { $_.CommandLine -match 'manage\.py.*runserver.*8081' } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
Start-Sleep -Seconds 1
Start-Process python -ArgumentList 'A:/3DTools/HumanBodyWeb/manage.py','runserver','8081' -WorkingDirectory 'A:/3DTools/HumanBodyWeb' -WindowStyle Hidden
