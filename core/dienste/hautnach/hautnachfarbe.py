# -*- coding: utf-8 -*-
"""Hautnachfarbe — `Blendimportfarbangleich.hinten` (die Ersatzfüllung einer Kachel im Ton der gebackenen Nachbarschaft) auf der GPU.

Dieselbe Rechnung wie die CPU-Fassung (`blendimportfarbangleich.py`, dort die Begründung, die Maßstäbe und die gemessenen Werte; die Konstanten kommen von dort): Löcher der Ersatzkachel
stopfen (`stopfen`, bleibt auf der CPU: 2048², Beschriftung und Abstandskarte), den Versatz Gebackenes − Ersatz auf dem groben Raster in drei Maßstäben glätten (GPU) und auf den Fehlstellen
der vollen Kachel anwenden (GPU). Felder als numpy hinein, ein Feld als numpy heraus; Abweichung gegen die CPU-Fassung ist Rundung (float32): höchstens eine Stufe von 255.

    f = Hautnachfarbe('cuda:0')
    voll = f.hinten(ersatz_pil, farbe, ungueltig)        # wie `Blendimportfarbangleich.hinten`
"""

import numpy as np
import warp as wp

from ..blendimportfarbangleich import Blendimportfarbangleich
from .hautnachfilter import Hautnachfilter

__all__ = ['Hautnachfarbe']


@wp.kernel
def _bloecke(farbe: wp.array3d(dtype=wp.uint8), gueltig: wp.array2d(dtype=wp.uint8), faktor: int, ersatz: wp.array3d(dtype=wp.uint8), weiss: int,
             gewicht: wp.array2d(dtype=wp.float32), uf0: wp.array2d(dtype=wp.float32), uf1: wp.array2d(dtype=wp.float32), uf2: wp.array2d(dtype=wp.float32)):
    """Je grobem Pixel: Anteil gültig und Mittel der gültigen gebackenen Farbe (`_bloecke`), daraus Gewicht und gewichteter Unterschied Gebackenes − Ersatz (`versatz`)."""
    y, x = wp.tid()
    n = float(faktor * faktor)
    anteil = float(0.0)
    s0 = float(0.0)
    s1 = float(0.0)
    s2 = float(0.0)
    for j in range(faktor):
        for i in range(faktor):
            if gueltig[y * faktor + j, x * faktor + i] != wp.uint8(0):
                anteil += 1.0
                s0 += float(farbe[y * faktor + j, x * faktor + i, 0])
                s1 += float(farbe[y * faktor + j, x * faktor + i, 1])
                s2 += float(farbe[y * faktor + j, x * faktor + i, 2])
    anteil = anteil / n
    helligkeit = wp.min(int(ersatz[y, x, 0]), wp.min(int(ersatz[y, x, 1]), int(ersatz[y, x, 2])))
    if helligkeit < weiss and anteil > 0.0:
        gewicht[y, x] = anteil
        m = 1.0 / wp.max(anteil * n, 1.0e-6)
        uf0[y, x] = (s0 * m - float(ersatz[y, x, 0])) * anteil
        uf1[y, x] = (s1 * m - float(ersatz[y, x, 1])) * anteil
        uf2[y, x] = (s2 * m - float(ersatz[y, x, 2])) * anteil
    else:
        gewicht[y, x] = 0.0
        uf0[y, x] = 0.0
        uf1[y, x] = 0.0
        uf2[y, x] = 0.0


@wp.kernel
def _ueberblenden(g: wp.array2d(dtype=wp.float32), d0: wp.array2d(dtype=wp.float32), d1: wp.array2d(dtype=wp.float32), d2: wp.array2d(dtype=wp.float32), min_gewicht: float,
                  e0: wp.array2d(dtype=wp.float32), e1: wp.array2d(dtype=wp.float32), e2: wp.array2d(dtype=wp.float32)):
    """Ein Maßstab: wo er genug Fläche sieht (`g / MIN_GEWICHT`, bis 1), gilt sein Versatz, sonst der gröbere (`ergebnis`)."""
    y, x = wp.tid()
    a = wp.clamp(g[y, x] / min_gewicht, 0.0, 1.0)
    n = wp.max(g[y, x], 1.0e-6)
    e0[y, x] = e0[y, x] * (1.0 - a) + (d0[y, x] / n) * a
    e1[y, x] = e1[y, x] * (1.0 - a) + (d1[y, x] / n) * a
    e2[y, x] = e2[y, x] * (1.0 - a) + (d2[y, x] / n) * a


@wp.func
def _zeiger(i: int, faktor: int, n: int) -> float:
    """Position im groben Raster zu Pixel `i` des feinen (Mitte auf Mitte, geklemmt) — `_hoch`."""
    return wp.clamp((float(i) + 0.5) / float(faktor) - 0.5, 0.0, float(n - 1))


