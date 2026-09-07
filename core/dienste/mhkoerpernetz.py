# -*- coding: utf-8 -*-
u"""Mhkoerpernetz — das ANGEZEIGTE Netz der MakeHuman-Figur.

Drei Fragen, in dieser Reihenfolge:

    1. Welche Teile?        Haut, Helfergeometrie, Gelenkwuerfel
    2. Geglaettet?          MakeHumans „Smooth", eine Stufe Catmull-Clark
    3. Was ist verdeckt?    die `delete_verts` der getragenen Stuecke

DIE REIHENFOLGE IST NICHT BELIEBIG. Maskiert wird ZULETZT, auf den fertigen
Dreiecken — nicht vorher auf den Vierecken. Der Grund ist der Zwischenspeicher
der Unterteilung: Ihre Gewichtsmatrix zu bauen kostet 2,1 s und haengt an der
Topologie. Wer erst maskiert, hat je Kleidungskombination eine andere
Topologie — und damit bei jedem An- und Ausziehen zwei Sekunden Rechnung. So
bleibt es EIN Unterteiler je Teileauswahl.

Dass das geht, liegt an der festen Ordnung der Unterteilung: Aus Viereck `f`
werden die Viererecke `4f … 4f+3` (`Unterteilungsstufe._neue_vierecke`), und
`_triangulieren` haengt zwei Dreiecksreihen aneinander — Dreieck `j` und
`j + N` gehoeren zum selben Viereck. Beides ist hier als `STUFENFAKTOR`
und als `np.tile(..., 2)` abgebildet.
"""

import logging

import numpy as np

from .mhbasisnetz import Mhbasisnetz
from .mhglaettung import Mhglaettung
from .mhloeschmaske import Mhloeschmaske
from .mhnetzformen import Mhnetzformen

logger = logging.getLogger('core')

__all__ = ['Mhkoerpernetz']


class Mhkoerpernetz:
    u"""Punkte, Dreiecke und Normalen fuer eine Anzeigeeinstellung."""

    #: Aus einem Viereck werden je Stufe vier — `Mhglaettung.STUFEN` = 1.
    STUFENFAKTOR = 4

    def __init__(self, teile, glatt=False, getragen=(), formung=None):
        self.teile = tuple(teile)
        self.glatt = bool(glatt)
        self.getragen = tuple(getragen)
        #: Die Reglerstellung (`Mhformung`); ohne sie das Basisnetz.
        self.formung = formung

    def bauen(self):
        u"""`{punkte, dreiecke, normalen, hoehe}` — Meter, Y oben, Fuesse auf 0.

        DIE HOEHE WIRD VOR DEM MASKIEREN GEMESSEN. Sonst schrumpfte die Figur,
        sobald sie Schuhe traegt: Deren `delete_verts` nehmen die Fuesse weg,
        und das gemessene Netz war danach 1,6536 m statt 1,6659 m hoch. Der
        Groessenregler haette bei jedem Kleidungsstueck einen anderen Wert
        angezeigt, ohne dass sich etwas bewegt haette.
        """
        basis = Mhbasisnetz.holen()
        vierecke = basis.vierecke(self.teile)
        nummern, lokale = Mhnetzformen.umschluesseln(vierecke)
        if not len(lokale):
            leer = np.zeros((0, 3), dtype=np.float32)
            return {'punkte': leer, 'dreiecke': np.zeros((0, 3), dtype=np.uint32),
                    'normalen': leer, 'hoehe': 0.0}
        roh = self.formung.punkte() if self.formung else None
        punkte = basis.punkte_am_boden(nummern, roh)
        punkte, dreiecke, je_viereck = self._flaechen(lokale, punkte)
        hoehe = float(punkte[:, 1].max() - punkte[:, 1].min())
        dreiecke = self._maskieren(vierecke, dreiecke, je_viereck)
        punkte, dreiecke = Mhnetzformen.verdichten(punkte, dreiecke)
        return {'punkte': punkte, 'dreiecke': dreiecke,
                'normalen': Mhnetzformen.normalen(punkte, dreiecke),
                'hoehe': hoehe}

    # ------------------------------------------------------------- Glaettung

    def _flaechen(self, lokale, punkte):
        u"""`(punkte, dreiecke, dreiecke je Basisviereck und Reihe)`."""
        if not self.glatt:
            return punkte, Mhnetzformen.dreiecke(lokale), 1
        glaettung = Mhglaettung.holen('+'.join(self.teile), lokale)
        return glaettung.punkte(punkte), glaettung.dreiecke, \
            Mhkoerpernetz.STUFENFAKTOR ** Mhglaettung.STUFEN

    # ---------------------------------------------------------- Loeschmaske

    def _maskieren(self, vierecke, dreiecke, je_viereck):
        u"""Die Vierecke wegnehmen, die unter Kleidung liegen."""
        if not self.getragen:
            return dreiecke
        verdeckt = Mhloeschmaske.vereinigt(self.getragen)
        if not verdeckt:
            return dreiecke
        # Ein Viereck faellt, sobald EINE seiner Ecken verdeckt ist — so macht
        # es MakeHuman auch. Andernfalls blieben Zipfel an jeder Kante stehen.
        behalten = ~np.isin(vierecke, np.fromiter(verdeckt, dtype=np.int64,
                                                  count=len(verdeckt))
                            ).any(axis=1)
        # Zwei Dreiecksreihen (`[a,b,c]` und `[a,c,d]`) hintereinander, je
        # Viereck `je_viereck` Stueck in jeder Reihe.
        gilt = np.tile(np.repeat(behalten, je_viereck), 2)
        logger.debug('MakeHuman: %d von %d Vierecken verdeckt',
                     int((~behalten).sum()), len(behalten))
        return dreiecke[gilt]
