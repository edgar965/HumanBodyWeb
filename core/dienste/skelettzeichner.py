# -*- coding: utf-8 -*-
"""Skelettzeichner — Gelenke und Linien in ein Videobild malen.

Herausgelöst aus `skelettvideo._render_video_with_skeleton` (97 Zeilen). Das
Zeichnen ist der eine Teil, der ohne Video prüfbar ist: Ein Bild, ein Satz
Punkte, ein erwartetes Ergebnis.

ZWEI REGELN, DIE HIER STECKEN
=============================
* **Nur sichere Punkte.** Unter `MINDESTSICHERHEIT` (0,3) wird nichts gemalt.
  MediaPipe liefert für verdeckte Gelenke Positionen mit niedriger Sicherheit —
  gezeichnet ergäbe das Linien quer durchs Bild.
* **Nur Punkte im Bild.** Eine Linie, deren Ende außerhalb liegt, wird gar nicht
  gezeichnet. Das ist absichtlich streng: Ein Arm, der halb aus dem Bild ragt,
  soll keine Linie zum Bildrand ziehen, die es im Skelett nicht gibt.
"""

from ..daten.gelenknamen import Gelenknamen


class Skelettzeichner:
    """Malt ein 2D-Skelett in ein OpenCV-Bild (BGR, Pixelkoordinaten)."""

    MINDESTSICHERHEIT = 0.3
    GELENKFARBE = (0, 200, 255)
    GELENKRADIUS = 3

    def __init__(self, verbindungen=None, farbe=(0, 255, 0), dicke=2):
        self.verbindungen = (verbindungen if verbindungen is not None
                             else Gelenknamen.alle_verbindungen())
        self.farbe = farbe
        self.dicke = dicke

    def zeichnen(self, bild, punkte):
        import cv2
        hoehe, breite = bild.shape[:2]
        for name_a, name_b in self.verbindungen:
            a, b = punkte.get(name_a), punkte.get(name_b)
            if not self._sichtbar(a, breite, hoehe) or \
                    not self._sichtbar(b, breite, hoehe):
                continue
            cv2.line(bild, (int(a[0]), int(a[1])), (int(b[0]), int(b[1])),
                     self.farbe, self.dicke, cv2.LINE_AA)
        for punkt in punkte.values():
            if self._sichtbar(punkt, breite, hoehe):
                cv2.circle(bild, (int(punkt[0]), int(punkt[1])),
                           self.GELENKRADIUS, self.GELENKFARBE, -1, cv2.LINE_AA)
        return bild

    def _sichtbar(self, punkt, breite, hoehe):
        """Punkt vorhanden, sicher genug und im Bild."""
        if not punkt or punkt[2] <= self.MINDESTSICHERHEIT:
            return False
        return 0 <= punkt[0] < breite and 0 <= punkt[1] < hoehe
