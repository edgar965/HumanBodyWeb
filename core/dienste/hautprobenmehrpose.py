# -*- coding: utf-8 -*-
"""Hautprobenmehrpose — `Hautproben`, bei denen jede Ansicht in der Haltung IHRES Fotos steht (08.10.2026).

N1: Das Vorderfoto zeigt einen Arm waagerecht und die Beine im Schritt, das Rückfoto hängende Arme und gerade Beine. Mit EINER Haltung für alle Ansichten lagen die Modellbeine neben den Fotobeinen — die Fotohaut deckte die Beinkachel
zu 7 %, die Unterschenkel zu 0 % (`Haltungsansicht`). Hier hat jede Ansicht ihre eigenen `Hautproben` (eigene Projektion mit einer Ansicht, eigene Lage und Normale der Texel in ihrer Haltung, eigenes Licht), und `farbe` legt die
Summen der Ansichten zusammen — dieselbe Rechnung wie `Hautproben.farbe`, nur mit je Ansicht anderer Lage. Das Raster der Texel (Maske, Zeilen und Spalten, Hand) hängt an UV und Dreiecken und ist für alle Haltungen gleich.

Dieselben Aufrufe wie bei `Hautproben` (`sammeln`, `licht_schaetzen`, `farbe`, `projektion`), damit `Koerperfotoprojektion` beide gleich behandelt.
"""

import numpy as np

from .hautproben import Hautproben

__all__ = ['Hautprobenmehrpose']


class _Projektionen:
    """Was `Koerperfotoprojektion._licht_uebertragen` von einer Projektion liest: `licht` und `ansichten` (hier die Ansichten aller Haltungen hintereinander)."""

    def __init__(self, proben):
        self._proben = proben

    @property
    def licht(self):
        return self._proben[0].projektion.licht

    @property
    def ansichten(self):
        return [a for p in self._proben for a in p.projektion.ansichten]


class Hautprobenmehrpose:
    def __init__(self, proben):
        """`proben`: je Ansicht ein `Hautproben` mit einer Projektion, die genau diese Ansicht trägt (in ihrer Haltung gebaut)."""
        self.proben = list(proben)
        self.projektion = _Projektionen(self.proben)

    def sammeln(self, karten_je_ansicht):
        """`karten_je_ansicht`: je Ansicht die Gruppenkarten der Kachel in DER Haltung dieser Ansicht → wie `Hautproben.sammeln`, dazu `proben` (die Proben je Ansicht); Maske, Texel und Hand stammen aus der ersten."""
        ps = [pr.sammeln(karten) for pr, karten in zip(self.proben, karten_je_ansicht, strict=True)]
        for p in ps[1:]:
            if not np.array_equal(p['index'], ps[0]['index']):
                raise ValueError('Hautprobenmehrpose: das Texelraster hängt an der Haltung — UV und Dreiecke sollten es bestimmen')
        return dict(ps[0], proben=ps)

    def licht_schaetzen(self, proben):
        """Das Licht jeder Ansicht aus den Hautpunkten ALLER Kacheln, in der Haltung dieser Ansicht."""
        for i, pr in enumerate(self.proben):
            pr.licht_schaetzen([p['proben'][i] for p in proben])

    def farbe(self, p):
        """`(farbe (N, 3) sRGB, deckung (N,), getroffen (N,) bool)` — die Summen aller Ansichten, dann wie `Hautproben.farbe`."""
        summe = gewicht = beste = 0.0
        for pr, pv in zip(self.proben, p['proben'], strict=True):
            s, g, b = pr.summen(pv)
            summe, gewicht, beste = summe + s, gewicht + g, np.maximum(beste, b)
        return Hautproben.abschluss(summe, gewicht, beste, p['hand'])
