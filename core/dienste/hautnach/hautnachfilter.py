# -*- coding: utf-8 -*-
"""Hautnachfilter — die Filter der Nacharbeit einer Haut-Kachel auf der GPU (NVIDIA Warp): Gauß-Filter und Dilatation, so wie `scipy.ndimage` sie auf der CPU rechnet.

    f = Hautnachfilter('cuda:0')
    glatt = f.gauss(feld, sigma)            # `scipy.ndimage.gaussian_filter(feld, sigma)`: float32 (h, w) auf der GPU → float32 (h, w) auf der GPU
    nah = f.dilatation(maske, schritte)     # `scipy.ndimage.binary_dilation(maske, iterations=schritte)` (4er-Nachbarschaft): uint8 (h, w) → uint8 (h, w)

Die Felder bleiben auf der GPU (`wp.array`); die Aufrufer holen sie erst am Ende der Nacharbeit. Maße des Gauß-Kerns wie scipy: Halbbreite `int(4·σ + 0,5)`, Gewichte `exp(−x²/2σ²)` auf Summe 1,
Rand gespiegelt (`mode='reflect'`: d c b a | a b c d | d c b a).
"""

import numpy as np
import warp as wp

__all__ = ['Hautnachfilter']


@wp.func
def _spiegel(i: int, n: int) -> int:
    """Index außerhalb `0 … n−1` gespiegelt (`scipy` `reflect`: der Randwert wird wiederholt)."""
    r = i
    while r < 0 or r >= n:
        if r < 0:
            r = -r - 1
        if r >= n:
            r = 2 * n - r - 1
    return r


@wp.kernel
def _gauss_zeilen(quelle: wp.array2d(dtype=wp.float32), kern: wp.array(dtype=wp.float32), radius: int, aus: wp.array2d(dtype=wp.float32)):
    """Entlang der Spalten (Achse 1) glätten."""
    y, x = wp.tid()
    b = quelle.shape[1]
    s = float(0.0)
    for k in range(-radius, radius + 1):
        s += kern[k + radius] * quelle[y, _spiegel(x + k, b)]
    aus[y, x] = s


@wp.kernel
def _gauss_spalten(quelle: wp.array2d(dtype=wp.float32), kern: wp.array(dtype=wp.float32), radius: int, aus: wp.array2d(dtype=wp.float32)):
    """Entlang der Zeilen (Achse 0) glätten."""
    y, x = wp.tid()
    h = quelle.shape[0]
    s = float(0.0)
    for k in range(-radius, radius + 1):
        s += kern[k + radius] * quelle[_spiegel(y + k, h), x]
    aus[y, x] = s


@wp.kernel
def _dilatieren(quelle: wp.array2d(dtype=wp.uint8), schritte: int, aus: wp.array2d(dtype=wp.uint8)):
    """Eine Raute vom Radius `schritte` (L1-Abstand): so weit reicht `schritte`-mal die Dilatation mit dem Kreuz."""
    y, x = wp.tid()
    h = quelle.shape[0]
    b = quelle.shape[1]
    gesetzt = int(0)
    for dy in range(-schritte, schritte + 1):
        yy = y + dy
        if yy >= 0 and yy < h:
            rest = schritte - wp.abs(dy)
            for dx in range(-rest, rest + 1):
                xx = x + dx
                if xx >= 0 and xx < b:
                    if quelle[yy, xx] != wp.uint8(0):
                        gesetzt = 1
    aus[y, x] = wp.uint8(gesetzt)


class Hautnachfilter:
    def __init__(self, geraet='cuda:0'):
        self.geraet = geraet
        wp.init()

    @staticmethod
    def kern(sigma):
        """Der Gauß-Kern wie `scipy.ndimage.gaussian_filter1d` ihn baut (Halbbreite `int(4σ + 0,5)`, Summe 1)."""
        radius = int(4.0 * float(sigma) + 0.5)
        x = np.arange(-radius, radius + 1, dtype=np.float64)
        k = np.exp(-0.5 / (float(sigma) ** 2) * x * x)
        return (k / k.sum()).astype(np.float32), radius

    def gauss(self, feld, sigma):
        """`feld`: `wp.array2d(float32)`; gibt ein neues Feld zurück."""
        k, radius = self.kern(sigma)
        kern = wp.array(k, dtype=wp.float32, device=self.geraet)
        zwischen = wp.empty_like(feld)
        aus = wp.empty_like(feld)
        wp.launch(_gauss_zeilen, dim=feld.shape, inputs=[feld, kern, radius, zwischen], device=self.geraet)
        wp.launch(_gauss_spalten, dim=feld.shape, inputs=[zwischen, kern, radius, aus], device=self.geraet)
        return aus

    def dilatation(self, maske, schritte):
        """`maske`: `wp.array2d(uint8)` (0/1); `schritte` ≥ 1."""
        aus = wp.empty_like(maske)
        wp.launch(_dilatieren, dim=maske.shape, inputs=[maske, int(schritte), aus], device=self.geraet)
        return aus

    def feld(self, a, dtype=wp.float32):
        """Ein numpy-Feld auf die GPU."""
        return wp.array(np.ascontiguousarray(a), dtype=dtype, device=self.geraet)
