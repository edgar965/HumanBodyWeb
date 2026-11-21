# -*- coding: utf-8 -*-
"""Hautnachfarbe — `Blendimportfarbangleich.hinten` (die Ersatzfüllung einer Kachel im Ton der gebackenen Nachbarschaft) auf der Karte.

Dieselbe Rechnung wie die CPU-Fassung (`blendimportfarbangleich.py`, dort die Begründung, die Maßstäbe und die gemessenen Werte; die Konstanten kommen von dort): Löcher der Ersatzkachel
stopfen (`stopfen`, bleibt auf der CPU: 2048², Beschriftung und Abstandskarte), den Versatz Gebackenes − Ersatz auf dem groben Raster in drei Maßstäben glätten (Karte) und auf den
Fehlstellen der vollen Kachel anwenden (Karte). Felder als numpy hinein, ein Feld als numpy heraus; Abweichung gegen die CPU-Fassung ist Rundung (float32): höchstens eine Stufe von 255.
Kerne `hn_bloecke`, `hn_ueberblenden`, `hn_anwenden` (`hautnachkerne_cu/hautnachfarbe.cuh`, `Hautnachkernbau`) — bis 21.11.2026 Warp-Kerne in dieser Datei.

    f = Hautnachfarbe('cuda:0')
    voll = f.hinten(ersatz_pil, farbe, ungueltig)        # wie `Blendimportfarbangleich.hinten`
"""

import torch
from KoerperKI_alle.torchfeld import Torchfeld

from ..blendimportfarbangleich import Blendimportfarbangleich
from .hautnachfilter import Hautnachfilter
from .hautnachkernbau import Hautnachkernbau

__all__ = ['Hautnachfarbe']


class Hautnachfarbe:
    def __init__(self, geraet='cuda:0'):
        self.geraet = torch.device(geraet)
        self.filter = Hautnachfilter(geraet)

    def _auf(self, a, dtype):
        return self.filter.feld(a, dtype)

    def versatz(self, ersatz, farbe, gueltig):
        """Der Versatz Gebackenes − Ersatz auf dem Raster der Ersatzkachel: drei Felder `(h, w)` float32 auf der Karte — wie `Blendimportfarbangleich.versatz`."""
        h, w = ersatz.shape[:2]
        g = self.geraet
        faktor = farbe.shape[0] // h
        gewicht, u0, u1, u2 = (torch.empty((h, w), dtype=torch.float32, device=g) for _ in range(4))
        f8 = self._auf(farbe, torch.uint8)
        with torch.cuda.device(g):
            Hautnachkernbau.rufen('hn_bloecke', h, w, f8, self._auf(Torchfeld.astype(gueltig, torch.uint8), torch.uint8), int(f8.shape[1]), faktor,
                                  self._auf(ersatz, torch.uint8), Blendimportfarbangleich.WEISS, gewicht, u0, u1, u2)
            ergebnis = [torch.zeros((h, w), dtype=torch.float32, device=g) for _ in range(3)]
            for sigma in sorted(Blendimportfarbangleich.SIGMA, reverse=True):         # von grob nach fein überblenden
                gl = self.filter.gauss(gewicht, sigma)
                d = [self.filter.gauss(u, sigma) for u in (u0, u1, u2)]
                Hautnachkernbau.rufen('hn_ueberblenden', h, w, gl, d[0], d[1], d[2], float(Blendimportfarbangleich.MIN_GEWICHT), *ergebnis)
        return ergebnis

    def hinten(self, ersatz, farbe, ungueltig):
        """Die Ersatzfarbe für jede Fehlstelle im Ton der Nachbarschaft: `(H, W, 3)` uint8 — wie `Blendimportfarbangleich.hinten` (`ersatz`: PIL-Bild, `farbe` (H, W, 3) uint8, `ungueltig` (H, W))."""
        from PIL import Image

        hoehe, breite = farbe.shape[:2]
        grob = Blendimportfarbangleich.stopfen(Torchfeld.feld(ersatz.convert('RGB')))
        faktor = max(1, hoehe // Blendimportfarbangleich.GROB_PX)
        while hoehe % faktor or breite % faktor:
            faktor -= 1
        if grob.shape[:2] != (hoehe // faktor, breite // faktor):
            grob = Torchfeld.feld(Image.fromarray(grob).resize((breite // faktor, hoehe // faktor), Image.LANCZOS))
        ergebnis = self.versatz(grob, farbe, ~ungueltig)
        voll = self._auf(Torchfeld.feld(Image.fromarray(grob).resize((breite, hoehe), Image.LANCZOS)), torch.uint8)
        e_h, e_w = ergebnis[0].shape
        with torch.cuda.device(self.geraet):
            Hautnachkernbau.rufen('hn_anwenden', hoehe, breite, voll, self._auf(Torchfeld.astype(ungueltig, torch.uint8), torch.uint8), *ergebnis, e_h, e_w, faktor,
                                  Blendimportfarbangleich.WEISS)
        return voll.cpu().numpy()
