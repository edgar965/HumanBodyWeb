# -*- coding: utf-8 -*-
"""Umareglerzug — was ein Reglerzug an einer UMA-Python-Figur ändert, und nur das.

WARUM (25.11.2026, Edgar: „alle regler unter 0,2 s“): Die volle Antwort
(`Szenenfigur.alles`) trägt bei jedem Zug 3,9 MB JSON — UV, Dreiecke, Normalen,
Hautgewichte und Reglerliste, die zur Rasse gehören und sich nicht bewegen.
Gemessen (Anime Elf Female 3.0, 16.277 Punkte): 78 ms Rechnung, 113 ms JSON.
Hier kommen die Punkte als Binärfeld, dazu Skelett, Bilanz und Stoffkäfig.

`genau`: Die Punkte gehen nie mit 16 Bit (`Netzkurz`) — sie sind dieselben
float32 wie in der vollen Antwort (bytegleich geprüft, zwei Stellungen).
Die Normalen hängen nicht an der DNA (`Gebaut.normalen`), auch das geprüft.
"""

import torch
from UMA_Python.stoffschwung import Umastoff
from UMA_Python.szene import Szenenfigur

from ..daten.netzfeld import Netzfeld

__all__ = ['Umareglerzug']


class Umareglerzug:
    """Die Form einer gebauten Figur bei gegebener Reglerstellung."""

    @staticmethod
    def antwort(gebaut, dna=None):
        punkte = Szenenfigur.nach_yoben(gebaut.punkte(dna))
        hoehe = float(punkte[:, 1].max() - punkte[:, 1].min()) if len(punkte) else 0.0
        return {
            'rasse': gebaut.rasse,
            'netz': {
                'punkte': Netzfeld.aus(punkte, torch.float32, genau=True),
                'punktzahl': len(punkte),
            },
            'skelett': Szenenfigur.skelett(gebaut, dna),
            'bilanz': {**gebaut.bilanz(), 'hoehe_m': round(hoehe, 4)},
            'stoff': Umastoff.antwort(gebaut, punkte),
        }
