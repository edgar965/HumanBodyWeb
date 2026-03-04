Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object { $_.CommandLine -match 'manage\.py.*runserver.*5020' } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
Start-Sleep -Seconds 1
Start-Process python -ArgumentList 'A:/HumanBodyTest/HumanBodyWeb/manage.py','runserver','5020' -WorkingDirectory 'A:/HumanBodyTest/HumanBodyWeb' -WindowStyle Hidden
