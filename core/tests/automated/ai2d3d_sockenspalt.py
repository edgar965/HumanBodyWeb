# -*- coding: utf-8 -*-
"""Spalten in der Socke der Genesis-Figur — Flächen, die tiefer als TIEFE_MM unter der gaußgeglätteten Socke liegen (die Zehen einzeln statt einer glatten Socke).

Je Socke (zusammenhängendes Stück der Hülle `socken`, über MIN_MM2) und Foto (Haltung des Fotos): die Punkte räumlich gaußgeglättet (σ = SIGMA_MM, über die Punkte der Socke), Tiefe =
Abstand unter der glatten Fläche längs ihrer Normale. Gezählt wird die Punktfläche (ein Drittel der anliegenden Dreiecke) der Punkte tiefer als TIEFE_MM, ohne die Punkte bis
RAND_MM am Rand der Hülle (dort zieht das Glätten den Rand nach innen). Eine Mulde mit dem Radius R liegt unter σ = 8 mm nur ~σ²/2R tief (Knöchel, Spann: R ≥ 30 mm → ≈ 1 mm).

    m = Ai2d3dsockenspalt()
    m.messen(x, dreiecke)      # [(Fläche mm², Spalt mm², tiefste mm)] je Socke
"""
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree

__all__ = ['Ai2d3dsockenspalt']


class Ai2d3dsockenspalt:
    SIGMA_MM, TIEFE_MM, RAND_MM, MIN_MM2 = 8.0, 2.0, 10.0, 5000.0
    BLOCK = 1024

    @staticmethod
    def _normalen(x, tri):
        n = np.cross(x[tri[:, 1]] - x[tri[:, 0]], x[tri[:, 2]] - x[tri[:, 0]])
        vn = np.zeros_like(x)
        for j in range(3):
            np.add.at(vn, tri[:, j], n)
        return vn / np.maximum(np.linalg.norm(vn, axis=1, keepdims=True), 1e-12), n

    def tiefe(self, x, tri):
        """(N,) mm unter der gaußgeglätteten Fläche (positiv = darunter)."""
        s = self.SIGMA_MM / 1000.0
        glatt = np.zeros_like(x)
        for i in range(0, len(x), self.BLOCK):
            d2 = ((x[i:i + self.BLOCK, None] - x[None]) ** 2).sum(2)
            w = np.exp(-d2 / (2 * s * s)) * (d2 < (3 * s) ** 2)
            glatt[i:i + self.BLOCK] = w @ x / w.sum(1, keepdims=True)
        vn, _n = self._normalen(glatt, tri)
        if float(((glatt - glatt.mean(0)) * vn).sum(1).mean()) < 0:
            vn = -vn
        return ((glatt - x) * vn).sum(1) * 1000.0

    def _stuecke(self, n, tri):
        k = np.concatenate([tri[:, [0, 1]], tri[:, [1, 2]], tri[:, [2, 0]]])
        g = coo_matrix((np.ones(len(k)), (k[:, 0], k[:, 1])), shape=(n, n))
        return connected_components(g, directed=False)[1]

    def messen(self, x, tri):
        """x (N, 3) m, tri (T, 3) → [(Fläche mm², Spalt mm², tiefste mm)] je Socke, größte zuerst."""
        x, tri = np.asarray(x, dtype=np.float64), np.asarray(tri, dtype=np.int64)
        _vn, n = self._normalen(x, tri)
        flaeche = np.zeros(len(x))
        for j in range(3):
            np.add.at(flaeche, tri[:, j], np.linalg.norm(n, axis=1) / 6 * 1e6)
        kante = np.sort(np.concatenate([tri[:, [0, 1]], tri[:, [1, 2]], tri[:, [2, 0]]]), 1)
        u, zahl = np.unique(kante, axis=0, return_counts=True)
        rand = np.zeros(len(x), dtype=bool)
        rand[u[zahl == 1].ravel()] = True
        if rand.any():
            nah = cKDTree(x[rand]).query(x, distance_upper_bound=self.RAND_MM / 1000.0)[0] < np.inf
        else:
            nah = rand
        marke = self._stuecke(len(x), tri)
        aus = []
        for m in np.unique(marke):
            k = np.nonzero(marke == m)[0]
            if flaeche[k].sum() < self.MIN_MM2:
                continue
            neu = -np.ones(len(x), dtype=np.int64)
            neu[k] = np.arange(len(k))
            t = neu[tri]
            t = t[(t >= 0).all(1)]
            d = self.tiefe(x[k], t)
            spalt = (d > self.TIEFE_MM) & ~nah[k]
            aus.append((int(flaeche[k].sum()), int(flaeche[k][spalt].sum()), round(float(d[~nah[k]].max()) if (~nah[k]).any() else 0.0, 1)))
        return sorted(aus, reverse=True)

    @staticmethod
    def kunstsocke(rillen=0, tiefe_mm=4.0, breite_mm=3.0):
        """(x, tri) einer glatten Socke ohne Öffnung (Ellipsoid 125 × 50 × 40 mm, ~3 mm Kanten); `rillen` Rillen längs vorn (wie Spalten zwischen Zehen), je `tiefe_mm` tief."""
        nu, nv = 88, 100
        u, v = np.meshgrid(np.linspace(0, np.pi, nu + 2)[1:-1], np.linspace(0, 2 * np.pi, nv, endpoint=False), indexing='ij')
        a, b, c = 0.125, 0.05, 0.04
        x = np.stack([a * np.cos(u), b * np.sin(u) * np.cos(v), c * np.sin(u) * np.sin(v)], -1).reshape(-1, 3)
        x = np.concatenate([x, [[a, 0, 0], [-a, 0, 0]]])
        vorn, hinten = len(x) - 2, len(x) - 1
        i = np.arange(nu - 1)[:, None] * nv + np.arange(nv)[None]
        j = np.arange(nu - 1)[:, None] * nv + (np.arange(nv)[None] + 1) % nv
        ring = np.arange(nv)
        tri = np.concatenate([np.stack([i, i + nv, j], -1).reshape(-1, 3), np.stack([j, i + nv, j + nv], -1).reshape(-1, 3),
                              np.stack([np.full(nv, vorn), ring, (ring + 1) % nv], -1), np.stack([np.full(nv, hinten), (nu - 1) * nv + (ring + 1) % nv, (nu - 1) * nv + ring], -1)])
        for r in range(rillen):
            y0 = (r - (rillen - 1) / 2) * 0.012
            weg = (x[:, 0] > 0.06) & (np.abs(x[:, 1] - y0) < breite_mm / 2000.0) & (x[:, 2] > 0)
            x[weg, 2] -= tiefe_mm / 1000.0
        return x, tri
