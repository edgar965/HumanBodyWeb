# -*- coding: utf-8 -*-
"""Blendimportschamring — den Kantenring des Hautlochs zu einer glatten Linie ziehen (09.10.2026).

BEFUND (Chrome, „cute girl", Haut und Stück nach dem Verschweißen, `Blendimportschamnaht`): Der Rand des Lochs besteht aus Kanten der
Haut — 2,3 bis 9 mm lang, mit Richtungswechseln bis 100° (die Dreiecke der Stufe 1 sind an den Leisten schmal und lang). Die Naht ist
dicht, aber ihre Linie ist gezähnt: Zähne von 2–3 mm, wo Stück und Haut verschieden aussehen (Poren, Härchen), und Edgar sah „gesägte
Zipfel". Bei Genesis läuft der Rand von Mund und Nase auf einer glatten Kantenfolge.

HIER: Die Ecken des Rings werden entlang der Fläche zur Mitte ihrer Nachbarn gezogen (Laplace, `DURCHGAENGE`), höchstens `MAX_MM`
weit und nur in der Tangentialebene (nicht in die Haut hinein). Eine Verschiebung, die ein Hautdreieck außerhalb des Lochs umklappen
würde, wird halbiert. Das Stück liegt danach auf der geglätteten Linie, und der Browser verschiebt die Hautpunkte des Rings um
dieselbe Strecke (`Hauteinzug`, `stueckloch.js`) — die Naht bleibt dicht, die Linie ist glatt. Ohne Django.
"""

import torch
from KoerperKI_alle.torchfeld import Torchfeld

__all__ = ['Blendimportschamring']


class Blendimportschamring:
    #: Durchgänge und Anteil, mit dem jede Ecke in die Mitte ihrer beiden Nachbarn rückt.
    DURCHGAENGE = 20
    ANTEIL = 0.5
    #: Weiter als das (mm) wandert keine Ecke — die Haut daneben soll nicht sichtbar verzerrt werden. Bei 2,5 mm blieben an den oberen
    #: Ecken des Rings Kerben von 5 mm (gesehen im Chrome, „cute girl", 09.10.2026).
    MAX_MM = 4.0
    #: Höchstens so oft wird eine Verschiebung halbiert, die ein Dreieck umklappt.
    HALBIERUNGEN = 6

    @staticmethod
    def normalen(punkte, dreiecke):
        """Flächengewichtete Punktnormalen (Länge 1)."""
        a, b, c = (punkte[dreiecke[:, i]] for i in range(3))
        flaeche = Torchfeld.cross(b - a, c - a)
        summe = torch.zeros_like(punkte)
        for i in range(3):
            Torchfeld.add_at(summe, dreiecke[:, i], flaeche)
        return summe / Torchfeld.maximum(Torchfeld.linalg_norm(summe, dim=1, keepdim=True), 1e-12)

    @classmethod
    def glaetten(cls, lage, normalen):
        """Die geglätteten Ecken `(k, 3)` des geschlossenen Rings `lage` mit den Normalen der Haut an seinen Ecken."""
        ziel = Torchfeld.kopie(Torchfeld.feld(lage, dtype=torch.float64))
        n = Torchfeld.feld(normalen, dtype=torch.float64)
        grenze = cls.MAX_MM / 1000.0
        for _ in range(cls.DURCHGAENGE):
            mittel = 0.5 * (torch.roll(ziel, 1, dims=0) + torch.roll(ziel, -1, dims=0))
            d = mittel - ziel
            d -= (d * n).sum(axis=1, keepdims=True) * n
            ziel = ziel + cls.ANTEIL * d
            v = ziel - lage
            laenge = Torchfeld.linalg_norm(v, dim=1, keepdim=True)
            ziel = lage + v * Torchfeld.minimum(1.0, grenze / Torchfeld.maximum(laenge, 1e-12))
        return ziel

    @staticmethod
    def flaechennormalen(punkte, dreiecke):
        """Nicht normierte Flächennormale je Dreieck."""
        return Torchfeld.cross(punkte[dreiecke[:, 1]] - punkte[dreiecke[:, 0]], punkte[dreiecke[:, 2]] - punkte[dreiecke[:, 0]])

    @classmethod
    def ziehen(cls, punkte, dreiecke, im_loch, ring_punkte, lage, normalen):
        """`(neue Lage des Rings, verschiebung)`: geglättet, und wo ein Hautdreieck AUSSERHALB des Lochs umklappte, kürzer.
        `verschiebung`: `{punkte: Nummern ALLER Figurpunkte auf dem Ring, d: ihre Verschiebung (m), halbiert: Zahl gekürzter Ecken}`.

        `punkte`/`dreiecke`: die Haut; `im_loch` je Dreieck; `ring_punkte`: die Nummern der Figurpunkte der Ecken (eine Nummer je
        Lage — Doppelgänger an UV-Nähten gelten gleich, sie liegen auf derselben Lage und ziehen mit)."""
        ziel = cls.glaetten(lage, normalen)
        schluessel = Torchfeld.astype(Torchfeld.round(punkte / 1e-6), torch.int64)
        _, rep = Torchfeld.unique(schluessel, axis=0, return_inverse=True)
        rep = rep.ravel()
        je_ecke = {int(rep[p]): i for i, p in enumerate(ring_punkte)}
        aussen = dreiecke[~im_loch]
        ecke_je_punkt = Torchfeld.feld([je_ecke.get(int(r), -1) for r in rep], copy=True)
        betroffen = (ecke_je_punkt[aussen] >= 0).any(axis=1)
        aussen = aussen[betroffen]
        halbiert = torch.zeros(len(lage), dtype=torch.bool, device='cuda')
        for _ in range(cls.HALBIERUNGEN + 1):
            verschiebung = torch.zeros_like(punkte)
            gehoert = ecke_je_punkt >= 0
            verschiebung[gehoert] = (ziel - lage)[ecke_je_punkt[gehoert]]
            vorher = cls.flaechennormalen(punkte, aussen)
            schlecht = (vorher * cls.flaechennormalen(punkte + verschiebung, aussen)).sum(axis=1) <= 0.0
            if not schlecht.any():
                break
            ecken = Torchfeld.unique(ecke_je_punkt[aussen[schlecht]].ravel())
            ecken = ecken[ecken >= 0]
            ziel[ecken] = lage[ecken] + 0.5 * (ziel[ecken] - lage[ecken])
            halbiert[ecken] = True
        ids = torch.flatten(ecke_je_punkt >= 0).nonzero()[:, 0]
        return ziel, {'punkte': Torchfeld.astype(ids, torch.int64), 'd': (ziel - lage)[ecke_je_punkt[ids]], 'halbiert': int(halbiert.sum())}