@wp.kernel
def _anwenden(voll: wp.array3d(dtype=wp.uint8), ungueltig: wp.array2d(dtype=wp.uint8), e0: wp.array2d(dtype=wp.float32), e1: wp.array2d(dtype=wp.float32),
              e2: wp.array2d(dtype=wp.float32), faktor: int, weiss: int):
    """Auf den Fehlstellen der vollen Kachel (nicht weiß) den bilinear hochgerechneten Versatz addieren, auf 0 … 255 klemmen."""
    y, x = wp.tid()
    h = e0.shape[0]
    w = e0.shape[1]
    if ungueltig[y, x] == wp.uint8(0):
        return
    if wp.min(int(voll[y, x, 0]), wp.min(int(voll[y, x, 1]), int(voll[y, x, 2]))) >= weiss:
        return
    fy = _zeiger(y, faktor, h)
    fx = _zeiger(x, faktor, w)
    y0 = int(wp.floor(fy))
    x0 = int(wp.floor(fx))
    y1 = wp.min(y0 + 1, h - 1)
    x1 = wp.min(x0 + 1, w - 1)
    wy = fy - float(y0)
    wx = fx - float(x0)
    d0 = (e0[y0, x0] * (1.0 - wx) + e0[y0, x1] * wx) * (1.0 - wy) + (e0[y1, x0] * (1.0 - wx) + e0[y1, x1] * wx) * wy
    d1 = (e1[y0, x0] * (1.0 - wx) + e1[y0, x1] * wx) * (1.0 - wy) + (e1[y1, x0] * (1.0 - wx) + e1[y1, x1] * wx) * wy
    d2 = (e2[y0, x0] * (1.0 - wx) + e2[y0, x1] * wx) * (1.0 - wy) + (e2[y1, x0] * (1.0 - wx) + e2[y1, x1] * wx) * wy
    voll[y, x, 0] = wp.uint8(wp.clamp(float(voll[y, x, 0]) + d0, 0.0, 255.0))
    voll[y, x, 1] = wp.uint8(wp.clamp(float(voll[y, x, 1]) + d1, 0.0, 255.0))
    voll[y, x, 2] = wp.uint8(wp.clamp(float(voll[y, x, 2]) + d2, 0.0, 255.0))


class Hautnachfarbe:
    def __init__(self, geraet='cuda:0'):
        self.geraet = geraet
        self.filter = Hautnachfilter(geraet)

    def _auf(self, a, dtype):
        return wp.array(np.ascontiguousarray(a), dtype=dtype, device=self.geraet)

    def versatz(self, ersatz, farbe, gueltig):
        """Der Versatz Gebackenes − Ersatz auf dem Raster der Ersatzkachel: drei Felder `(h, w)` float32 auf der GPU — wie `Blendimportfarbangleich.versatz`."""
        h, w = ersatz.shape[:2]
        g = self.geraet
        faktor = farbe.shape[0] // h
        gewicht, u0, u1, u2 = (wp.empty((h, w), dtype=wp.float32, device=g) for _ in range(4))
        wp.launch(_bloecke, dim=(h, w), inputs=[self._auf(farbe, wp.uint8), self._auf(gueltig.astype(np.uint8), wp.uint8), faktor, self._auf(ersatz, wp.uint8),
                                                Blendimportfarbangleich.WEISS, gewicht, u0, u1, u2], device=g)
        ergebnis = [wp.zeros((h, w), dtype=wp.float32, device=g) for _ in range(3)]
        for sigma in sorted(Blendimportfarbangleich.SIGMA, reverse=True):         # von grob nach fein überblenden
            gl = self.filter.gauss(gewicht, sigma)
            d = [self.filter.gauss(u, sigma) for u in (u0, u1, u2)]
            wp.launch(_ueberblenden, dim=(h, w), inputs=[gl, d[0], d[1], d[2], Blendimportfarbangleich.MIN_GEWICHT, *ergebnis], device=g)
        return ergebnis

    def hinten(self, ersatz, farbe, ungueltig):
        """Die Ersatzfarbe für jede Fehlstelle im Ton der Nachbarschaft: `(H, W, 3)` uint8 — wie `Blendimportfarbangleich.hinten` (`ersatz`: PIL-Bild, `farbe` (H, W, 3) uint8, `ungueltig` (H, W))."""
        from PIL import Image

        hoehe, breite = farbe.shape[:2]
        grob = Blendimportfarbangleich.stopfen(np.asarray(ersatz.convert('RGB')))
        faktor = max(1, hoehe // Blendimportfarbangleich.GROB_PX)
        while hoehe % faktor or breite % faktor:
            faktor -= 1
        if grob.shape[:2] != (hoehe // faktor, breite // faktor):
            grob = np.asarray(Image.fromarray(grob).resize((breite // faktor, hoehe // faktor), Image.LANCZOS))
        ergebnis = self.versatz(grob, farbe, ~ungueltig)
        voll = self._auf(np.asarray(Image.fromarray(grob).resize((breite, hoehe), Image.LANCZOS)), wp.uint8)
        wp.launch(_anwenden, dim=(hoehe, breite), inputs=[voll, self._auf(ungueltig.astype(np.uint8), wp.uint8), *ergebnis, faktor, Blendimportfarbangleich.WEISS], device=self.geraet)
        return voll.numpy()
