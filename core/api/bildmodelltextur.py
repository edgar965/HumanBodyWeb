# -*- coding: utf-8 -*-
"""Bildmodelltexturendpunkte — die Tabelle der Texturbilder (20.09.2026).

POST /api/bildmodell/<id>/texturreihenfolge/   `{reihenfolge: [datei, …]}` — die Zeilen der
                                                Texturtabelle in dieser Reihe (Spalte „Nr.",
                                                `bilder[].textur_reihe`); Antwort `{ok, reihe,
                                                texturbilder}`.

Edgar: „bei den Texturbildern auch eine Zahl in jeder Zeile, ändere ich die, wird das Bild
sofort verschoben" — wie die Spalte „Nr." der Proportionentabelle (`reihenfolge/`), mit
eigener Nummer, weil die Texturtabelle alle Bilder zeigt, nicht nur die Hauptbilder.
"""

import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from ..dienste.bildmodelltextur import Bildmodelltextur
from ..models import Bildmodellauftrag

__all__ = ['Bildmodelltexturendpunkte']


class Bildmodelltexturendpunkte:
    @staticmethod
    @require_POST
    def reihenfolge(request, job_id):
        job = get_object_or_404(Bildmodellauftrag, pk=job_id)
        try:
            rumpf = json.loads(request.body or b'{}')
        except ValueError:
            return JsonResponse({'error': 'Kein JSON'}, status=400)
        nummern = Bildmodelltextur.reihenfolge(job.bilder, rumpf.get('reihenfolge'))
        if not nummern:
            return JsonResponse({'error': 'Keine bekannten Dateien in der Reihenfolge'}, status=400)
        job.save(update_fields=['bilder', 'updated_at'])
        return JsonResponse({'ok': True, 'reihe': nummern,
                             'texturbilder': Bildmodelltextur.liste(job.bilder)})
