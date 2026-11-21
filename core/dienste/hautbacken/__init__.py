# -*- coding: utf-8 -*-
"""Hautbacken — die Haut einer fremden Datei auf die Genesis-Kacheln backen, ohne Blender (eigene CUDA-Kerne auf der GPU, `hautbackenkerne_cu/`; bis 21.11.2026 NVIDIA Warp).

Edgar (10.10.2026): „portiere das Backen, mach dafür einen eigenen Ordner, portiere schön objektorientiert, und mache tests, ob das gleiche herauskommt wie bei Blender." und
„übernimm den ganzen Code, keine Fehler! Erfinde nichts!!" — darum ist der Rechenweg Cycles' Rechenweg, aus dem Blender-Quelltext (v5.2.2) übernommen, und jede Stelle, die davon abweicht
oder noch fehlt, steht im Kopf ihrer Datei und im Bericht des Imports.

    Hautbackenkachel   legt die UV-Dreiecke der Figur ins Raster und schießt je Texel einen Strahl auf den Körper (`Hautbackenquelle`, BVH)
    Hautbackenretri    die Dreiecke der Vierecke in der Ruhelage, wie Blender sie dort bildet
    Hautbackentangenten / Hautbackenblendernormalen   MikkTSpace und Blenders Normalenrechnung (C++ aus dem Blender-Quelltext, DLL) und eine Python-Fassung von `mesh_normals.cc`
    Hautbackenrand     der Rand um die getroffenen Texel (Blender: `bake.margin`)
    graph/             der Knotengraph des Materials, ausgewertet wie Cycles (`Hautbackengraph`, `Hautgraph`, Knoten unter `knoten/`)

Die Zahlen und die Gegenproben stehen in `.claude/rules/blendimport-hautbacken.md`; die Tests rechnen 296 Zoo-Materialien gegen Blenders Bilder (`core/tests/unit/test_hautbacken_zoo.py`).
"""

from .hautbackenflaeche import Hautbackenflaeche
from .hautbackenkachel import Hautbackenkachel
from .hautbackenquelle import Hautbackenquelle
from .hautbackenrand import Hautbackenrand
from .hautbackenretri import Hautbackenretri
from .hautbackentangenten import Hautbackentangenten
from .hautbackentreffer import Hautbackentreffer

__all__ = ['Hautbackenflaeche', 'Hautbackenkachel', 'Hautbackenquelle', 'Hautbackenrand', 'Hautbackenretri', 'Hautbackentangenten', 'Hautbackentreffer']
