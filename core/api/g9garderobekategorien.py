# -*- coding: utf-8 -*-
u"""Die Einteilung der Genesis-9-Garderobe (`G9garderobekategorien`).

    GET  /api/character/genesis9-figur/garderobe/kategorien/
         {kategorien: [Name], zuordnung: {kennung: Name}}
    POST dieselbe Adresse, {kennung, kategorie}
         -> derselbe Stand danach; 400 bei untauglichem Namen, 404 bei
         unbekanntem Stueck.

Eigener Endpunkt statt eines Feldes in der Garderobenliste: die Liste ist
eine Ablage je Bibliotheksstand (`G9listenablage`), die Einteilung aendert
sich mit jedem Klick im Kontextmenue — der Browser legt beides zusammen
(`Genesis9garderobekategorien`).
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from Genesis9.garderobe import G9garderobe
from Genesis9.garderobekategorien import G9garderobekategorien
from Genesis9.pfade import G9pfade

from ..daten.anfragerumpf import Anfragerumpf

__all__ = ['G9garderobekategorienapi']


class G9garderobekategorienapi:
    u"""Lesen und Verschieben."""

    @staticmethod
    @csrf_exempt
    @require_http_methods(['GET', 'POST'])
    def kategorien(request):
        if request.method == 'GET':
            return JsonResponse(G9garderobekategorien.laden())
        rumpf, fehler = Anfragerumpf.lesen(request)
        if fehler is not None:
            return fehler
        if not isinstance(rumpf, dict):
            return JsonResponse({'fehler': u'Rumpf ist kein Objekt'}, status=400)
        kennung = str(rumpf.get('kennung') or '')
        eintrag = G9garderobe.eintrag(kennung) if G9pfade.vorhanden() else None
        if eintrag is None:
            return JsonResponse({'fehler': u'Unbekanntes Stück: %s' % kennung}, status=404)
        try:
            stand = G9garderobekategorien.verschieben(
                kennung, rumpf.get('kategorie'),
                vorgabe=G9garderobekategorien.vorgabe(eintrag))
        except ValueError as grund:
            return JsonResponse({'fehler': str(grund)}, status=400)
        return JsonResponse(stand)
