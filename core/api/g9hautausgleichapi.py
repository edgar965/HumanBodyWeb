# -*- coding: utf-8 -*-
"""Hautausgleich: Gleichmäßigkeit, Symmetrie, Schatten aufhellen, Retusche auf der Albedo der Haut (`G9hautausgleich`, 18.11.2026).

    POST /api/character/genesis9-figur/hautausgleich/
        JSON {quellen: {1001: 'Runtime/Textures/…jpg', …}, werte: {gleich, symmetrie, schatten, retusche, behalten, eigen}, geschlecht: 'female'|'male'}   (Werte 0 … 1)
        → {kacheln: {1001: 'Runtime/Textures/HAUTAUSGLEICH/…jpg', …}, werte} | {fehler} (400/404)

Die Quellen sind die Albedo-Pfade, die der Körper gerade trägt (Bibliothekspfade, `Genesis9hautausgleich` im Browser); die Antwort sind neue Bilder in der
eigenen Bibliothek, geladen wie jedes Hautbild über `/textur/`. Alle Werte 0 → die Quellen zurück. Wie die übrigen Bedienfeld-Aufrufe ohne CSRF-Token.
Seit 20.11.2026 auch die Hautkacheln eines Mesh-Genesis-Tests (`/api/meshgenesis/test/<k>/figur/<g>/bild/10xx.jpg`, Figur der Foto-Genesis-Jobseite): sie gehen über
`Meshgenesistesthautkorrektur.bibliothek` als Bibliotheksbild in die Rechnung.

    POST /api/meshgenesis/test/<kennung>/hautkorrektur/<geschlecht>/   JSON {werte: {Name: %}} → {werte} (abgelegt am Test, `Meshgenesistesthautkorrektur`)
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
        from ..dienste.meshgenesistesthautkorrektur import Meshgenesistesthautkorrektur
        quellen = {}
        for k, v in daten['quellen'].items():
            if str(v).startswith('/api/meshgenesis/test/'):                   # Kachel eines Tests (Jobseite): als Bibliotheksbild
                v = Meshgenesistesthautkorrektur.bibliothek(v)
                if v is None:
                    return JsonResponse({'fehler': 'Hautkachel des Tests nicht gefunden: %s' % daten['quellen'][k]}, status=404)
            quellen[k] = v
        try:
            kacheln = G9hautausgleich.rechnen(quellen, werte, daten.get('geschlecht'))
        except FileNotFoundError as fehler:
            return JsonResponse({'fehler': str(fehler)}, status=404)
        return JsonResponse({'kacheln': {str(k): v for k, v in kacheln.items()}, 'werte': werte})

    @staticmethod
    @csrf_exempt
    @require_POST
    def speichern(request, kennung, geschlecht):
        """Die Korrekturen der Figur eines Tests ablegen (Foto-Genesis-Jobseite, 20.11.2026) → {werte} | {fehler} (400/404)."""
        from ..dienste.meshgenesistesthautkorrektur import Meshgenesistesthautkorrektur
        try:
            daten = json.loads(request.body or b'{}')
        except json.JSONDecodeError:
            return JsonResponse({'fehler': 'Ungültige Anfrage (kein JSON).'}, status=400)
        if not isinstance(daten, dict) or not isinstance(daten.get('werte'), dict):
            return JsonResponse({'fehler': 'Ungültige Anfrage: werte fehlt.'}, status=400)
        werte = Meshgenesistesthautkorrektur.schreiben(kennung, geschlecht, daten['werte'])
        if werte is None:
            return JsonResponse({'fehler': 'Test %s (%s) ohne Haut' % (kennung, geschlecht)}, status=404)
        return JsonResponse({'werte': werte})
