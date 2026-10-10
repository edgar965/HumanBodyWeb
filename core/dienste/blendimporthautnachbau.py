# -*- coding: utf-8 -*-
"""Blendimporthautnachbau — backt die Haut-Kacheln eines Imports im Speicher auf der GPU (`core/dienste/hautbacken`), wenn das Material des Körpers einfach genug ist.

Blender brauchte dafür 13,7 Minuten (Rosemary Winters, 12 Bilder à 68 s) und schrieb jedes Bild auf die Platte, die Nacharbeit las es zurück. Der Nachbau liefert die drei Bilder je
Kachel als Felder im Speicher (`kachel`), Blender bleibt der Rückfall (`moeglich` nennt den Grund, `Blendimporthaut` schreibt ihn in den Bericht). Gleich wie Blender, gemessen:
Rosemarys Kachel 1001 gegen Blenders rohes Bild — Farbe mittlere Abweichung 0,88 von 255 (vorher mit falscher Schwerpunkt-Konvention 6,8), Testszene Normalenkarte 0,14, Rauheit 0,28
(`core/tests/unit/test_hautbacken_gegen_blender.py`, Zahlen in `.claude/rules/blendimport-hautbacken.md`).
"""

import logging

import cv2
import numpy as np

from .hautbacken import Hautbacken, Hautbackenbild, Hautbackenflaeche, Hautbackenmaterial, Hautbackenquelle

logger = logging.getLogger('core')

__all__ = ['Blendimporthautnachbau']


class Blendimporthautnachbau:
    def __init__(self, netz, npz, ruhe_blender, genesis, figur_blender, px, melden=None):
        """`netz`: Eintrag des Körpers im Inventar; `npz`: seine Datei (`dreiecke`, `uv_ecken`); `ruhe_blender`: die Körperpunkte in der Ruhelage der Figur (Blender-Achsen);
        `genesis`: `Blendimportlage.genesis()`; `figur_blender`: die Punkte der Figur in Blender-Achsen; `px`: Seitenlänge der Kacheln."""
        self.material = Hautbackenmaterial(netz)
        self.melden = melden or (lambda anteil, text: None)
        self.px = int(px)
        self.genesis, self.figur_punkte = genesis, figur_blender
        self.quelle = Hautbackenquelle(ruhe_blender, npz['dreiecke'], npz['uv_ecken'])
        self.backer = Hautbacken(self.quelle, self.px)
        self.farbe = Hautbackenbild.aus_datei(self.material.farbe)
        self.rauheit = Hautbackenbild.aus_datei(self.material.rauheit) if self.material.rauheit else None
        self.normalen = Hautbackenbild.aus_datei(self.material.normalen) if self.material.normalen else Hautbackenbild(np.full((1, 1, 3), (128, 128, 255), np.uint8))

    @staticmethod
    def moeglich(netz, npz):
        """`(bool, Grund)`: Backt der Nachbau diesen Körper? Ein einfaches Material (Export: `einfach`), ein einziger Materialindex und eine GPU mit Warp."""
        ok, grund = Hautbackenmaterial(netz).moeglich()
        if not ok:
            return False, grund
        if len(np.unique(npz['material'])) > 1:
            return False, 'die Dreiecke des Körpers nutzen mehrere Materialien'
        try:
            import warp as wp

            wp.init()
            if not wp.get_cuda_device_count():
                return False, 'keine CUDA-GPU für Warp'
        except Exception as fehler:  # noqa: BLE001 — jede Störung von Warp heißt: Blender backt
            return False, 'Warp nicht nutzbar: %s' % str(fehler)[:120]
        return True, ''

    def kachel(self, nummer):
        """`{'farbe', 'normalen', 'rauheit': (px, px, 3) uint8, 'getroffen': Anteil in %}` einer Kachel — mit Rand wie Blender, Texel ohne Treffer schwarz bzw. flach."""
        g = self.genesis
        dreiecke = g['dreiecke'][g['kachel'] == nummer]
        figur = Hautbackenflaeche(self.figur_punkte, dreiecke, g['uv'][dreiecke])
        wert = self.material.rauheit_wert
        e = self.backer.backen(figur, farbe=self.farbe, rauheit=self.rauheit, normalen=self.normalen)
        if self.rauheit is None:
            e['rauheit'] = self._konstante(e['maske'], e['belegt'], wert)
        e['getroffen'] = round(100.0 * float(e['maske'].mean()), 1)
        return e

    @staticmethod
    def _konstante(maske, belegt, wert):
        """Eine Rauheit ohne Bild: Blender backt den festen Wert als Grau — dort, wo getroffen oder im Rand."""
        grau = int(np.clip(round(float(wert) * 255.0), 0, 255))
        aus = np.zeros(belegt.shape + (3,), np.uint8)
        aus[belegt] = grau
        return aus

    @staticmethod
    def grau(rgb):
        """Die Rauheit als Grauwerte (PIL `convert('L')`: 0,299 R + 0,587 G + 0,114 B)."""
        return cv2.cvtColor(np.ascontiguousarray(rgb), cv2.COLOR_RGB2GRAY)
