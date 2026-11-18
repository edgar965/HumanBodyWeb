# -*- coding: utf-8 -*-
u"""Hautkartegitter — Gitter und Nachbarschaften der Haut-Maske als Felder auf der Karte (18.11.2026, `Hautkarterechnung`).

`Hautkartegitter(punkte, h)`: wie `Hautmaskegeometrie.punktgitter` (Zelle `floor(p / h)`, Schlüssel `zelle(i, j, k)`), als sortierte Schlüssel und Folge —
je Zelle die Punkte aufsteigend, wie JS sie ansieht (`push` in Punktreihenfolge). `kanten(dreiecke)`: die Kanten eines Netzes einmal, mit ihrer Zahl an
Dreiecken. `csr(von, nach, n)`: Nachbarlisten. `rand_folge`: die Randkanten in der Reihenfolge, in der JS' `Map` sie zuerst sah (`Saumschnitt.kanten`).
"""
import torch

__all__ = ['Hautkartegitter']


class Hautkartegitter:

    def __init__(self, punkte, h):
        self.h = float(h)
        self.punkte = punkte
        z = torch.floor(punkte / self.h).to(torch.int64)
        schl = ((z[:, 0] + 1024) * 2048 + (z[:, 1] + 1024)) * 2048 + (z[:, 2] + 1024)
        self.folge = torch.argsort(schl, stable=True)
        self.schl = schl.index_select(0, self.folge).contiguous()

    @staticmethod
    def kanten(dreiecke, n):
        u"""(Schlüssel a·n + b mit a < b, Zahl der Dreiecke je Kante, erste Stelle im Scan) — der Scan wie JS: je Dreieck (a,b), (b,c), (c,a)."""
        t = dreiecke.reshape(-1, 3).to(torch.int64)
        a = torch.stack([t[:, 0], t[:, 1], t[:, 2]], 1).reshape(-1)
        b = torch.stack([t[:, 1], t[:, 2], t[:, 0]], 1).reshape(-1)
        schl = torch.minimum(a, b) * n + torch.maximum(a, b)
        einzeln, rueck, zahl = torch.unique(schl, return_inverse=True, return_counts=True)
        stelle = torch.full((len(einzeln),), len(schl), dtype=torch.int64, device=schl.device)
        stelle = stelle.scatter_reduce(0, rueck, torch.arange(len(schl), device=schl.device), reduce='amin')
        return einzeln, zahl, stelle

    @staticmethod
    def csr(von, nach, n):
        u"""Nachbarlisten (anfang (n+1,), ziel) aus gerichteten Paaren; je Punkt in der Reihenfolge der Paare."""
        folge = torch.argsort(von, stable=True)
        ziel = nach.index_select(0, folge).contiguous()
        zahl = torch.bincount(von, minlength=n)
        anfang = torch.zeros(n + 1, dtype=torch.int64, device=von.device)
        anfang[1:] = torch.cumsum(zahl, 0)
        return anfang, ziel

    @staticmethod
    def gleiche_lage(punkte):
        u"""Je Punkt die Nummer des ersten Punkts gleicher Lage (Werte gleich, −0 wie 0 — JS vergleicht Zeichenketten von Zahlen), aufsteigend."""
        return Hautkartegitter.gleiche_zeilen(punkte + 0.0)

    @staticmethod
    def gleiche_bits(punkte32):
        u"""Wie `gleiche_lage`, aber nach den Bits der float32-Lage (`Maskeninseln.gleicheLage`: −0 und 0 sind verschieden)."""
        return Hautkartegitter.gleiche_zeilen(punkte32.contiguous().view(torch.int32))

    @staticmethod
    def gleiche_zeilen(p):
        u"""Je Zeile die Nummer der ersten gleichen Zeile."""
        n = len(p)
        folge = torch.arange(n, device=p.device)
        for d in (2, 1, 0):                                     # lexikographisch, stabil: zuletzt nach x
            folge = folge.index_select(0, torch.argsort(p[folge, d], stable=True))
        q = p.index_select(0, folge)
        neu = torch.ones(n, dtype=torch.bool, device=p.device)
        if n > 1:
            neu[1:] = (q[1:] != q[:-1]).any(1)
        gruppe = torch.cumsum(neu.to(torch.int64), 0) - 1
        erste = torch.full((int(n),), n, dtype=torch.int64, device=p.device)
        erste = erste.scatter_reduce(0, gruppe, folge, reduce='amin')
        aus = torch.empty(n, dtype=torch.int64, device=p.device)
        aus[folge] = erste.index_select(0, gruppe)
        return aus
