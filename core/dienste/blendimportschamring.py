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

import numpy as np

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
        flaeche = np.cross(b - a, c - a)
        summe = np.zeros_like(punkte)
        for i in range(3):
            np.add.at(summe, dreiecke[:, i], flaeche)
        return summe / np.maximum(np.linalg.norm(summe, axis=1, keepdims=True), 1e-12)

    @classmethod
    def glaetten(cls, lage, normalen):
        """Die geglätteten Ecken `(k, 3)` des geschlossenen Rings `lage` mit den Normalen der Haut an seinen Ecken."""
        ziel = np.asarray(lage, dtype=np.float64).copy()
        n = np.asarray(normalen, dtype=np.float64)
        grenze = cls.MAX_MM / 1000.0
        for _ in range(cls.DURCHGAENGE):
            mittel = 0.5 * (np.roll(ziel, 1, axis=0) + np.roll(ziel, -1, axis=0))
            d = mittel - ziel
            d -= (d * n).sum(axis=1, keepdims=True) * n
            ziel = ziel + cls.ANTEIL * d
            v = ziel - lage
            laenge = np.linalg.norm(v, axis=1, keepdims=True)
            ziel = lage + v * np.minimum(1.0, grenze / np.maximum(laenge, 1e-12))
        return ziel

    @staticmethod
    def flaechennormalen(punkte, dreiecke):
        """Nicht normierte Flächennormale je Dreieck."""
        return np.cross(punkte[dreiecke[:, 1]] - punkte[dreiecke[:, 0]], punkte[dreiecke[:, 2]] - punkte[dreiecke[:, 0]])

    @classmethod
    def ziehen(cls, punkte, dreiecke, im_loch, ring_punkte, lage, normalen):
        """`(neue Lage des Rings, verschiebung)`: geglättet, und wo ein Hautdreieck AUSSERHALB des Lochs umklappte, kürzer.
        `verschiebung`: `{punkte: Nummern ALLER Figurpunkte auf dem Ring, d: ihre Verschiebung (m), halbiert: Zahl gekürzter Ecken}`.

        `punkte`/`dreiecke`: die Haut; `im_loch` je Dreieck; `ring_punkte`: die Nummern der Figurpunkte der Ecken (eine Nummer je
        Lage — Doppelgänger an UV-Nähten gelten gleich, sie liegen auf derselben Lage und ziehen mit)."""
        ziel = cls.glaetten(lage, normalen)
        schluessel = np.round(punkte / 1e-6).astype(np.int64)
        _, rep = np.unique(schluessel, axis=0, return_inverse=True)
        rep = rep.ravel()
        je_ecke = {int(rep[p]): i for i, p in enumerate(ring_punkte)}
        aussen = dreiecke[~im_loch]
        ecke_je_punkt = np.array([je_ecke.get(int(r), -1) for r in rep])
        betroffen = (ecke_je_punkt[aussen] >= 0).any(axis=1)
        aussen = aussen[betroffen]
        halbiert = np.zeros(len(lage), dtype=bool)
        for _ in range(cls.HALBIERUNGEN + 1):
            verschiebung = np.zeros_like(punkte)
            gehoert = ecke_je_punkt >= 0
            verschiebung[gehoert] = (ziel - lage)[ecke_je_punkt[gehoert]]
            vorher = cls.flaechennormalen(punkte, aussen)
            schlecht = (vorher * cls.flaechennormalen(punkte + verschiebung, aussen)).sum(axis=1) <= 0.0
            if not schlecht.any():
                break
            ecken = np.unique(ecke_je_punkt[aussen[schlecht]].ravel())
            ecken = ecken[ecken >= 0]
            ziel[ecken] = lage[ecken] + 0.5 * (ziel[ecken] - lage[ecken])
            halbiert[ecken] = True
        ids = np.flatnonzero(ecke_je_punkt >= 0)
        return ziel, {'punkte': ids.astype(np.int64), 'd': (ziel - lage)[ecke_je_punkt[ids]], 'halbiert': int(halbiert.sum())}
