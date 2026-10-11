# -*- coding: utf-8 -*-
"""Hautnachnormalen — `Blendimportnormalen` (falsch getroffene Normalen flachlegen, nur das Feindetail behalten) auf der GPU.

Dieselbe Rechnung wie die CPU-Fassung (`blendimportnormalen.py`, dort die Begründung und die gemessenen Werte; die Konstanten kommen von dort), Zahlen und Schnittstelle gleich: Felder
als numpy hinein, Felder als numpy heraus. Abweichungen sind Rundung (float32 statt float64 in der Mittelung, `rint` auf der GPU): höchstens eine Stufe von 255.

    n = Hautnachnormalen('cuda:0')
    neu, anteil = n.saeubern(normal, leer, grad)         # wie `Blendimportnormalen.saeubern`
    neu = n.feindetail(normal, leer, sigma_px)           # wie `Blendimportnormalen.feindetail`
"""

import math

import numpy as np
import warp as wp

from ..blendimportnormalen import Blendimportnormalen
from .hautnachfilter import Hautnachfilter

__all__ = ['Hautnachnormalen']


@wp.kernel
def _falsche(normal: wp.array3d(dtype=wp.uint8), leer: wp.array2d(dtype=wp.uint8), grenze: float, aus: wp.array2d(dtype=wp.uint8)):
    """Kippung über der Grenze (`z < cos(Grad)·|n|`), ohne Fehlstellen."""
    y, x = wp.tid()
    a = float(normal[y, x, 0]) / 127.5 - 1.0
    b = float(normal[y, x, 1]) / 127.5 - 1.0
    c = float(normal[y, x, 2]) / 127.5 - 1.0
    laenge = wp.sqrt(a * a + b * b + c * c)
    if c < grenze * wp.max(laenge, 1.0e-6) and leer[y, x] == wp.uint8(0):
        aus[y, x] = wp.uint8(1)
    else:
        aus[y, x] = wp.uint8(0)


@wp.kernel
def _flachlegen(normal: wp.array3d(dtype=wp.uint8), schlecht: wp.array2d(dtype=wp.uint8), leer: wp.array2d(dtype=wp.uint8), aus: wp.array3d(dtype=wp.uint8)):
    """Falsche Treffer (samt Rand, ohne Fehlstellen) werden flach; sonst bleibt der Wert."""
    y, x = wp.tid()
    flach = schlecht[y, x] != wp.uint8(0) and leer[y, x] == wp.uint8(0)
    for k in range(3):
        if flach:
            if k == 2:
                aus[y, x, k] = wp.uint8(255)
            else:
                aus[y, x, k] = wp.uint8(128)
        else:
            aus[y, x, k] = normal[y, x, k]


@wp.kernel
def _zaehlen(schlecht: wp.array2d(dtype=wp.uint8), leer: wp.array2d(dtype=wp.uint8), summe: wp.array(dtype=wp.int64)):
    y, x = wp.tid()
    if schlecht[y, x] != wp.uint8(0) and leer[y, x] == wp.uint8(0):
        wp.atomic_add(summe, 0, wp.int64(1))


@wp.kernel
def _neigung(normal: wp.array3d(dtype=wp.uint8), leer: wp.array2d(dtype=wp.uint8), tx: wp.array2d(dtype=wp.float32), ty: wp.array2d(dtype=wp.float32),
             gueltig: wp.array2d(dtype=wp.float32)):
    """Neigung `x/z`, `y/z` (z nach unten auf 0,05 begrenzt) und das Gültigkeitsfeld (1 = getroffen)."""
    y, x = wp.tid()
    a = float(normal[y, x, 0]) / 127.5 - 1.0
    b = float(normal[y, x, 1]) / 127.5 - 1.0
    c = wp.max(float(normal[y, x, 2]) / 127.5 - 1.0, 0.05)
    tx[y, x] = a / c
    ty[y, x] = b / c
    g = float(1.0)
    if leer[y, x] != wp.uint8(0):
        g = 0.0
    gueltig[y, x] = g


