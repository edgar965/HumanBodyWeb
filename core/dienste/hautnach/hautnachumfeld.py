# -*- coding: utf-8 -*-
"""Hautnachumfeld — `Blendimportumfeld` (die Haut-Kachel um das Scham-Stück trägt dort die Farbe des Originals) auf der GPU.

Dieselbe Rechnung wie die CPU-Fassung (`blendimportumfeld.py`, dort die Begründung, die Maße und die gemessenen Werte; Konstanten, `fuellen` und die Berichtszahlen kommen von dort — die Klasse
erbt). Auf die GPU verlegt sind die beiden Schritte, die dort Minuten brauchten:

    texel            die Texel einer Fehlstelle in und um die Figurdreiecke (UV-Raum der Kachel): je Dreieck die Texel seines Rechtecks, Schwerpunktkoordinaten in `float64` wie auf der CPU;
                     Texel IM Dreieck gehen vor Texeln nur in der Zugabe `RAND` (im Dreieck gewinnt das letzte, in der Zugabe das erste Dreieck — die Reihenfolge der CPU-Schleife, als
                     `atomic_max` bzw. `atomic_min` über die Dreiecksnummer). Die CPU rechnet je UV-Insel eigene Gitter; hier gilt EIN Gitter — nur an der Grenze zweier Inseln, wo die
                     Zugabe der einen in die andere reicht, kann ein Texel einem anderen Dreieck gehören (dort gewinnt nun immer das Innere).
    original_farbe   der nächste Punkt auf der Fläche des Originals (`wp.mesh_query_point_no_sign`, höchstens `ABSTAND_MAX_M`) und die Farbe aus dem Farbbild an seiner UV (bilinear).

    umfeld = Hautnachumfeld(stueck, figur, original, farbbild, 'cuda:0')
    umfeld.fuellen(kachel, farbe, leer)                          # wie `Blendimportumfeld.fuellen`
"""

import numpy as np
import warp as wp

from ..blendimportumfeld import Blendimportumfeld

__all__ = ['Hautnachumfeld']

KEINE = 2 ** 31 - 1


@wp.func
def _bary(px: wp.array2d(dtype=wp.float64), t: int, x: wp.float64, y: wp.float64) -> wp.vec3d:
    """Schwerpunktkoordinaten `(l1, l2, l3)` des Punkts `(x, y)` im UV-Dreieck `t` (Pixel; Ecken a, b, c) — wie die CPU; bei entartetem Dreieck `(−1, −1, −1)`."""
    a0 = px[t, 0]
    a1 = px[t, 1]
    b0 = px[t, 2]
    b1 = px[t, 3]
    c0 = px[t, 4]
    c1 = px[t, 5]
    det = (b1 - c1) * (a0 - c0) + (c0 - b0) * (a1 - c1)
    if wp.abs(det) < wp.float64(1.0e-9):
        return wp.vec3d(wp.float64(-1.0), wp.float64(-1.0), wp.float64(-1.0))
    l1 = ((b1 - c1) * (x - c0) + (c0 - b0) * (y - c1)) / det
    l2 = ((c1 - a1) * (x - c0) + (a0 - c0) * (y - c1)) / det
    return wp.vec3d(l1, l2, wp.float64(1.0) - l1 - l2)


@wp.kernel
def _rastern(px: wp.array2d(dtype=wp.float64), rand: wp.float64, innen: wp.array2d(dtype=wp.int32), zugabe: wp.array2d(dtype=wp.int32)):
    """Je Dreieck die Texel seines Rechtecks: im Dreieck → `atomic_max(innen, t)`, in der Zugabe `RAND` → `atomic_min(zugabe, t)`."""
    t = wp.tid()
    hoehe = innen.shape[0]
    breite = innen.shape[1]
    xs0 = wp.min(px[t, 0], wp.min(px[t, 2], px[t, 4]))
    xs1 = wp.max(px[t, 0], wp.max(px[t, 2], px[t, 4]))
    ys0 = wp.min(px[t, 1], wp.min(px[t, 3], px[t, 5]))
    ys1 = wp.max(px[t, 1], wp.max(px[t, 3], px[t, 5]))
    x0 = wp.max(int(wp.floor(xs0)) - 1, 0)
    x1 = wp.min(int(wp.ceil(xs1)) + 2, breite)
    y0 = wp.max(int(wp.floor(ys0)) - 1, 0)
    y1 = wp.min(int(wp.ceil(ys1)) + 2, hoehe)
    for gy in range(y0, y1):
        for gx in range(x0, x1):
            b = _bary(px, t, wp.float64(gx) + wp.float64(0.5), wp.float64(gy) + wp.float64(0.5))
            kleinste = wp.min(b[0], wp.min(b[1], b[2]))
            if kleinste >= wp.float64(0.0):
                wp.atomic_max(innen, gy, gx, t)
            elif kleinste >= -rand:
                wp.atomic_min(zugabe, gy, gx, t)


