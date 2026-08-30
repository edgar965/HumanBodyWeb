# -*- coding: utf-8 -*-
"""Skelettvideo — Video mit Skelett-Überlagerung oder Skelett auf Schwarz.

UMBAU 17.08.2026
================
`_render_video_with_skeleton` war 97 Zeilen und tat vier Dinge: Zielpfad und
Zwischenspeicher bestimmen, die Punktquelle wählen (BVH-Projektion oder
2D-Erkennung), Bild für Bild zeichnen, schreiben. Das Zeichnen liegt jetzt in
`skelettzeichner.Skelettzeichner` (ohne Video prüfbar), der Ablauf in `Skelettfilm`.

DIE BILDZUORDNUNG IST DER KNIFFLIGE TEIL
========================================
Video und Bewegungsdaten haben nicht gleich viele Bilder. Zugeordnet wird
VERHÄLTNISMÄSSIG (`vi / (videobilder-1) * (punkte-1)`) — genauso rechnet die
Three.js-Wiedergabe (`currentTime / duration * clipDuration`). Wer hier
stattdessen 1:1 zählt, bekommt ein Skelett, das dem Video vorausläuft oder
nachhinkt, und sucht den Fehler in der Kamera.
"""

import logging
import os
from pathlib import Path

from django.conf import settings

from .bvh_projektion import Bvhprojektion
from .keypoints_quellen import Keypointsquellen
from .skelettzeichner import Skelettzeichner
from ..daten.gelenknamen import Gelenknamen

logger = logging.getLogger('core')

#: Die Kanten des gezeichneten Skeletts — aus `Gelenknamen`, nicht hier.
#:
#: Vorher stand hier jede Kante ZWEIMAL: einmal mit `midhip`/`nose` (OpenPose)
#: und einmal mit `hip`/`head` (MocapNET/MediaPipe). Seit `Gelenkquelle` die
#: OpenPose-Namen beim Lesen umschreibt, gibt es nur noch eine Schreibweise
#: (Kriterium 7: keine verschiedenen Namen für dasselbe).
_BODY_CONNECTIONS = Gelenknamen.alle_verbindungen()


class Skelettfilm:
    """Schreibt das Video mit Skelett — und nutzt eine fertige Datei wieder."""

    UEBERLAGERUNG = (0, 255, 0)
    NUR_RIG = (255, 255, 255)
    DICKE = 3
    VORGABE_FPS = 30

    def __init__(self, job, ueberlagern=True):
        self.job = job
        self.ueberlagern = ueberlagern
        self.ordner = Path(settings.MEDIA_ROOT) / 'output' / str(job.id)
        self.video = Path(settings.MEDIA_ROOT) / str(job.video_file)

    # ------------------------------------------------------------------ Ablauf

    def erzeugen(self):
        """Pfad zum Video — oder `None`, wenn es keine Punkte gibt."""
        ziel = self.zielpfad()
        if ziel.exists():
            return ziel
        breite, hoehe = self._masse()
        punkte, verbindungen, masse = self._punkte(breite, hoehe)
        if not punkte:
            return None
        return self._schreiben(ziel, punkte, verbindungen, *masse)

    def zielpfad(self):
        """`<pipeline>_<name>_overlay.mp4` bzw. `…_rig_only[_bvh].mp4`."""
        zusatz = '_overlay' if self.ueberlagern else '_rig_only'
        if self._aus_bvh():
            zusatz += '_bvh'
        self.ordner.mkdir(parents=True, exist_ok=True)
        return self.ordner / ('%s_%s%s.mp4' % (self.job.pipeline,
                                               Path(self.job.name).stem, zusatz))

    def _aus_bvh(self):
        """Nur für das Rig auf Schwarz und nur bei v4.

        Für die Überlagerung braucht es die 2D-Erkennung: Nur sie sitzt auf
        denselben Bildpunkten wie das Video. Die BVH-Projektion hat ihre eigene
        Kamera und läge daneben.
        """
        return (not self.ueberlagern and self.job.pipeline == 'v4'
                and self.job.bvh_file and os.path.exists(self.job.bvh_file))

    # ---------------------------------------------------------------- Bausteine

    def _masse(self):
        import cv2
        film = cv2.VideoCapture(str(self.video))
        masse = (int(film.get(cv2.CAP_PROP_FRAME_WIDTH)),
                 int(film.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        film.release()
        return masse

    def _punkte(self, breite, hoehe):
        """`(punkte je Bild, Verbindungen, (breite, hoehe))`.

        Erst die BVH-Projektion (vollständiges v4-Rig mit eigenen Kanten), dann
        die 2D-Erkennung. Scheitert die Projektion, ist das kein Abbruch — das
        Video bekommt dann das 2D-Skelett.
        """
        if self._aus_bvh():
            try:
                punkte, kanten = Bvhprojektion.punkte(self.job.bvh_file,
                                                      breite, hoehe)
                if punkte and kanten:
                    return punkte, kanten, (breite, hoehe)
            except Exception:                                      # noqa: BLE001
                logger.warning('BVH-Projektion fehlgeschlagen — kein Rig im Video',
                               exc_info=True)
        punkte, masse = Keypointsquellen.in_pixeln(self.job)
        return punkte, _BODY_CONNECTIONS, masse

    def _schreiben(self, ziel, punkte, verbindungen, breite, hoehe):
        import cv2
        import numpy as np
        film = cv2.VideoCapture(str(self.video))
        bildrate = film.get(cv2.CAP_PROP_FPS) or (self.job.fps or self.VORGABE_FPS)
        anzahl = int(film.get(cv2.CAP_PROP_FRAME_COUNT))
        if not self.ueberlagern:
            film.release()
            film = None
        zeichner = Skelettzeichner(
            verbindungen,
            farbe=self.UEBERLAGERUNG if self.ueberlagern else self.NUR_RIG,
            dicke=self.DICKE)
        schreiber = cv2.VideoWriter(str(ziel),
                                    cv2.VideoWriter_fourcc(*'mp4v'),
                                    bildrate, (breite, hoehe))
        for nummer in range(anzahl):
            bild = self._bild(film, breite, hoehe, np)
            zeichner.zeichnen(bild, punkte[self.zuordnen(nummer, anzahl,
                                                         len(punkte))])
            schreiber.write(bild)
        schreiber.release()
        if film:
            film.release()
        return ziel

    def _bild(self, film, breite, hoehe, np):
        """Das Videobild — oder Schwarz (Rig-Modus und am Dateiende)."""
        if film is not None:
            gelesen, bild = film.read()
            if gelesen:
                return bild
        return np.zeros((hoehe, breite, 3), dtype=np.uint8)

    @staticmethod
    def zuordnen(nummer, videobilder, punktbilder):
        """Videobild -> Bewegungsbild, verhältnismäßig (siehe Modul-Docstring)."""
        if videobilder <= 1 or punktbilder <= 1:
            return 0
        stelle = int(nummer / (videobilder - 1) * (punktbilder - 1))
        return max(0, min(stelle, punktbilder - 1))
