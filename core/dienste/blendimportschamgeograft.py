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
from .blendimportschamregister import Blendimportschamregister
from .blendimportschamring import Blendimportschamring

logger = logging.getLogger('core')

__all__ = ['Blendimportschamgeograft']


class Blendimportschamgeograft:
    #: Liegt der Rand des Stücks im Bau weiter (mm) vom Ring, als diese Grenze, reicht das Stück über das Loch hinaus: Das Einrasten zöge Dreiecke
    #: über Zentimeter zu langen Keilen (gemessen 09.10.2026 an „Asian Female": Rand bis 62,6 mm vom Ring, 322 Dreiecke mit einer Kante über
    #: 15 mm, im Chrome ein Keil an der linken Leiste) — dann bleibt das Stück ohne Naht, der Browser rechnet wie vorher. Gemessen an den
    #: Stücken, die gut sitzen: „cute girl" größter Abstand 8,2 mm, „Fallout ranger" 12,7 mm. Die Grenze liegt dazwischen und darüber (Setzung).
    MAX_RAND_WEG_MM = 20.0
    #: Trägt das Stück einen Anbau (Penis, Hoden: `Blendimportscham.begrenzen`), gilt diese Grenze: der Schnitt folgt dort der Hülle des Anbaus, und der
    #: Rand liegt weiter vom Ring. Gemessen 10.10.2026 an der BodyParts3D-Haut: bis 22,3 mm; mit 40 mm gebaut war die Naht sauber (Stück von 6.840 auf
    #: 3.751 Punkte, über 25 mm lange Kanten 11 statt 30, nichts entartet). 30 mm ist eine Setzung zwischen diesem Stück und dem schlechten „Asian Female" (62,6 mm).
    MAX_RAND_WEG_ANBAU_MM = 30.0

    @staticmethod
    def verschweissen(flaeche, werte, punkte, dreiecke, uv_ecken, anbau=False):
        """`{punkte, dreiecke, uv_ecken, loch, bericht}` oder `{'aus': Grund}`. `anbau`: das Stück trägt Penis/Hoden (weitere Grenze für den Rand).

        `flaeche`: die Haut der Figur (trimesh, Stufe 1 — Dreiecke wie im Browser); `werte`: der Schnittwert je Hautpunkt
        (`Blendimportscham.schnittwerte`, negativ = unter dem Stück). `loch`: `dreiecke` der Haut, die entfallen, `von` (ihre Zahl),
        `ring` (Lage der Ringecken im Bau), `ring_punkte` (Nummern der Hautpunkte), `ring_d` (Verschiebung der Glättung je Ecke) und
        `verschiebung` (Nummern ALLER Hautpunkte auf dem Ring samt Verschiebung)."""
        try:
            haut = Blendimportschamloch(flaeche.vertices, flaeche.faces)
            im_loch = haut.loch(werte)
            punkte, dreiecke, uv_ecken, abgeschnitten = Blendimportschamregister.beschneiden(haut, im_loch, punkte, dreiecke, uv_ecken)
            ring = haut.ring(im_loch)
            ring_punkte = haut.ringpunkte(ring)
            normalen = Blendimportschamring.normalen(haut.punkte, haut.dreiecke)[ring_punkte]
            lage0 = haut.lage(ring)
            lage, verschiebung = Blendimportschamring.ziehen(haut.punkte, haut.dreiecke, im_loch, ring_punkte, lage0, normalen)
            punkte, dreiecke, uv_ecken, naht = Blendimportschamnaht(lage).anlegen(punkte, dreiecke, uv_ecken)
            grenze = Blendimportschamgeograft.MAX_RAND_WEG_ANBAU_MM if anbau else Blendimportschamgeograft.MAX_RAND_WEG_MM
            if naht['rand_weg_max_mm'] > grenze:
                raise ValueError('der Rand des Stücks liegt bis %.1f mm neben dem Ring (Grenze %.0f mm): es reicht über das Loch hinaus'
                                 % (naht['rand_weg_max_mm'], grenze))
        except ValueError as fehler:
            logger.warning('Scham-Stück ohne Naht: %s', fehler)
            return {'aus': str(fehler)}
        loch = {'dreiecke': np.flatnonzero(im_loch).astype(np.int64), 'von': int(len(flaeche.faces)), 'ring': lage,
                'ring_punkte': ring_punkte, 'verschiebung': verschiebung, 'ring_d': lage - lage0}
        bericht = dict(haut.bericht(im_loch, ring), **naht, abgeschnitten=abgeschnitten, ring_gezogen_halbiert=verschiebung['halbiert'],
                       ring_gezogen_max_mm=round(float(np.linalg.norm(verschiebung['d'], axis=1).max()) * 1000.0, 2))
        return {'punkte': punkte, 'dreiecke': dreiecke, 'uv_ecken': uv_ecken, 'loch': loch, 'bericht': bericht}
