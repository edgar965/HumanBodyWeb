# -*- coding: utf-8 -*-
"""Schammessungknick — der Knick der Fläche ÜBER die Naht, Kante für Kante (11.10.2026).

Warum eine eigene Messgröße: die Normalenwinkel am Ring (`Schammessungnaht`) vergleichen Punktnormalen — sie sahen am Ring 17 und 59 des Daz-Stücks „gut" aus (Median 9°), während
im Chrome die Naht dort sprang. Gemessen wurde danach an jeder Ringkante der Winkel zwischen dem Hautdreieck und dem Stückdreieck, die sich die Kante teilen: an vier Kanten
(16/17 und 58/59) lagen sie mit 147–160° aufeinander zurückgeklappt, an weiteren acht über 30°. Die Haut wird dabei so genommen, wie der Browser sie zeigt: mit der Verschiebung der
Glättung des Rings (`loch['verschiebung']`, `Hauteinzug`).

    kanten            Zahl der Ringkanten, an denen ein Haut- und ein Stückdreieck gefunden wurden
    median_grad, p90_grad, max_grad   Knick (Winkel der Flächennormalen) in Grad
    ueber_30, ueber_60, ueber_90      Zahl der Kanten darüber (über 90° = das Stück liegt auf der Haut zurückgeklappt)
    schlimmste        die fünf größten: `[Ringecke, Grad]`
"""
import numpy as np

__all__ = ['Schammessungknick']


class Schammessungknick:
    #: Ein Punkt gilt als auf dem Ring, wenn er höchstens so weit (m) von der Ringecke liegt.
    LAGE_M = 1e-7

    @staticmethod
    def haut_lage(figur, loch):
        """Die Punkte der Figur, wie der Browser sie zeigt: mit der Verschiebung der Ringpunkte (`loch['verschiebung']`)."""
        fp = np.array(figur['punkte'], dtype=np.float64)
        v = (loch or {}).get('verschiebung')
        if v is not None and len(v['punkte']):
            fp[np.asarray(v['punkte'], dtype=np.int64)] += np.asarray(v['d'], dtype=np.float64)
        return fp

    @staticmethod
    def sichtbare(figur, loch):
        """Die Dreiecke der Haut ohne die des Lochs, `(M, 3)`."""
        fd = np.asarray(figur['dreiecke'], dtype=np.int64)
        sichtbar = np.ones(len(fd), dtype=bool)
        sichtbar[np.asarray(loch['dreiecke'], dtype=np.int64)] = False
        return fd[sichtbar]

    @staticmethod
    def normale(p, t):
        n = np.cross(p[t[1]] - p[t[0]], p[t[2]] - p[t[0]])
        return n / max(float(np.linalg.norm(n)), 1e-30)

    @classmethod
    def ringkanten(cls, fp, haut, ring_punkte):
        """`[(j, Dreieck der Haut)]` für jede Ringkante `j → j+1`, die als Kante in einem sichtbaren Hautdreieck steht (einige Kanten des Rings sind Sehnen: dort fehlt sie)."""
        ring_punkte = np.asarray(ring_punkte, dtype=np.int64)
        k = len(ring_punkte)
        hat = np.isin(haut, ring_punkte).any(axis=1)
        kante = {}
        for t in haut[hat]:
            for e in range(3):
                kante[(int(t[e]), int(t[(e + 1) % 3]))] = t
        aus = []
        for j in range(k):
            a, b = int(ring_punkte[j]), int(ring_punkte[(j + 1) % k])
            t = kante.get((a, b), kante.get((b, a)))
            if t is not None:
                aus.append((j, t))
        return aus

    @classmethod
    def winkel(cls, punkte, dreiecke, figur, loch):
        """`[(j, Grad)]`: der Knick über die Ringkante `j → j+1` (Winkel zwischen den Flächennormalen des Haut- und des Stückdreiecks), für jede Kante, an der beide gefunden wurden."""
        from scipy.spatial import cKDTree

        p = np.asarray(punkte, dtype=np.float64)
        d = np.asarray(dreiecke, dtype=np.int64).reshape(-1, 3)
        ring = np.asarray(loch['ring'], dtype=np.float64)
        k = len(ring)
        fp = cls.haut_lage(figur, loch)
        kanten = cls.ringkanten(fp, cls.sichtbare(figur, loch), loch['ring_punkte'])
        auf_ring = [np.asarray(x, dtype=np.int64) for x in cKDTree(p).query_ball_point(ring, cls.LAGE_M)]
        stueck = {}
        for t in d:
            for e in range(3):
                stueck[(int(t[e]), int(t[(e + 1) % 3]))] = t
        aus = []
        for j, haut_dreieck in kanten:
            tb = next((stueck[xy] for x in auf_ring[j] for y in auf_ring[(j + 1) % k] for xy in ((int(x), int(y)), (int(y), int(x))) if xy in stueck), None)
            if tb is not None:
                aus.append((j, float(np.degrees(np.arccos(np.clip(cls.normale(fp, haut_dreieck) @ cls.normale(p, tb), -1.0, 1.0))))))
        return aus

    @classmethod
    def messen(cls, punkte, dreiecke, figur, loch):
        winkel = cls.winkel(punkte, dreiecke, figur, loch)
        if not winkel:
            return {'kanten': 0, 'hinweis': 'keine Ringkante mit Haut- und Stückdreieck gefunden'}
        w = np.array([x[1] for x in winkel])
        schlimm = sorted(winkel, key=lambda x: -x[1])[:5]
        return {'kanten': int(len(w)), 'median_grad': round(float(np.median(w)), 1), 'p90_grad': round(float(np.percentile(w, 90)), 1), 'max_grad': round(float(w.max()), 1),
                'ueber_30': int((w > 30).sum()), 'ueber_60': int((w > 60).sum()), 'ueber_90': int((w > 90).sum()), 'schlimmste': [[int(j), round(g, 1)] for j, g in schlimm]}
