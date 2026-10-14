# -*- coding: utf-8 -*-
"""Mesh3dvariantenendpunkte — Varianten eines Mesh-3D-Auftrags rechnen, übernehmen, löschen (13.10.2026).

POST /api/mesh3d/<kennung>/varianten/              {feld, werte?} → die Varianten anlegen und starten (`Mesh3dvarianten.anlegen`)
POST /api/mesh3d/<kennung>/varianten/uebernehmen/  {id}           → eine Variante zur Ausgabe machen (Wert gilt im Import, Modell wird gespeichert)
POST /api/mesh3d/<kennung>/varianten/loeschen/     {id?}          → eine oder alle Varianten entfernen
POST /api/mesh3d/<kennung>/varianten/anhalten/                    → den Varianten-Prozess beenden (was wartete oder rechnete, steht auf „angehalten“)

Lesen geht über den Zustand der Jobseite (`zustand.varianten`, `Mesh3dvergleich`). `400` mit dem Grund, wenn etwas nicht geht (ValueError der Dienste: Weg, laufender Import, Hauptausgabe fehlt).
"""

import json
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from ..dienste.mesh3dvarianten import Mesh3dvarianten
from ..dienste.mesh3dvariantenlauf import Mesh3dvariantenlauf
from ..dienste.mesh3dzustand import Mesh3dzustand

logger = logging.getLogger('core')

__all__ = ['Mesh3dvariantenendpunkte']


class Mesh3dvariantenendpunkte:
    @staticmethod
    def _rumpf(request):
        try:
            daten = json.loads(request.body or b'{}')
        except ValueError:
            return {}
        return daten if isinstance(daten, dict) else {}

    @staticmethod
    def _pruefen(kennung):
        return None if Mesh3dzustand.stand(kennung) is not None else JsonResponse({'error': 'Kein Auftrag %s' % kennung}, status=404)

    @staticmethod
    @require_POST
    def anlegen(request, kennung):
        fehler = Mesh3dvariantenendpunkte._pruefen(kennung)
        if fehler:
            return fehler
        rumpf = Mesh3dvariantenendpunkte._rumpf(request)
        werte = rumpf.get('werte')
        try:
            antwort = Mesh3dvarianten.anlegen(kennung, str(rumpf.get('feld') or ''), [str(w) for w in werte] if isinstance(werte, list) else None)
        except ValueError as grund:
            return JsonResponse({'error': str(grund)}, status=400)
        return JsonResponse({'ok': True, **antwort})

    @staticmethod
    @require_POST
    def uebernehmen(request, kennung):
        fehler = Mesh3dvariantenendpunkte._pruefen(kennung)
        if fehler:
            return fehler
        try:
            antwort = Mesh3dvarianten.uebernehmen(kennung, str(Mesh3dvariantenendpunkte._rumpf(request).get('id') or ''))
        except ValueError as grund:
            return JsonResponse({'error': str(grund)}, status=400)
        return JsonResponse({'ok': True, **antwort})

    @staticmethod
    @require_POST
    def loeschen(request, kennung):
        fehler = Mesh3dvariantenendpunkte._pruefen(kennung)
        if fehler:
            return fehler
        eintrag = Mesh3dvariantenendpunkte._rumpf(request).get('id')
        try:
            n = Mesh3dvarianten.loeschen(kennung, str(eintrag) if eintrag else None)
        except ValueError as grund:
            return JsonResponse({'error': str(grund)}, status=400)
        return JsonResponse({'ok': True, 'geloescht': n})

    @staticmethod
    @require_POST
    def anhalten(request, kennung):
        fehler = Mesh3dvariantenendpunkte._pruefen(kennung)
        if fehler:
            return fehler
        Mesh3dvariantenlauf.anhalten(kennung)
        return JsonResponse({'ok': True})
