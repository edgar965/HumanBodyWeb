# -*- coding: utf-8 -*-
"""Blendimportatlas — aus einem kleinen Ausschnitt eines Netzes einen eigenen kleinen Bildatlas schneiden (08.10.2026).

WARUM: Der Körper von „cute girl" hat EINEN 8192-px-Atlas für den ganzen Leib (Farbe 101 MB, Normalen 99 MB, Rauheit 45 MB als PNG).
Das Scham-Stück (`Blendimportscham`) nutzt davon fünf kleine Inseln — gemessen 2,4 Mpx von 67 Mpx. Es bekommt deshalb nur diese
Inseln, in Originalauflösung (ein Texel des Originals bleibt ein Texel), nebeneinander in einem Bild von 2048 px Breite.

Die Inseln sind die zusammenhängenden Teile der Ausschnitt-Dreiecke über gemeinsame UV-Ecken. Jede Insel behält ihr Rechteck samt
Rand (`RAND_PX`), damit Mip-Stufen und Filterung nicht ins Nachbarbild bluten; das Rechteck darf Texel von Nachbarinseln des
Originals enthalten — sie werden nie angesprochen.

Spiegelbild der Rechnung: UV-Ursprung unten links (Blender), Bildzeile 0 oben — `v` wird beim Schneiden gespiegelt.
"""

import numpy as np
from scipy import sparse
from scipy.sparse import csgraph

__all__ = ['Blendimportatlas']


class Blendimportatlas:
    #: Rand um jede Insel in Texeln des Originals.
    RAND_PX = 12
    #: Breite des Atlas; reicht eine Zeile nicht, wird sie verdoppelt.
    BREITE = 2048
    #: UV-Ecken, die auf diese Genauigkeit gleich sind, gehören zur selben Naht (Ganzzahl-Rasterung von 1/AUFLOESUNG).
    AUFLOESUNG = 100000

    @classmethod
    def inseln(cls, uv_ecken):
        """Nummer der UV-Insel je Dreieck; `uv_ecken` (T, 3, 2)."""
        t = len(uv_ecken)
        if t == 0:
            return np.zeros(0, dtype=np.int64)
        raster = np.round(np.asarray(uv_ecken, dtype=np.float64).reshape(-1, 2) * cls.AUFLOESUNG).astype(np.int64)
        _, ecke = np.unique(raster, axis=0, return_inverse=True)
        zeile = np.repeat(np.arange(t), 3)
        je = sparse.csr_matrix((np.ones(3 * t), (zeile, ecke.reshape(-1))), shape=(t, int(ecke.max()) + 1))
        return csgraph.connected_components((je @ je.T) > 0, directed=False)[1]

    @classmethod
    def rechtecke(cls, uv_ecken, insel, groesse):
        """`(x0, y0, x1, y1)` je Insel in Texeln des Quellbilds (Zeile 0 oben), samt Rand, auf das Bild begrenzt.
        `groesse` = (Breite, Höhe) des Quellbilds."""
        breite, hoehe = groesse
        uv = np.asarray(uv_ecken, dtype=np.float64)
        aus = []
        for i in range(int(insel.max()) + 1 if len(insel) else 0):
            u, v = uv[insel == i][..., 0].reshape(-1), uv[insel == i][..., 1].reshape(-1)
            x0, x1 = np.floor(u.min() * breite) - cls.RAND_PX, np.ceil(u.max() * breite) + cls.RAND_PX
            y0, y1 = np.floor((1.0 - v.max()) * hoehe) - cls.RAND_PX, np.ceil((1.0 - v.min()) * hoehe) + cls.RAND_PX
            aus.append((int(max(0, x0)), int(max(0, y0)), int(min(breite, x1)), int(min(hoehe, y1))))
        return aus

    @classmethod
    def packen(cls, rechtecke):
        """Regalpackung: `(orte, (breite, hoehe))` — `orte[i]` = (x, y) der linken oberen Ecke im Atlas. Das höchste zuerst."""
        breite = cls.BREITE
        bmax = max((x1 - x0 for x0, _, x1, _ in rechtecke), default=0)
        while breite < bmax:
            breite *= 2
        reihenfolge = sorted(range(len(rechtecke)), key=lambda i: -(rechtecke[i][3] - rechtecke[i][1]))
        orte = [None] * len(rechtecke)
        x = y = zeilenhoehe = 0
        for i in reihenfolge:
            x0, y0, x1, y1 = rechtecke[i]
            b, h = x1 - x0, y1 - y0
            if x + b > breite:
                x, y, zeilenhoehe = 0, y + zeilenhoehe, 0
            orte[i] = (x, y)
            x += b
            zeilenhoehe = max(zeilenhoehe, h)
        hoehe = int(-(-(y + zeilenhoehe) // 8) * 8) or 8
        return orte, (breite, hoehe)

    @staticmethod
    def neue_uv(uv_ecken, insel, rechtecke, orte, groesse, atlas):
        """UV je Dreiecksecke im Atlas (Ursprung unten links, wie das Original)."""
        uv = np.asarray(uv_ecken, dtype=np.float64)
        aus = np.zeros_like(uv)
        for i, (x0, y0, _, _) in enumerate(rechtecke):
            m = insel == i
            px = uv[m][..., 0] * groesse[0] - x0 + orte[i][0]
            py = (1.0 - uv[m][..., 1]) * groesse[1] - y0 + orte[i][1]
            aus[m] = np.stack([px / atlas[0], 1.0 - py / atlas[1]], axis=-1)
        return aus

    @staticmethod
    def schneiden(bild, rechtecke, orte, atlas):
        """Der Atlas aus `bild` (H, W, K): jede Insel an ihren Ort kopiert, Rest schwarz."""
        aus = np.zeros((atlas[1], atlas[0]) + bild.shape[2:], dtype=bild.dtype)
        for (x0, y0, x1, y1), (ax, ay) in zip(rechtecke, orte, strict=True):
            aus[ay:ay + (y1 - y0), ax:ax + (x1 - x0)] = bild[y0:y1, x0:x1]
        return aus