@wp.kernel
def _zaehlen(innen: wp.array2d(dtype=wp.int32), zugabe: wp.array2d(dtype=wp.int32), leer: wp.array2d(dtype=wp.uint8), keine: int, summe: wp.array(dtype=wp.int32)):
    y, x = wp.tid()
    if leer[y, x] != wp.uint8(0) and (innen[y, x] >= 0 or zugabe[y, x] != keine):
        wp.atomic_add(summe, 0, 1)


@wp.kernel
def _sammeln(px: wp.array2d(dtype=wp.float64), innen: wp.array2d(dtype=wp.int32), zugabe: wp.array2d(dtype=wp.int32), leer: wp.array2d(dtype=wp.uint8), keine: int,
             zaehler: wp.array(dtype=wp.int32), zeile: wp.array(dtype=wp.int32), spalte: wp.array(dtype=wp.int32), eigner: wp.array(dtype=wp.int32), lam: wp.array2d(dtype=wp.float64)):
    """Die Texel der Fehlstellen mit Besitzer: Zeile, Spalte, Dreieck und Schwerpunktkoordinaten."""
    y, x = wp.tid()
    if leer[y, x] == wp.uint8(0):
        return
    t = int(-1)
    if innen[y, x] >= 0:
        t = innen[y, x]
    elif zugabe[y, x] != keine:
        t = zugabe[y, x]
    if t < 0:
        return
    i = wp.atomic_add(zaehler, 0, 1)
    b = _bary(px, t, wp.float64(x) + wp.float64(0.5), wp.float64(y) + wp.float64(0.5))
    zeile[i] = y
    spalte[i] = x
    eigner[i] = t
    lam[i, 0] = b[0]
    lam[i, 1] = b[1]
    lam[i, 2] = b[2]


@wp.kernel
def _naechster(mesh: wp.uint64, orte: wp.array(dtype=wp.vec3), uv_ecken: wp.array(dtype=wp.vec2), farbbild: wp.array3d(dtype=wp.uint8), abstand_max: float,
               farbe: wp.array(dtype=wp.vec3), gefunden: wp.array(dtype=wp.int32)):
    """Der nächste Punkt der Fläche zu jedem Ort (höchstens `abstand_max`), seine UV aus den Ecken und die Farbe daran (bilinear, Texelmitten bei ganzen Zahlen, außen geklemmt)."""
    i = wp.tid()
    q = wp.mesh_query_point_no_sign(mesh, orte[i], abstand_max)
    if not q.result:
        gefunden[i] = 0
        return
    gefunden[i] = 1
    f = q.face
    uv = uv_ecken[f * 3] * q.u + uv_ecken[f * 3 + 1] * q.v + uv_ecken[f * 3 + 2] * (1.0 - q.u - q.v)
    hoehe = farbbild.shape[0]
    breite = farbbild.shape[1]
    x = wp.clamp(uv[0] * float(breite) - 0.5, 0.0, float(breite) - 1.0001)
    y = wp.clamp((1.0 - uv[1]) * float(hoehe) - 0.5, 0.0, float(hoehe) - 1.0001)
    x0 = int(wp.floor(x))
    y0 = int(wp.floor(y))
    fx = x - float(x0)
    fy = y - float(y0)
    c = wp.vec3(0.0, 0.0, 0.0)
    for k in range(3):
        oben = float(farbbild[y0, x0, k]) * (1.0 - fx) + float(farbbild[y0, x0 + 1, k]) * fx
        unten = float(farbbild[y0 + 1, x0, k]) * (1.0 - fx) + float(farbbild[y0 + 1, x0 + 1, k]) * fx
        c[k] = oben * (1.0 - fy) + unten * fy
    farbe[i] = c


