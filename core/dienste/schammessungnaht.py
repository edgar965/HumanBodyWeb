# -*- coding: utf-8 -*-
"""Schammessungnaht — wie sitzt der Rand des Scham-Stücks auf dem Loch der Haut? (10.10.2026)

Edgar: „die Naht ist noch sichtbar". Was die Naht im Bild verrät, ist gemessen (09.10.2026, `messung_naht.js`): die Normalen am Rand weichen von denen der Haut ab (98 Ringecken:
Median 19°, p90 73°, größter 82°) — das Licht springt, nicht die Geometrie. Hier die Zahlen, die vor dem Bild stehen:

    rand_zu_ring_mm     jeder Randpunkt des Stücks → nächste Ringecke (Lage nach der Glättung im Bau) und umgekehrt: 0 heißt „Kante an Kante", ein Spalt beginnt über ~0,1 mm
    ring_glaettung_mm   um so viel rückte die Glättung den Ring gegen die Haut (der Browser rückt den Rand zur Laufzeit auf die Haut, wie sie dann ist: `stuecknaht.js`)
    normalen_grad       Winkel zwischen der Normale des Stücks am Randpunkt und der Normale der sichtbaren Haut an der zugehörigen Ringecke (Betrag des Skalarprodukts, also ohne Drehsinn);
                        `umgekehrt` = Anteil der Randpunkte, deren Normalen gegeneinander zeigen (Wicklung)
Der Rand sind die Kanten mit genau einem Dreieck, nach Lage verschweißt (UV-Nähte zählen nicht).
"""
import numpy as np

__all__ = ['Schammessungnaht']


class Schammessungnaht:
    #: Punkte, die um weniger als das (m) auseinanderliegen, sind derselbe (UV-Nähte teilen sie): Rundung auf 0,01 mm.
    LAGE_M = 1e-5

    def __init__(self, punkte, dreiecke, ring_lage, ring_normalen, ring_d=None):
        """`punkte`, `dreiecke`: das Stück; `ring_lage`: `(R, 3)` Ringecken; `ring_normalen`: `(R, 3)` Normalen der sichtbaren Haut an den Ringecken (gleiche Reihenfolge);
        `ring_d`: `(R, 3)` Verschiebung der Glättung (optional)."""
        import trimesh

        p = np.asarray(punkte, dtype=np.float64)
        schluessel = np.round(p / self.LAGE_M).astype(np.int64)
        _, erste, rep = np.unique(schluessel, axis=0, return_index=True, return_inverse=True)
        d = rep.ravel()[np.asarray(dreiecke, dtype=np.int64)]
        self.punkte = p[erste]
        self.netz = trimesh.Trimesh(self.punkte, d, process=False)
        kanten = np.sort(np.concatenate([d[:, [0, 1]], d[:, [1, 2]], d[:, [2, 0]]]), axis=1)
        eindeutig, zahl = np.unique(kanten, axis=0, return_counts=True)
        self.rand_nummern = np.unique(eindeutig[zahl == 1])
        #: `(R, 3)` Randpunkte des Stücks.
        self.rand = self.punkte[self.rand_nummern]
        self.ring_lage = np.asarray(ring_lage, dtype=np.float64)
        self.ring_normalen = np.asarray(ring_normalen, dtype=np.float64)
        self.ring_d = None if ring_d is None else np.asarray(ring_d, dtype=np.float64)

    def messen(self):
        from scipy.spatial import cKDTree

        from .schammessungrahmen import Schammessungrahmen

        if not len(self.rand):
            return {'hinweis': 'das Stück hat keinen Rand'}
        stat = Schammessungrahmen.statistik
        zum_ring, naechster = cKDTree(self.ring_lage).query(self.rand)
        aus = {'randpunkte': int(len(self.rand)), 'ringecken': int(len(self.ring_lage)), 'rand_zu_ring_mm': stat(zum_ring * 1000.0),
               'ring_zu_rand_mm': stat(cKDTree(self.rand).query(self.ring_lage)[0] * 1000.0)}
        if self.ring_d is not None:
            aus['ring_glaettung_mm'] = stat(np.linalg.norm(self.ring_d, axis=1) * 1000.0)
        n_stueck = np.asarray(self.netz.vertex_normals)[self.rand_nummern]
        n_haut = self.ring_normalen[naechster]
        skalar = np.einsum('ij,ij->i', n_stueck, n_haut) / np.maximum(np.linalg.norm(n_stueck, axis=1) * np.linalg.norm(n_haut, axis=1), 1e-12)
        winkel = np.degrees(np.arccos(np.clip(np.abs(skalar), 0.0, 1.0)))
        aus['normalen_grad'] = dict(stat(winkel), umgekehrt=round(float((skalar < 0).mean()), 3))
        return aus
