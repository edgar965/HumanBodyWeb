# -*- coding: utf-8 -*-
u"""Ein SMPL-Koerper in anderer Form: Groesse und Fuelle als Regler.

    POST /api/character/smpl-figur/formen/
         {geschlecht: 'male'|'female', groesse: -100..100, fuelle: -100..100}
      -> {name, geschlecht, betas, punkte, dreiecke, hoehe, masse, regler}

WARUM ES DIESEN ENDPUNKT GIBT (Edgar, 06.09.2026: „der mann in Fall 2 soll
schlank sein, finde den Regler, dass du ihn schlank machst!"): Im
Online-Tool gibt es diesen Regler nicht — gemessen im laufenden Tool bleibt
der 3D-Koerper bei Bust 70 / Waist 55 / Hips 70 Punkt fuer Punkt derselbe
(142.500 Punkte, 172 cm). Formbar ist ein SMPL-Koerper nur ueber seine
Blendshapes; welcher Regler welches Beta mit welchem Vorzeichen bewegt,
steht gemessen in `GarmentCode/smplform.py`.

Der erzeugte Koerper wird abgelegt (`GarmentCode/koerper/smpl/<name>.obj`
und `.yaml`) und traegt einen Fingerabdruck der Betas im Namen — zwei
gleiche Regler ergeben dieselbe Datei, zwei verschiedene nie dieselbe.
"""
import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

logger = logging.getLogger('core')

__all__ = ['Smplformung']


class Smplformung:
    u"""Erzeugt eine geformte SMPL-Variante und liefert ihr Netz."""

    @staticmethod
    @csrf_exempt
    @require_POST
    def formen(request):
        from GarmentCode.smplform import Smplform
        from ..dienste.smplvarianten import Smplvarianten

        try:
            anfrage = json.loads(request.body.decode('utf-8') or '{}')
        except ValueError:
            anfrage = {}
        geschlecht = 'male' if str(anfrage.get('geschlecht')) == 'male' else 'female'
        groesse = anfrage.get('groesse', 0)
        fuelle = anfrage.get('fuelle', 0)

        try:
            daten = Smplvarianten.aus_reglern(geschlecht, groesse, fuelle)
        except (OSError, ValueError) as fehler:
            logger.warning('SMPL-Formung fehlgeschlagen (%s, %s/%s): %s',
                           geschlecht, groesse, fuelle, fehler)
            return JsonResponse({'fehler': str(fehler)}, status=500)

        punkte = daten['punkte']
        return JsonResponse({
            'name': daten['name'],
            'geschlecht': geschlecht,
            'smpl': True,
            'betas': daten['betas'],
            'regler': Smplform.regler(geschlecht, daten['betas']),
            'punkte': punkte.tolist(),
            'dreiecke': daten['dreiecke'].tolist(),
            'hoehe': float(daten['hoehe']),
            'masse': {k: float(v) for k, v in daten['masse'].items()},
        })
