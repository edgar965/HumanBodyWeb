"""
Restart Django server
"""
import subprocess
import time
import psutil

# Kill Django process
for proc in psutil.process_iter(['pid', 'cmdline']):
    try:
        cmdline = proc.info['cmdline']
        text = str(cmdline).lower() if cmdline else ''
        if 'python' in text and 'manage.py' in text and 'runserver' in text:
            print(f"Killing process {proc.info['pid']}: {' '.join(cmdline)}")
            proc.kill()
            time.sleep(2)
    # stumm gewollt: Der Prozess kann zwischen dem Auflisten und dem `kill`
    # von selbst enden — genau das war das Ziel. Fremde Prozesse ohne Zugriff
    # gehen uns nichts an.
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

# Start new server
print("Starting new server...")
subprocess.Popen(
    ['python', 'A:/3DTools/HumanBodyWeb/manage.py', 'runserver', '8081'],
    cwd='A:/3DTools/HumanBodyWeb',
    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess,
                                                         'CREATE_NO_WINDOW') else 0
)
print("Server restarted!")
time.sleep(3)
