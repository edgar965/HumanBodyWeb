# -*- coding: utf-8 -*-
"""Persongrenzen — wo im Foto die Person anfängt und aufhört.

Aus `Fotoausrichtung.automatisch` herausgelöst (17.08.2026). Dort standen vier
Werte (`person_top`, `person_bottom`, `person_cx`, `person_detected`) als lose
Variablen und wurden durch zwei Prüfungen und den Rückfallzweig getragen —
Kriterium 10.

WIE ERKANNT WIRD, UND WARUM SO GROB
===================================
Die Fotos dieser Kette sind Aufnahmen vor hellem Grund. Alles unter dem
Schwellwert 240 gilt als „nicht Hintergrund"; von den gefundenen Zeilen werden
das 1. und das 99. Perzentil genommen, nicht Minimum und Maximum — ein einzelnes
dunkles Pixel am Bildrand (Schatten, Staub, Zeitstempel) würde die Grenze sonst
über das ganze Bild ziehen.

Weniger als `MIND_PIXEL` dunkle Punkte heißen „keine Person gefunden". Dann
gelten die Bildgrenzen, und die Prüfung in `Fotoausrichtung` fällt auf ihren
groben Maßstab zurück.
"""

import logging

import numpy as np

logger = logging.getLogger('core')


class Persongrenzen:
    """Oberkante, Unterkante und Mitte der Person — oder das ganze Bild."""

    #: Helligkeit, ab der ein Pixel als Hintergrund gilt.
    SCHWELLE = 240

    #: So viele dunkle Pixel müssen es sein, damit es eine Person ist.
    MIND_PIXEL = 100

    #: Perzentile statt Minimum/Maximum — gegen einzelne Störpixel.
    UNTEN_PERZENTIL = 1
    OBEN_PERZENTIL = 99

    def __init__(self, oben, unten, mitte_x, erkannt):
        self.oben = oben
        self.unten = unten
        self.mitte_x = mitte_x
        self.erkannt = erkannt

    @property
    def hoehe(self):
        return self.unten - self.oben

    @property
    def mitte_y(self):
        return (self.oben + self.unten) / 2.0

    @classmethod
    def ganzes_bild(cls, img_w, img_h):
        return cls(0.0, float(img_h), img_w / 2.0, False)

    @classmethod
    def aus_foto(cls, pfad, img_w, img_h):
        """Grenzen aus dem Foto — ohne Foto oder ohne Fund das ganze Bild."""
        if not pfad:
            return cls.ganzes_bild(img_w, img_h)
        try:
            import cv2
            foto = cv2.imread(pfad)
            if foto is None:
                return cls.ganzes_bild(img_w, img_h)
            grau = cv2.cvtColor(foto, cv2.COLOR_BGR2GRAY)
            _, maske = cv2.threshold(grau, cls.SCHWELLE, 255,
                                     cv2.THRESH_BINARY_INV)
            zeilen, spalten = np.where(maske > 0)
        except Exception:                                        # noqa: BLE001
            logger.debug('Personengrenzen nicht bestimmbar: %s', pfad,
                         exc_info=True)
            return cls.ganzes_bild(img_w, img_h)
        if len(zeilen) <= cls.MIND_PIXEL:
            return cls.ganzes_bild(img_w, img_h)
        return cls(float(np.percentile(zeilen, cls.UNTEN_PERZENTIL)),
                   float(np.percentile(zeilen, cls.OBEN_PERZENTIL)),
                   float(np.median(spalten)), True)
