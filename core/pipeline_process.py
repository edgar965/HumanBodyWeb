# -*- coding: utf-8 -*-
"""PipelineProzess — die EINE Stelle, an der ML-Subprozesse gestartet werden.

WARUM (Review 12.08.2026)
------------------------
Django (Python 3.14) startet die Pipelines in der ML-Umgebung (Python 3.10) und
liest deren stdout zeilenweise als Fortschrittskanal. Sechs Startstellen, drei
unterschiedliche Ausstattungen:

* Zeichensatz: NUR EINE der vier Stellen setzte `encoding='utf-8',
  errors='replace'`. Die anderen verließen sich auf die Windows-Landeseinstellung
  — hier gemessen `cp1252`, UTF-8-Modus aus. Gibt eine ML-Bibliothek etwas
  außerhalb von cp1252 aus (Fortschrittsbalken, ein Pfad mit Umlaut wie
  `0030_BallettLänger.mp4`), kommt im besten Fall Buchstabensalat an, im
  schlechteren stirbt die Leseschleife mit `UnicodeDecodeError` — und der Auftrag
  gilt als gescheitert, während die Pipeline auf der Grafikkarte weiterrechnet.
* stderr: Fünf von sechs Stellen räumten stderr mit einem eigenen Faden ab, die
  OpenPose-Stelle nicht — bei `stderr=PIPE`. OpenPose/Caffe schreibt dort viel.
  Läuft der Pipe-Puffer (etwa 64 KB) voll, blockiert der Kindprozess beim
  Schreiben, während Django auf die nächste stdout-Zeile wartet. Beide warten
  dann aufeinander.

Deshalb wird hier gestartet und nicht mehr in den Aufrufstellen. Die Leselogik
bleibt bei den Aufrufern — sie ist je Pipeline verschieden (`TOTAL:`, `STATUS:`,
tqdm) und soll nicht in einen Helfer gepresst werden.

WAS DIESE KLASSE NICHT ÄNDERT
-----------------------------
Die bestehende Prüfung der Aufrufer bleibt gültig und wird bewusst nicht
ersetzt: Rückgabewert prüfen, Ausgabedatei prüfen, STOP_FLAG beachten, teilweise
erzeugte BVH-Dateien retten. Das war schon vorher sauber gebaut.
"""
import logging
import os
import subprocess
import threading

logger = logging.getLogger('core')


class PipelineProzess:
    """Startet einen Subprozess mit einheitlichem Zeichensatz und abgeräumtem stderr.

        p = PipelineProzess.starten(cmd, cwd=..., env_extra={'CUDA_VISIBLE_DEVICES': '0'})
        for zeile in p.proc.stdout:
            ...
        p.warten(timeout=1800)
        if p.proc.returncode != 0:
            raise RuntimeError(p.fehlertext())
    """

    #: So viele stderr-Zeilen werden behalten. Mehr braucht keine Fehlermeldung,
    #: und ein Modell-Download mit Fortschrittsbalken schreibt Zehntausende.
    STDERR_ZEILEN = 400

    def __init__(self, proc, stderr_zeilen, drain):
        self.proc = proc
        self._stderr_zeilen = stderr_zeilen
        self._drain = drain

    # ------------------------------------------------------------------- Starten

    @classmethod
    def starten(cls, cmd, cwd=None, env_extra=None, stderr_sammeln=True):
        """Subprozess starten. stdout ist zeilengepuffert und UTF-8-dekodiert.

        `stderr_sammeln=True` liest stderr in einem eigenen Faden mit (gegen den
        vollen Puffer) und behält die letzten Zeilen für die Fehlermeldung."""
        env = cls.umgebung(env_extra)
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE if stderr_sammeln else subprocess.DEVNULL,
            text=True,
            bufsize=1,                      # zeilenweise, sonst kommt Fortschritt in Schüben
            encoding='utf-8',
            errors='replace',               # ein Ersatzzeichen ist besser als ein Absturz
            cwd=str(cwd) if cwd else None,
            env=env,
        )
        zeilen, drain = [], None
        if stderr_sammeln:
            drain = threading.Thread(target=cls._stderr_lesen,
                                     args=(proc.stderr, zeilen), daemon=True)
            drain.start()
        return cls(proc, zeilen, drain)

    @staticmethod
    def umgebung(env_extra=None):
        """Umgebung für den Kindprozess.

        `PYTHONIOENCODING` und `PYTHONUTF8` wirken auf der ANDEREN Seite: Sie
        bringen den Kindprozess dazu, UTF-8 zu schreiben — `encoding='utf-8'`
        allein sagt nur, wie wir lesen. Beides gehört zusammen.

        `PYTHONUNBUFFERED` sorgt dafür, dass der Fortschritt fortlaufend
        ankommt; ohne das puffert Python blockweise, sobald die Ausgabe nicht an
        ein Terminal geht, und die Anzeige springt.

        `os.environ` wird geerbt (die Pipelines brauchen PATH und CUDA-Variablen),
        aber `PYTHONPATH`/`PYTHONHOME` werden entfernt: Django läuft in 3.14, die
        Pipelines in 3.10 — ein geerbter Suchpfad zieht Pakete der falschen
        Version herein."""
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PYTHONUTF8'] = '1'
        env['PYTHONUNBUFFERED'] = '1'
        for schluessel in ('PYTHONPATH', 'PYTHONHOME'):
            env.pop(schluessel, None)
        if env_extra:
            env.update({k: str(v) for k, v in env_extra.items()})
        return env

    @property
    def stderr_zeilen(self):
        """Die mitgelesenen stderr-Zeilen (dieselbe Liste, die weiter gefüllt wird).

        Die Aufrufer in `views.py` bauen daraus ihre Fehlermeldungen; sie geben
        die Liste weiter, statt sie zu kopieren, damit auch Zeilen enthalten sind,
        die erst nach dem Zugriff eintreffen."""
        return self._stderr_zeilen

    @staticmethod
    def _stderr_lesen(strom, ziel):
        try:
            for zeile in strom:
                ziel.append(zeile)
                if len(ziel) > PipelineProzess.STDERR_ZEILEN:
                    del ziel[:-PipelineProzess.STDERR_ZEILEN]
        except (ValueError, OSError):
            pass                     # Strom wurde geschlossen — der Prozess ist fertig

    # -------------------------------------------------------------------- Warten

    def warten(self, timeout=None):
        """Auf das Ende warten und den stderr-Faden einsammeln."""
        try:
            self.proc.wait(timeout=timeout)
        finally:
            if self._drain:
                self._drain.join(timeout=5)
        return self.proc.returncode

    def fehlertext(self, max_zeichen=4000):
        """Die letzten stderr-Zeilen, gekürzt — für Fehlermeldungen."""
        return ''.join(self._stderr_zeilen)[-max_zeichen:].strip()

    def beenden(self):
        """Prozessbaum beenden.

        `taskkill /T` statt `proc.kill()`: Die Pipelines starten selbst weiter
        (ffmpeg, Torch-Arbeiter). Ein `kill` auf den Vater lässt die Kinder mit
        belegtem Grafikspeicher zurück — beim nächsten Lauf fehlt dann VRAM."""
        if self.proc.poll() is not None:
            return
        if os.name == 'nt':
            try:
                subprocess.run(['taskkill', '/PID', str(self.proc.pid), '/T', '/F'],
                               capture_output=True, timeout=15)
                return
            except (OSError, subprocess.SubprocessError):
                logger.warning('PipelineProzess: taskkill fehlgeschlagen, nutze kill()')
        try:
            self.proc.kill()
        except OSError:
            pass
