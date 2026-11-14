# -*- coding: utf-8 -*-
u"""Bauart eines Stücks der Genesis-9-Garderobe am Eintrag setzen (`G9bauart`, 12.11.2026).

    GET  /api/character/genesis9-figur/garderobe/bauarten/
         {arten, bauart: {kennung: art}, nachgeben_mm: {kennung: mm}}
    POST /api/character/genesis9-figur/garderobe/<kennung>/bauart/   {bauart, nachgeben_mm}
         je null = zurück auf den Vorschlag; Antwort {bauart, nachgeben_mm, vorschlag} des Stücks; 400 bei untauglichem Wert,
         404 bei unbekanntem Stück.

Edgar, 12.11.2026: „mach alles, mit deinen Empfehlungen, mit dem Feature haut nachgeben lassen“ — die Bauart steht am Eintrag der Garderobe,
nicht in der Stückdatei (Konzept „Genesis zuerst“, Entscheidung 3). Nach dem Setzen holt der Browser das Stück neu (`Genesis9bauartwahl`):
Der Schlüssel des Antwortvorrats trägt den Stand (`G9antworten.schluessel`).
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from Genesis9.bauart import G9bauart
from Genesis9.garderobe import G9garderobe
from Genesis9.pfade import G9pfade

from ..daten.anfragerumpf import Anfragerumpf

__all__ = ['G9bauartapi']


class G9bauartapi:

    @staticmethod
    @require_GET
    def liste(request):
        stand = G9bauart.laden()
        return JsonResponse({'arten': list(G9bauart.ARTEN), 'grenzen_mm': list(G9bauart.NACHGEBEN_MM), **stand})

    @staticmethod
    @csrf_exempt
    @require_POST
    def setzen(request, kennung):
        rumpf, fehler = Anfragerumpf.lesen(request)
        if fehler is not None:
            return fehler
        if not isinstance(rumpf, dict):
            return JsonResponse({'fehler': u'Rumpf ist kein Objekt'}, status=400)
        eintrag = G9garderobe.eintrag(kennung) if G9pfade.vorhanden() else None
        if eintrag is None:
            return JsonResponse({'fehler': u'Unbekanntes Stück: %s' % kennung}, status=404)
        try:
            stand = G9bauart.setzen(kennung, rumpf.get('bauart') or None, rumpf.get('nachgeben_mm'))
        except ValueError as grund:
            return JsonResponse({'fehler': str(grund)}, status=400)
        art, tiefe = G9bauart.gesetzt(kennung, stand)
        return JsonResponse({'kennung': kennung, 'bauart': art, 'nachgeben_mm': tiefe, 'vorschlag': G9bauart.vorschlag(eintrag)})
