# -*- coding: utf-8 -*-
"""Ai2d3daktionsendpunkte — Löschen und Neuanlage auf `/2d-3d-AI/` (24.10.2026), wie `Mesh3daipapierkorbendpunkt` und „Neuer Test aus einem Mesh“ auf `/mesh-3D-AI/`.

    POST /api/2d3dai/loeschen/    {art: 'jobs'|'tests', ids: [...]}            → {ok, ziel, ergebnis: [{kennung, ok, fehler?}]}   (`Ai2d3dpapierkorb`: verschieben bzw. ausblenden)
    POST /api/2d3dai/test-neu/    Formular: fotos (mehrere), name               → {ok, kennung, adresse}                           (`Ai2d3dfotoneu`, ohne Rechnen)
    POST /api/2d3dai/<job>/koerpergroesse/   {koerpergroesse_m: 1.85 | null}  → {ok, koerpergroesse_m}                          (`Ai2d3dkoerpergroesse`, nur Tests)
    POST /api/2d3dai/<job>/name/             {name}                            → {ok, name}                                      (`Mesh3dainame`, nur Tests)
"""

import json
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from ..dienste.ai2d3dfotoneu import Ai2d3dfotoneu
from ..dienste.ai2d3djobs import Ai2d3djobs
from ..dienste.ai2d3dkoerpergroesse import Ai2d3dkoerpergroesse
from ..dienste.ai2d3dpapierkorb import Ai2d3dpapierkorb
from ..dienste.mesh3dainame import Mesh3dainame

logger = logging.getLogger('core')

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

    @staticmethod
    @require_POST
    def koerpergroesse(request, job):
        """Die Körpergröße der Person eines Tests in seine job.json (`Ai2d3dkoerpergroesse`), Feld oben auf der Testseite."""
        gefunden = Ai2d3djobs.job(job)
        if gefunden is None:
            return JsonResponse({'error': 'Kein Job %s' % job}, status=404)
        try:
            rumpf = json.loads(request.body or b'{}')
            if not isinstance(rumpf, dict) or Ai2d3dkoerpergroesse.FELD not in rumpf:
                raise ValueError('Erwartet {%s: Meter | null}' % Ai2d3dkoerpergroesse.FELD)
            meter = Ai2d3dkoerpergroesse.setzen(gefunden, rumpf[Ai2d3dkoerpergroesse.FELD])
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True, Ai2d3dkoerpergroesse.FELD: meter})

    @staticmethod
    @require_POST
    def name(request, job):
        """Den Namen eines Tests ändern (24.10.2026, Edgar: „hast den Stift wieder vergessen, mit dem ich den Job umbenennen kann. das war drin bei mesh3d-AI job!“) — derselbe Stift
        (`gemeinsam/auftragname.js`) und dieselbe Ablage wie Mesh3D-AI: `name.json` im Testordner (`Mesh3dainame`), die job.json bleibt; Kennung und Adresse bleiben."""
        gefunden = Ai2d3djobs.job(job)
        if gefunden is None or gefunden.get('art') != 'foto':
            return JsonResponse({'error': 'Kein Test %s' % job}, status=404)
        try:
            rumpf = json.loads(request.body or b'{}')
        except ValueError:
            return JsonResponse({'error': 'Rumpf ist kein JSON mit name'}, status=400)
        try:
            name = Mesh3dainame.setzen(gefunden['ordner'], rumpf.get('name') if isinstance(rumpf, dict) else None, gefunden['name_vorgabe'])
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        logger.info('2d-3d-AI Test %s umbenannt: „%s“ → „%s“ (ursprünglich „%s“)', gefunden['id'], gefunden['name'], name, gefunden['name_vorgabe'])
        return JsonResponse({'ok': True, 'name': name})
