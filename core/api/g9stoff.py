# -*- coding: utf-8 -*-
"""Bauplan eines dForce-Stuecks fuer den Stoffschwung im Browser.

    GET /api/character/genesis9-figur/garderobe/<kennung>/stoff/<nummer>/?stufen=1
        {punkte, zeilen, kanten, indptr, indices, data, hautgewichte}

`nummer` ist die Stelle des Teils in `G9garderobe.teile(kennung)` — dieselbe
Ordnung wie `teile` in der Netzantwort. Die Antwort haengt nur am Stueck und
der Stufe, nicht an den Reglern: der Browser holt sie einmal je Stueck
(`genesis9stoffschwung.js`) und bekommt je Reglerzug nur noch Freiheit und
Lage des Kaefigs mit dem Netz (`teil.stoff`). Groesse Dancing Queen Dress,
Stufe 1: 75.977 Zeilen, Matrix ~460.000 Eintraege (rund 5 MB base64).
"""

from django.http import JsonResponse
from django.views.decorators.http import require_GET
from Genesis9.garderobe import G9garderobe
from Genesis9.netzstufe import G9netzstufe
from Genesis9.pfade import G9pfade
from Genesis9.stoff import G9stoff

from core.daten.netzantwort import Netzantwort

from .g9figur import FEHLT

__all__ = ['G9stoffapi']


class G9stoffapi:
    """Lesender Endpunkt auf Kanten, Unterteilungsmatrix und Kaefighaut."""

    @staticmethod
    @require_GET
    def bauplan(request, kennung, nummer):
        if not G9pfade.vorhanden():
            return JsonResponse({'fehler': FEHLT}, status=404)
        try:
            teile = G9garderobe.teile(kennung)
            folger, _lage = teile[int(nummer)]
        except (ValueError, IndexError, OSError, KeyError) as fehler:
            return JsonResponse({'fehler': str(fehler)}, status=404)
        if not getattr(folger, 'dynamisch', False):
            return JsonResponse({'fehler': 'Kein dForce-Stück'}, status=404)
        try:
            stufen = int(request.GET.get('stufen', G9netzstufe.browser()))
        except TypeError, ValueError:
            stufen = G9netzstufe.browser()
        plan = G9stoff.bauplan(folger, folger.netzstufe(stufen))
        return JsonResponse(
            {
                'kennung': kennung,
                'nummer': int(nummer),
                'stufen': stufen,
                'punkte': plan['punkte'],
                'zeilen': plan['zeilen'],
                'kanten': Netzantwort.feld(plan['kanten'], 'faces'),
                'indptr': Netzantwort.feld(plan['indptr'], 'indptr', typ='int32'),
                'indices': Netzantwort.feld(plan['indices'], 'indices', typ='int32'),
                'data': Netzantwort.feld(plan['data'], 'data'),
                'hautgewichte': Netzantwort.hautgewichte(plan['haut']),
            }
        )
