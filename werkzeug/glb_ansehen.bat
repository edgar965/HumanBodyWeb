@echo off
rem glb_ansehen — eine .glb/.gltf mit laufender Animation ansehen.
rem
rem F3D (C:\Program Files\F3D) kann glTF-Animationen abspielen; es fehlte nur
rem der Aufruf. Benutzung:
rem
rem   glb_ansehen.bat <datei.glb>
rem   oder eine Datei auf diese .bat ziehen
rem
rem Als Standardprogramm setzen: Rechtsklick auf eine .glb -> Öffnen mit ->
rem andere App -> diese Datei wählen und „Immer verwenden" ankreuzen.
rem
rem Tasten in F3D: Leertaste hält die Animation an und startet sie wieder,
rem W wechselt zwischen mehreren Animationen, H zeigt die Hilfe.

set F3D="C:\Program Files\F3D\bin\f3d.exe"
if not exist %F3D% (
    echo F3D nicht gefunden: %F3D%
    pause
    exit /b 1
)
if "%~1"=="" (
    echo Benutzung: %~nx0 ^<datei.glb^>
    pause
    exit /b 1
)
%F3D% --animation-autoplay --animation-progress --filename --grid "%~1"
