# -*- coding: utf-8 -*-
u"""Hautkartewege — `Hautwege.wege` auf der Karte (18.11.2026, `Hautkarterechnung`): kürzeste Wege über die Netzkanten von vielen Quellen.

JS rechnet Dijkstra mit Halde; hier Kanten gleichzeitig entspannt, bis sich nichts mehr ändert. Der Fixpunkt ist derselbe — je Punkt das Minimum über
die Nachbarn von (Weg des Nachbarn + Kantenlänge), Quellen 0 —, also dieselben Zahlen. Weiter gerechnet wird nur von Punkten innerhalb der Reichweite
(Dijkstra bricht dort ab); darüber `inf`. Kantenlänge wie `Math.hypot` in V8 (größter Betrag, Kahan-Summe der Quotienten), Nähte (gleiche Lage,
`Hautkartegitter.gleiche_lage`) mit Länge 0. Geprüft wird alle `TAKT` Runden, ob sich etwas änderte (ein Abholen je Prüfung).
"""
import torch

from .hautkartegitter import Hautkartegitter

__all__ = ['Hautkartewege']


class Hautkartewege:
    #: Runden zwischen zwei Prüfungen auf Stillstand.
    TAKT = 8
    #: Sicherung: mehr Runden als Punkte braucht kein kürzester Weg.
    HOECHSTENS = 100000

    @staticmethod
    def hypot(dx, dy, dz):
        u"""V8s `Math.hypot` für drei Werte, elementweise (jede Rechnung ein eigener Kern — keine FMA)."""
        a, b, c = dx.abs(), dy.abs(), dz.abs()
        m = torch.maximum(torch.maximum(a, b), c)
        teiler = torch.where(m == 0, torch.ones_like(m), m)
        s = torch.zeros_like(m)
        k = torch.zeros_like(m)
        for w in (a, b, c):
            n = w / teiler
            summand = n * n - k
            vorl = s + summand
            k = (vorl - s) - summand
            s = vorl
        return torch.where(m == 0, torch.zeros_like(m), torch.sqrt(s) * m)

    @classmethod
    def kanten(cls, P, T):
        u"""Gerichtete Kanten (von, nach, Länge) — je Dreieck (a,b), (b,c), (c,a) in beide Richtungen, dazu die Nähte."""
        t = T.reshape(-1, 3).to(torch.int64)
        erste = Hautkartegitter.gleiche_lage(P)
        naht = torch.nonzero(erste != torch.arange(len(P), device=P.device)).reshape(-1)
        a = torch.cat([t[:, 0], t[:, 1], t[:, 2], naht])
        b = torch.cat([t[:, 1], t[:, 2], t[:, 0], erste.index_select(0, naht)])
        von, nach = torch.cat([a, b]), torch.cat([b, a])
        d = P.index_select(0, nach) - P.index_select(0, von)
        return von, nach, cls.hypot(d[:, 0], d[:, 1], d[:, 2])

    @classmethod
    def wege(cls, P, T, quellen, reichweite, kanten=None):
        u"""(n,) float64: Weg zur nächsten Quelle (`quellen` (n,) bool), höchstens `reichweite`, darüber inf."""
        von, nach, laenge = kanten if kanten is not None else cls.kanten(P, T)
        inf = torch.tensor(float('inf'), dtype=torch.float64, device=P.device)
        weg = torch.where(quellen, torch.zeros((), dtype=torch.float64, device=P.device), inf)
        runde = 0
        while runde < cls.HOECHSTENS:
            vorher = weg
            for _ in range(cls.TAKT):
                quelle = weg.index_select(0, von)
                neu = torch.where(quelle <= reichweite, quelle + laenge, inf)
                weg = weg.scatter_reduce(0, nach, neu, reduce='amin')
            runde += cls.TAKT
            if torch.equal(weg, vorher):
                break
        return torch.where(weg > reichweite, inf, weg)
