# -*- coding: utf-8 -*-
"""Hautbackentreffer — was die Strahlen einer Kachel getroffen haben: je Texel das Dreieck des Körpers und die Schwerpunktkoordinaten darin (auf der Karte)."""

__all__ = ['Hautbackentreffer']


class Hautbackentreffer:
    def __init__(self, px, face, hu, hv):
        self.px = px
        self.face = face           # (px, px) int32 auf der Karte: Dreieck des Körpers, -1 ohne Treffer (bis 21.11.2026 `wp.array2d`)
        self.hu = hu               # (px, px) float32: Gewicht der Ecke 1
        self.hv = hv               # (px, px) float32: Gewicht der Ecke 2

    def maske(self):
        """`(px, px)` bool im Speicher: wo ein Strahl den Körper getroffen hat."""
        return (self.face >= 0).cpu().numpy()
