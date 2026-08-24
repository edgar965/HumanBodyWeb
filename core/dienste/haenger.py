# -*- coding: utf-8 -*-
"""Haenger — steht ein Auftrag still, ohne dass jemand es merkt?

Aus `core/api/auftraege.py` herausgelöst (17.08.2026, `dateigroesse`). Dort
lagen drei Funktionen und zwei Konstanten zu derselben Frage zwischen den
Endpunkten verstreut — `_haenger_erkennen`, `_prozess_lebt`,
`_haenger_freigeben`, `HAENGT_NACH`, `_ARBEITSZUSTAENDE`.

WARUM ES DIESE PRÜFUNG ÜBERHAUPT GIBT
=====================================
Eine Pipeline läuft als eigener Prozess. Stirbt der (Absturz, Neustart des
Servers, harter Kill), bleibt der Auftrag in der Datenbank auf „läuft" stehen —
für immer. Die Oberfläche zeigt dann einen Fortschritt, der sich nie mehr
bewegt, und die Sperre „ein Auftrag läuft schon" blockiert alle weiteren.

Zwei Fristen, weil es zwei Fragen sind:

* `STILL_MINUTEN` (5) — „zeigt die Oberfläche einen toten Auftrag?" Hier wird
  zusätzlich geprüft, ob wirklich kein Prozess mehr lebt.
* `FREIGABE_MINUTEN` (10) — „darf ein neuer Auftrag starten?" Dort zählt nur die
  Zeit; die Frist ist doppelt so lang, damit ein langsamer, aber lebender Lauf
  nicht abgeräumt wird.
"""

import logging
from pathlib import Path

from django.conf import settings
from django.utils import timezone

from .laufende_prozesse import LaufendeProzesse
from ..pipelines.werkzeuge import _is_pid_alive

logger = logging.getLogger('core')


class Haenger:
    """Erkennt stillstehende Aufträge und gibt die Sperre frei."""

    #: Zustände, in denen noch gerechnet werden sollte.
    ARBEITET = ('detecting_2d', 'openpose', 'openpose_csv', 'mediapipe',
                'lifting_3d', 'mocapnet', 'v4_processing', 'processing')

    #: Zustände, in denen ein Auftrag die Sperre hält.
    LAEUFT = ('processing', 'v4_processing')

    #: Minuten ohne Fortschritt, nach denen ein Auftrag als hängend gilt.
    STILL_MINUTEN = 5

    #: Minuten, nach denen ein stillstehender Auftrag die Sperre freigibt.
    FREIGABE_MINUTEN = 10

    @classmethod
    def erkennen(cls, job):
        """Steht dieser Auftrag still und lebt kein Prozess mehr? Dann gescheitert."""
        if job.status not in cls.ARBEITET:
            return False
        alter = (timezone.now() - job.updated_at).total_seconds()
        if alter <= cls.STILL_MINUTEN * 60:
            return False
        if cls.prozess_lebt(str(job.id)):
            return False
        job.status = 'failed'
        job.error_message = ('Pipeline stalled (no progress for '
                             '%d min, no running process)' % (alter // 60))
        job.save(update_fields=['status', 'error_message'])
        logger.warning('Auftrag %s als hängend erkannt (%d min ohne Fortschritt)',
                       job.id, alter // 60)
        return True

    @staticmethod
    def prozess_lebt(jid):
        """Läuft zu diesem Auftrag noch ein Prozess — als Objekt oder per PID-Datei?"""
        prozess = LaufendeProzesse.holen(jid)
        if prozess and prozess.poll() is None:
            return True
        pid_datei = Path(settings.MEDIA_ROOT) / 'output' / jid / 'pipeline.pid'
        if not pid_datei.exists():
            return False
        try:
            return _is_pid_alive(int(pid_datei.read_text().strip()))
        except (ValueError, OSError):
            logger.debug('PID-Datei %s nicht lesbar', pid_datei, exc_info=True)
            return False

    @classmethod
    def freigeben(cls):
        """Aufträge, die lange stillstehen, auf gescheitert setzen.

        Läuft vor dem Anlegen eines neuen Auftrags — sonst blockiert ein
        toter Auftrag die Sperre auf Dauer.
        """
        from ..models import BVHJob
        grenze = timezone.now() - timezone.timedelta(minutes=cls.FREIGABE_MINUTEN)
        return BVHJob.objects.filter(
            status__in=cls.LAEUFT, updated_at__lt=grenze).update(
                status='failed',
                error_message='Auto-cancelled: stuck > %d min'
                              % cls.FREIGABE_MINUTEN)
