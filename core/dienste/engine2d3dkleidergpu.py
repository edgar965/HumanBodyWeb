# -*- coding: utf-8 -*-
"""Engine2d3dKleidergpu — rechnet gerade ein anderer Auftrag auf der Grafikkarte? (30.09.2026)

Es gibt genau eine GPU, und die Modelle belegen sie ganz. Zwei Läufe zugleich enden nicht in einer
Warteschlange, sondern im Absturz (am 27.09.2026 starb ein zweiter TRELLIS.2-Lauf beim Laden der Gewichte
mit Rückgabewert 3221225477, und im Auftrag stand nur ein abgeschnittener Fortschrittsbalken als
„Fehlermeldung", `Meshendpunkte._anderer_lauf`).

„Haar Engine" prüft alle Bereiche, die die Karte halten können: sich selbst, „BlenderModel", „Mesh" und
„Mesh to 3D". Umgekehrt wissen die drei nichts von „Haar Engine" — dort ist nichts geändert.
"""

from ..models import Blendermodellauftrag, Engine2d3dKleiderauftrag, Meshauftrag, Meshfigurauftrag
from .blendermodellarbeiter import Blendermodellarbeiter
from .engine2d3dkleiderarbeiter import Engine2d3dKleiderarbeiter
from .mesharbeiter import Mesharbeiter
from .meshfigurarbeiter import Meshfigurarbeiter

__all__ = ['Engine2d3dKleidergpu']


class Engine2d3dKleidergpu:
    #: (Bereich, Modell, Arbeiter) — wer die Karte halten kann.
    BEREICHE = (
        ('Haar Engine', Engine2d3dKleiderauftrag, Engine2d3dKleiderarbeiter),
        ('BlenderModel', Blendermodellauftrag, Blendermodellarbeiter),
        ('Mesh', Meshauftrag, Mesharbeiter),
        ('Mesh to 3D', Meshfigurauftrag, Meshfigurarbeiter),
    )

    @classmethod
    def belegt_durch(cls, job=None):
        """Meldung, wenn ein ANDERER Auftrag rechnet — sonst ''."""
        for bereich, modell, arbeiter in cls.BEREICHE:
            laufende = modell.objects.filter(status='laeuft')
            if job is not None and isinstance(job, modell):
                laufende = laufende.exclude(pk=job.pk)
            for anderer in laufende:
                if arbeiter.lebt(anderer):
                    return (
                        '„%s" (%s) rechnet gerade — es gibt nur eine Grafikkarte. '
                        'Erst abwarten oder dort anhalten.' % (anderer.name or anderer.kennung, bereich)
                    )
        return ''
