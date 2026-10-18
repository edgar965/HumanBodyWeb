# -*- coding: utf-8 -*-
"""G9hautzeichnungablage — Stand, Dateien und Bau der Muskel-/Fettkarten (`G9hautzeichnung`); Mechanik in `G9hautfaltenablage`."""
from .g9hautfaltenablage import G9hautfaltenablage
from .g9hautzeichnung import G9hautzeichnung

__all__ = ['G9hautzeichnungablage']


class G9hautzeichnungablage(G9hautfaltenablage):
    """Die Ablage der Muskel- und Fettzeichnung."""

    PRODUKT = G9hautzeichnung
