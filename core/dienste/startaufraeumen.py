# -*- coding: utf-8 -*-
"""Startaufraeumen — Aufträge einsammeln, die einen Serverneustart erlebt haben.

Herausgelöst aus `core/apps.CoreConfig.ready` (92 Zeilen). In einer `ready()`
gehört möglichst wenig: Sie läuft beim Start jedes Serverprozesses, und was dort
scheitert, verhindert den Start.

DREI FÄLLE, IN DIESER REIHENFOLGE
=================================
1. **Es gibt schon eine BVH.** Der Unterprozess ist während des Neustarts fertig
   geworden. Der Auftrag gilt als fertig — die Datei ist das Ergebnis, unabhängig
   davon, ob noch ein Prozess lebt.
2. **Die PID lebt noch.** Der Lauf schreibt weiter in seine Logdatei (deshalb
   schreiben die SMPL-Pipelines in eine Datei und nicht in eine Pipe). Ein Faden
   nimmt die Beobachtung wieder auf.
3. **Sonst.** Der Auftrag gilt als gescheitert, mit einem Hinweis, der zum
   Neustart-Knopf passt.

Reihenfolge ist wichtig: Wer erst die PID prüft, hängt einen Beobachter an einen
Prozess, dessen Arbeit längst auf der Platte liegt — und der Auftrag bliebe auf
„läuft" stehen, bis der Beobachter aufgibt.
"""

import glob
import logging
import os
import threading
from pathlib import Path

from django.conf import settings

logger = logging.getLogger('core')


class Startaufraeumen:
    """Verwaiste Aufträge nach einem Serverstart einordnen."""

    #: Zustände, die „läuft gerade" bedeuten.
    LAUFEND = ('detecting_2d', 'openpose', 'openpose_csv', 'mediapipe',
               'lifting_3d', 'mocapnet', 'v4_processing', 'processing')
    #: Kleiner heisst: die BVH ist ein Rumpf ohne Bewegung.
    MINDESTGROESSE = 100
    VORGABE_BILDRATE = 30.0
    NEUSTART_HINWEIS = ('Server was restarted while job was running. '
                        'Click "Neu starten" to retry.')

    def durchgehen(self):
        """Alle verwaisten Aufträge einordnen; liefert die Zahl je Fall."""
        from core.models import BVHJob
        zaehler = {'fertig': 0, 'weiter': 0, 'gescheitert': 0}
        for auftrag in BVHJob.objects.filter(status__in=self.LAUFEND):
            zaehler[self._einordnen(auftrag)] += 1
        return zaehler

    def _einordnen(self, auftrag):
        ordner = Path(settings.MEDIA_ROOT) / 'output' / str(auftrag.id)
        fertige = self._bvh(ordner)
        if fertige:
            self._als_fertig(auftrag, fertige, ordner / 'pipeline.pid')
            return 'fertig'
        if self._weiter_beobachten(auftrag, ordner / 'pipeline.pid'):
            return 'weiter'
        self._als_gescheitert(auftrag)
        return 'gescheitert'

    # ------------------------------------------------------------------ Fall 1

    def _bvh(self, ordner):
        """Die erste BVH im Ordner, die mehr als einen Rumpf enthält."""
        for datei in glob.glob(str(ordner / '*.bvh')):
            if os.path.getsize(datei) > self.MINDESTGROESSE:
                return datei
        return None

    def _als_fertig(self, auftrag, bvh, pid_datei):
        auftrag.bvh_file = bvh
        auftrag.status = 'complete'
        auftrag.progress = 100
        auftrag.progress_detail = 'Complete (recovered after restart)'
        auftrag.error_message = ''
        auftrag.fps = self._bildrate(auftrag)
        auftrag.save()
        self._pid_weg(pid_datei)
        logger.info('Job %s: BVH gefunden, als fertig vermerkt', auftrag.id)

    def _bildrate(self, auftrag):
        """Bildrate aus dem Video — die Wiedergabe braucht sie.

        Ohne sie liefe die Animation mit 30 statt der echten Rate: sichtbar zu
        schnell oder zu langsam, ohne Fehlermeldung.
        """
        try:
            import cv2
            pfad = Path(settings.MEDIA_ROOT) / str(auftrag.video_file)
            film = cv2.VideoCapture(str(pfad))
            rate = film.get(cv2.CAP_PROP_FPS) or self.VORGABE_BILDRATE
            film.release()
            return rate
        except Exception:                                          # noqa: BLE001
            logger.debug('Video-FPS nicht lesbar — Vorgabe %s wird benutzt',
                         self.VORGABE_BILDRATE, exc_info=True)
            return self.VORGABE_BILDRATE

    @staticmethod
    def _pid_weg(pid_datei):
        try:
            pid_datei.unlink()
        except (FileNotFoundError, OSError):
            # stumm gewollt: Die Datei ist eine Notiz, kein Ergebnis.
            logger.debug('uebergangen', exc_info=True)

    # ------------------------------------------------------------------ Fall 2

    def _weiter_beobachten(self, auftrag, pid_datei):
        """True, wenn ein lebender Prozess wieder beobachtet wird."""
        if not pid_datei.exists():
            return False
        from core.pipelines.prozesspruefung import Prozesspruefung
        from core.pipelines.wiederaufnahme import Wiederaufnahme
        try:
            pid = int(pid_datei.read_text().strip())
        except (ValueError, FileNotFoundError, OSError):
            logger.debug('PID-Datei %s unlesbar', pid_datei, exc_info=True)
            return False
        if not Prozesspruefung.lebt(pid):
            return False
        threading.Thread(target=Wiederaufnahme.fahren,
                         args=(str(auftrag.id), pid), daemon=True).start()
        logger.info('Job %s: PID %s laeuft noch, wird weiter beobachtet',
                    auftrag.id, pid)
        return True

    # ------------------------------------------------------------------ Fall 3

    def _als_gescheitert(self, auftrag):
        auftrag.status = 'failed'
        auftrag.error_message = self.NEUSTART_HINWEIS
        auftrag.save()
        logger.warning('Job %s: als fehlgeschlagen vermerkt (Serverneustart)',
                       auftrag.id)

    # --------------------------------------------------------- Zwischendateien

    @staticmethod
    def zwischendateien():
        """Alte Zwischendateien entfernen — einmal je Serverstart.

        `ProjektTemp.hausmeister` lief bisher NUR beim Anlegen einer neuen
        Zwischendatei (Review 15.08.2026). Wer wochenlang nur liest, behielt den
        Müll für immer.
        """
        try:
            from core.projekt_temp import ProjektTemp
            entfernt = ProjektTemp.hausmeister(erzwingen=True)
            if entfernt:
                logger.info('Start: %d alte Zwischendateien entfernt', entfernt)
            return entfernt
        except Exception:                                          # noqa: BLE001
            # Kein Abbruch: Das Aufräumen darf den Serverstart nicht kosten.
            logger.warning('Aufräumen der Zwischendateien beim Start '
                           'fehlgeschlagen', exc_info=True)
            return 0
