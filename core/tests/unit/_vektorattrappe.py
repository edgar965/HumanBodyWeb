# -*- coding: utf-8 -*-
u"""Vektorattrappe — so viel `mathutils.Vector`, wie ein Import braucht.

Herausgeloest am 02.09.2026 aus `blenderattrappe.py` (Befund
`klassen-je-datei`: zwei eigenstaendige Klassen in einer Datei). `Vektor`
ist der einzige Teil der Attrappe, der wirklich RECHNET — elf Methoden,
abhaengig von nichts ausser `math`. Die Attrappe selbst reicht ihn nur
weiter.

WAS ER KANN UND WAS NICHT
=========================
Addieren, subtrahieren, skalieren, Laenge, normalisieren, x/y/z. Er ist
ein `tuple` und damit unveraenderlich — Blenders `Vector` ist das nicht.
Code, der `v.x = 3` schreibt, faellt hier auf; das ist erwuenscht, denn
solcher Code stuende auf Modulebene und liefe beim Import.
"""
import math

__all__ = ['Vektor']


class Vektor(tuple):
    u"""So viel Vektor, wie Code auf Modulebene braucht."""

    def __new__(cls, werte=(0.0, 0.0, 0.0)):
        return super().__new__(cls, tuple(float(w) for w in werte))

    def __add__(self, anderer):
        return Vektor(x + y for x, y in zip(self, anderer))

    def __sub__(self, anderer):
        return Vektor(x - y for x, y in zip(self, anderer))

    def __mul__(self, faktor):
        return Vektor(x * faktor for x in self)

    __rmul__ = __mul__

    @property
    def length(self):
        return math.sqrt(sum(x * x for x in self))

    def copy(self):
        return Vektor(self)

    def normalized(self):
        laenge = self.length
        if laenge == 0:
            return Vektor(self)
        return Vektor(x / laenge for x in self)

    @property
    def x(self):
        return self[0]

    @property
    def y(self):
        return self[1]

    @property
    def z(self):
        return self[2]
