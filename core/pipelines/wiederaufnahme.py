# -*- coding: utf-8 -*-
"""Wiederaufnahme — einen noch laufenden Pipeline-Prozess weiter beobachten.

Nach einem Serverneustart läuft der Unterprozess weiter (die SMPL-Pipelines
schreiben in eine LOGDATEI, nicht in eine Pipe — genau dafür). Diese Klasse nimmt
die Beobachtung wieder auf und bucht am Ende das Ergebnis.

WARUM EIGENES MODUL (18.08.2026)
================================
Das stand als `werkzeuge.remonitor_smpl_job` und rief `Startaufraeumen`, während
`Startaufraeumen` wiederum `werkzeuge` rief — ein Ring, den `abhaengigkeiten`
gemeldet hat. Jetzt hängen beide an `dienste.auftragsabschluss.Auftragsabschluss`
und nicht mehr aneinander.

WARUM NACH DEM ENDE NOCH EINMAL GELESEN WIRD
============================================
`job.refresh_from_db()` vor dem Buchen: Der Nutzer kann den Auftrag während der
Beobachtung abgebrochen haben. Ohne das erneute Lesen würde ein abgebrochener
Lauf am Ende doch als „fertig" gebucht.
"""

import logging
import time
from pathlib import Path

from django.conf import settings

from ..dienste.auftragsabschluss import Auftragsabschluss

logger = logging.getLogger('core.pipeline')


class Wiederaufnahme:
    """Beobachtet einen laufenden Prozess weiter und bucht das Ergebnis."""

    #: Zustände, in denen ein Auftrag noch als laufend gilt.
    LAUFEND = ('processing', 'v4_processing')
    #: Kurz warten, damit die letzten Schreibvorgänge des Prozesses ankommen.
    NACHLAUF_S = 1

    @classmethod
    def fahren(cls, job_id, pid):
        from core.models import BVHJob
        try:
            auftrag = BVHJob.objects.get(id=job_id)
        # stumm gewollt: Ist der Auftrag inzwischen geloescht, gibt es nichts zu
        # beobachten — das ist kein Fehler.
        except BVHJob.DoesNotExist:
            return
        ordner = Auftragsabschluss.ordner(job_id)
        cls._beobachten(auftrag, ordner, pid)
        time.sleep(cls.NACHLAUF_S)
        auftrag.refresh_from_db()
        if auftrag.status not in cls.LAUFEND:
            return                      # zwischenzeitlich abgebrochen
        cls._buchen(auftrag, ordner)

    @classmethod
    def _beobachten(cls, auftrag, ordner, pid):
        from .logbeobachter import Logbeobachter
        from .videolaenge import Videolaenge
        video = Path(settings.MEDIA_ROOT) / str(auftrag.video_file)
        bilder = Videolaenge.bilder(video) if video.exists() else 0
        Logbeobachter(auftrag, ordner / 'pipeline.log', bilder,
                      pid=pid).verfolgen()

    @classmethod
    def _buchen(cls, auftrag, ordner):
        bvh = Auftragsabschluss.bvh(ordner)
        if bvh:
            Auftragsabschluss.als_fertig(auftrag, bvh, ordner / 'pipeline.pid',
                                         meldung='Complete')
            logger.info('[remonitor] Job %s: BVH found, marked complete.',
                        auftrag.id)
            return
        Auftragsabschluss.als_gescheitert(
            auftrag, Auftragsabschluss.logauszug(ordner / 'pipeline.log'))
        logger.error('[remonitor] Job %s: no BVH found, marked failed.',
                     auftrag.id)
        Auftragsabschluss.pid_weg(ordner / 'pipeline.pid')
