# -*- coding: utf-8 -*-
"""Mesh3dairechnenendpunkte — Knopf „Rechnen“ von Mesh3D-AI (23.10.2026, `Mesh3dairechenlauf`, `Mesh3dairechenschlange`).

    POST /api/mesh3dai/test-neu/                       Formular: datei, name, geschlecht  → {ok, kennung, adresse}   (anlegen und rechnen)
    POST /api/mesh3dai/test/<kennung>/rechnen/                                            → {ok, stand}             (einreihen und rechnen)
    GET  /api/mesh3dai/test/<kennung>/rechnen/stand/                                      → {stand, schlange, laeuft}
"""
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from ..dienste.mesh3dairechenlauf import Mesh3dairechenlauf
from ..dienste.mesh3dairechenschlange import Mesh3dairechenschlange
from ..dienste.mesh3daitest import Mesh3daitest

__all__ = ['Mesh3dairechnenendpunkte']


class Mesh3dairechnenendpunkte:
    @staticmethod
    def _bekannt(kennung):
        return Mesh3daitest.KENNUNG.match(str(kennung)) and (Mesh3daitest.ordner() / kennung).is_dir()

    @staticmethod
    @require_POST
    def neu(request):
        datei = request.FILES.get('datei')
        if datei is None:
            return JsonResponse({'error': 'Keine Datei'}, status=400)
        try:
            kennung = Mesh3dairechenschlange.anlegen(request.POST.get('name'), datei, request.POST.get('geschlecht'))
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        Mesh3dairechenschlange.starten(kennung)
        return JsonResponse({'ok': True, 'kennung': kennung, 'adresse': '/mesh-3D-AI/test/%s/' % kennung})

    @staticmethod
    @require_POST
    def starten(request, kennung):
        if not Mesh3dairechnenendpunkte._bekannt(kennung):
            return JsonResponse({'error': 'Kein Test %s' % kennung}, status=404)
        if Mesh3dairechenschlange.laeuft() and Mesh3dairechenschlange.laeuft().get('kennung') == kennung:
            return JsonResponse({'error': 'Der Test rechnet schon'}, status=409)
        return JsonResponse({'ok': True, 'stand': Mesh3dairechenschlange.starten(kennung)})

    @staticmethod
    @require_GET
    def stand(request, kennung):
        if not Mesh3dairechnenendpunkte._bekannt(kennung):
            return JsonResponse({'error': 'Kein Test %s' % kennung}, status=404)
        schlange = Mesh3dairechenschlange.schlange()
        return JsonResponse({'stand': Mesh3dairechenlauf(kennung).stand(), 'laeuft': Mesh3dairechenschlange.laeuft(),
                             'platz': schlange.index(kennung) + 1 if kennung in schlange else None})