@wp.kernel
def _verkleinern(feld: wp.array2d(dtype=wp.float32), gueltig: wp.array2d(dtype=wp.float32), t: int, klein: wp.array2d(dtype=wp.float32), gewicht: wp.array2d(dtype=wp.float32)):
    """Mittel von `feld·gültig` und von `gültig` je `t × t`-Block."""
    y, x = wp.tid()
    s = float(0.0)
    g = float(0.0)
    for j in range(t):
        for i in range(t):
            w = gueltig[y * t + j, x * t + i]
            s += feld[y * t + j, x * t + i] * w
            g += w
    klein[y, x] = s / float(t * t)
    gewicht[y, x] = g / float(t * t)


@wp.kernel
def _teilen(zaehler: wp.array2d(dtype=wp.float32), nenner: wp.array2d(dtype=wp.float32), aus: wp.array2d(dtype=wp.float32)):
    y, x = wp.tid()
    aus[y, x] = zaehler[y, x] / wp.max(nenner[y, x], 1.0e-3)


@wp.kernel
def _hochskalieren(klein: wp.array2d(dtype=wp.float32), aus: wp.array2d(dtype=wp.float32)):
    """`scipy.ndimage.zoom(…, order=1)`: die Ränder fallen aufeinander (`in = out · (n_in − 1)/(n_out − 1)`), dazwischen bilinear."""
    y, x = wp.tid()
    h = aus.shape[0]
    w = aus.shape[1]
    hk = klein.shape[0]
    wk = klein.shape[1]
    fy = float(0.0)
    fx = float(0.0)
    if h > 1:
        fy = float(y) * float(hk - 1) / float(h - 1)
    if w > 1:
        fx = float(x) * float(wk - 1) / float(w - 1)
    y0 = wp.min(int(wp.floor(fy)), hk - 1)
    x0 = wp.min(int(wp.floor(fx)), wk - 1)
    y1 = wp.min(y0 + 1, hk - 1)
    x1 = wp.min(x0 + 1, wk - 1)
    wy = fy - float(y0)
    wx = fx - float(x0)
    oben = klein[y0, x0] * (1.0 - wx) + klein[y0, x1] * wx
    unten = klein[y1, x0] * (1.0 - wx) + klein[y1, x1] * wx
    aus[y, x] = oben * (1.0 - wy) + unten * wy


@wp.kernel
def _kodieren(tx: wp.array2d(dtype=wp.float32), ty: wp.array2d(dtype=wp.float32), tx_tief: wp.array2d(dtype=wp.float32), ty_tief: wp.array2d(dtype=wp.float32),
              gueltig: wp.array2d(dtype=wp.float32), leer: wp.array2d(dtype=wp.uint8), aus: wp.array3d(dtype=wp.uint8)):
    """Feindetail = Neigung minus großflächige Neigung; zurück in eine Normale, auf Bytes (`rint`), Fehlstellen flach."""
    y, x = wp.tid()
    hx = (tx[y, x] - tx_tief[y, x]) * gueltig[y, x]
    hy = (ty[y, x] - ty_tief[y, x]) * gueltig[y, x]
    laenge = wp.sqrt(hx * hx + hy * hy + 1.0)
    w0 = hx / laenge
    w1 = hy / laenge
    w2 = 1.0 / laenge
    if leer[y, x] != wp.uint8(0):
        aus[y, x, 0] = wp.uint8(128)
        aus[y, x, 1] = wp.uint8(128)
        aus[y, x, 2] = wp.uint8(255)
    else:
        aus[y, x, 0] = wp.uint8(wp.clamp(wp.round((w0 + 1.0) * 127.5), 0.0, 255.0))
        aus[y, x, 1] = wp.uint8(wp.clamp(wp.round((w1 + 1.0) * 127.5), 0.0, 255.0))
        aus[y, x, 2] = wp.uint8(wp.clamp(wp.round((w2 + 1.0) * 127.5), 0.0, 255.0))


