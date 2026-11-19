# -*- coding: utf-8 -*-
"""Hautausgleich: Gleichmäßigkeit, Symmetrie, Schatten aufhellen, Retusche auf der Albedo der Haut (`G9hautausgleich`, 18.11.2026).

    POST /api/character/genesis9-figur/hautausgleich/
        JSON {quellen: {1001: 'Runtime/Textures/…jpg', …}, werte: {gleich, symmetrie, schatten, retusche, behalten, eigen}, geschlecht: 'female'|'male'}   (Werte 0 … 1)
        → {kacheln: {1001: 'Runtime/Textures/HAUTAUSGLEICH/…jpg', …}, werte} | {fehler} (400/404)

Die Quellen sind die Albedo-Pfade, die der Körper gerade trägt (Bibliothekspfade, `Genesis9hautausgleich` im Browser); die Antwort sind neue Bilder in der
eigenen Bibliothek, geladen wie jedes Hautbild über `/textur/`. Alle Werte 0 → die Quellen zurück. Wie die übrigen Bedienfeld-Aufrufe ohne CSRF-Token.
"""
import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from Genesis9.hautausgleich import G9hautausgleich

logger = logging.getLogger('core')

__all__ = ['G9hautausgleichapi']


class G9hautausgleichapi:
    """Rechnen des Hautausgleichs."""

    @staticmethod
    @csrf_exempt
    @require_POST
    def rechnen(request):
        try:
            daten = json.loads(request.body or b'{}')
        except json.JSONDecodeError:
            return JsonResponse({'fehler': 'Ungültige Anfrage (kein JSON).'}, status=400)
        if not isinstance(daten, dict) or not isinstance(daten.get('quellen'), dict):
            return JsonResponse({'fehler': 'Ungültige Anfrage: quellen fehlt.'}, status=400)
        werte = G9hautausgleich.werte(daten.get('werte'))
        try:
            kacheln = G9hautausgleich.rechnen(daten['quellen'], werte, daten.get('geschlecht'))
        except FileNotFoundError as fehler:
            return JsonResponse({'fehler': str(fehler)}, status=404)
        return JsonResponse({'kacheln': {str(k): v for k, v in kacheln.items()}, 'werte': werte})
