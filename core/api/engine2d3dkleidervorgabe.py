# -*- coding: utf-8 -*-
"""Engine2d3dKleidervorgabeendpunkte — der Prompt des Rundenberaters im Reiter „Bewertung" lesen und speichern (05.10.2026).

    GET  /api/engine2d3dkleider/vorgabe/             {text, gespeichert, hoechstens} — der Text von `2d3DIterationen/Edgar/vorgaben/abgleich.md`
    POST /api/engine2d3dkleider/vorgabe/speichern/   {text} → ersetzt die Datei (Vorfassung bleibt als `abgleich.md.vorher`); 400 bei einem Text, den der Prompt nicht brauchen kann

Gespeichert wird in die Datei, nicht in die Datenbank: `Nachbesserungsprompt` liest sie bei jedem Bau des Prompts, der neue Text gilt also ab der nächsten Iteration —
auch für eine Nachbesserung, die gerade läuft (ihre laufende Anfrage an die KI hat den alten Text schon).
"""

import logging

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from Edgar.vorgabe import Vorgabe

from .engine2d3dkleider import Engine2d3dKleiderendpunkte

logger = logging.getLogger('core')

__all__ = ['Engine2d3dKleidervorgabeendpunkte']


class Engine2d3dKleidervorgabeendpunkte:
    @staticmethod
    def antwort(vorgabe, text=None):
        return {'ok': True, 'text': vorgabe.lesen() if text is None else text, 'gespeichert': vorgabe.gespeichert(), 'hoechstens': Vorgabe.HOECHSTENS}

    @staticmethod
    @require_GET
    def lesen(request):
        vorgabe = Vorgabe()
        try:
            return JsonResponse(Engine2d3dKleidervorgabeendpunkte.antwort(vorgabe), json_dumps_params={'ensure_ascii': False})
        except OSError as fehler:
            logger.warning('Vorgabe nicht lesbar: %s', fehler)
            return JsonResponse({'error': 'Der Prompt ist nicht lesbar: %s' % fehler}, status=500)

    @staticmethod
    @require_POST
    def speichern(request):
        vorgabe = Vorgabe()
        try:
            text = vorgabe.speichern(Engine2d3dKleiderendpunkte.rumpf(request).get('text'))
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400, json_dumps_params={'ensure_ascii': False})
        except OSError as fehler:
            logger.warning('Vorgabe nicht gespeichert: %s', fehler)
            return JsonResponse({'error': 'Der Prompt ist nicht gespeichert: %s' % fehler}, status=500)
        logger.info('2D3D Kleider: Prompt des Rundenberaters gespeichert (%d Zeichen), gilt ab der nächsten Iteration', len(text))
        return JsonResponse(Engine2d3dKleidervorgabeendpunkte.antwort(vorgabe, text), json_dumps_params={'ensure_ascii': False})
