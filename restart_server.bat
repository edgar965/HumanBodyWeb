@echo off
REM Den Entwicklungsserver dieses Projekts neu starten.
REM
REM Ruft restart_server.py, statt dasselbe ein zweites Mal zu bauen.
REM Dort steht, WARUM nur der Prozess am eigenen Port beendet wird:
REM Die alte Fassung hat am 10.09.2026 einen fremden Django-Server
REM eines anderen Projekts mit abgeschossen (shortlongx, Port 5020).
REM Und warum am Ende geprueft wird, ob der Port wirklich antwortet:
REM Sie meldete Erfolg, obwohl der Server gar nicht hochkam.
REM
REM Der Interpreter ist der dieses Projekts, nicht "python" aus dem
REM PATH - damit startete der Server nicht.
REM
REM Diese Datei ist bewusst ohne Umlaute: cmd.exe liest sie in der
REM Konsolen-Codepage, nicht in UTF-8, und zerlegt sonst die Zeilen.

setlocal
set "PY=%~dp0..\python14\Scripts\python.exe"
if not exist "%PY%" set "PY=python"

pushd "%~dp0"
"%PY%" restart_server.py
set ERG=%ERRORLEVEL%
popd
endlocal & exit /b %ERG%
