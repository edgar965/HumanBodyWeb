# -*- coding: utf-8 -*-
u"""Hautkartenormalen — `Hautmaskegeometrie.normalen` auf der Karte (18.11.2026, `Hautkarterechnung`).

Wie JS: je Dreieck das Kreuzprodukt (ungeteilt), je Punkt die Summe in der Reihenfolge der Dreiecke (ein Faden je Punkt über seine Einträge, sortiert
nach Dreieck und Ecke — dieselben Additionen in derselben Folge); deckungsgleiche Punkte legen ihre Summen beim ersten zusammen, aufsteigend, und
übernehmen sie; Vorzeichen über das signierte Volumen; normiert mit `hypot3` (V8s `Math.hypot`) — `vz · N / l`.
"""
import sys

import torch
import warp as wp

from .hautkartegitter import Hautkartegitter
from .hautkartewarphilfe import hypot3

wp.set_module_options({'fuse_fp': False, 'enable_backward': False})

__all__ = ['Hautkartenormalen']


@wp.kernel
def summen(P: wp.array2d(dtype=wp.float64), T: wp.array2d(dtype=wp.int64), anfang: wp.array(dtype=wp.int64), eintrag: wp.array(dtype=wp.int64),
           N: wp.array2d(dtype=wp.float64)):
    i = wp.tid()
    sx = wp.float64(0.0)
    sy = wp.float64(0.0)
    sz = wp.float64(0.0)
    for e in range(int(anfang[i]), int(anfang[i + 1])):
        k = int(eintrag[e])
        a = int(T[k, 0])
        b = int(T[k, 1])
        c = int(T[k, 2])
        ux = P[b, 0] - P[a, 0]
        uy = P[b, 1] - P[a, 1]
        uz = P[b, 2] - P[a, 2]
        vx = P[c, 0] - P[a, 0]
        vy = P[c, 1] - P[a, 1]
        vz = P[c, 2] - P[a, 2]
        sx = sx + (uy * vz - uz * vy)
        sy = sy + (uz * vx - ux * vz)
        sz = sz + (ux * vy - uy * vx)
    N[i, 0] = sx
    N[i, 1] = sy
    N[i, 2] = sz


@wp.kernel
def naehte(N: wp.array2d(dtype=wp.float64), anfang: wp.array(dtype=wp.int64), glied: wp.array(dtype=wp.int64), aus: wp.array2d(dtype=wp.float64)):
    # je Gruppe deckungsgleicher Punkte (erster zuerst, dann aufsteigend): N[erster] += N[i] der Reihe nach, alle übernehmen die Summe
    g = wp.tid()
    von = int(anfang[g])
    bis = int(anfang[g + 1])
    erster = int(glied[von])
    sx = N[erster, 0]
    sy = N[erster, 1]
    sz = N[erster, 2]
    for e in range(von + 1, bis):
        i = int(glied[e])
        sx = sx + N[i, 0]
        sy = sy + N[i, 1]
        sz = sz + N[i, 2]
    for e in range(von, bis):
        i = int(glied[e])
        aus[i, 0] = sx
        aus[i, 1] = sy
        aus[i, 2] = sz


@wp.kernel
def normieren(N: wp.array2d(dtype=wp.float64), vz: wp.float64):
    i = wp.tid()
    laenge = hypot3(N[i, 0], N[i, 1], N[i, 2])
    if laenge == wp.float64(0.0):
        laenge = wp.float64(1.0)
    N[i, 0] = vz * N[i, 0] / laenge
    N[i, 1] = vz * N[i, 1] / laenge
    N[i, 2] = vz * N[i, 2] / laenge


wp.load_module(sys.modules[__name__], device='cuda')


class Hautkartenormalen:

    @staticmethod
    def rechnen(P, T):
        u"""(n, 3) float64 Punkte, (m, 3) int64 Dreiecke → (n, 3) float64 Außennormalen wie JS."""
        n, g = len(P), P.device
        a = lambda t, typ: wp.from_torch(t.contiguous(), dtype=typ)  # noqa: E731
        ecke = T.reshape(-1)
        dreieck = torch.arange(len(T), device=g).repeat_interleave(3)
        anfang, eintrag = Hautkartegitter.csr(ecke, dreieck, n)          # je Punkt die Dreiecke in Scan-Reihenfolge (stabil)
        roh = torch.empty((n, 3), dtype=torch.float64, device=g)
        strom = wp.stream_from_torch(torch.cuda.current_stream(g))
        if n:
            wp.launch(summen, dim=n, inputs=[a(P, wp.float64), a(T, wp.int64), a(anfang, wp.int64), a(eintrag, wp.int64), wp.from_torch(roh, dtype=wp.float64)],
                      stream=strom)
        erste = Hautkartegitter.gleiche_lage(P)
        anfang_g, glied = Hautkartegitter.csr(erste, torch.arange(n, device=g), n)
        mit = anfang_g[1:] > anfang_g[:-1]
        gruppen = torch.nonzero(mit).reshape(-1)
        anfang_gruppe = torch.cat([anfang_g[:-1][mit], anfang_g[-1:]])
        N = roh.clone()
        if len(gruppen):
            wp.launch(naehte, dim=len(gruppen), inputs=[wp.from_torch(roh, dtype=wp.float64), a(anfang_gruppe, wp.int64), a(glied, wp.int64),
                                                         wp.from_torch(N, dtype=wp.float64)], stream=strom)
        t = T.reshape(-1, 3)
        A, B, C = P[t[:, 0]], P[t[:, 1]], P[t[:, 2]]
        vol = (A[:, 0] * (B[:, 1] * C[:, 2] - B[:, 2] * C[:, 1]) - A[:, 1] * (B[:, 0] * C[:, 2] - B[:, 2] * C[:, 0])
               + A[:, 2] * (B[:, 0] * C[:, 1] - B[:, 1] * C[:, 0])).sum()
        vz = 1.0 if float(vol) >= 0 else -1.0          # eine Zahl je Rechnung: das Vorzeichen
        if n:
            wp.launch(normieren, dim=n, inputs=[wp.from_torch(N, dtype=wp.float64), vz], stream=strom)
        return N
