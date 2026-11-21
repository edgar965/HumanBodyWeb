# -*- coding: utf-8 -*-
"""Hautwert — der Wert an einer Buchse für einen Stapel von Texeln: Art + ein Feld auf der Karte.

Arten wie im Export (`blendmaterialknoten.py`): `f` Zahl (float32 `(n,)`), `c` Farbe, `v` Vektor (float32 `(n, 3)`). Ganze Zahlen und Schalter rechnet der Graph als `f`.
Bis 21.11.2026 `wp.array` (float bzw. vec3); seitdem torch-Tensoren für die eigenen CUDA-Kerne (`Hautbackenkernbau`).
"""

import torch

__all__ = ['Hautwert']


class Hautwert:
    __slots__ = ('art', 'daten')

    def __init__(self, art, daten):
        self.art, self.daten = art, daten

    @staticmethod
    def form(art, n):
        return (n,) if art == 'f' else (n, 3)

    @classmethod
    def leer(cls, art, n, geraet):
        return cls(art, torch.zeros(cls.form(art, n), dtype=torch.float32, device=geraet))
