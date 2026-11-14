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

import torch
from KoerperKI_alle.torchfeld import Torchfeld
from PIL import Image
from .iterationsbild import Iterationsbild

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

    aus_vorlage = classmethod(Iterationsbild.aus_vorlage.__func__)          # dieselbe Rechnung wie `Iterationsbild.aus_vorlage` (bis 08.11.2026 eine Kopie hier)

    aus_render = classmethod(Iterationsbild.aus_render.__func__)          # dieselbe Rechnung wie `Iterationsbild.aus_render` (bis 08.11.2026 eine Kopie hier)

    @classmethod
    def _normieren(cls, rgb, maske, groesse=None):
        breite, hoehe = groesse or (cls.BREITE, cls.HOEHE)
        zeilen = torch.flatten(maske.sum(axis=1) >= cls.MINDESTENS).nonzero()[:, 0]
        if len(zeilen) < 2:
            return cls(torch.zeros((hoehe, breite, 3), dtype=torch.float32, device='cuda'), torch.zeros((hoehe, breite), dtype=torch.bool, device='cuda'))
        y0, y1 = int(zeilen[0]), int(zeilen[-1]) + 1
        rumpf = maske[y0 + int(0.3 * (y1 - y0)) : y0 + int(0.7 * (y1 - y0))]
        spalten = torch.flatten(rumpf.sum(axis=0) > 0).nonzero()[:, 0]
        gewichte = rumpf.sum(axis=0)[spalten]
        cx = float(Torchfeld.average(spalten, weights=gewichte)) if len(spalten) else maske.shape[1] / 2
        massstab = hoehe * (1 - 2 * cls.RAND) / (y1 - y0)
        links = cx - breite / 2 / massstab
        oben = y0 - cls.RAND * hoehe / massstab
        kasten = (links, oben, links + breite / massstab, oben + hoehe / massstab)
        groesse = (breite, hoehe)
        farbe = Image.fromarray(Torchfeld.roh(Torchfeld.astype(Torchfeld.clip(rgb, 0, 1) * 255, torch.uint8))).transform(
            groesse, Image.EXTENT, kasten, resample=Image.BILINEAR
        )
        ziel = Image.fromarray(Torchfeld.roh(Torchfeld.astype(maske * 255, torch.uint8))).transform(
            groesse, Image.EXTENT, kasten, resample=Image.BILINEAR
        )
        return cls(Torchfeld.feld(farbe, dtype=torch.float32) / 255.0, Torchfeld.feld(ziel) > 127)

    def aufgefuellt(self, schritte=200, erosion=4):
        """Die Farbe, mit nach außen verlängertem Rand: Bildpunkte außerhalb der Figur bekommen die mittlere
        Farbe der schon gefüllten Nachbarn, Runde um Runde. Für die Fotoprojektion
        (`effekte/blender/kostuem/fototextur.py`): Wo das Modell über den Umriss der Vorlage hinausragt, soll
        dort nicht das Weiß des Hintergrunds auf dem Stoff landen, sondern die Farbe des nächsten Figurrands.
        Der äußerste Rand der Figur (`erosion` Bildpunkte: Schimmer, JPEG-Rauschen, Antialiasing — fast weiß,
        aber „Figur" nach der Schwelle) zählt nicht als Quelle; sonst wäre die Verlängerung hell, und ein
        Stab, der neben dem Umriss der Vorlage sitzt, würde weiß. → (Höhe, Breite, 3) float 0…1."""
        kern = Torchfeld.kopie(self.maske)
        for _ in range(erosion):
            kern = (
                kern
                & torch.roll(kern, 1, dims=0)
                & torch.roll(kern, -1, dims=0)
                & torch.roll(kern, 1, dims=1)
                & torch.roll(kern, -1, dims=1)
            )
        if kern.sum() < 50:  # winzige Figur: keine Erosion
            kern = Torchfeld.kopie(self.maske)
        farbe = Torchfeld.astype(torch.where(kern[..., None], self.farbe, 0.0), torch.float32)
        gefuellt = Torchfeld.kopie(kern)
        for _ in range(schritte):
            if gefuellt.all():
                break
            summe = torch.zeros_like(farbe)
            anzahl = torch.zeros(gefuellt.shape, dtype=torch.float32, device='cuda')
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dy == 0 and dx == 0:
                        continue
                    summe += torch.roll(torch.roll(farbe * gefuellt[..., None], dy, dims=0), dx, dims=1)
                    anzahl += torch.roll(torch.roll(Torchfeld.astype(gefuellt, torch.float32), dy, dims=0), dx, dims=1)
            neu = (~gefuellt) & (anzahl > 0)
            farbe[neu] = summe[neu] / anzahl[neu][:, None]
            gefuellt |= neu
        return torch.where(gefuellt[..., None], farbe, self.farbe)

    als_bild = Iterationsbild.als_bild          # dieselbe Rechnung wie `Iterationsbild.als_bild` (bis 08.11.2026 eine Kopie hier)
