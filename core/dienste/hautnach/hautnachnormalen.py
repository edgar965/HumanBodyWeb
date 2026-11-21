# -*- coding: utf-8 -*-
"""Hautnachnormalen — `Blendimportnormalen` (falsch getroffene Normalen flachlegen, nur das Feindetail behalten) auf der Karte.

Dieselbe Rechnung wie die CPU-Fassung (`blendimportnormalen.py`, dort die Begründung und die gemessenen Werte; die Konstanten kommen von dort), Zahlen und Schnittstelle gleich: Felder
als numpy hinein, Felder als numpy heraus. Abweichungen sind Rundung (float32 statt float64 in der Mittelung, `rint` auf der Karte): höchstens eine Stufe von 255. Kerne `hn_falsche`,
`hn_flachlegen`, `hn_neigung`, `hn_verkleinern`, `hn_teilen`, `hn_hochskalieren`, `hn_kodieren` (`hautnachkerne_cu/hautnachnormalen.cuh`, `Hautnachkernbau`) — bis 21.11.2026
Warp-Kerne in dieser Datei; der Zähler der geänderten Texel (vorher `atomic_add`) ist eine torch-Summe.

    n = Hautnachnormalen('cuda:0')
    neu, anteil = n.saeubern(normal, leer, grad)         # wie `Blendimportnormalen.saeubern`
    neu = n.feindetail(normal, leer, sigma_px)           # wie `Blendimportnormalen.feindetail`
"""

import math

import torch
from KoerperKI_alle.torchfeld import Torchfeld

from ..blendimportnormalen import Blendimportnormalen
from .hautnachfilter import Hautnachfilter
from .hautnachkernbau import Hautnachkernbau

__all__ = ['Hautnachnormalen']

U8, F32 = torch.uint8, torch.float32


class Hautnachnormalen:
    def __init__(self, geraet='cuda:0'):
        self.geraet = torch.device(geraet)
        self.filter = Hautnachfilter(geraet)

    def _auf(self, a, dtype):
        return self.filter.feld(a, dtype)

    def _fehl(self, leer, h, w):
        if leer is None:
            return torch.zeros((h, w), dtype=U8, device=self.geraet)
        return self._auf(Torchfeld.astype(leer, torch.uint8), U8)

    def saeubern(self, normal, leer=None, grad=None):
        """`(neue Karte, Anteil der geänderten Texel in %)` — `normal` (H, W, 3) uint8; wie `Blendimportnormalen.saeubern`; ändert die Eingabe nicht."""
        h, w = normal.shape[:2]
        rufen = Hautnachkernbau.rufen
        n = self._auf(normal, U8)
        fehl = self._fehl(leer, h, w)
        schlecht = torch.zeros((h, w), dtype=U8, device=self.geraet)
        with torch.cuda.device(self.geraet):
            rufen('hn_falsche', h, w, n, fehl, math.cos(math.radians(Blendimportnormalen.GRENZE_GRAD if grad is None else grad)), schlecht)
            if Blendimportnormalen.RAND_PX:
                schlecht = self.filter.dilatation(schlecht, Blendimportnormalen.RAND_PX)
            aus = torch.empty_like(n)
            rufen('hn_flachlegen', h, w, n, schlecht, fehl, aus)
        summe = int(((schlecht != 0) & (fehl == 0)).sum())
        return aus.cpu().numpy(), round(100.0 * summe / float(h * w), 3)

    def feindetail(self, normal, leer=None, sigma_px=None, teiler=4):
        """Die Karte nur mit ihrem Feindetail (`FORM_PX`) — wie `Blendimportnormalen.feindetail`; die Eingabe bleibt unverändert."""
        h, w = normal.shape[:2]
        if h % teiler or w % teiler:
            teiler = 1
        sigma = (Blendimportnormalen.FORM_PX if sigma_px is None else float(sigma_px)) / teiler
        n = self._auf(normal, U8)
        fehl = self._fehl(leer, h, w)
        tx, ty, gueltig = (torch.empty((h, w), dtype=F32, device=self.geraet) for _ in range(3))
        with torch.cuda.device(self.geraet):
            Hautnachkernbau.rufen('hn_neigung', h, w, n, fehl, tx, ty, gueltig)
            tief = [self._tief(f, gueltig, sigma, teiler) for f in (tx, ty)]
            aus = torch.empty_like(n)
            Hautnachkernbau.rufen('hn_kodieren', h, w, tx, ty, tief[0], tief[1], gueltig, fehl, aus)
        return aus.cpu().numpy()

    def _tief(self, feld, gueltig, sigma, teiler):
        """Gewichtetes Mittel der gültigen Neigung, auf `teiler` verkleinert, geglättet und wieder in voller Größe (`tief` der CPU-Fassung)."""
        h, w = feld.shape
        hk, wk = h // teiler, w // teiler
        klein, gewicht = (torch.empty((hk, wk), dtype=F32, device=self.geraet) for _ in range(2))
        Hautnachkernbau.rufen('hn_verkleinern', hk, wk, feld, gueltig, w, teiler, klein, gewicht)
        mittel = torch.empty_like(klein)
        Hautnachkernbau.rufen('hn_teilen', hk * wk, self.filter.gauss(klein, sigma), self.filter.gauss(gewicht, sigma), mittel)
        if teiler == 1:
            return mittel
        voll = torch.empty((h, w), dtype=F32, device=self.geraet)
        Hautnachkernbau.rufen('hn_hochskalieren', h, w, mittel, hk, wk, voll)
        return voll
