# -*- coding: utf-8 -*-
"""Meshfigurarbeiter — der abgelöste Prozess eines Auftrags „Mesh to 3D".

Wie `Mesharbeiter`: `manage.py meshfigur_fahren <id>` als eigener Prozess ohne Fenster, damit
ein Neustart des Servers (jede Python-Änderung) den Lauf nicht mitreißt — ein Lauf dauert
Minuten (GPU-Registrierung in mehreren Runden). PID und Log liegen im Auftragsordner.
"""

import logging
import os
import signal
import sys
from pathlib import Path

from django.conf import settings
from django.utils import timezone

from ..daten.meshfigurablage import Meshfigurablage
from .auftragsarbeiter import Auftragsarbeiter

logger = logging.getLogger('core')

__all__ = ['Meshfigurarbeiter']


class Meshfigurarbeiter:
    BEFEHL = 'meshfigur_fahren'

    @classmethod
    def starten(cls, job, ab=None):
        ablage = Meshfigurablage(job.kennung)
        ablage.anlegen()
        befehl = [sys.executable, str(Path(settings.BASE_DIR) / 'manage.py'), cls.BEFEHL, str(job.id)]
        if ab:
            befehl += ['--ab', ab]
        with open(ablage.log(), 'ab') as protokoll:
            prozess = Auftragsarbeiter._popen(befehl, protokoll)
        ablage.pid().write_text(str(prozess.pid))
        job.pid = prozess.pid
        job.status = 'laeuft'
        job.error_message = ''
        job.progress = 0
        job.progress_detail = 'Arbeitsprozess gestartet'
        job.started_at = timezone.now()
        job.finished_at = None
        job.save(
            update_fields=[
                'pid',
                'status',
                'error_message',
                'progress',
                'progress_detail',
                'started_at',
                'finished_at',
                'updated_at',
            ]
        )
        logger.info('Mesh to 3D %s: Arbeitsprozess %s (ab %s)', job.kennung, prozess.pid, ab or 'Anfang')
        return prozess.pid

    @classmethod
    def lebt(cls, job):
        if not job.pid:
            return False
        from ..pipelines.prozesspruefung import Prozesspruefung

        return Prozesspruefung.lebt(int(job.pid))

    @classmethod
    def anhalten(cls, job):
        """Status zuerst (der Lauf prüft ihn zwischen den Schritten), dann der Prozess samt Kindern
        (`taskkill /T` — der Runner in python10 hält die Grafikkarte)."""
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
            logger.warning('Mesh to 3D %s: Prozess %s nicht beendet: %s', job.kennung, pid, fehler)
        job.pid = None
        job.save(update_fields=['pid', 'updated_at'])
