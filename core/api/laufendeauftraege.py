# -*- coding: utf-8 -*-
"""Laufendeauftraege — der Fortschritt aller laufenden Aufträge in EINER Antwort (27.09.2026).

Edgar: „mach fortschrittsbalken bei allen Jobs". Die drei Tabellen auf
`/modell-aus-dateien/` (Mesh, Mesh to 3D, Modell aus Bildern) zeigten den Fortschritt nur
so, wie er beim Seitenaufruf war — er wuchs nicht. Dieser Endpunkt ist die Quelle dafür:

    GET /api/modell-aus-dateien/laufende/
    → {'mesh': [{'id', 'status', 'progress', 'progress_detail'}, …], 'meshfigur': […],
       'bildmodell': […]}

Bewusst schmal: Die vorhandenen `…/<id>/zustand/`-Endpunkte liefern Bilder, Ergebnis, Pfade,
Fotolinien — bei einem Takt von zwei Sekunden und mehreren Zeilen wäre das ein Vielfaches
der nötigen Daten (die Ladezeit-Lehre von heute Mittag, `mesh.md`). Hier kommen nur die
laufenden Aufträge und nur vier Felder, in EINER Anfrage für alle drei Bereiche.

Async wie `Meshendpunkte.zustand`: Die Seite fragt im Takt, und Daphne hat EINEN geteilten
Faden für synchrone Sichten.
"""

import logging

from asgiref.sync import sync_to_async
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from ..models import Bildmodellauftrag, Blendermodellauftrag, Meshauftrag, Meshfigurauftrag

logger = logging.getLogger('core')

__all__ = ['Laufendeauftraege']


class Laufendeauftraege:
    #: Schlüssel in der Antwort → Modell. Die Schlüssel sind dieselben Namen, die die
    #: Tabellen als `key` tragen (`Meshtabelle`, `Meshfigurtabelle`, `Bildmodelltabelle`,
    #: `Blendermodelltabelle`).
    BEREICHE = (('mesh', Meshauftrag), ('meshfigur', Meshfigurauftrag),
                ('bildmodell', Bildmodellauftrag), ('blendermodell', Blendermodellauftrag))
    FELDER = ('id', 'status', 'progress', 'progress_detail', 'schritt')

    @staticmethod
    def _sammeln():
        aus = {}
        for name, modell in Laufendeauftraege.BEREICHE:
            zeilen = modell.objects.filter(status='laeuft').values(*Laufendeauftraege.FELDER)
            aus[name] = [{'id': str(z['id']), 'status': z['status'],
                          'progress': z['progress'] or 0,
                          'progress_detail': z['progress_detail'] or z['schritt'] or ''}
                         for z in zeilen]
        return aus

    @staticmethod
    @require_GET
    async def liste(request):
        return JsonResponse(await sync_to_async(Laufendeauftraege._sammeln, thread_sensitive=True)())
