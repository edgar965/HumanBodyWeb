# -*- coding: utf-8 -*-
"""Meshgenesisstandardanimationendpunkte — die Standardanimation der Ergebnisfigur von Mesh-Genesis (22.10.2026, `Meshgenesisanimationswahl`).

GET  /api/meshgenesis/<job>/standardanimation/          {wahl, kategorie, name, standard, standardwahl, fehlt, kategorien}
POST dieselbe Adresse {"bvh": "Kategorie/Name"}      speichert die Wahl des Jobs (400 mit Grund, wenn es die Datei nicht gibt)
GET/POST /api/meshgenesis/test/<kennung>/standardanimation/   dasselbe für einen Test
Wie `/api/mesh3d/<kennung>/animation/` bei Mesh-3D — `/api/meshgenesis/<job>/animation/` ist schon vergeben (die Bilder der Spagat-Bewegung der Zeilen).
"""
import json

from django.http import Http404, JsonResponse
from django.views.decorators.http import require_http_methods

from ..dienste.meshgenesisanimationswahl import Meshgenesisanimationswahl

__all__ = ['Meshgenesisstandardanimationendpunkte']


class Meshgenesisstandardanimationendpunkte:
    @staticmethod
    def _antworten(request, wahl, was):
        if wahl is None:
            raise Http404('Kein %s' % was)
        if request.method == 'GET':
            return JsonResponse(wahl.antwort())
        try:
            wert = json.loads(request.body or b'{}').get('bvh')
        except (ValueError, AttributeError):
            wert = None
        try:
            wahl.setzen(wert)
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse(wahl.antwort())

    @staticmethod
    @require_http_methods(['GET', 'POST'])
    def job(request, job):
        return Meshgenesisstandardanimationendpunkte._antworten(request, Meshgenesisanimationswahl.fuer_job(job), 'Job %s' % job)

    @staticmethod
    @require_http_methods(['GET', 'POST'])
    def test(request, kennung):
        return Meshgenesisstandardanimationendpunkte._antworten(request, Meshgenesisanimationswahl.fuer_test(kennung), 'Test %s' % kennung)
