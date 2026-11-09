# -*- coding: utf-8 -*-
"""Engine2d3dKleidergpu — rechnet gerade ein anderer Auftrag auf der Grafikkarte? (30.09.2026)

Es gibt genau eine GPU, und die Modelle belegen sie ganz. Zwei Läufe zugleich enden nicht in einer
Warteschlange, sondern im Absturz (am 27.09.2026 starb ein zweiter TRELLIS.2-Lauf beim Laden der Gewichte
mit Rückgabewert 3221225477, und im Auftrag stand nur ein abgeschnittener Fortschrittsbalken als
„Fehlermeldung", `Meshendpunkte._anderer_lauf`).

„2D3D Kleider" prüft alle Bereiche, die die Karte halten können: sich selbst, „BlenderModel", „Mesh" und
„Mesh to 3D". Umgekehrt wissen die drei nichts von „2D3D Kleider" — dort ist nichts geändert.
"""

from ..models import Blendermodellauftrag, Engine2d3dKleiderauftrag, Meshauftrag, Meshfigurauftrag
from .blendermodellarbeiter import Blendermodellarbeiter
from .engine2d3dkleiderarbeiter import Engine2d3dKleiderarbeiter
from .mesharbeiter import Mesharbeiter
from .meshfigurarbeiter import Meshfigurarbeiter
from .blendermodellgpu import Blendermodellgpu

__all__ = ['Engine2d3dKleidergpu']


class Engine2d3dKleidergpu:
    #: (Bereich, Modell, Arbeiter) — wer die Karte halten kann.
    BEREICHE = (
        ('2D3D Kleider', Engine2d3dKleiderauftrag, Engine2d3dKleiderarbeiter),
        ('BlenderModel', Blendermodellauftrag, Blendermodellarbeiter),
        ('Mesh', Meshauftrag, Mesharbeiter),
        ('Mesh to 3D', Meshfigurauftrag, Meshfigurarbeiter),
    )

    belegt_durch = classmethod(Blendermodellgpu.belegt_durch.__func__)          # dieselbe Rechnung wie `Blendermodellgpu.belegt_durch` (bis 08.11.2026 eine Kopie hier)
