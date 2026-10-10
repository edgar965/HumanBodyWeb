# -*- coding: utf-8 -*-
"""Hautbackentreffer — was die Strahlen einer Kachel getroffen haben: je Texel das Dreieck des Körpers und die Schwerpunktkoordinaten darin (auf dem Gerät)."""

__all__ = ['Hautbackentreffer']


class Hautbackentreffer:
    def __init__(self, px, face, hu, hv):
        self.px = px
        self.face = face           # wp.array2d int32: Dreieck des Körpers, -1 ohne Treffer
        self.hu = hu               # wp.array2d float32: Gewicht der Ecke 1
        self.hv = hv               # wp.array2d float32: Gewicht der Ecke 2

    def maske(self):
        """`(px, px)` bool im Speicher: wo ein Strahl den Körper getroffen hat."""
        return self.face.numpy() >= 0
