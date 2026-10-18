# -*- coding: utf-8 -*-
"""G9mimikfaltenablage — Stand, Datei und Bau des Mimikfalten-Atlas (`G9mimikfalten`); Mechanik in `G9hautfaltenablage`."""
from .g9hautfaltenablage import G9hautfaltenablage
from .g9mimikfalten import G9mimikfalten

__all__ = ['G9mimikfaltenablage']


class G9mimikfaltenablage(G9hautfaltenablage):
    """Die Ablage der Mimikfalten (ein Atlas für beide Geschlechter)."""

    PRODUKT = G9mimikfalten
