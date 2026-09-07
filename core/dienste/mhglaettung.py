# -*- coding: utf-8 -*-
u"""Mhglaettung — MakeHumans „Smooth" fuer das Basisnetz.

MakeHuman hat den Schalter selbst: ohne ihn sieht man die 13.378 Vierecke,
mit ihm einen glatten Koerper. Gerechnet wird dasselbe wie dort — eine Stufe
Catmull-Clark, `humanbody_core.catmull_clark.CatmullClarkSubdivider`, die im
Projekt schon den HumanBody-Koerper glaettet.

WARUM EIN ZWISCHENSPEICHER (gemessen 06.09.2026)
================================================
    Unterteiler bauen   2,11 s      Anwenden   0,017 s

Die Gewichtsmatrix haengt nur an der TOPOLOGIE, nicht an den Punkten — sie
wird einmal je Teileauswahl gebaut und bleibt liegen. Ohne das kostete jedes
Ein- und Ausschalten zwei Sekunden.

Ergebnis fuer die Koerpergruppe: 13.380 -> 53.514 Punkte, 107.024 Dreiecke.

DER UMLAUFSINN WIRD ZURUECKGEDREHT
==================================
`CatmullClarkSubdivider._triangulieren` macht aus `[a,b,c,d]` bewusst
`[a,c,b]` und `[a,d,c]` — fuer die HumanBody-Netze, die aus Blender kommen.
Das MakeHuman-Netz braucht die andere Folge (gemessen am Volumen, siehe
`Mhbasisnetz`), also wird hier `[0, 2, 1]` angewandt: einmal umgedreht,
einmal zurueck.
"""

import logging
import threading
import time

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Mhglaettung']


class Mhglaettung:
    u"""Eine gebaute Unterteilung je Teileauswahl."""

    #: MakeHuman glaettet um genau eine Stufe.
    STUFEN = 1

    _gebaut = {}
    _schloss = threading.Lock()

    def __init__(self, unterteiler, dreiecke):
        self._unterteiler = unterteiler
        #: (T, 3) uint32, Umlaufsinn wie in `Mhbasisnetz.dreiecke`.
        self.dreiecke = dreiecke

    # ------------------------------------------------------------------ bauen

    @classmethod
    def holen(cls, schluessel, vierecke):
        u"""Die Unterteilung zu dieser Teileauswahl — beim ersten Mal gebaut.

        @param schluessel eindeutiger Name der Auswahl (`koerper+helfer`)
        @param vierecke   (F, 4) mit LUECKENLOSEN Punktnummern ab 0
        """
        if schluessel in cls._gebaut:
            return cls._gebaut[schluessel]
        with cls._schloss:
            if schluessel not in cls._gebaut:
                cls._gebaut[schluessel] = cls._bauen(schluessel, vierecke)
        return cls._gebaut[schluessel]

    @classmethod
    def _bauen(cls, schluessel, vierecke):
        from humanbody_core.catmull_clark import CatmullClarkSubdivider
        beginn = time.perf_counter()
        unterteiler = CatmullClarkSubdivider(
            np.asarray(vierecke, dtype=np.int64), levels=cls.STUFEN)
        # Zurueckdrehen: der Unterteiler liefert `[a,c,b]`, hier gilt `[a,b,c]`.
        dreiecke = np.asarray(unterteiler.triangles)[:, [0, 2, 1]]
        logger.info(u'MakeHuman-Glättung „%s" gebaut: %.2f s, %d Dreiecke',
                    schluessel, time.perf_counter() - beginn, len(dreiecke))
        return cls(unterteiler, dreiecke.astype(np.uint32))

    # --------------------------------------------------------------- rechnen

    def punkte(self, grundpunkte):
        u"""Die feinen Punkte zu diesen Grundpunkten (0,017 s)."""
        return self._unterteiler.subdivide(
            np.asarray(grundpunkte, dtype=np.float64)).astype(np.float32)

    def verteilen(self, matrix):
        u"""Eine Groesse je Grundpunkt auf die feinen Punkte verteilen.

        DIESELBE Matrix wie fuer die Punkte, und das ist der Grund, warum es
        stimmt: Ein feiner Punkt, der geometrisch zu 25 % aus einem
        Grundpunkt entsteht, gehoert auch zu 25 % zu dessen Knochen. Fuer
        Hautgewichte (`Mhhaut`) — mit einer anderen Rechnung liefe die
        Verformung an der Glaettung vorbei, und die Figur risse an den
        Kanten auf.
        """
        return self._unterteiler._weights @ np.asarray(matrix, dtype=np.float64)
