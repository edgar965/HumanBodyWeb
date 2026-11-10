# -*- coding: utf-8 -*-
"""Fotogenesispshumanendpunkte — die Bildplätze der PSHuman-Eingabe eines Tests von Foto-Genesis (03.11.2026,
`Fotogenesispshumaneingabe`). Ausgeliefert wird nur, was der Platz nennt (eigenes Bild, Foto des Jobs, von PSHuman
erzeugte Ansicht), nie ein Pfad aus der Anfrage.

GET  /api/fotogenesis/<job>/pshuman/bild/<winkel>/<art>/          art: eingabe | farbe | normale
POST /api/fotogenesis/<job>/pshuman/eingabe/<winkel>/             Formular mit `datei` → {ok, platz}
POST /api/fotogenesis/<job>/pshuman/eingabe/<winkel>/entfernen/   → {ok, platz} (die Datei bleibt umbenannt liegen)
"""

import logging

from django.http import FileResponse, Http404, JsonResponse
from django.views.decorators.http import require_GET, require_POST

from ..dienste.fotogenesisjobs import Fotogenesisjobs
from ..dienste.fotogenesispshumaneingabe import Fotogenesispshumaneingabe

logger = logging.getLogger('core')

__all__ = ['Fotogenesispshumanendpunkte']


class Fotogenesispshumanendpunkte:

    @staticmethod
    def _test(job):
        gefunden = Fotogenesisjobs.job(job)
        return gefunden if gefunden is not None and gefunden.get('art') == 'foto' else None

    @staticmethod
    @require_GET
    def bild(request, job, winkel, art):
        gefunden = Fotogenesispshumanendpunkte._test(job)
        try:
            pfad = Fotogenesispshumaneingabe.pfad(gefunden, winkel, art) if gefunden else None
        except ValueError:
            pfad = None
        if pfad is None:
            raise Http404('Kein Bild %s/%s in %s' % (winkel, art, job))
        art_kopf = Fotogenesispshumaneingabe.ENDUNGEN.get(pfad.suffix.lower(), 'application/octet-stream')
        return FileResponse(open(pfad, 'rb'), content_type=art_kopf)

    @staticmethod
    @require_POST
    def eingabe(request, job, winkel):
        gefunden = Fotogenesispshumanendpunkte._test(job)
        if gefunden is None:
            return JsonResponse({'error': 'Kein Test %s' % job}, status=404)
        datei = request.FILES.get('datei')
        if datei is None:
            return JsonResponse({'error': 'Formularfeld „datei“ fehlt'}, status=400)
        try:
            platz = Fotogenesispshumaneingabe.hochladen(gefunden, winkel, datei)
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True, 'platz': platz})

    @staticmethod
    @require_POST
    def entfernen(request, job, winkel):
        gefunden = Fotogenesispshumanendpunkte._test(job)
        if gefunden is None:
            return JsonResponse({'error': 'Kein Test %s' % job}, status=404)
        try:
            platz = Fotogenesispshumaneingabe.entfernen(gefunden, winkel)
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True, 'platz': platz})
