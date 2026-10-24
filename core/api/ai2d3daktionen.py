# -*- coding: utf-8 -*-
"""Ai2d3daktionsendpunkte — Löschen und Neuanlage auf `/2d-3d-AI/` (24.10.2026), wie `Mesh3daipapierkorbendpunkt` und „Neuer Test aus einem Mesh“ auf `/mesh-3D-AI/`.

    POST /api/2d3dai/loeschen/    {art: 'jobs'|'tests', ids: [...]}            → {ok, ziel, ergebnis: [{kennung, ok, fehler?}]}   (`Ai2d3dpapierkorb`: verschieben bzw. ausblenden)
    POST /api/2d3dai/test-neu/    Formular: fotos (mehrere), name               → {ok, kennung, adresse}                           (`Ai2d3dfotoneu`, ohne Rechnen)
"""

import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from ..dienste.ai2d3dfotoneu import Ai2d3dfotoneu
from ..dienste.ai2d3djobs import Ai2d3djobs
from ..dienste.ai2d3dpapierkorb import Ai2d3dpapierkorb

__all__ = ['Ai2d3daktionsendpunkte']


class Ai2d3daktionsendpunkte:
    @staticmethod
    @require_POST
    def loeschen(request):
        try:
            rumpf = json.loads(request.body or b'{}')
        except ValueError:
            return JsonResponse({'error': 'Rumpf ist kein JSON'}, status=400)
        art, ids = (rumpf.get('art'), rumpf.get('ids')) if isinstance(rumpf, dict) else (None, None)
        if art not in Ai2d3dpapierkorb.ARTEN or not isinstance(ids, list) or not ids:
            return JsonResponse({'error': 'Erwartet {art: jobs|tests, ids: [...]}'}, status=400)
        aus = Ai2d3dpapierkorb.loeschen(art, ids, Ai2d3djobs.alle())
        return JsonResponse(dict(aus, ok=all(e['ok'] for e in aus['ergebnis'])))

    @staticmethod
    @require_POST
    def neu(request):
        try:
            kennung = Ai2d3dfotoneu.anlegen(request.POST.get('name'), request.FILES.getlist('fotos'))
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True, 'kennung': kennung, 'adresse': '/2d-3d-AI/test/%s/' % kennung})
