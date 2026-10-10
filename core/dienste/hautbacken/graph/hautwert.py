# -*- coding: utf-8 -*-
"""Hautwert — der Wert an einer Buchse für einen Stapel von Texeln: Art + ein Feld auf der GPU.

Arten wie im Export (`blendmaterialknoten.py`): `f` Zahl (`wp.array` float), `c` Farbe, `v` Vektor (`wp.array` vec3). Ganze Zahlen und Schalter rechnet der Graph als `f`.
"""

import warp as wp

__all__ = ['Hautwert']


class Hautwert:
    __slots__ = ('art', 'daten')

    def __init__(self, art, daten):
        self.art, self.daten = art, daten

    @staticmethod
    def dtype(art):
        return wp.float32 if art == 'f' else wp.vec3

    @classmethod
    def leer(cls, art, n, geraet):
        return cls(art, wp.zeros(n, dtype=cls.dtype(art), device=geraet))
