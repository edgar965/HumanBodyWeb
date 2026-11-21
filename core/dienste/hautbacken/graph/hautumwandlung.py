# -*- coding: utf-8 -*-
"""Hautumwandlung — die Umwandlungen zwischen den Buchsenarten, die Cycles beim Verbinden einfügt (`ConvertNode`, `intern/cycles/kernel/svm/convert.h`):

    Zahl → Farbe/Vektor   `NODE_CONVERT_FV`: (f, f, f)
    Farbe → Zahl          `NODE_CONVERT_CF`: `linear_rgb_to_gray` = dot(c, `rgb_to_y`) — die Leuchtdichte-Gewichte des Arbeitsfarbraums (`GRAU`)
    Vektor → Zahl         `NODE_CONVERT_VF`: `average`
    Farbe ↔ Vektor        keine Rechnung (beides `float3`)

Kerne `hb_f_zu_v`, `hb_c_zu_f`, `hb_v_zu_f` (`Hautbackenkernbau`; bis 21.11.2026 Warp-Kerne hier); feste Werte als `torch.full` (float32 wie vorher).
"""

import torch

from ..hautbackenkernbau import Hautbackenkernbau
from .hautwert import Hautwert

__all__ = ['Hautumwandlung']


class Hautumwandlung:
    GRAU = (0.2126729, 0.7151522, 0.0721750)

    @staticmethod
    def konstante(art, wert, n, geraet):
        """Ein Feld der Länge `n` mit dem festen Wert (Zahl, oder drei Zahlen für Farbe/Vektor)."""
        if art == 'f':
            return Hautwert(art, torch.full((n,), float(wert), dtype=torch.float32, device=geraet))
        v = torch.tensor([float(wert[0]), float(wert[1]), float(wert[2])], dtype=torch.float32, device=geraet)
        return Hautwert(art, v.expand(n, 3).contiguous())

    @classmethod
    def nach(cls, wert, art, geraet):
        """Der Wert als Art `art` (`f`, `c`, `v`)."""
        if wert.art == art:
            return wert
        n = len(wert.daten)
        rufen = Hautbackenkernbau.rufen
        with torch.cuda.device(geraet):
            if art == 'f':
                aus = torch.zeros(n, dtype=torch.float32, device=geraet)
                if wert.art == 'c':
                    rufen('hb_c_zu_f', n, wert.daten, *cls.GRAU, aus)
                else:
                    rufen('hb_v_zu_f', n, wert.daten, aus)
                return Hautwert('f', aus)
            if wert.art == 'f':
                aus = torch.zeros((n, 3), dtype=torch.float32, device=geraet)
                rufen('hb_f_zu_v', n, wert.daten, aus)
                return Hautwert(art, aus)
        return Hautwert(art, wert.daten)           # Farbe ↔ Vektor: dasselbe Feld
