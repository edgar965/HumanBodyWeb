# -*- coding: utf-8 -*-
"""Kostuemmodell — was `Kostuemrunde.modell` aus einem Wertesatz baut: das Modell aus Teilen und, wenn fällig, das Sichtmodell.

`glb`/`fotos`: Figur + Kostüm aus TEILEN am Rig (Fototextur: {winkel: Bild der Fototextur}). `sicht`/`sichtfotos`: das Sichtmodell
(`effekte/blender/kostuem/sichtmodell.py`: Umriss der Fotos mit Fototextur, am selben Rig) und seine Ansichten. Leere Werte
(`None`, `{}`) heißen: nicht gebaut oder der Bau ist gescheitert (Fehler im Log, die Runde bleibt gültig).
"""

__all__ = ['Kostuemmodell']


class Kostuemmodell:
    def __init__(self, glb=None, fotos=None, sicht=None, sichtfotos=None):
        self.glb = glb
        self.fotos = fotos or {}
        self.sicht = sicht
        self.sichtfotos = sichtfotos or {}
