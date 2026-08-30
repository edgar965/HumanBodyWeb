# -*- coding: utf-8 -*-
"""Auftragsabschluss — einen Pipeline-Auftrag als fertig oder gescheitert buchen.

WARUM DIESE KLASSE (18.08.2026)
==============================
Dieselben vier Schritte brauchten ZWEI Stellen: das Aufräumen nach einem
Serverstart (`Startaufraeumen`) und die Wiederaufnahme eines noch laufenden
Prozesses (`Wiederaufnahme`). Beide riefen sich gegenseitig auf, und das Werkzeug
`abhaengigkeiten` meldete den Ring:

    pipelines.werkzeuge -> dienste.startaufraeumen -> pipelines.werkzeuge

Jetzt hängen beide an DIESER Klasse, und keine an der anderen.

DIE VIER SCHRITTE
=================
    bvh(ordner)              die erste BVH mit Bewegung darin
    als_fertig(...)          Auftrag auf „complete", Bildrate nachziehen
    als_gescheitert(...)     Auftrag auf „failed" mit Grund
    pid_weg(pfad)            die PID-Notiz entfernen

Die MINDESTGROESSE ist der Kern: Eine BVH mit 50 Byte ist ein Kopf ohne
Bewegung. Sie als Ergebnis zu buchen heißt, dem Nutzer einen leeren Lauf als
fertig zu melden.
"""

import glob
import logging
import os
from pathlib import Path

from django.conf import settings
from .videobildrate import Videobildrate

logger = logging.getLogger('core')


class Auftragsabschluss:
    """Bucht das Ergebnis eines Pipeline-Auftrags."""

    #: Kleiner heisst: die BVH ist ein Rumpf ohne Bewegung.
    MINDESTGROESSE = 100
    #: Weitergereicht — der Wert und seine Begruendung stehen in
    #: `videobildrate.py`.
    VORGABE_BILDRATE = Videobildrate.VORGABE
    NEUSTART_HINWEIS = ('Server was restarted while job was running. '
                        'Click "Neu starten" to retry.')

    @classmethod
    def ordner(cls, job_id):
        return Path(settings.MEDIA_ROOT) / 'output' / str(job_id)

    @classmethod
    def bvh(cls, ordner):
        """Die erste BVH im Ordner, die mehr als einen Rumpf enthält."""
        for datei in glob.glob(str(Path(ordner) / '*.bvh')):
            if os.path.getsize(datei) > cls.MINDESTGROESSE:
                return datei
        return None

    @classmethod
    def als_fertig(cls, auftrag, bvh, pid_datei=None, meldung=None):
        auftrag.bvh_file = bvh
        auftrag.status = 'complete'
        auftrag.progress = 100
        auftrag.progress_detail = meldung or 'Complete (recovered after restart)'
        auftrag.error_message = ''
        auftrag.fps = cls.bildrate(auftrag)
        auftrag.save()
        if pid_datei is not None:
            cls.pid_weg(pid_datei)
        logger.info('Job %s: BVH gefunden, als fertig vermerkt', auftrag.id)

    @classmethod
    def als_gescheitert(cls, auftrag, grund=None):
        auftrag.status = 'failed'
        auftrag.error_message = grund or cls.NEUSTART_HINWEIS
        auftrag.save()
        logger.warning('Job %s: als fehlgeschlagen vermerkt', auftrag.id)

    @classmethod
    def bildrate(cls, auftrag):
        """Bildrate aus dem Video — siehe `Videobildrate`.

        Bleibt als Durchreicher stehen: Die Klassenkonstante
        `VORGABE_BILDRATE` ist Teil der bisherigen Schnittstelle.
        """
        return Videobildrate.zu(auftrag)

    @staticmethod
    def pid_weg(pid_datei):
        try:
            Path(pid_datei).unlink()
        except (FileNotFoundError, OSError):
            # stumm gewollt: Die Datei ist eine Notiz, kein Ergebnis.
            logger.debug('uebergangen', exc_info=True)

    @staticmethod
    def logauszug(logdatei, zeichen=500):
        """Das Ende der Logdatei als Fehlergrund — der Nutzer soll ihn sehen."""
        try:
            text = Path(logdatei).read_text(encoding='utf-8', errors='replace')
        except OSError:
            logger.debug('Pipeline-Log %s nicht lesbar', logdatei, exc_info=True)
            return 'Pipeline finished but no BVH output was found.'
        return ('Pipeline finished but no BVH output found.\n%s'
                % text[-zeichen:])
