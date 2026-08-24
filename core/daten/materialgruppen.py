# -*- coding: utf-8 -*-
"""Materialgruppen — Dreiecke nach Material sortieren und in Bereiche schneiden.

Three.js kann EINEN Geometriepuffer mit mehreren Materialien zeichnen, wenn dazu
Bereiche angegeben sind: je Material `{materialIndex, start, count}` mit
Indexwerten (also Dreieck × 3). Voraussetzung ist, dass die Dreiecke desselben
Materials **beieinanderliegen** — deshalb wird zuerst stabil sortiert.

Herausgelöst aus `api/netz.character_mesh` (141 Zeilen, Grenze 60). Dort war das
der längste Block: Vierecke aufteilen, sortieren, Bereichsgrenzen suchen — mitten
in einer Ansicht, die eigentlich nur antworten soll.

DIE ZWEI FALLEN, DIE HIER STECKEN
=================================
* **Stabil sortieren.** `np.argsort(..., kind='stable')` erhält die Reihenfolge
  innerhalb eines Materials. Mit der Vorgabe (`quicksort`) wären die Dreiecke
  innerhalb einer Gruppe durchgewürfelt — sichtbar wird das erst bei
  transparenten Materialien, deren Zeichenreihenfolge zählt.
* **Wicklung beim Aufteilen.** Ein Viereck (0,1,2,3) wird zu (0,2,1) und
  (0,3,2), nicht zu (0,1,2)/(0,2,3): Die Umlaufrichtung muss erhalten bleiben,
  sonst zeigen die Normalen nach innen und die Fläche wird unsichtbar.
"""

import numpy as np


class Materialgruppen:
    """Dreiecke plus Bereichsangaben für Three.js."""

    #: Ein Index besteht aus drei Werten je Dreieck.
    JE_DREIECK = 3

    def __init__(self, dreiecke, materialien=None, namen=None):
        self.dreiecke = dreiecke
        self.materialien = materialien
        self.namen = list(namen or [])

    # ------------------------------------------------------------ Erzeugen

    @classmethod
    def aus_flaechen(cls, flaechen, materialien=None, namen=None):
        """Aus Vierecken ODER Dreiecken — mit erhaltener Umlaufrichtung."""
        if flaechen.ndim == 2 and flaechen.shape[1] == 4:
            dreiecke = np.concatenate([flaechen[:, [0, 2, 1]],
                                       flaechen[:, [0, 3, 2]]], axis=0)
            # Jedes Viereck liefert ZWEI Dreiecke — die Materialliste muss
            # mitwachsen, sonst passt sie nicht mehr zu den Dreiecken.
            if materialien is not None:
                materialien = np.concatenate([materialien, materialien], axis=0)
        elif flaechen.shape[1] == 3:
            dreiecke = flaechen[:, [0, 2, 1]]
        else:
            dreiecke = flaechen
        return cls(dreiecke, materialien, namen)

    # ------------------------------------------------------------- Abfragen

    def sortiert(self):
        """Die Dreiecke, nach Material gruppiert (stabil)."""
        if self.materialien is None:
            return self.dreiecke
        return self.dreiecke[np.argsort(self.materialien, kind='stable')]

    def bereiche(self):
        """`[{materialIndex, start, count}]` — leer ohne Materialangaben."""
        if self.materialien is None or not len(self.materialien):
            return []
        folge = self.materialien[np.argsort(self.materialien, kind='stable')]
        bereiche, anfang = [], 0
        for stelle in range(1, len(folge)):
            if folge[stelle] != folge[anfang]:
                bereiche.append(self._bereich(folge[anfang], anfang, stelle))
                anfang = stelle
        bereiche.append(self._bereich(folge[anfang], anfang, len(folge)))
        return bereiche

    def _bereich(self, material, anfang, ende):
        # Dictionary gewollt: geht unveraendert als JSON an Three.js.
        return {'materialIndex': int(material),
                'start': int(anfang * self.JE_DREIECK),
                'count': int((ende - anfang) * self.JE_DREIECK)}
