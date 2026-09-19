# -*- coding: utf-8 -*-
"""Bildmodellarbeiter — der abgelöste Prozess eines Bildmodell-Auftrags.

Wie `Auftragsarbeiter` (Video → BVH): `manage.py bildmodell_fahren <id>
--ab <schritt>` als eigener Prozess ohne Fenster, damit ein Neustart des
Servers (jede Python-Änderung) den Lauf nicht mitreißt. PID und Log liegen
im Auftragsordner (`Bildmodellablage`), die PID auch im Modell.
"""

import logging
import os
import signal
import sys
from pathlib import Path

from django.conf import settings

from ..daten.bildmodellablage import Bildmodellablage
from .auftragsarbeiter import Auftragsarbeiter

logger = logging.getLogger('core')

__all__ = ['Bildmodellarbeiter']


class Bildmodellarbeiter:
    BEFEHL = 'bildmodell_fahren'

    @classmethod
    def starten(cls, job, ab='sichtung'):
        ablage = Bildmodellablage(job.kennung)
        ablage.anlegen()
        befehl = [
            sys.executable,
            str(Path(settings.BASE_DIR) / 'manage.py'),
            cls.BEFEHL,
            str(job.id),
            '--ab',
            ab,
        ]
        with open(ablage.log(), 'ab') as protokoll:
            prozess = Auftragsarbeiter._popen(befehl, protokoll)
        ablage.pid().write_text(str(prozess.pid))
        job.pid = prozess.pid
        job.status = 'laeuft'
        job.error_message = ''
        job.save(update_fields=['pid', 'status', 'error_message', 'updated_at'])
        logger.info('Bildmodell %s: Arbeitsprozess %s ab %s', job.kennung, prozess.pid, ab)
        return prozess.pid

    @classmethod
    def lebt(cls, job):
        if not job.pid:
            return False
        from ..pipelines.prozesspruefung import Prozesspruefung

        return Prozesspruefung.lebt(int(job.pid))

    @classmethod
    def anhalten(cls, job):
        """Den Lauf beenden: Status zuerst (der Lauf prüft ihn zwischen den
        Schritten), dann der Prozess samt Kindern."""
        job.status = 'angehalten'
        job.save(update_fields=['status', 'updated_at'])
        pid = job.pid
        if not pid:
            return
        try:
            if os.name == 'nt':
                import subprocess

                subprocess.run(['taskkill', '/PID', str(pid), '/T', '/F'], capture_output=True, check=False)
            else:
                os.kill(int(pid), signal.SIGTERM)
        except OSError as fehler:
            logger.warning('Bildmodell %s: Prozess %s nicht beendet: %s', job.kennung, pid, fehler)
        job.pid = None
        job.save(update_fields=['pid', 'updated_at'])
