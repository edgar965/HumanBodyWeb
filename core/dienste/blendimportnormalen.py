# -*- coding: utf-8 -*-
"""Blendimportnormalen — falsch getroffene Stellen der gebackenen Normalenkarte flachlegen (08.10.2026).

Das Backen („Selected to Active", `blendbacken.py`) wirft je Texel der Genesis-Figur einen Strahl auf das Original. Wo beide
Flächen nicht übereinanderliegen und die Stelle konkav ist — das Dekolleté, wo sich die Brüste berühren, der Schritt, die
Fingerzwischenräume — trifft er manchmal das falsche Stück (die andere Brust, die Nachbarfläche, eine Rückseite). Die
Tangentenraum-Normale dieses Treffers steht dann weit schief zur Figur.

Gemessen am ersten Import (2026.10.08.11.28.06, `normalen_kippung.py`, Kachel 1002, Mitte des Rumpfs): Brusthöhe 1,00–1,25 m
Kippung im Mittel 6–7° (höchstens 34°), dagegen 1,30–1,40 m (Dekolleté) 26° bzw. 38° im Mittel, bis 168°, 976 Punkte über 45°.
Das beleuchtete sich als weißer „Pflaster"-Fleck (Edgar: „was ist das Pflaster zwischen den Brüsten von cute girl?"). Nägel
(Kachel 1005): Median 32°, Kopf (1001) 3,8 %, Hände (1004) 3,2 % der Texel über 30°.

Der Median der belegten Texel liegt bei 5–7° (gemessen, alle Hautkacheln). Die Grenze von 50° ist eine Setzung, kein Messwert:
Was darüber liegt, gilt als falscher Treffer, das Texel und sein Rand (`RAND_PX`) werden flach (die Normale der Figur selbst
gilt dann). Je Kachel steht der Anteil der geänderten Texel im Bericht (`normalen_flach`).
"""

import math

import numpy as np

__all__ = ['Blendimportnormalen']


class Blendimportnormalen:
    FLACH = (128, 128, 255)
    #: Grad zur flachen Normale (0, 0, 1), ab denen ein Texel als falscher Treffer gilt.
    GRENZE_GRAD = 50.0
    #: So viele Pixel um einen falschen Treffer werden mit flachgelegt (Übergang).
    RAND_PX = 3
    BAND = 512

    @classmethod
    def falsche(cls, normal, leer=None):
        """Maske (H, W) der Texel mit Kippung über `GRENZE_GRAD`, ohne `leer` — bandweise (8192² in float32 wäre ein Gigabyte)."""
        grenze = math.cos(math.radians(cls.GRENZE_GRAD))
        maske = np.zeros(normal.shape[:2], dtype=bool)
        for oben in range(0, normal.shape[0], cls.BAND):
            band = normal[oben:oben + cls.BAND].astype(np.float32) / 127.5 - 1.0
            laenge = np.linalg.norm(band, axis=2)
            maske[oben:oben + cls.BAND] = band[..., 2] < grenze * np.maximum(laenge, 1e-6)
        if leer is not None:
            maske &= ~leer
        return maske

    @classmethod
    def saeubern(cls, normal, leer=None):
        """`(neue Karte, Anteil der geänderten Texel in %)` — `normal` (H, W, 3) uint8; ändert die Eingabe nicht."""
        from scipy import ndimage

        schlecht = cls.falsche(normal, leer)
        if schlecht.any() and cls.RAND_PX:
            schlecht = ndimage.binary_dilation(schlecht, iterations=cls.RAND_PX)
        if leer is not None:
            schlecht &= ~leer
        neu = normal.copy()
        neu[schlecht] = cls.FLACH
        return neu, round(100.0 * float(schlecht.mean()), 3)
