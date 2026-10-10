# -*- coding: utf-8 -*-
"""Hautbackenrand — der Rand um die gebackenen Flächen (Blender: `bake.margin`, hier 16 Texel).

Blender füllt die Texel neben einer gebackenen Fläche bis `margin` Texel weit, damit Mip-Stufen und Filter an den Inselkanten nicht ins Schwarze greifen; gemessen an Rosemarys
Kachel 1001 liegen 502.994 nicht schwarze Texel bis 16,2 px außerhalb der Inseln. Blenders Vorgabe ist `ADJACENT_FACES` (die Nachbarfläche setzt sich über die Kante fort, braucht die
3D-Nachbarschaft der ganzen Figur); der Nachbau nimmt dafür die Farbe des nächsten gebackenen Texels im Umkreis von 16 Texeln (euklidisch) — als Polster gleichwertig, an den Kanten
anders gefärbt. Ein Rand, der in jedem Schritt wie ein Quadrat wächst (`EXTEND` in Blender), reichte in den Diagonalen 41 % weiter als Blender: auf der Testszene füllte er 788 Texel,
die Blender leer lässt. Was dahinter bleibt, ist leer und wird wie bisher von `Blendimporthaut` gefüllt (`leer` = fast schwarz).
"""

import cv2
import numpy as np
import warp as wp

from . import hautbackenkernel as kern

__all__ = ['Hautbackenrand']


class Hautbackenrand:
    BREITE_PX = 16

    def __init__(self, geraet='cuda:0', breite=BREITE_PX):
        self.geraet, self.breite = geraet, int(breite)

    def erweitern(self, bild, maske):
        """`(bild, maske)`: `bild` `(h, w, 3)` uint8 im Speicher, `maske` `(h, w)` bool (gebacken). Gibt Bild und Maske mit dem Rand zurück."""
        h, w = maske.shape
        nah = cv2.dilate(maske.astype(np.uint8), np.ones((2 * self.breite + 1, 2 * self.breite + 1), np.uint8))
        a_bild = wp.array(np.ascontiguousarray(bild), dtype=wp.uint8, device=self.geraet)
        a_maske = wp.array(maske.astype(np.uint8), dtype=wp.uint8, device=self.geraet)
        a_nah = wp.array(nah, dtype=wp.uint8, device=self.geraet)
        aus = wp.empty_like(a_bild)
        aus_maske = wp.empty_like(a_maske)
        wp.launch(kern.erweitern, dim=(h, w), inputs=[a_bild, a_maske, a_nah, self.breite, aus, aus_maske], device=self.geraet)
        return aus.numpy(), aus_maske.numpy().astype(bool)
