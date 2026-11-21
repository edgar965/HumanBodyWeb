# -*- coding: utf-8 -*-
"""Hautnachfilter — die Filter der Nacharbeit einer Haut-Kachel auf der Karte: Gauß-Filter und Dilatation, so wie `scipy.ndimage` sie auf der CPU rechnet.

    f = Hautnachfilter('cuda:0')
    glatt = f.gauss(feld, sigma)            # `scipy.ndimage.gaussian_filter(feld, sigma)`: float32 (h, w) auf der Karte → float32 (h, w) auf der Karte
    nah = f.dilatation(maske, schritte)     # `scipy.ndimage.binary_dilation(maske, iterations=schritte)` (4er-Nachbarschaft): uint8 (h, w) → uint8 (h, w)

Die Felder bleiben auf der Karte (torch); die Aufrufer holen sie erst am Ende der Nacharbeit. Maße des Gauß-Kerns wie scipy: Halbbreite `int(4·σ + 0,5)`, Gewichte `exp(−x²/2σ²)` auf
Summe 1, Rand gespiegelt (`mode='reflect'`: d c b a | a b c d | d c b a). Kerne `hn_gauss_zeilen`, `hn_gauss_spalten`, `hn_dilatieren` (`hautnachkerne_cu/`, `Hautnachkernbau`) —
bis 21.11.2026 Warp-Kerne in dieser Datei (Felder als `wp.array`).
"""

import torch
from KoerperKI_alle.torchfeld import Torchfeld

from .hautnachkernbau import Hautnachkernbau

__all__ = ['Hautnachfilter']


class Hautnachfilter:
    def __init__(self, geraet='cuda:0'):
        self.geraet = torch.device(geraet)

    @staticmethod
    def kern(sigma):
        """Der Gauß-Kern wie `scipy.ndimage.gaussian_filter1d` ihn baut (Halbbreite `int(4σ + 0,5)`, Summe 1)."""
        radius = int(4.0 * float(sigma) + 0.5)
        x = torch.arange(-radius, radius + 1, dtype=torch.float64, device='cuda')
        k = Torchfeld.exp(-0.5 / (float(sigma) ** 2) * x * x)
        return Torchfeld.astype(k / k.sum(), torch.float32), radius

    def gauss(self, feld, sigma):
        """`feld`: float32 (h, w) auf der Karte; gibt ein neues Feld zurück."""
        k, radius = self.kern(sigma)
        kern = k.to(self.geraet).contiguous()
        feld = feld.contiguous()
        h, w = feld.shape
        zwischen = torch.empty_like(feld)
        aus = torch.empty_like(feld)
        with torch.cuda.device(self.geraet):
            Hautnachkernbau.rufen('hn_gauss_zeilen', h, w, feld, kern, radius, zwischen)
            Hautnachkernbau.rufen('hn_gauss_spalten', h, w, zwischen, kern, radius, aus)
        return aus

    def dilatation(self, maske, schritte):
        """`maske`: uint8 (h, w) auf der Karte (0/1); `schritte` ≥ 1."""
        maske = maske.contiguous()
        h, w = maske.shape
        aus = torch.empty_like(maske)
        with torch.cuda.device(self.geraet):
            Hautnachkernbau.rufen('hn_dilatieren', h, w, maske, int(schritte), aus)
        return aus

    def feld(self, a, dtype=torch.float32):
        """Ein Feld (numpy, PIL oder Tensor) auf die Karte, zusammenhängend im Typ `dtype`."""
        return Torchfeld.feld(a).to(device=self.geraet, dtype=dtype).contiguous()
