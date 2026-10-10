# -*- coding: utf-8 -*-
"""Hautbackennormalen — die Normalenkarte der Kachel: die Normale des Körpers (mit seiner Normalenkarte) im Tangentenraum der Figur (Blender: `bake(type='NORMAL', normal_space='TANGENT')`).

Wie Blender es tut: Cycles liefert die Normale des Körpers am Treffer — geglättet über die Punkte, durch den Knoten „Normal Map" aus der Karte gestört —, Blender rechnet sie danach in den
Tangentenraum des Bake-Ziels um (Tangente und Normale der Figur, Bitangente = Normale × Tangente · Vorzeichen) und kodiert `n · 0,5 + 0,5`. Texel ohne Treffer bleiben die flache Normale
(128, 128, 255) — gemessen an Blenders Golden-Bild der Testszene.
Die Tangenten rechnen beide Seiten aus den UV (`Hautbackenflaeche.tangenten`), Blender mit MikkTSpace; die Abweichung steht in `.claude/rules/blendimport-hautbacken.md`.
"""

import numpy as np
import warp as wp

from . import hautbackenkernel as kern

__all__ = ['Hautbackennormalen']


class Hautbackennormalen:
    FLACH = (128, 128, 255)

    def __init__(self, quelle):
        self.quelle = quelle

    def backen(self, kachel, treffer, karte, staerke=1.0):
        """`(px, px, 3)` uint8 im Speicher. `karte`: `Hautbackenbild` der Normalenkarte des Körpers (Tangentenraum, Non-Color)."""
        g, px = kachel.geraet, kachel.px
        q_tri, q_nor, q_tang = self.quelle.normalen()
        f_tang = wp.array(kachel.figur.tangenten().reshape(-1, 4), dtype=wp.vec4, device=g)
        aus = wp.zeros((px, px, 3), dtype=wp.uint8, device=g)
        wp.launch(kern.normalen_backen, dim=(px, px),
                  inputs=[treffer.face, treffer.hu, treffer.hv, q_tri, q_nor, q_tang, self.quelle.uv, karte.feld, float(staerke), kachel.ids, kachel.bary, kachel._tri,
                          kachel._nor, f_tang, aus], device=g)
        daten = aus.numpy()
        daten[~treffer.maske()] = self.FLACH
        return np.ascontiguousarray(daten)
