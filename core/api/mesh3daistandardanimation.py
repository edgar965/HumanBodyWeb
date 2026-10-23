# -*- coding: utf-8 -*-
"""Mesh3daistandardanimationendpunkte — die Standardanimation der Ergebnisfigur von Mesh3D-AI (22.10.2026, `Mesh3daianimationswahl`).

GET  /api/mesh3dai/<job>/standardanimation/          {wahl, kategorie, name, standard, standardwahl, fehlt, kategorien}
POST dieselbe Adresse {"bvh": "Kategorie/Name"}      speichert die Wahl des Jobs (400 mit Grund, wenn es die Datei nicht gibt)
GET/POST /api/mesh3dai/test/<kennung>/standardanimation/   dasselbe für einen Test
Wie `/api/mesh3d/<kennung>/animation/` bei Mesh-3D — `/api/mesh3dai/<job>/animation/` ist schon vergeben (die Bilder der Spagat-Bewegung der Zeilen).
"""
import json

from django.http import Http404, JsonResponse
from django.views.decorators.http import require_http_methods

from ..dienste.mesh3daianimationswahl import Mesh3daianimationswahl

__all__ = ['Mesh3daistandardanimationendpunkte']


class Mesh3daistandardanimationendpunkte:
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
        return Mesh3daistandardanimationendpunkte._antworten(request, Mesh3daianimationswahl.fuer_job(job), 'Job %s' % job)

    @staticmethod
    @require_http_methods(['GET', 'POST'])
    def test(request, kennung):
        return Mesh3daistandardanimationendpunkte._antworten(request, Mesh3daianimationswahl.fuer_test(kennung), 'Test %s' % kennung)
