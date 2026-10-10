# -*- coding: utf-8 -*-
"""Hautumwandlung — die Umwandlungen zwischen den Buchsenarten, die Cycles beim Verbinden einfügt (`ConvertNode`, `intern/cycles/kernel/svm/convert.h`):

    Zahl → Farbe/Vektor   `NODE_CONVERT_FV`: (f, f, f)
    Farbe → Zahl          `NODE_CONVERT_CF`: `linear_rgb_to_gray` = dot(c, `rgb_to_y`) — die Leuchtdichte-Gewichte des Arbeitsfarbraums (`GRAU`)
    Vektor → Zahl         `NODE_CONVERT_VF`: `average`
    Farbe ↔ Vektor        keine Rechnung (beides `float3`)
"""

import warp as wp

from ..hautfunktionen import average3
from .hautwert import Hautwert

__all__ = ['Hautumwandlung']


@wp.kernel
def _f_zu_v(a: wp.array(dtype=wp.float32), aus: wp.array(dtype=wp.vec3)):
    i = wp.tid()
    aus[i] = wp.vec3(a[i], a[i], a[i])


@wp.kernel
def _c_zu_f(a: wp.array(dtype=wp.vec3), y: wp.vec3, aus: wp.array(dtype=wp.float32)):
    i = wp.tid()
    aus[i] = wp.dot(a[i], y)


@wp.kernel
def _v_zu_f(a: wp.array(dtype=wp.vec3), aus: wp.array(dtype=wp.float32)):
    i = wp.tid()
    aus[i] = average3(a[i])


@wp.kernel
def _fuellen_f(wert: float, aus: wp.array(dtype=wp.float32)):
    i = wp.tid()
    aus[i] = wert


@wp.kernel
def _fuellen_v(wert: wp.vec3, aus: wp.array(dtype=wp.vec3)):
    i = wp.tid()
    aus[i] = wert


class Hautumwandlung:
    #: `kernel_data.film.rgb_to_y`: die Gewichte der Leuchtdichte im Arbeitsfarbraum (Blender-Vorgabe Linear Rec.709). Gemessen wird der Wert im Vergleich mit Blender
    #: (`test_hautbacken_knoten.py`, Baustein Farbe → Zahl), nicht angenommen — bis die Messung vorliegt, steht hier die Vorgabe von OpenColorIO für Rec.709.
    GRAU = (0.2126729, 0.7151522, 0.0721750)

    @staticmethod
    def konstante(art, wert, n, geraet):
        """Ein Feld der Länge `n` mit dem festen Wert (Zahl, oder drei Zahlen für Farbe/Vektor)."""
        if art == 'f':
            feld = wp.zeros(n, dtype=wp.float32, device=geraet)
            wp.launch(_fuellen_f, dim=n, inputs=[float(wert), feld], device=geraet)
        else:
            feld = wp.zeros(n, dtype=wp.vec3, device=geraet)
            wp.launch(_fuellen_v, dim=n, inputs=[wp.vec3(float(wert[0]), float(wert[1]), float(wert[2])), feld], device=geraet)
        return Hautwert(art, feld)

    @classmethod
    def nach(cls, wert, art, geraet):
        """Der Wert als Art `art` (`f`, `c`, `v`)."""
        if wert.art == art:
            return wert
        n = len(wert.daten)
        if art == 'f':
            aus = wp.zeros(n, dtype=wp.float32, device=geraet)
            if wert.art == 'c':
                wp.launch(_c_zu_f, dim=n, inputs=[wert.daten, wp.vec3(*cls.GRAU), aus], device=geraet)
            else:
                wp.launch(_v_zu_f, dim=n, inputs=[wert.daten, aus], device=geraet)
            return Hautwert('f', aus)
        if wert.art == 'f':
            aus = wp.zeros(n, dtype=wp.vec3, device=geraet)
            wp.launch(_f_zu_v, dim=n, inputs=[wert.daten, aus], device=geraet)
            return Hautwert(art, aus)
        return Hautwert(art, wert.daten)           # Farbe ↔ Vektor: dasselbe Feld
