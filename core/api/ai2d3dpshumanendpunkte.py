# -*- coding: utf-8 -*-
"""Ai2d3dpshumanendpunkte — die Bildplätze der PSHuman-Eingabe eines Tests von 2d-3d-AI (03.11.2026,
`Ai2d3dpshumaneingabe`). Ausgeliefert wird nur, was der Platz nennt (eigenes Bild, Foto des Jobs, von PSHuman
erzeugte Ansicht), nie ein Pfad aus der Anfrage.

GET  /api/2d3dai/<job>/pshuman/bild/<winkel>/<art>/          art: eingabe | farbe | normale
POST /api/2d3dai/<job>/pshuman/eingabe/<winkel>/             Formular mit `datei` → {ok, platz}
POST /api/2d3dai/<job>/pshuman/eingabe/<winkel>/entfernen/   → {ok, platz} (die Datei bleibt umbenannt liegen)
"""

import logging

from django.http import FileResponse, Http404, JsonResponse
from django.views.decorators.http import require_GET, require_POST

from ..dienste.ai2d3djobs import Ai2d3djobs
from ..dienste.ai2d3dpshumaneingabe import Ai2d3dpshumaneingabe

logger = logging.getLogger('core')

__all__ = ['Ai2d3dpshumanendpunkte']


class Ai2d3dpshumanendpunkte:

    @staticmethod
    def _test(job):
        gefunden = Ai2d3djobs.job(job)
        return gefunden if gefunden is not None and gefunden.get('art') == 'foto' else None

    @staticmethod
    @require_GET
    def bild(request, job, winkel, art):
        gefunden = Ai2d3dpshumanendpunkte._test(job)
        try:
            pfad = Ai2d3dpshumaneingabe.pfad(gefunden, winkel, art) if gefunden else None
        except ValueError:
            pfad = None
        if pfad is None:
            raise Http404('Kein Bild %s/%s in %s' % (winkel, art, job))
        art_kopf = Ai2d3dpshumaneingabe.ENDUNGEN.get(pfad.suffix.lower(), 'application/octet-stream')
        return FileResponse(open(pfad, 'rb'), content_type=art_kopf)

    @staticmethod
    @require_POST
    def eingabe(request, job, winkel):
        gefunden = Ai2d3dpshumanendpunkte._test(job)
        if gefunden is None:
            return JsonResponse({'error': 'Kein Test %s' % job}, status=404)
        datei = request.FILES.get('datei')
        if datei is None:
            return JsonResponse({'error': 'Formularfeld „datei“ fehlt'}, status=400)
        try:
            platz = Ai2d3dpshumaneingabe.hochladen(gefunden, winkel, datei)
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True, 'platz': platz})

    @staticmethod
    @require_POST
    def entfernen(request, job, winkel):
        gefunden = Ai2d3dpshumanendpunkte._test(job)
        if gefunden is None:
            return JsonResponse({'error': 'Kein Test %s' % job}, status=404)
        try:
            platz = Ai2d3dpshumaneingabe.entfernen(gefunden, winkel)
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True, 'platz': platz})
