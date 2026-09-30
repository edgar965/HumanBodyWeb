# -*- coding: utf-8 -*-
"""Haarenginearbeiter — der abgelöste Prozess eines Auftrags „Haar Engine".

Wie `Meshfigurarbeiter`: `manage.py haarengine_fahren <id>` als eigener Prozess ohne Fenster, damit ein
Neustart des Servers (jede Python-Änderung) den Lauf nicht mitreißt — ein Lauf dauert Minuten bis Stunden
und hält die Grafikkarte. PID und Log liegen im Auftragsordner.
"""

import logging
import os
import signal
import sys
from pathlib import Path

from django.conf import settings
from django.utils import timezone

from ..daten.haarengineablage import Haarengineablage
from .auftragsarbeiter import Auftragsarbeiter

logger = logging.getLogger('core')

__all__ = ['Haarenginearbeiter']


class Haarenginearbeiter:
    BEFEHL = 'haarengine_fahren'

    @classmethod
    def starten(cls, job, ab=None, bis=None):
        ablage = Haarengineablage(job.kennung)
        ablage.anlegen()
        befehl = [sys.executable, str(Path(settings.BASE_DIR) / 'manage.py'), cls.BEFEHL, str(job.id)]
        if ab:
            befehl += ['--ab', ab]
        if bis:
            befehl += ['--bis', bis]
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
        logger.info(
            'Haar Engine %s: Arbeitsprozess %s (ab %s bis %s)',
            job.kennung,
            prozess.pid,
            ab or 'Anfang',
            bis or 'Ende',
        )
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
        (`taskkill /T` — die Runner in python10 halten die Grafikkarte)."""
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
            logger.warning('Haar Engine %s: Prozess %s nicht beendet: %s', job.kennung, pid, fehler)
        job.pid = None
        job.save(update_fields=['pid', 'updated_at'])
