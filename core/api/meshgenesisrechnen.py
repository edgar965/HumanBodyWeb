# -*- coding: utf-8 -*-
"""Meshgenesisrechnenendpunkte — Knopf „Rechnen“ von Mesh-Genesis (23.10.2026, `Meshgenesisrechenlauf`, `Meshgenesisrechenschlange`).

    POST /api/meshgenesis/test-neu/                       Formular: datei, name, geschlecht  → {ok, kennung, adresse}   (anlegen und rechnen)
    POST /api/meshgenesis/test/<kennung>/rechnen/         {ab?}                              → {ok, stand}             (einreihen und rechnen; ab: Schlüssel des ersten Schritts, 400 bei unbekanntem Schritt oder fehlendem Vorlauf)
    GET  /api/meshgenesis/test/<kennung>/rechnen/stand/                                      → {stand, schlange, laeuft}
"""
import json

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from ..dienste.meshgenesisrechenlauf import Meshgenesisrechenlauf
from ..dienste.meshgenesisrechenschlange import Meshgenesisrechenschlange
from ..dienste.meshgenesistest import Meshgenesistest

__all__ = ['Meshgenesisrechnenendpunkte']


class Meshgenesisrechnenendpunkte:
    @staticmethod
    def _bekannt(kennung):
        return Meshgenesistest.KENNUNG.match(str(kennung)) and (Meshgenesistest.ordner() / kennung).is_dir()

    @staticmethod
    @require_POST
    def neu(request):
        datei = request.FILES.get('datei')
        if datei is None:
            return JsonResponse({'error': 'Keine Datei'}, status=400)
        try:
            kennung = Meshgenesisrechenschlange.anlegen(request.POST.get('name'), datei, request.POST.get('geschlecht'))
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        Meshgenesisrechenschlange.starten(kennung)
        return JsonResponse({'ok': True, 'kennung': kennung, 'adresse': '/mesh-genesis/test/%s/' % kennung})

    @staticmethod
    @require_POST
    def starten(request, kennung):
        if not Meshgenesisrechnenendpunkte._bekannt(kennung):
            return JsonResponse({'error': 'Kein Test %s' % kennung}, status=404)
        if Meshgenesisrechenschlange.laeuft() and Meshgenesisrechenschlange.laeuft().get('kennung') == kennung:
            return JsonResponse({'error': 'Der Test rechnet schon'}, status=409)
        try:
            ab = json.loads(request.body or b'{}').get('ab') or None
            return JsonResponse({'ok': True, 'stand': Meshgenesisrechenschlange.starten(kennung, ab=ab)})
        except (ValueError, AttributeError) as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)

    @staticmethod
    @require_GET
    def stand(request, kennung):
        if not Meshgenesisrechnenendpunkte._bekannt(kennung):
            return JsonResponse({'error': 'Kein Test %s' % kennung}, status=404)
        schlange = Meshgenesisrechenschlange.schlange()
        return JsonResponse({'stand': Meshgenesisrechenlauf(kennung).stand(), 'laeuft': Meshgenesisrechenschlange.laeuft(),
                             'platz': schlange.index(kennung) + 1 if kennung in schlange else None})
