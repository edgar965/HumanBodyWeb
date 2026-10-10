# -*- coding: utf-8 -*-
"""Hautbackenbild — ein Bild des Materials (Farbe, Rauheit, Normalenkarte) als Byte-Feld auf dem Gerät, und das Abtasten am Treffer."""

import cv2
import numpy as np
import warp as wp

from . import hautbackenkernel as kern

__all__ = ['Hautbackenbild']


class Hautbackenbild:
    def __init__(self, daten, geraet='cuda:0'):
        """`daten`: `(h, w, 3)` uint8 (RGB)."""
        if daten.ndim != 3 or daten.shape[2] != 3 or daten.dtype != np.uint8:
            raise ValueError('Ein Bild des Materials ist (h, w, 3) uint8, nicht %s %s' % (daten.shape, daten.dtype))
        self.geraet = geraet
        self.hoehe, self.breite = daten.shape[:2]
        self.feld = wp.array(np.ascontiguousarray(daten), dtype=wp.uint8, device=geraet)

    @staticmethod
    def lesen(pfad):
        """`(h, w, 3)` uint8 RGB aus einer Datei: Grau wird dreifach, Alpha fällt weg, 16 Bit wird auf 8 Bit gebracht (Blender backt ebenfalls 8 Bit)."""
        roh = cv2.imread(str(pfad), cv2.IMREAD_UNCHANGED)
        if roh is None:
            raise OSError('Bild nicht lesbar: %s' % pfad)
        if roh.dtype == np.uint16:
            roh = (roh >> 8).astype(np.uint8)
        elif roh.dtype != np.uint8:
            roh = np.clip(roh * 255.0 + 0.5, 0, 255).astype(np.uint8)
        if roh.ndim == 2:
            roh = np.repeat(roh[..., None], 3, axis=2)
        elif roh.shape[2] == 4:
            roh = roh[..., :3]
        return np.ascontiguousarray(roh[..., ::-1])

    @classmethod
    def aus_datei(cls, pfad, geraet='cuda:0'):
        return cls(cls.lesen(pfad), geraet)

    def abtasten(self, treffer, quelle):
        """`(px, px, 3)` uint8 im Speicher: das Bild am Treffer jedes Texels, bilinear; Texel ohne Treffer bleiben 0 (Blender: schwarz)."""
        aus = wp.zeros((treffer.px, treffer.px, 3), dtype=wp.uint8, device=self.geraet)
        wp.launch(kern.abtasten, dim=(treffer.px, treffer.px), inputs=[treffer.face, treffer.hu, treffer.hv, quelle.uv, self.feld, aus], device=self.geraet)
        return aus.numpy()
