# -*- coding: utf-8 -*-
u"""Hautkartenormalen — `Hautmaskegeometrie.normalen` auf der Karte (18.11.2026, `Hautkarterechnung`).

Wie JS: je Dreieck das Kreuzprodukt (ungeteilt), je Punkt die Summe in der Reihenfolge der Dreiecke (ein Faden je Punkt über seine Einträge, sortiert
nach Dreieck und Ecke — dieselben Additionen in derselben Folge); deckungsgleiche Punkte legen ihre Summen beim ersten zusammen, aufsteigend, und
übernehmen sie; Vorzeichen über das signierte Volumen; normiert mit `hypot3` (V8s `Math.hypot`) — `vz · N / l`. Die Kerne `hk_summen`, `hk_naehte`,
`hk_normieren` (`hautkartekerne_cu/hautkartenormalen.cuh`, `Hautkartekernbau`) — bis 21.11.2026 Warp-Kerne in dieser Datei.
"""
import torch

from .hautkartegitter import Hautkartegitter
from .hautkartekernbau import Hautkartekernbau

__all__ = ['Hautkartenormalen']

F64, I64 = torch.float64, torch.int64
_a = Hautkartekernbau.feld


class Hautkartenormalen:

    @staticmethod
    def rechnen(P, T):
        u"""(n, 3) float64 Punkte, (m, 3) int64 Dreiecke → (n, 3) float64 Außennormalen wie JS."""
        n, g = len(P), P.device
        rufen = Hautkartekernbau.rufen
        ecke = T.reshape(-1)
        dreieck = torch.arange(len(T), device=g).repeat_interleave(3)
        anfang, eintrag = Hautkartegitter.csr(ecke, dreieck, n)          # je Punkt die Dreiecke in Scan-Reihenfolge (stabil)
        roh = torch.empty((n, 3), dtype=torch.float64, device=g)
        with torch.cuda.device(g):
            if n:
                rufen('hk_summen', n, _a(P, F64), _a(T, I64), _a(anfang, I64), _a(eintrag, I64), roh)
            erste = Hautkartegitter.gleiche_lage(P)
            anfang_g, glied = Hautkartegitter.csr(erste, torch.arange(n, device=g), n)
            mit = anfang_g[1:] > anfang_g[:-1]
            gruppen = torch.nonzero(mit).reshape(-1)
            anfang_gruppe = torch.cat([anfang_g[:-1][mit], anfang_g[-1:]])
            N = roh.clone()
            if len(gruppen):
                rufen('hk_naehte', len(gruppen), roh, _a(anfang_gruppe, I64), _a(glied, I64), N)
            t = T.reshape(-1, 3)
            A, B, C = P[t[:, 0]], P[t[:, 1]], P[t[:, 2]]
            vol = (A[:, 0] * (B[:, 1] * C[:, 2] - B[:, 2] * C[:, 1]) - A[:, 1] * (B[:, 0] * C[:, 2] - B[:, 2] * C[:, 0])
                   + A[:, 2] * (B[:, 0] * C[:, 1] - B[:, 1] * C[:, 0])).sum()
            vz = 1.0 if float(vol) >= 0 else -1.0          # eine Zahl je Rechnung: das Vorzeichen
            if n:
                rufen('hk_normieren', n, N, vz)
        return N