class Hautnachumfeld(Blendimportumfeld):
    def __init__(self, stueck, figur, original, farbbild, geraet='cuda:0'):
        super().__init__(stueck, figur, original, farbbild)
        self.geraet = geraet
        wp.init()
        self._mesh = None

    def texel(self, dreiecke, leer):
        """`(zeile, spalte, dreieck, schwerpunkt)` der Fehlstellen-Texel in und um die Figurdreiecke `dreiecke` — wie `Blendimportumfeld.texel` (Gitter: siehe Kopf)."""
        g = self.geraet
        hoehe, breite = leer.shape
        uv = self.figur['uv'][self.figur['dreiecke'][dreiecke]]                    # (T, 3, 2)
        px = np.stack([uv[..., 0] * breite, (1.0 - uv[..., 1]) * hoehe], axis=-1).reshape(len(dreiecke), 6)
        a_px = wp.array(np.ascontiguousarray(px, dtype=np.float64), dtype=wp.float64, device=g)
        innen = wp.full((hoehe, breite), -1, dtype=wp.int32, device=g)
        zugabe = wp.full((hoehe, breite), KEINE, dtype=wp.int32, device=g)
        wp.launch(_rastern, dim=len(dreiecke), inputs=[a_px, wp.float64(self.RAND), innen, zugabe], device=g)
        a_leer = wp.array(np.ascontiguousarray(leer.astype(np.uint8)), dtype=wp.uint8, device=g)
        summe = wp.zeros(1, dtype=wp.int32, device=g)
        wp.launch(_zaehlen, dim=(hoehe, breite), inputs=[innen, zugabe, a_leer, KEINE, summe], device=g)
        n = int(summe.numpy()[0])
        zeile, spalte, eigner = (wp.zeros(max(n, 1), dtype=wp.int32, device=g) for _ in range(3))
        lam = wp.zeros((max(n, 1), 3), dtype=wp.float64, device=g)
        zaehler = wp.zeros(1, dtype=wp.int32, device=g)
        wp.launch(_sammeln, dim=(hoehe, breite), inputs=[a_px, innen, zugabe, a_leer, KEINE, zaehler, zeile, spalte, eigner, lam], device=g)
        z, s, e, lm = zeile.numpy()[:n].astype(np.int64), spalte.numpy()[:n].astype(np.int64), eigner.numpy()[:n].astype(np.int64), lam.numpy()[:n]
        ordnung = np.lexsort((s, z))                                                # Zeile, dann Spalte — wie `np.nonzero` der CPU-Fassung
        return z[ordnung], s[ordnung], e[ordnung], lm[ordnung]

    def original_farbe(self, orte):
        """`(farbe (n, 3) float, gefunden (n,) bool)`: die Farbe des Originals am nächsten Punkt seiner Fläche zu jedem Ort — wie `Blendimportumfeld.original_farbe`."""
        g = self.geraet
        o = self.original
        if self._mesh is None:
            self._mesh = (wp.Mesh(points=wp.array(np.ascontiguousarray(o['punkte'], dtype=np.float32), dtype=wp.vec3, device=g),
                                  indices=wp.array(np.ascontiguousarray(o['dreiecke'], dtype=np.int32).reshape(-1), dtype=wp.int32, device=g)),
                          wp.array(np.ascontiguousarray(o['uv_ecken'], dtype=np.float32).reshape(-1, 2), dtype=wp.vec2, device=g),
                          wp.array(np.ascontiguousarray(self.farbbild), dtype=wp.uint8, device=g))
        mesh, uv_ecken, bild = self._mesh
        n = len(orte)
        farbe = wp.zeros(max(n, 1), dtype=wp.vec3, device=g)
        gefunden = wp.zeros(max(n, 1), dtype=wp.int32, device=g)
        wp.launch(_naechster, dim=n, inputs=[mesh.id, wp.array(np.ascontiguousarray(orte, dtype=np.float32), dtype=wp.vec3, device=g), uv_ecken, bild, float(self.ABSTAND_MAX_M),
                                              farbe, gefunden], device=g)
        return farbe.numpy()[:n].astype(np.float64), gefunden.numpy()[:n].astype(bool)
