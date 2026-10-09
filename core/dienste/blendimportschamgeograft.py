# -*- coding: utf-8 -*-
"""Blendimportschamgeograft — das Scham-Stück wie ein Daz-Geograft mit der Haut verschweißen (09.10.2026).

Edgar, 09.10.2026, mit Bild: „bei der Scham gibt es immer noch die Probleme an den Rändern. Schau nach, wie Genesis das mit der Nase
und dem Mund macht, und mach es genau so." Bei Genesis ist ein Rand eine Kante, keine Überlappung: Lippen und Mundhöhle sind EIN Netz
(`Mouth Cavity` teilt sich die Kachel mit dem Kopf), und Daz' Geograft „Anatomical Elements" verschweißt seine Randpunkte Punkt für
Punkt mit einem Loch im Körper. Die Schritte hier, in dieser Reihenfolge:

    Loch      die Haut-Dreiecke unter dem Stück als EIN Kantenring der Figur (`Blendimportschamloch`)
    Ring      die Linie des Rings wird geglättet (`Blendimportschamring`): der Browser rückt die Hautpunkte um dasselbe Stück
    Naht      der Rand des Stücks liegt genau auf den Ecken des Rings (`Blendimportschamnaht`)

Ohne Django. Hat das Loch keinen einfachen Rand, bleibt das Stück, wie es war — der Browser rechnet das Loch dann wie bisher
(`hautverdeckung.js`).
"""

import logging

import numpy as np

from .blendimportschamloch import Blendimportschamloch
from .blendimportschamnaht import Blendimportschamnaht
from .blendimportschamring import Blendimportschamring

logger = logging.getLogger('core')

__all__ = ['Blendimportschamgeograft']


class Blendimportschamgeograft:
    @staticmethod
    def verschweissen(flaeche, werte, punkte, dreiecke, uv_ecken):
        """`{punkte, dreiecke, uv_ecken, loch, bericht}` oder `{'aus': Grund}`.

        `flaeche`: die Haut der Figur (trimesh, Stufe 1 — Dreiecke wie im Browser); `werte`: der Schnittwert je Hautpunkt
        (`Blendimportscham.schnittwerte`, negativ = unter dem Stück). `loch`: `dreiecke` der Haut, die entfallen, `von` (ihre Zahl),
        `ring` (Lage der Ringecken im Bau), `ring_punkte` (Nummern der Hautpunkte), `ring_d` (Verschiebung der Glättung je Ecke) und
        `verschiebung` (Nummern ALLER Hautpunkte auf dem Ring samt Verschiebung)."""
        try:
            haut = Blendimportschamloch(flaeche.vertices, flaeche.faces)
            im_loch = haut.loch(werte)
            ring = haut.ring(im_loch)
            ring_punkte = haut.ringpunkte(ring)
            normalen = Blendimportschamring.normalen(haut.punkte, haut.dreiecke)[ring_punkte]
            lage0 = haut.lage(ring)
            lage, verschiebung = Blendimportschamring.ziehen(haut.punkte, haut.dreiecke, im_loch, ring_punkte, lage0, normalen)
            punkte, dreiecke, uv_ecken, naht = Blendimportschamnaht(lage).anlegen(punkte, dreiecke, uv_ecken)
        except ValueError as fehler:
            logger.warning('Scham-Stück ohne Naht: %s', fehler)
            return {'aus': str(fehler)}
        loch = {'dreiecke': np.flatnonzero(im_loch).astype(np.int64), 'von': int(len(flaeche.faces)), 'ring': lage,
                'ring_punkte': ring_punkte, 'verschiebung': verschiebung, 'ring_d': lage - lage0}
        bericht = dict(haut.bericht(im_loch, ring), **naht, ring_gezogen_halbiert=verschiebung['halbiert'],
                       ring_gezogen_max_mm=round(float(np.linalg.norm(verschiebung['d'], axis=1).max()) * 1000.0, 2))
        return {'punkte': punkte, 'dreiecke': dreiecke, 'uv_ecken': uv_ecken, 'loch': loch, 'bericht': bericht}
