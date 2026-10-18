# -*- coding: utf-8 -*-
"""G9hautebenenablage — Stand, Dateien und Bau der Gebietskarten (`G9hautebenen`); Mechanik in `G9hautfaltenablage`."""
from .g9hautebenen import G9hautebenen
from .g9hautfaltenablage import G9hautfaltenablage

__all__ = ['G9hautebenenablage']


class G9hautebenenablage(G9hautfaltenablage):
    """Die Ablage der Gebiete für Sommersprossen und Altersflecken."""

    PRODUKT = G9hautebenen
