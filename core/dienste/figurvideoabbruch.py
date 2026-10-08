# -*- coding: utf-8 -*-
"""Figurvideoabbruch — einen laufenden Videolauf des Server-Wegs abbrechen.

WARUM (Edgar, 08.10.2026: „mach einen Button Abbrechen für die Video Erzeugung und brich den job ab"):
Der Lauf ist ein Unterprozess (`ModelPhysik/filmlauf.py`) mit OpenGL-Kontext und Minuten Rechenzeit; ohne
Abbruch hält er Grafikkarte und Kerne, bis er von selbst endet.

Zwei Wege zum Prozess:
- Das Verzeichnis `LaufendeProzesse` kennt den Prozess, solange der Server nicht neu geladen hat. Das
  `Popen`-Objekt hält das Handle: `poll()` sagt zuverlässig, ob er noch läuft, und die PID kann nicht
  anderweitig vergeben sein.
- Der Autoreload des Entwicklungsservers (eine andere Sitzung speichert eine Python-Datei) leert dieses
  Verzeichnis, der Lauf geht aber weiter. Darum merkt sich `starten` die PID in `prozess.json`. Windows
  vergibt PIDs rasch neu — vor dem Beenden muss die Befehlszeile der PID die Kennung des Auftrags nennen,
  sonst bliebe der Abbruch ein Schuss auf irgendeinen fremden Prozess.

Beendet wird samt Kindern (`taskkill /T`): Der Lauf startet ffmpeg selbst.
"""

import json
import logging
import os
import subprocess
import time

from ..pipelines.prozesspruefung import Prozesspruefung
from .laufende_prozesse import LaufendeProzesse

logger = logging.getLogger('core')


class Figurvideoabbruch:
    """Beendet den Unterprozess eines Videolaufs und schreibt „abgebrochen" in den Stand."""

    PID_DATEI = 'prozess.json'
    #: So lange wartet der Abbruch, bis der Prozess wirklich weg ist — erst danach darf der Stand überschrieben
    #: werden, sonst schriebe der sterbende Lauf ihn noch einmal.
    WARTEN_S = 5.0
    TEXT = 'vom Nutzer abgebrochen'

    @classmethod
    def pid_merken(cls, ordner, pid):
        with open(os.path.join(ordner, cls.PID_DATEI), 'w', encoding='utf-8') as datei:
            json.dump({'pid': int(pid)}, datei)

    @classmethod
    def abbrechen(cls, kennung, ordner):
        """`{'abgebrochen': bool, 'prozess_beendet': bool, 'grund': str}` — `kennung` ist schon bereinigt."""
        stand_pfad = os.path.join(ordner, 'fortschritt.json')
        stand = cls._lesen(stand_pfad)
        if stand.get('fertig'):
            return {'abgebrochen': False, 'prozess_beendet': False, 'grund': 'Das Video war schon fertig.'}
        pid = cls._pid(kennung, ordner)
        beendet = False
        if pid:
            cls._beenden(pid)
            beendet = True
        LaufendeProzesse.entfernen('figurvideo_' + kennung)
        stand.setdefault('phase', 'Abgebrochen')
        stand.setdefault('anteil', 0.0)
        stand.update(fehler=cls.TEXT, abgebrochen=True)
        with open(stand_pfad, 'w', encoding='utf-8') as datei:
            json.dump(stand, datei, ensure_ascii=False)
        logger.info('Figurvideo %s abgebrochen (Prozess %s)', kennung, pid if beendet else 'war nicht mehr da')
        return {'abgebrochen': True, 'prozess_beendet': beendet, 'grund': ''}

    # ------------------------------------------------------------ Prozess

    @classmethod
    def _pid(cls, kennung, ordner):
        """PID des laufenden Prozesses — oder `None`, wenn keiner (mehr) läuft."""
        prozess = LaufendeProzesse.holen('figurvideo_' + kennung)
        if prozess is not None:
            return prozess.pid if prozess.poll() is None else None
        daten = cls._lesen(os.path.join(ordner, cls.PID_DATEI))
        pid = daten.get('pid')
        if pid and Prozesspruefung.lebt(pid) and kennung in cls._befehlszeile(pid):
            return int(pid)
        return None

    @staticmethod
    def _befehlszeile(pid):
        """Befehlszeile einer PID (Windows); leer, wenn sie sich nicht lesen lässt."""
        try:
            antwort = subprocess.run(
                ['powershell', '-NoProfile', '-NonInteractive', '-Command',
                 '(Get-CimInstance Win32_Process -Filter "ProcessId=%d").CommandLine' % int(pid)],
                capture_output=True, text=True, timeout=15, check=False,
            )
            return antwort.stdout or ''
        except (OSError, subprocess.SubprocessError) as fehler:
            logger.warning('Figurvideo: Befehlszeile von %s nicht lesbar: %s', pid, fehler)
            return ''

    @classmethod
    def _beenden(cls, pid):
        try:
            if os.name == 'nt':
                subprocess.run(['taskkill', '/PID', str(pid), '/T', '/F'], capture_output=True, check=False)
            else:
                os.kill(pid, 15)
        except OSError as fehler:
            logger.warning('Figurvideo: Prozess %s nicht beendet: %s', pid, fehler)
            return
        ende = time.monotonic() + cls.WARTEN_S
        while Prozesspruefung.lebt(pid) and time.monotonic() < ende:
            time.sleep(0.1)

    @staticmethod
    def _lesen(pfad):
        if not os.path.isfile(pfad):
            return {}
        try:
            with open(pfad, encoding='utf-8') as datei:
                return json.load(datei)
        except (OSError, ValueError):
            # Eine halb geschriebene Datei zählt als „nichts da" — der Abbruch schreibt sie gleich neu.
            return {}
