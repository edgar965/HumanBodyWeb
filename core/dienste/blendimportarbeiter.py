# -*- coding: utf-8 -*-
"""Blendimportarbeiter — der abgelöste Prozess eines Blender-Imports.

Wie `Meshfigurarbeiter`: `manage.py blendimport_fahren <kennung>` als eigener Prozess ohne Fenster, damit ein Neustart
des Servers den Lauf nicht mitreißt (ein Import dauert Minuten: „Mesh to 3D" auf der GPU, Backen in Blender). PID und
Log liegen im Ordner des Imports (`Blendimportablage`).
"""

import logging
import os
import subprocess
import sys
from pathlib import Path

from django.conf import settings

from .auftragsarbeiter import Auftragsarbeiter

logger = logging.getLogger('core')

__all__ = ['Blendimportarbeiter']


class Blendimportarbeiter:
    BEFEHL = 'blendimport_fahren'

    @classmethod
    def starten(cls, ablage, ab=None):
        ablage.anlegen()
        befehl = [sys.executable, str(Path(settings.BASE_DIR) / 'manage.py'), cls.BEFEHL, ablage.kennung]
        if ab:
            befehl += ['--ab', ab]
        with open(ablage.log(), 'ab') as protokoll:
            prozess = Auftragsarbeiter._popen(befehl, protokoll)
        ablage.pid().write_text(str(prozess.pid))
        stand = ablage.stand()
        stand.update(status='laeuft', fehler='', fortschritt=0, detail='Arbeitsprozess gestartet', pid=prozess.pid)
        ablage.stand_schreiben(stand)
        logger.info('Blender-Import %s: Arbeitsprozess %s (ab %s)', ablage.kennung, prozess.pid, ab or 'Anfang')
        return prozess.pid

    @staticmethod
    def pid(ablage):
        try:
            return int(ablage.pid().read_text().strip())
        # stumm gewollt: keine PID-Datei heißt kein laufender Arbeiter
        except (OSError, ValueError):
            return None

    @classmethod
    def lebt(cls, ablage):
        from ..pipelines.prozesspruefung import Prozesspruefung

        pid = cls.pid(ablage)
        return bool(pid) and Prozesspruefung.lebt(pid)

    @classmethod
    def anhalten(cls, ablage):
        """Stand zuerst (der Lauf prüft ihn), dann der Prozess samt Kindern (Runner, Blender halten die GPU)."""
        stand = ablage.stand()
        stand.update(status='angehalten', detail='Angehalten')
        ablage.stand_schreiben(stand)
        figur = (stand.get('ergebnis') or {}).get('figur') or {}
        if figur.get('id'):
            from ..models import Meshfigurauftrag

            Meshfigurauftrag.objects.filter(pk=figur['id'], status='laeuft').update(status='angehalten')
        pid = cls.pid(ablage)
        if not pid:
            return
        try:
            if os.name == 'nt':
                subprocess.run(['taskkill', '/PID', str(pid), '/T', '/F'], capture_output=True, check=False)
            else:
                os.kill(pid, 15)
        except OSError as fehler:
            logger.warning('Blender-Import %s: Prozess %s nicht beendet: %s', ablage.kennung, pid, fehler)
