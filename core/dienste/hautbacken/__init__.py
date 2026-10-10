# -*- coding: utf-8 -*-
"""Hautbacken — die Haut einer fremden Datei auf die Genesis-Kacheln backen, ohne Blender (NVIDIA Warp auf der GPU).

Edgar (10.10.2026): „portiere das Backen, mach dafür einen eigenen Ordner, portiere schön objektorientiert, und mache tests, ob das gleiche herauskommt wie bei Blender."
Blender backte 12 Bilder (4 Kacheln × Farbe, Rauheit, Normalen) in 13,7 Minuten (Rosemary Winters, 68 s je Bild); die Probe in Warp brauchte für ein Bild 5,2 s, davon 3,8 s
zum Entpacken des Quellbildes. Die Schritte: `Hautbackenkachel` legt die UV-Dreiecke der Figur ins Raster und schießt je Texel einen Strahl auf den Körper (`Hautbackenquelle`),
`Hautbackenbild` tastet am Treffer die Bilder des Materials ab. Die Regeln (Auszug, Strahllänge, Normalen) sind an Blenders Ergebnis gemessen, nicht erdacht — die Zahlen und
die Gegenproben stehen in `.claude/rules/blendimport-hautbacken.md`.
"""

from .hautbacken import Hautbacken
from .hautbackenbild import Hautbackenbild
from .hautbackenflaeche import Hautbackenflaeche
from .hautbackenkachel import Hautbackenkachel
from .hautbackenmaterial import Hautbackenmaterial
from .hautbackennormalen import Hautbackennormalen
from .hautbackenquelle import Hautbackenquelle
from .hautbackenrand import Hautbackenrand
from .hautbackentangenten import Hautbackentangenten
from .hautbackentreffer import Hautbackentreffer

__all__ = ['Hautbacken', 'Hautbackenbild', 'Hautbackenflaeche', 'Hautbackenkachel', 'Hautbackenmaterial', 'Hautbackennormalen', 'Hautbackenquelle', 'Hautbackenrand',
           'Hautbackentangenten', 'Hautbackentreffer']
