# -*- coding: utf-8 -*-
"""Kostuembild — Vorlage und Render auf dieselbe Fläche bringen, damit man sie Pixel für Pixel vergleichen
kann.

Beide werden an der Figur ausgerichtet, nicht am Bildrand: Höhe = vom höchsten Punkt (Hutspitze) bis zu den
Füßen, waagerecht auf den Schwerpunkt des RUMPFBANDS (30–70 % der Figurhöhe) — ein dünner Stab verschiebt dort
kaum etwas, eine Rahmenmitte über Stab und Krempe dagegen schon. So spielt es keine Rolle, wie groß die Figur
im Vorlagenbild ist oder wo die Kamera im Render stand.

Vorlage: Figur auf WEISSEM Grund (der Bogen `Vorlage.jpeg`, geschnitten von `vorlage_teilen.py`) — Figur ist,
was merklich vom Weiß abweicht (Summe der drei Kanäle > 40 unter 765; JPEG-Rauschen liegt darunter, der
hellgraue Bart darüber). Render: der Alphakanal (`film_transparent`).
"""

import numpy as np
from PIL import Image

__all__ = ['Kostuembild']


class Kostuembild:
    BREITE, HOEHE = 128, 192
    #: Rand über dem höchsten Punkt, als Anteil der Flächenhöhe.
    RAND = 0.03
    WEISS_SCHWELLE = 40
    #: Eine Zeile/Spalte gehört zur Figur, wenn so viele Pixel darin Figur sind (einzelne Ausreißer zählen
    # nicht).
    MINDESTENS = 3

    def __init__(self, farbe, maske):
        #: (HOEHE, BREITE, 3) float 0…1 und (HOEHE, BREITE) bool.
        self.farbe = farbe
        self.maske = maske

    @classmethod
    def aus_vorlage(cls, pfad):
        with Image.open(pfad) as bild:
            rgb = np.asarray(bild.convert('RGB'), dtype=np.float32)
        maske = (765.0 - rgb.sum(axis=2)) > cls.WEISS_SCHWELLE
        return cls._normieren(rgb / 255.0, maske)

    @classmethod
    def aus_render(cls, pfad):
        with Image.open(pfad) as bild:
            rgba = np.asarray(bild.convert('RGBA'), dtype=np.float32) / 255.0
        return cls._normieren(rgba[..., :3], rgba[..., 3] > 0.5)

    @classmethod
    def _normieren(cls, rgb, maske):
        zeilen = np.flatnonzero(maske.sum(axis=1) >= cls.MINDESTENS)
        if len(zeilen) < 2:
            return cls(
                np.zeros((cls.HOEHE, cls.BREITE, 3), np.float32), np.zeros((cls.HOEHE, cls.BREITE), bool)
            )
        y0, y1 = int(zeilen[0]), int(zeilen[-1]) + 1
        rumpf = maske[y0 + int(0.3 * (y1 - y0)) : y0 + int(0.7 * (y1 - y0))]
        spalten = np.flatnonzero(rumpf.sum(axis=0) > 0)
        gewichte = rumpf.sum(axis=0)[spalten]
        cx = float(np.average(spalten, weights=gewichte)) if len(spalten) else maske.shape[1] / 2
        massstab = cls.HOEHE * (1 - 2 * cls.RAND) / (y1 - y0)
        links = cx - cls.BREITE / 2 / massstab
        oben = y0 - cls.RAND * cls.HOEHE / massstab
        kasten = (links, oben, links + cls.BREITE / massstab, oben + cls.HOEHE / massstab)
        groesse = (cls.BREITE, cls.HOEHE)
        farbe = Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8)).transform(
            groesse, Image.EXTENT, kasten, resample=Image.BILINEAR
        )
        ziel = Image.fromarray((maske * 255).astype(np.uint8)).transform(
            groesse, Image.EXTENT, kasten, resample=Image.BILINEAR
        )
        return cls(np.asarray(farbe, np.float32) / 255.0, np.asarray(ziel) > 127)

    def als_bild(self, hintergrund=(255, 255, 255)):
        """Farbe auf Hintergrund — für die Vergleichstafel."""
        grund = np.empty_like(self.farbe)
        grund[:] = np.asarray(hintergrund, np.float32) / 255.0
        bild = np.where(self.maske[..., None], self.farbe, grund)
        return Image.fromarray((bild * 255).astype(np.uint8))
