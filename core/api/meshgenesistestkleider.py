# -*- coding: utf-8 -*-
"""Meshgenesistestkleiderendpunkte — Kleider und Bestandteile eines Tests (17.10.2026 nachts, `Meshgenesistestkleider`, `Meshgenesistestmodell`).

GET  /api/meshgenesis/test/<kennung>/kleider/<geschlecht>/                    Stücke mit beiden Wegen (a Katalog, b aus dem Netz) und der wirksamen Wahl
POST /api/meshgenesis/test/<kennung>/kleider/<geschlecht>/wahl/               {"stueck": id, "wahl": "a"|"b"|"aus"} oder {"alle": "a"|"b"}
GET  /api/meshgenesis/test/<kennung>/kleid/<geschlecht>/<weg>/<id>/netz/      das Stück als Anzeigenetz (Binärpaket wie die Figur, `Meshgenesisflaechennetz`)
GET  /api/meshgenesis/test/<kennung>/kleid/<geschlecht>/<weg>/<id>/bild/<n>   seine Textur
GET  /api/meshgenesis/test/<kennung>/modell/<geschlecht>/                     Stand der Übernahme ins Modell
POST /api/meshgenesis/test/<kennung>/modell/<geschlecht>/                     {"name": …} — Figur + gewählte Stücke als Genesis-Modell speichern (eigener Prozess)
"""

import json

from django.http import Http404, HttpResponse, JsonResponse
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from ..dienste.auftragsdatei import Auftragsdatei
from ..dienste.meshgenesistestkleider import Meshgenesistestkleider

__all__ = ['Meshgenesistestkleiderendpunkte']


class Meshgenesistestkleiderendpunkte:
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
        daten = Meshgenesistestkleider.liste(kennung, geschlecht)
        if daten is None:
            return JsonResponse({'error': 'Test %s oder Geschlecht %s unbekannt' % (kennung, geschlecht)}, status=404)
        return JsonResponse(daten)

    # `staticmethod`, nicht `classmethod`: `require_POST` liest `request.method` am ERSTEN Argument — mit `classmethod` wäre das die Klasse (500 bei jedem Aufruf, gesehen 17.10.2026).
    @staticmethod
    @require_POST
    def wahl(request, kennung, geschlecht):
        rumpf = Meshgenesistestkleiderendpunkte._rumpf(request)
        if 'alle' in rumpf:
            ok = Meshgenesistestkleider.wahl_setzen(kennung, geschlecht, None, rumpf.get('alle'))
        else:
            ok = Meshgenesistestkleider.wahl_setzen(kennung, geschlecht, rumpf.get('stueck'), rumpf.get('wahl'))
        if not ok:
            return JsonResponse({'error': 'Wahl nicht gesetzt: %s' % rumpf}, status=400)
        return JsonResponse(Meshgenesistestkleider.liste(kennung, geschlecht))

    @staticmethod
    @require_POST
    def speichern(request, kennung, geschlecht):
        """Name und Kategorie eines Stücks für „Übernehmen und als Modell speichern“ (22.10.2026, `Meshgenesistestkleidspeichern`): {stueck, name?, kategorie?}."""
        rumpf = Meshgenesistestkleiderendpunkte._rumpf(request)
        try:
            ok = Meshgenesistestkleider.speichern_setzen(kennung, geschlecht, rumpf.get('stueck'), rumpf.get('name'), rumpf.get('kategorie'))
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        if not ok:
            return JsonResponse({'error': 'Test %s, Geschlecht %s oder Stück %s unbekannt' % (kennung, geschlecht, rumpf.get('stueck'))}, status=400)
        return JsonResponse(Meshgenesistestkleider.liste(kennung, geschlecht))

    @staticmethod
    @require_GET
    def netz(request, kennung, geschlecht, weg, stueck):
        paket = Meshgenesistestkleider.paket(kennung, geschlecht, weg, stueck, stufe=1 if request.GET.get('stufe') == '1' else 0)
        if paket is None:
            raise Http404('Kein Stück %s/%s für Test %s (%s)' % (weg, stueck, kennung, geschlecht))
        return HttpResponse(paket, content_type='application/octet-stream')

    @staticmethod
    @require_GET
    def bild(request, kennung, geschlecht, weg, stueck, name):
        pfad = Meshgenesistestkleider.bild(kennung, geschlecht, weg, stueck, name)
        if pfad is None:
            raise Http404('Kein Bild %s' % name)
        return Auftragsdatei.antwort(request, pfad)

    @staticmethod
    @require_http_methods(['GET', 'POST'])
    def modell(request, kennung, geschlecht):
        from ..dienste.meshgenesistestmodell import Meshgenesistestmodell
        if request.method == 'GET':
            stand = Meshgenesistestmodell.stand(kennung, geschlecht)
            return JsonResponse(stand) if stand is not None else JsonResponse({'error': 'Test %s unbekannt' % kennung}, status=404)
        antwort, status = Meshgenesistestmodell.starten(kennung, geschlecht, str(Meshgenesistestkleiderendpunkte._rumpf(request).get('name') or '').strip())
        return JsonResponse(antwort, status=status)
