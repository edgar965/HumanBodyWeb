# -*- coding: utf-8 -*-
"""Auftragsnameendpunkte — den Namen eines Auftrags ändern (29.09.2026).

Edgar: „die namen sollen in allen Jobs angegeben werden können … geänderte namen dann auch
in der Übersicht". Ein Auftrag bekam seinen Namen bisher nur beim Anlegen; wer sich vertippt
hatte oder nach dem Lauf wusste, was drinsteht, konnte ihn nicht mehr ändern.

    POST /api/modell-aus-dateien/<bereich>/<uuid:job_id>/name/   {name}
    bereich = bildmodell | mesh | meshfigur
    → {ok, name}

EIN Endpunkt für alle drei Reiter, wie `Auftragsduplikatendpunkte` — die drei Modelle
tragen dasselbe Feld (`name`, `max_length=200`), und die Tabellen der Übersicht zeigen
genau dieses Feld. Deshalb steht der neue Name dort beim nächsten Aufruf ohne weiteres Zutun.

**Was der Name sonst noch berührt:** „Mesh to 3D" legt gespeicherte Figuren unter ihm ab und
der Mesh-Lauf kopiert sein Ergebnis als `<name>_<kennung>.glb` nach `output/Export/Foto3D`.
Beides geschieht BEIM LAUF — ein Umbenennen benennt bereits abgelegte Dateien nicht um
(sonst hinge an einem Textfeld ein Dateiumzug). Der Name hier ist die Beschriftung des
Auftrags, nicht der Schlüssel seiner Ablage; die Kennung bleibt unverändert.
"""

import json
import logging

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from ..models import Bildmodellauftrag, Blendermodellauftrag, Haarengineauftrag, Meshauftrag, Meshfigurauftrag

logger = logging.getLogger('core')

__all__ = ['Auftragsnameendpunkte']


class Auftragsnameendpunkte:
    #: Bereich → Modell. Dieselben Schlüssel wie in `Laufendeauftraege` und `Auftragsduplikat`
    #: (die `key` der Tabellen; `blendermodell` seit 29.09.2026, `haarengine` seit 30.09.2026).
    BEREICHE = {'bildmodell': Bildmodellauftrag, 'mesh': Meshauftrag, 'meshfigur': Meshfigurauftrag,
                'blendermodell': Blendermodellauftrag, 'haarengine': Haarengineauftrag}
    LAENGE = 200

    @staticmethod
    @require_POST
    def setzen(request, bereich, job_id):
        modell = Auftragsnameendpunkte.BEREICHE.get(bereich)
        if modell is None:
            return JsonResponse({'error': 'Unbekannter Bereich „%s"' % bereich}, status=404)
        try:
            name = (json.loads(request.body or b'{}').get('name') or '').strip()
        except (ValueError, AttributeError):
            return JsonResponse({'error': 'Rumpf ist kein JSON mit name'}, status=400)
        if not name:
            return JsonResponse({'error': 'Der Name darf nicht leer sein'}, status=400)
        name = name[:Auftragsnameendpunkte.LAENGE]
        job = get_object_or_404(modell, id=job_id)
        alt = job.name
        job.name = name
        job.save(update_fields=['name', 'updated_at'])
        logger.info('%s %s umbenannt: „%s" → „%s"', bereich, job.kennung, alt, name)
        return JsonResponse({'ok': True, 'name': name})
