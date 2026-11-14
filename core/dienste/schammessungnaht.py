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
import torch
from KoerperKI_alle.torchfeld import Torchfeld

__all__ = ['Schammessungnaht']


class Schammessungnaht:
    #: Punkte, die um weniger als das (m) auseinanderliegen, sind derselbe (UV-Nähte teilen sie): Rundung auf 0,01 mm.
    LAGE_M = 1e-5
    #: Breite des Bands am Rand (m), in dem die Knicke der Fläche gezählt werden.
    BAND_M = 0.012

    @classmethod
    def randpunkte(cls, punkte, dreiecke):
        """`(R, 3)` Randpunkte eines Netzes (Kanten mit genau einem Dreieck, nach Lage verschweißt) — auch für den Bake, der zum Rand hin in die Hautfarbe überblendet."""
        return cls(punkte, dreiecke, torch.zeros((0, 3), dtype=torch.float64, device='cuda'), torch.zeros((0, 3), dtype=torch.float64, device='cuda')).rand

    def __init__(self, punkte, dreiecke, ring_lage, ring_normalen, ring_d=None):
        """`punkte`, `dreiecke`: das Stück; `ring_lage`: `(R, 3)` Ringecken; `ring_normalen`: `(R, 3)` Normalen der sichtbaren Haut an den Ringecken (gleiche Reihenfolge);
        `ring_d`: `(R, 3)` Verschiebung der Glättung (optional)."""
        import trimesh

        p = Torchfeld.feld(punkte, dtype=torch.float64)
        schluessel = Torchfeld.astype(Torchfeld.round(p / self.LAGE_M), torch.int64)
        _, erste, rep = Torchfeld.unique(schluessel, axis=0, return_index=True, return_inverse=True)
        d = rep.ravel()[Torchfeld.feld(dreiecke, dtype=torch.int64)]
        self.punkte = p[erste]
        self.netz = trimesh.Trimesh(self.punkte, d, process=False)
        kanten = torch.sort(Torchfeld.cat([d[:, [0, 1]], d[:, [1, 2]], d[:, [2, 0]]]), dim=1, stable=True).values
        eindeutig, zahl = Torchfeld.unique(kanten, axis=0, return_counts=True)
        self.rand_nummern = Torchfeld.unique(eindeutig[zahl == 1])
        #: `(R, 3)` Randpunkte des Stücks.
        self.rand = self.punkte[self.rand_nummern]
        self.ring_lage = Torchfeld.feld(ring_lage, dtype=torch.float64)
        self.ring_normalen = Torchfeld.feld(ring_normalen, dtype=torch.float64)
        self.ring_d = None if ring_d is None else Torchfeld.feld(ring_d, dtype=torch.float64)

    def messen(self):
        from KoerperKI_alle.kartenbaum import Kartenbaum as cKDTree

        from .schammessungrahmen import Schammessungrahmen

        if not len(self.rand):
            return {'hinweis': 'das Stück hat keinen Rand'}
        stat = Schammessungrahmen.statistik
        zum_ring, naechster = cKDTree(self.ring_lage).query(self.rand)
        aus = {'randpunkte': int(len(self.rand)), 'ringecken': int(len(self.ring_lage)), 'rand_zu_ring_mm': stat(zum_ring * 1000.0),
               'ring_zu_rand_mm': stat(cKDTree(self.rand).query(self.ring_lage)[0] * 1000.0)}
        if self.ring_d is not None:
            aus['ring_glaettung_mm'] = stat(Torchfeld.linalg_norm(self.ring_d, dim=1) * 1000.0)
        n_stueck = Torchfeld.feld(self.netz.vertex_normals)[self.rand_nummern]
        n_haut = self.ring_normalen[naechster]
        skalar = Torchfeld.einsum('ij,ij->i', n_stueck, n_haut) / Torchfeld.maximum(Torchfeld.linalg_norm(n_stueck, dim=1) * Torchfeld.linalg_norm(n_haut, dim=1), 1e-12)
        winkel = Torchfeld.degrees(Torchfeld.arccos(Torchfeld.clip(Torchfeld.abs(skalar), 0.0, 1.0)))
        aus['normalen_grad'] = dict(stat(winkel), umgekehrt=round(float((skalar < 0).mean()), 3))
        aus['kanten_am_rand'] = self._kanten(cKDTree(self.rand))
        return aus

    def _kanten(self, baum):
        """Knicke der Fläche im Band `BAND_M` am Rand: Winkel zwischen den Normalen benachbarter Dreiecke, Anteil über 60° und über 90° — die gefalteten Keile am Ring, die im Chrome als
        Sprünge der Naht erscheinen (gesehen 10.10.2026 am seitlichen Ring von „cute girl Daz"). Das Band der Stücke bis 12 mm vom Rand, Kantenmitte als Ort."""
        kanten = self.netz.face_adjacency_edges
        mitte = 0.5 * (self.punkte[kanten[:, 0]] + self.punkte[kanten[:, 1]])
        im_band = baum.query(mitte)[0] <= self.BAND_M
        winkel = Torchfeld.degrees(self.netz.face_adjacency_angles[im_band])
        if not len(winkel):
            return None
        return {'kanten': int(len(winkel)), 'median_grad': round(float(Torchfeld.median(winkel)), 1), 'ueber_60': round(float((winkel > 60).mean()), 3), 'ueber_90': round(float((winkel > 90).mean()), 3)}
