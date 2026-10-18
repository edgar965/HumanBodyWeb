# -*- coding: utf-8 -*-
"""Mesh3daitestkleiderendpunkte — Kleider und Bestandteile eines Tests (17.10.2026 nachts, `Mesh3daitestkleider`, `Mesh3daitestmodell`).

GET  /api/mesh3dai/test/<kennung>/kleider/<geschlecht>/                    Stücke mit beiden Wegen (a Katalog, b aus dem Netz) und der wirksamen Wahl
POST /api/mesh3dai/test/<kennung>/kleider/<geschlecht>/wahl/               {"stueck": id, "wahl": "a"|"b"|"aus"} oder {"alle": "a"|"b"}
GET  /api/mesh3dai/test/<kennung>/kleid/<geschlecht>/<weg>/<id>/netz/      das Stück als Anzeigenetz (Binärpaket wie die Figur, `Mesh3daiflaechennetz`)
GET  /api/mesh3dai/test/<kennung>/kleid/<geschlecht>/<weg>/<id>/bild/<n>   seine Textur
GET  /api/mesh3dai/test/<kennung>/modell/<geschlecht>/                     Stand der Übernahme ins Modell
POST /api/mesh3dai/test/<kennung>/modell/<geschlecht>/                     {"name": …} — Figur + gewählte Stücke als Genesis-Modell speichern (eigener Prozess)
"""

import json

from django.http import Http404, HttpResponse, JsonResponse
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from ..dienste.auftragsdatei import Auftragsdatei
from ..dienste.mesh3daitestkleider import Mesh3daitestkleider

__all__ = ['Mesh3daitestkleiderendpunkte']


class Mesh3daitestkleiderendpunkte:
    @staticmethod
    def _rumpf(request):
        try:
            wert = json.loads(request.body or b'{}')
        except (ValueError, AttributeError):
            wert = {}
        return wert if isinstance(wert, dict) else {}

    @staticmethod
    @require_GET
    def liste(request, kennung, geschlecht):
        daten = Mesh3daitestkleider.liste(kennung, geschlecht)
        if daten is None:
            return JsonResponse({'error': 'Test %s oder Geschlecht %s unbekannt' % (kennung, geschlecht)}, status=404)
        return JsonResponse(daten)

    # `staticmethod`, nicht `classmethod`: `require_POST` liest `request.method` am ERSTEN Argument — mit `classmethod` wäre das die Klasse (500 bei jedem Aufruf, gesehen 17.10.2026).
    @staticmethod
    @require_POST
    def wahl(request, kennung, geschlecht):
        rumpf = Mesh3daitestkleiderendpunkte._rumpf(request)
        if 'alle' in rumpf:
            ok = Mesh3daitestkleider.wahl_setzen(kennung, geschlecht, None, rumpf.get('alle'))
        else:
            ok = Mesh3daitestkleider.wahl_setzen(kennung, geschlecht, rumpf.get('stueck'), rumpf.get('wahl'))
        if not ok:
            return JsonResponse({'error': 'Wahl nicht gesetzt: %s' % rumpf}, status=400)
        return JsonResponse(Mesh3daitestkleider.liste(kennung, geschlecht))

    @staticmethod
    @require_GET
    def netz(request, kennung, geschlecht, weg, stueck):
        paket = Mesh3daitestkleider.paket(kennung, geschlecht, weg, stueck)
        if paket is None:
            raise Http404('Kein Stück %s/%s für Test %s (%s)' % (weg, stueck, kennung, geschlecht))
        return HttpResponse(paket, content_type='application/octet-stream')

    @staticmethod
    @require_GET
    def bild(request, kennung, geschlecht, weg, stueck, name):
        pfad = Mesh3daitestkleider.bild(kennung, geschlecht, weg, stueck, name)
        if pfad is None:
            raise Http404('Kein Bild %s' % name)
        return Auftragsdatei.antwort(request, pfad)

    @staticmethod
    @require_http_methods(['GET', 'POST'])
    def modell(request, kennung, geschlecht):
        from ..dienste.mesh3daitestmodell import Mesh3daitestmodell
        if request.method == 'GET':
            stand = Mesh3daitestmodell.stand(kennung, geschlecht)
            return JsonResponse(stand) if stand is not None else JsonResponse({'error': 'Test %s unbekannt' % kennung}, status=404)
        antwort, status = Mesh3daitestmodell.starten(kennung, geschlecht, str(Mesh3daitestkleiderendpunkte._rumpf(request).get('name') or '').strip())
        return JsonResponse(antwort, status=status)
