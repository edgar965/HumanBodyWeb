# -*- coding: utf-8 -*-
"""Bildmodellproportionenendpunkte — die Eingaben des Proportionen-Popups ablegen.

Edgar (19.09.2026): „Mit einem Popup kommt ein Fenster, wo ich diese anpassen
kann. Diese Proportionen nutzt du dann für deine Berechnung."

POST `api/bildmodell/<id>/proportionen/` mit `{proportionen: {schluessel: cm}}`
schreibt die geprüften Werte (`Bildmodelloptionen.proportionen_pruefen`) nach
`job.optionen.proportionen` — leer heißt „keine Vorgabe", das rohe Zielnetz
gilt. Wirksam werden sie mit dem nächsten Lauf ab „Anpassung"
(`Bildmodellzielproportionen` formt das Zielnetz); der Start-Endpunkt behält
sie, wenn der Aufruf keine eigenen mitbringt.
"""

import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from ..dienste.bildmodelloptionen import Bildmodelloptionen
from ..models import Bildmodellauftrag

__all__ = ['Bildmodellproportionenendpunkte']


class Bildmodellproportionenendpunkte:
    """Ein Endpunkt: Proportionen stellen."""

    @staticmethod
    @require_POST
    def stellen(request, job_id):
        job = get_object_or_404(Bildmodellauftrag, pk=job_id)
        try:
            rumpf = json.loads(request.body or b'{}')
        except ValueError:
            rumpf = {}
        werte = Bildmodelloptionen.proportionen_pruefen(rumpf.get('proportionen'))
        optionen = dict(job.optionen or {})
        optionen['proportionen'] = werte
        job.optionen = optionen
        job.save(update_fields=['optionen', 'updated_at'])
        return JsonResponse({'ok': True, 'proportionen': werte})
