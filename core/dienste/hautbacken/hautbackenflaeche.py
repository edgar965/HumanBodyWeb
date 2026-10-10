# -*- coding: utf-8 -*-
"""Hautbackenflaeche — ein Dreiecksnetz mit UV je Ecke, dazu geglättete Normalen und Tangenten (Grundlage von Figur und Quellkörper).

Beide Seiten des Backens brauchen dasselbe: die Figur (Genesis, eine Kachel) schießt Strahlen entlang ihrer Normalen und legt ihren Tangentenraum fest, der Quellkörper liefert
am Treffer Normale und Tangente für die Normalenkarte. Die Regeln folgen Blender:

* Normalen: nach dem Winkel an der Ecke gewichtet (Blenders Vorgabe, seit 2.8), je Punkt. Eine Fläche nach ihrer Größe zu gewichten machte am Körper von Rosemary Winters keinen Unterschied
  (Abweichung gegen Blenders Bild 6,78 → 6,77 von 255, `ProjektTemp/_wegwerf/blendimport_massstab/bake_kalibrieren.py`).
* Tangenten: je Dreieck aus den UV, je Ecke über alle Dreiecke summiert, die denselben Punkt MIT derselben UV teilen — an einer UV-Naht trennen sie sich (wie MikkTSpace); das
  Vorzeichen der Bitangente steht in `w`.
"""

import numpy as np

__all__ = ['Hautbackenflaeche']


class Hautbackenflaeche:
    #: Zwei UV, die sich um weniger unterscheiden, gelten als dieselbe (Naht-Erkennung der Tangenten).
    UV_RUNDUNG = 1.0e5

    def __init__(self, punkte, dreiecke, uv_ecken):
        self.punkte = np.ascontiguousarray(punkte, dtype=np.float64)
        self.dreiecke = np.ascontiguousarray(dreiecke, dtype=np.int32)
        self.uv_ecken = np.ascontiguousarray(uv_ecken, dtype=np.float32)
        if self.dreiecke.ndim != 2 or self.dreiecke.shape[1] != 3 or self.uv_ecken.shape != (len(self.dreiecke), 3, 2):
            raise ValueError('Dreiecke %s und UV je Ecke %s passen nicht zusammen' % (self.dreiecke.shape, self.uv_ecken.shape))
        self._normalen = None
        self._tangenten = None

    @classmethod
    def aus_obj(cls, pfad):
        """Ein OBJ, wie `Blendimportlage.genesis_objs` es schreibt: `v`, `vt` und Dreiecke mit `Punkt/UV` — die UV stehen je Ecke."""
        v, uv, ecken = [], [], []
        with open(pfad, encoding='utf-8') as datei:
            for zeile in datei:
                if zeile.startswith('v '):
                    v.append([float(a) for a in zeile.split()[1:4]])
                elif zeile.startswith('vt '):
                    uv.append([float(a) for a in zeile.split()[1:3]])
                elif zeile.startswith('f '):
                    ecken.append([tuple(int(i) - 1 for i in teil.split('/')[:2]) for teil in zeile.split()[1:]])
        dreiecke, uv_ecken = [], []
        for f in ecken:
            for k in range(1, len(f) - 1):                      # Fächer: ein Viereck wird zwei Dreiecke
                dreiecke.append([f[0][0], f[k][0], f[k + 1][0]])
                uv_ecken.append([uv[f[0][1]], uv[f[k][1]], uv[f[k + 1][1]]])
        return cls(np.array(v), np.array(dreiecke), np.array(uv_ecken))

    # ------------------------------------------------------------------ Normalen, Tangenten

    def _flaechennormalen(self):
        p = self.punkte[self.dreiecke]
        n = np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0])
        return n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1.0e-30)

    def normalen(self):
        """`(N, 3)` float32: je Punkt die Flächennormalen der angrenzenden Dreiecke, nach dem Winkel an der Ecke gewichtet."""
        if self._normalen is None:
            p, fn = self.punkte[self.dreiecke], self._flaechennormalen()
            summe = np.zeros_like(self.punkte)
            for k in range(3):
                e1, e2 = p[:, (k + 1) % 3] - p[:, k], p[:, (k + 2) % 3] - p[:, k]
                kosinus = (e1 * e2).sum(axis=1) / np.maximum(np.linalg.norm(e1, axis=1) * np.linalg.norm(e2, axis=1), 1.0e-30)
                np.add.at(summe, self.dreiecke[:, k], fn * np.arccos(np.clip(kosinus, -1.0, 1.0))[:, None])
            self._normalen = (summe / np.maximum(np.linalg.norm(summe, axis=1, keepdims=True), 1.0e-30)).astype(np.float32)
        return self._normalen

    def tangenten(self):
        """`(M, 3, 4)` float32: je Dreieck und Ecke die Tangente (Richtung wachsendes u, x y z) und das Vorzeichen der Bitangente (w)."""
        if self._tangenten is None:
            p, uv = self.punkte[self.dreiecke], self.uv_ecken.astype(np.float64)
            e1, e2 = p[:, 1] - p[:, 0], p[:, 2] - p[:, 0]
            d1, d2 = uv[:, 1] - uv[:, 0], uv[:, 2] - uv[:, 0]
            det = d1[:, 0] * d2[:, 1] - d2[:, 0] * d1[:, 1]
            r = np.where(np.abs(det) > 1.0e-20, 1.0 / np.where(np.abs(det) > 1.0e-20, det, 1.0), 0.0)[:, None]
            t = (e1 * d2[:, 1:2] - e2 * d1[:, 1:2]) * r
            b = (e2 * d1[:, 0:1] - e1 * d2[:, 0:1]) * r
            # je Ecke: Tangente und Bitangente über die Dreiecke summieren, die Punkt UND UV teilen (Naht trennt)
            schluessel = np.concatenate([self.dreiecke.reshape(-1, 1).astype(np.float64), np.round(uv.reshape(-1, 2) * self.UV_RUNDUNG)], axis=1)
            _, gruppe = np.unique(schluessel, axis=0, return_inverse=True)
            gruppe = gruppe.reshape(-1)
            st, sb = np.zeros((gruppe.max() + 1, 3)), np.zeros((gruppe.max() + 1, 3))
            np.add.at(st, gruppe, np.repeat(t, 3, axis=0))
            np.add.at(sb, gruppe, np.repeat(b, 3, axis=0))
            n = self.normalen()[self.dreiecke.reshape(-1)].astype(np.float64)
            ts = st[gruppe]
            ts = ts - n * (n * ts).sum(axis=1, keepdims=True)
            ts = ts / np.maximum(np.linalg.norm(ts, axis=1, keepdims=True), 1.0e-30)
            vorzeichen = np.where((np.cross(n, ts) * sb[gruppe]).sum(axis=1) < 0.0, -1.0, 1.0)
            self._tangenten = np.concatenate([ts, vorzeichen[:, None]], axis=1).reshape(-1, 3, 4).astype(np.float32)
        return self._tangenten