class Hautnachnormalen:
    def __init__(self, geraet='cuda:0'):
        self.geraet = geraet
        self.filter = Hautnachfilter(geraet)

    def _auf(self, a, dtype):
        return wp.array(np.ascontiguousarray(a), dtype=dtype, device=self.geraet)

    def saeubern(self, normal, leer=None, grad=None):
        """`(neue Karte, Anteil der geänderten Texel in %)` — `normal` (H, W, 3) uint8; wie `Blendimportnormalen.saeubern`; ändert die Eingabe nicht."""
        h, w = normal.shape[:2]
        g = self.geraet
        n = self._auf(normal, wp.uint8)
        fehl = self._auf(np.zeros((h, w), np.uint8) if leer is None else leer.astype(np.uint8), wp.uint8)
        schlecht = wp.zeros((h, w), dtype=wp.uint8, device=g)
        wp.launch(_falsche, dim=(h, w), inputs=[n, fehl, math.cos(math.radians(Blendimportnormalen.GRENZE_GRAD if grad is None else grad)), schlecht], device=g)
        if Blendimportnormalen.RAND_PX:
            schlecht = self.filter.dilatation(schlecht, Blendimportnormalen.RAND_PX)
        aus = wp.empty_like(n)
        wp.launch(_flachlegen, dim=(h, w), inputs=[n, schlecht, fehl, aus], device=g)
        summe = wp.zeros(1, dtype=wp.int64, device=g)
        wp.launch(_zaehlen, dim=(h, w), inputs=[schlecht, fehl, summe], device=g)
        return aus.numpy(), round(100.0 * int(summe.numpy()[0]) / float(h * w), 3)

    def feindetail(self, normal, leer=None, sigma_px=None, teiler=4):
        """Die Karte nur mit ihrem Feindetail (`FORM_PX`) — wie `Blendimportnormalen.feindetail`; die Eingabe bleibt unverändert."""
        h, w = normal.shape[:2]
        g = self.geraet
        if h % teiler or w % teiler:
            teiler = 1
        sigma = (Blendimportnormalen.FORM_PX if sigma_px is None else float(sigma_px)) / teiler
        n = self._auf(normal, wp.uint8)
        fehl = self._auf(np.zeros((h, w), np.uint8) if leer is None else leer.astype(np.uint8), wp.uint8)
        tx, ty, gueltig = (wp.empty((h, w), dtype=wp.float32, device=g) for _ in range(3))
        wp.launch(_neigung, dim=(h, w), inputs=[n, fehl, tx, ty, gueltig], device=g)
        tief = [self._tief(f, gueltig, sigma, teiler) for f in (tx, ty)]
        aus = wp.empty_like(n)
        wp.launch(_kodieren, dim=(h, w), inputs=[tx, ty, tief[0], tief[1], gueltig, fehl, aus], device=g)
        return aus.numpy()

    def _tief(self, feld, gueltig, sigma, teiler):
        """Gewichtetes Mittel der gültigen Neigung, auf `teiler` verkleinert, geglättet und wieder in voller Größe (`tief` der CPU-Fassung)."""
        h, w = feld.shape
        g = self.geraet
        klein, gewicht = (wp.empty((h // teiler, w // teiler), dtype=wp.float32, device=g) for _ in range(2))
        wp.launch(_verkleinern, dim=klein.shape, inputs=[feld, gueltig, teiler, klein, gewicht], device=g)
        mittel = wp.empty_like(klein)
        wp.launch(_teilen, dim=klein.shape, inputs=[self.filter.gauss(klein, sigma), self.filter.gauss(gewicht, sigma), mittel], device=g)
        if teiler == 1:
            return mittel
        voll = wp.empty((h, w), dtype=wp.float32, device=g)
        wp.launch(_hochskalieren, dim=(h, w), inputs=[mittel, voll], device=g)
        return voll
