# -*- coding: utf-8 -*-
"""Das Closure-Modell des Principled BSDF: aus seinen Eingängen die gewichtete mittlere Normale, die Cycles beim Backen der Normalen schreibt (`surface_shader_average_normal`).

Die Rechnung ist `svm_node_closure_bsdf` (`kernel/svm/closure.h`) mit den Gewichten jeder Closure (Schichtung, Albedo-Tabellen, Energieerhaltung), Blender v5.2.2. Siehe `Hautclosure`
(Ablauf und Grenzen) und `hautclosurekernel.py` (die Rechnung je Texel)."""

from .hautclosure import Hautclosure

__all__ = ['Hautclosure']
