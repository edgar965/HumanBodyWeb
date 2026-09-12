# -*- coding: utf-8 -*-
u"""Der portierte UMA-Konformer als Endpunkt — zum Ansehen, nicht nur Messen.

    GET  /api/umapython/paare/
      -> {paare: [{name, stueck, koerper, stoffpunkte}]}

    POST /api/umapython/anpassen/
         {name, umfang: 0.7..1.4, laenge: 0.8..1.2}
      -> {koerpernetz, stoffnetz, bilanz, ...}

WARUM (08.09.2026, Edgar: „zum testen mach im Dialog beim Hinzufügen eines
Modells einen zusätzlichen Button: UMA Python"): Ein Konformer lässt sich
in Zahlen prüfen — die Ruhe-Probe fällt bei jedem Bezugsfehler auf null
oder eben nicht. Ob ein Kleidungsstück SITZT, sieht man trotzdem nur im
Bild. Der Reiter stellt deshalb Körper und Stoff nebeneinander in die
Szene, und die zwei Regler verformen den Körper, während der Port den
Stoff nachzieht.

Der Körper wird radial und in der Höhe skaliert — eine definierte
geometrische Verformung, keine Körperform. Die Referenzkörper von
GarmentCode haben keine Formparameter; für die Frage „folgt der Stoff?"
ist eine nachvollziehbare Verformung ohnehin die bessere.
"""
import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

logger = logging.getLogger('core')

__all__ = ['Umapythonendpunkte']


class Umapythonendpunkte:
    u"""Paare listen und den Konformer darauf rechnen lassen."""

    #: Grenzen der beiden Regler. Weiter zu gehen bringt nichts: Ab etwa
    #: 40 % Umfangszuwachs steht der Körper überall durch den Stoff, und
    #: die Kollisionskorrektur deckelt bei 50 mm.
    UMFANG = (0.7, 1.4)
    LAENGE = (0.8, 1.2)

    @staticmethod
    @require_GET
    def paare(request):
        from UMA_Python.paare import Umapythonpaare
        try:
            return JsonResponse({'paare': Umapythonpaare.paare()})
        except OSError as fehler:
            logger.warning('UMA_Python: Paare nicht lesbar: %s', fehler)
            return JsonResponse({'paare': [], 'fehler': str(fehler)})

    @staticmethod
    @csrf_exempt
    @require_POST
    def anpassen(request):
        from UMA_Python.paare import Umapythonpaare
        try:
            wunsch = json.loads(request.body or b'{}')
        except ValueError:
            return JsonResponse({'fehler': 'Kein gültiges JSON'}, status=400)

        name = str(wunsch.get('name') or '').strip()
        if not name:
            return JsonResponse({'fehler': 'Kein Paar angegeben'}, status=400)
        umfang = Umapythonendpunkte._grenze(
            wunsch.get('umfang', 1.0), *Umapythonendpunkte.UMFANG)
        laenge = Umapythonendpunkte._grenze(
            wunsch.get('laenge', 1.0), *Umapythonendpunkte.LAENGE)

        try:
            antwort = Umapythonpaare.anpassen(name, umfang, laenge)
        except (OSError, ValueError) as fehler:
            logger.warning('UMA_Python: %s nicht anpassbar: %s', name, fehler)
            return JsonResponse({'fehler': str(fehler)}, status=400)
        if antwort.get('fehler'):
            return JsonResponse(antwort, status=400)
        return JsonResponse(antwort)

    @staticmethod
    def _grenze(wert, unten, oben):
        u"""Ein Regler kommt aus dem Browser — er wird begrenzt, nicht
        geglaubt. Ein Umfang von 0 liesse den Körper zur Linie kollabieren
        und jede Flächennormale undefiniert werden."""
        try:
            zahl = float(wert)
        # stumm gewollt: ein unlesbarer Reglerwert aus dem Browser faellt auf 1,0
        except (TypeError, ValueError):
            return 1.0
        return max(unten, min(oben, zahl))
