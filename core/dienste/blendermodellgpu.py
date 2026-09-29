# -*- coding: utf-8 -*-
"""Blendermodellgpu — rechnet gerade ein anderer Auftrag auf der Grafikkarte? (29.09.2026)

Es gibt genau eine GPU, und die Modelle belegen sie ganz (TRELLIS.2-4B lädt allein rund 16 GB). Zwei
Läufe zugleich enden nicht in einer Warteschlange, sondern im Absturz: Am 27.09.2026 starb ein zweiter
TRELLIS.2-Lauf beim Laden der Gewichte mit Rückgabewert 3221225477 (0xC0000005), und im Auftrag stand
nur ein abgeschnittener Fortschrittsbalken als „Fehlermeldung" (`Meshendpunkte._anderer_lauf`).

Dort wird nur der eigene Reiter geprüft. „BlenderModel" hält die Karte in seinen Schritten genauso, also
prüft es alle drei Bereiche, die sie brauchen: sich selbst, „Mesh" und „Mesh to 3D". Umgekehrt weiß „Mesh"
von „BlenderModel" nichts — dort ist nichts geändert.
"""

from ..models import Blendermodellauftrag, Meshauftrag, Meshfigurauftrag
from .blendermodellarbeiter import Blendermodellarbeiter
from .mesharbeiter import Mesharbeiter
from .meshfigurarbeiter import Meshfigurarbeiter

__all__ = ['Blendermodellgpu']


class Blendermodellgpu:
    #: (Bereich, Modell, Arbeiter) — wer die Karte halten kann.
    BEREICHE = (
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
