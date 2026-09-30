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
    def aus_vorlage(cls, pfad, groesse=None):
        """`groesse`: (Breite, Höhe) der Fläche — ohne die Vorgabe 128 × 192 der Note."""
        with Image.open(pfad) as bild:
            rgb = np.asarray(bild.convert('RGB'), dtype=np.float32)
        maske = (765.0 - rgb.sum(axis=2)) > cls.WEISS_SCHWELLE
        return cls._normieren(rgb / 255.0, maske, groesse)

    @classmethod
    def aus_render(cls, pfad, groesse=None):
        with Image.open(pfad) as bild:
            rgba = np.asarray(bild.convert('RGBA'), dtype=np.float32) / 255.0
        return cls._normieren(rgba[..., :3], rgba[..., 3] > 0.5, groesse)

    @classmethod
    def _normieren(cls, rgb, maske, groesse=None):
        breite, hoehe = groesse or (cls.BREITE, cls.HOEHE)
        zeilen = np.flatnonzero(maske.sum(axis=1) >= cls.MINDESTENS)
        if len(zeilen) < 2:
            return cls(np.zeros((hoehe, breite, 3), np.float32), np.zeros((hoehe, breite), bool))
        y0, y1 = int(zeilen[0]), int(zeilen[-1]) + 1
        rumpf = maske[y0 + int(0.3 * (y1 - y0)) : y0 + int(0.7 * (y1 - y0))]
        spalten = np.flatnonzero(rumpf.sum(axis=0) > 0)
        gewichte = rumpf.sum(axis=0)[spalten]
        cx = float(np.average(spalten, weights=gewichte)) if len(spalten) else maske.shape[1] / 2
        massstab = hoehe * (1 - 2 * cls.RAND) / (y1 - y0)
        links = cx - breite / 2 / massstab
        oben = y0 - cls.RAND * hoehe / massstab
        kasten = (links, oben, links + breite / massstab, oben + hoehe / massstab)
        groesse = (breite, hoehe)
        farbe = Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8)).transform(
            groesse, Image.EXTENT, kasten, resample=Image.BILINEAR
        )
        ziel = Image.fromarray((maske * 255).astype(np.uint8)).transform(
            groesse, Image.EXTENT, kasten, resample=Image.BILINEAR
        )
        return cls(np.asarray(farbe, np.float32) / 255.0, np.asarray(ziel) > 127)

    def aufgefuellt(self, schritte=200, erosion=4):
        """Die Farbe, mit nach außen verlängertem Rand: Bildpunkte außerhalb der Figur bekommen die mittlere
        Farbe der schon gefüllten Nachbarn, Runde um Runde. Für die Fotoprojektion
        (`effekte/blender/kostuem/fototextur.py`): Wo das Modell über den Umriss der Vorlage hinausragt, soll
        dort nicht das Weiß des Hintergrunds auf dem Stoff landen, sondern die Farbe des nächsten Figurrands.
        Der äußerste Rand der Figur (`erosion` Bildpunkte: Schimmer, JPEG-Rauschen, Antialiasing — fast weiß,
        aber „Figur" nach der Schwelle) zählt nicht als Quelle; sonst wäre die Verlängerung hell, und ein
        Stab, der neben dem Umriss der Vorlage sitzt, würde weiß. → (Höhe, Breite, 3) float 0…1."""
        kern = self.maske.copy()
        for _ in range(erosion):
            kern = (
                kern
                & np.roll(kern, 1, axis=0)
                & np.roll(kern, -1, axis=0)
                & np.roll(kern, 1, axis=1)
                & np.roll(kern, -1, axis=1)
            )
        if kern.sum() < 50:  # winzige Figur: keine Erosion
            kern = self.maske.copy()
        farbe = np.where(kern[..., None], self.farbe, 0.0).astype(np.float32)
        gefuellt = kern.copy()
        for _ in range(schritte):
            if gefuellt.all():
                break
            summe = np.zeros_like(farbe)
            anzahl = np.zeros(gefuellt.shape, np.float32)
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dy == 0 and dx == 0:
                        continue
                    summe += np.roll(np.roll(farbe * gefuellt[..., None], dy, axis=0), dx, axis=1)
                    anzahl += np.roll(np.roll(gefuellt.astype(np.float32), dy, axis=0), dx, axis=1)
            neu = (~gefuellt) & (anzahl > 0)
            farbe[neu] = summe[neu] / anzahl[neu][:, None]
            gefuellt |= neu
        return np.where(gefuellt[..., None], farbe, self.farbe)

    def als_bild(self, hintergrund=(255, 255, 255)):
        """Farbe auf Hintergrund — für die Vergleichstafel."""
        grund = np.empty_like(self.farbe)
        grund[:] = np.asarray(hintergrund, np.float32) / 255.0
        bild = np.where(self.maske[..., None], self.farbe, grund)
        return Image.fromarray((bild * 255).astype(np.uint8))
