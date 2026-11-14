# -*- coding: utf-8 -*-
"""Hbdreiecksuche — der nächste Punkt auf einem Dreiecksnetz und seine UV, vektorisiert.

Für `Bildmodellhautverschiebung` (21.09.2026): 12,8 Mio. Texel der Genesis-9-Kacheln
suchen ihren Oberflächenpunkt auf dem HumanBody-Netz. Kandidaten sind die `K`
Dreiecke mit dem nächsten Schwerpunkt (cKDTree), darunter wird der exakt nächste
Punkt genommen (Ericson, „Real-Time Collision Detection" 5.1.5, als NumPy über alle
Kandidaten zugleich) und seine baryzentrischen Anteile mischen die UVs der drei
ECKEN — je Ecke die UV ihrer Fläche (`uv_loops`), darum stimmt es an Nähten.
Gerechnet in Blöcken (`BLOCK` Punkte × K Kandidaten), sonst wächst der Speicher
auf Gigabytes.
"""
import torch
from KoerperKI_alle.torchfeld import Torchfeld

__all__ = ['Hbdreiecksuche']


class Hbdreiecksuche:
    """Punkte (N, 3), Dreiecke `ecken` (T, 3) Punktnummern, `uvs` (T, 3, 2) je Ecke."""

    K = 8
    BLOCK = 200000
    #: Kerne für die Schwerpunktsuche — nicht alle, Dev-Server und Chrome laufen nebenher.
    KERNE = 2

    def __init__(self, punkte, ecken, uvs):
        from KoerperKI_alle.kartenbaum import Kartenbaum as cKDTree

        self.punkte = Torchfeld.feld(punkte, dtype=torch.float64)
        self.ecken = Torchfeld.feld(ecken, dtype=torch.int64)
        self.uvs = Torchfeld.feld(uvs, dtype=torch.float64)
        self.dreiecke = self.punkte[self.ecken]                           # (T, 3, 3)
        self.baum = cKDTree(self.dreiecke.mean(axis=1))
        self.k = min(self.K, len(self.ecken))

    def uv(self, pos):
        """`(uv (n, 2), abstand (n,))` — UV des nächsten Oberflächenpunkts je Anfragepunkt."""
        pos = Torchfeld.feld(pos, dtype=torch.float64)
        uv = torch.zeros((len(pos), 2), dtype=torch.float64, device='cuda')
        abstand = torch.zeros(len(pos), dtype=torch.float64, device='cuda')
        for anfang in range(0, len(pos), self.BLOCK):
            p = pos[anfang:anfang + self.BLOCK]
            _w, kand = self.baum.query(p, k=self.k, workers=self.KERNE)
            kand = Torchfeld.feld(kand, dtype=torch.int64).reshape(len(p), -1)   # (m, K)
            b, d2 = self.naechster(Torchfeld.repeat_interleave(p, kand.shape[1], dim=0), self.dreiecke[kand.ravel()])
            b = b.reshape(len(p), -1, 3)
            d2 = d2.reshape(len(p), -1)
            beste = d2.argmin(axis=1)
            zeile = Torchfeld.arange(len(p))
            t = kand[zeile, beste]
            uv[anfang:anfang + len(p)] = Torchfeld.einsum('mk,mkc->mc', b[zeile, beste], self.uvs[t])
            abstand[anfang:anfang + len(p)] = Torchfeld.sqrt(d2[zeile, beste])
        return uv, abstand

    @staticmethod
    def naechster(p, dreieck):
        """Nächster Punkt auf je einem Dreieck: `p` (m, 3), `dreieck` (m, 3, 3) →
        `(anteile (m, 3), abstand² (m,))` — Ericson 5.1.5, alle Fälle als Masken."""
        a, b, c = dreieck[:, 0], dreieck[:, 1], dreieck[:, 2]
        ab, ac, ap = b - a, c - a, p - a
        d1, d2 = (ab * ap).sum(1), (ac * ap).sum(1)
        bp = p - b
        d3, d4 = (ab * bp).sum(1), (ac * bp).sum(1)
        cp = p - c
        d5, d6 = (ab * cp).sum(1), (ac * cp).sum(1)
        va, vb, vc = d3 * d6 - d5 * d4, d5 * d2 - d1 * d6, d1 * d4 - d3 * d2
        # Innen (Vorgabe), dann die Fälle in Ericsons Reihenfolge rückwärts überschreiben —
        # so gewinnt der zuerst geprüfte Fall (Ecke A vor Kante AB vor Innen).
        nenner = va + vb + vc
        sicher = Torchfeld.abs(nenner) > 1e-30
        v = torch.where(sicher, vb / torch.where(sicher, nenner, 1.0), 0.0)
        w = torch.where(sicher, vc / torch.where(sicher, nenner, 1.0), 0.0)
        # Kante BC
        m = (va <= 0) & (d4 - d3 >= 0) & (d5 - d6 >= 0)
        t = (d4 - d3) / Torchfeld.maximum((d4 - d3) + (d5 - d6), 1e-30)
        v, w = torch.where(m, 1.0 - t, v), torch.where(m, t, w)
        # Kante AC
        m = (vb <= 0) & (d2 >= 0) & (d6 <= 0)
        t = d2 / Torchfeld.maximum(d2 - d6, 1e-30)
        v, w = torch.where(m, 0.0, v), torch.where(m, t, w)
        # Ecke C
        m = (d6 >= 0) & (d5 <= d6)
        v, w = torch.where(m, 0.0, v), torch.where(m, 1.0, w)
        # Kante AB
        m = (vc <= 0) & (d1 >= 0) & (d3 <= 0)
        t = d1 / Torchfeld.maximum(d1 - d3, 1e-30)
        v, w = torch.where(m, t, v), torch.where(m, 0.0, w)
        # Ecke B
        m = (d3 >= 0) & (d4 <= d3)
        v, w = torch.where(m, 1.0, v), torch.where(m, 0.0, w)
        # Ecke A
        m = (d1 <= 0) & (d2 <= 0)
        v, w = torch.where(m, 0.0, v), torch.where(m, 0.0, w)
        u = 1.0 - v - w
        naechst = a + v[:, None] * ab + w[:, None] * ac
        return Torchfeld.stack([u, v, w], axis=1), ((p - naechst) ** 2).sum(1)
