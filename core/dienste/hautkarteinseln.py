# -*- coding: utf-8 -*-
u"""Hautkarteinseln — `Maskeninseln.schliessen` auf der Karte (18.11.2026, `Hautkartemaske`): kleine freie Inseln im Verdeckten schließen.

Dieselbe Regel wie JS: zusammenhängende Gruppen freier Punkte (über Dreieckskanten, Punkte gleicher Lage nach den float32-Bits vereint), die über eine
Kante an Verdecktes stoßen, höchstens `hoechstens` Punkte oder `flaeche_max` m² ganz freier Dreiecke haben und nicht die größte Gruppe sind, werden
verdeckt. Statt Union-Find: Etiketten (kleinste Nummer der Gruppe) über die Kanten gereicht, mit Zeigersprung — dieselbe Einteilung. Die Fläche je Gruppe
wird anders aufsummiert als in JS (Reihenfolge der Dreiecke) — nur gleich an der Schwelle könnte das kippen.
"""
import torch

from .hautkartegitter import Hautkartegitter

__all__ = ['Hautkarteinseln']


class Hautkarteinseln:
    TAKT = 4

    @classmethod
    def schliessen(cls, maske, T, hoechstens, pos32, flaeche_max):
        u"""`maske` (n,) uint8 wird ergänzt (neues Feld zurück) — und die Zahl der geschlossenen Punkte (Tensor)."""
        n, g = len(maske), maske.device
        frei = maske == 0
        t = T.reshape(-1, 3)
        a = torch.cat([t[:, 0], t[:, 1], t[:, 2]])
        b = torch.cat([t[:, 1], t[:, 2], t[:, 0]])
        erste = Hautkartegitter.gleiche_bits(pos32)
        naht = (erste != torch.arange(n, device=g)) & frei & frei.index_select(0, erste)
        beide = frei.index_select(0, a) & frei.index_select(0, b)
        u = torch.cat([a[beide], torch.nonzero(naht).reshape(-1)])
        v = torch.cat([b[beide], erste[naht]])
        u, v = torch.cat([u, v]), torch.cat([v, u])
        etikett = torch.arange(n, device=g)
        while True:
            vorher = etikett
            for _ in range(cls.TAKT):
                etikett = etikett.scatter_reduce(0, u, etikett.index_select(0, v), reduce='amin')
                etikett = etikett.index_select(0, etikett)
            if torch.equal(etikett, vorher):
                break
        # Die Küste: freie Gruppen, die über eine Kante an Verdecktes stoßen
        gemischt = frei.index_select(0, a) != frei.index_select(0, b)
        freies_ende = torch.where(frei.index_select(0, a), a, b)[gemischt]
        kueste = torch.zeros(n, dtype=torch.bool, device=g)
        kueste[etikett.index_select(0, freies_ende)] = True
        groesse = torch.bincount(etikett[frei], minlength=n)
        groesste = groesse.max()
        klein = groesse <= hoechstens
        if flaeche_max > 0:
            P = pos32.to(torch.float64)
            ganz = frei.index_select(0, t[:, 0]) & frei.index_select(0, t[:, 1]) & frei.index_select(0, t[:, 2])
            tf = t[ganz]
            A, B, C = P.index_select(0, tf[:, 0]), P.index_select(0, tf[:, 1]), P.index_select(0, tf[:, 2])
            uu, ww = B - A, C - A
            x = uu[:, 1] * ww[:, 2] - uu[:, 2] * ww[:, 1]
            y = uu[:, 2] * ww[:, 0] - uu[:, 0] * ww[:, 2]
            z = uu[:, 0] * ww[:, 1] - uu[:, 1] * ww[:, 0]
            flaeche = torch.zeros(n, dtype=torch.float64, device=g)
            flaeche.index_put_((etikett.index_select(0, tf[:, 0]),), torch.sqrt(x * x + y * y + z * z) / 2, accumulate=True)
            klein = klein | (flaeche <= flaeche_max)
        schliessen = klein & (groesse < groesste) & kueste
        zu = frei & schliessen.index_select(0, etikett)
        return torch.where(zu, torch.ones_like(maske), maske), zu.sum()
