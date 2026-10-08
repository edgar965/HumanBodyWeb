# -*- coding: utf-8 -*-
"""Blendimportrand — der Saum um die Fehlstellen einer gebackenen Kachel (08.10.2026).

Wo kein Strahl das Original trifft, ist das gebackene Bild schwarz; `Blendimporthaut.nacharbeiten` ersetzt diese Fehlstellen
(`leer`: Helligkeit ≤ 6). Der Rand dazwischen ist KEIN reines Schwarz: Blender mischt am Inselrand die letzte Farbe mit dem
Schwarz der Umgebung, das JPEG verwischt es um wenige Stufen weiter. Solche Randpixel liegen über der Schwelle und blieben als
dünne dunkle Linie stehen — gesehen 08.10.2026 in Kachel 1002 um die Inseln der Scham (schwarze Konturen im 8K-Bild, im
Browser als Nähte um die Schamlippen). Hier bekommen die Pixel im Saum (`RAND_PX` um jede Fehlstelle) das gewichtete Mittel der
gültigen Pixel daneben; die Fehlstelle selbst füllt weiter die Kachel von „Mesh to 3D".
"""

import numpy as np

__all__ = ['Blendimportrand']


class Blendimportrand:
    #: So viele Pixel um eine Fehlstelle gelten als Saum.
    RAND_PX = 2

    @classmethod
    def saum(cls, leer, rand=None):
        """Maske der Saumpixel: höchstens `rand` Pixel neben einer Fehlstelle, selbst keine."""
        from scipy import ndimage

        rand = cls.RAND_PX if rand is None else int(rand)
        if rand <= 0 or not leer.any():
            return np.zeros_like(leer)
        return ndimage.binary_dilation(leer, iterations=rand) & ~leer

    @classmethod
    def schliessen(cls, farbe, leer, rand=None):
        """`(neue Farbe, Saummaske)` — `farbe` (H, W, 3) uint8; die Saumpixel werden aus den gültigen Pixeln in ihrer Nähe
        (Gaußgewicht, Radius `rand`) gemittelt; die Eingabe bleibt unverändert, `leer` selbst wird nicht angefasst."""
        from scipy import ndimage

        rand = cls.RAND_PX if rand is None else int(rand)
        saum = cls.saum(leer, rand)
        if not saum.any():
            return farbe, saum
        kern = ~(saum | leer)
        gewicht = ndimage.gaussian_filter(kern.astype(np.float32), rand)
        ok = saum & (gewicht > 1e-3)
        neu = farbe.copy()
        for k in range(farbe.shape[2]):
            summe = ndimage.gaussian_filter(farbe[..., k].astype(np.float32) * kern, rand)
            neu[..., k][ok] = np.clip(summe[ok] / gewicht[ok], 0, 255).astype(farbe.dtype)
        return neu, saum
