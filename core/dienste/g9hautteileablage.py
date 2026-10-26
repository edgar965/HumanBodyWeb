# -*- coding: utf-8 -*-
"""G9hautteileablage — Stand, Dateien und Bau der Teilkarten (`G9hautteile`, 25.10.2026); Mechanik in `G9hautfaltenablage`."""
from .g9hautfaltenablage import G9hautfaltenablage
from .g9hautteile import G9hautteile

__all__ = ['G9hautteileablage']


class G9hautteileablage(G9hautfaltenablage):
    """Die Ablage der Körperteil-Anteile je Texel (Hautfarbe und Tattoo je Teil)."""

    PRODUKT = G9hautteile
