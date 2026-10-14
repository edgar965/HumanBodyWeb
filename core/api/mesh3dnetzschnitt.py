# -*- coding: utf-8 -*-
"""Mesh3dnetzschnittendpunkte — ein Teil des Netzes ausschneiden (13.10.2026), siehe `Mesh3dnetzschnitt`.

    POST /api/mesh3d/<kennung>/netzauswahl/   {schnitte}                  → {ok, flaechen, entfernt, anteil, behalten, teile_vorher, teile_nachher, schnitte}   (schreibt nichts)
    POST /api/mesh3d/<kennung>/netzschnitt/   {schnitte, uebernehmen?}    → {ok, datei, ordner, flaechen_vorher, flaechen_nachher, entfernt, anteil, uebernommen, grund?}
    POST /api/mesh3d/<kennung>/netzuebernahme/ {datei}                    → {ok, uebernommen, verworfen?, weg?, grund?}   (eine gespeicherte Datei zur Quelle des Auftrags machen)
    POST /api/mesh3d/<kennung>/netzzurueck/   {}                          → {ok, datei, uebernommen, verworfen?, weg?, grund?}   (den gespeicherten Schnitt zurücknehmen: die Datei davor wird wieder Quelle; 400, wenn die Quelle keine bearbeitete ist)
    POST /api/mesh3d/<kennung>/netzwieder/    {}                          → {ok, datei, uebernommen, verworfen?, weg?, grund?}   (den zurückgenommenen Schnitt wiederholen: die jüngste Datei, die aus der jetzigen Quelle entstand, wird wieder Quelle; 400 ohne eine)

`schnitte` ist eine Liste von Auswahlen (`Mesh3dnetzauswahl`: Schritte „insel“, „rahmen“, „kasten“, „umkehren“); deren Flächen werden entfernt. 404 ohne Auftrag, 400 mit dem Grund (kein Netz, nichts
ausgewählt, Quelle keine GLB). Kann die Datei nicht zur Quelle werden (der Auftrag rechnet), bleibt sie gespeichert: Antwort 200 mit `uebernommen: false` und `grund`.
"""

import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from ..dienste.mesh3dnetzschnitt import Mesh3dnetzschnitt

__all__ = ['Mesh3dnetzschnittendpunkte']


class Mesh3dnetzschnittendpunkte:
    @staticmethod
    def _rumpf(request):
        try:
            rumpf = json.loads(request.body or b'{}')
        except ValueError:
            rumpf = {}
        return rumpf if isinstance(rumpf, dict) else {}

    @staticmethod
    def _dienst(kennung):
        try:
            return Mesh3dnetzschnitt(kennung), None
        except ValueError as fehler:
            return None, JsonResponse({'error': str(fehler)}, status=404)

    @staticmethod
    @require_POST
    def auswahl(request, kennung):
        dienst, fehler = Mesh3dnetzschnittendpunkte._dienst(kennung)
        if fehler:
            return fehler
        try:
            return JsonResponse({'ok': True, **dienst.vorschau(Mesh3dnetzschnittendpunkte._rumpf(request).get('schnitte', []))})
        except ValueError as grund:
            return JsonResponse({'error': str(grund)}, status=400)

    @staticmethod
    @require_POST
    def uebernahme(request, kennung):
        dienst, fehler = Mesh3dnetzschnittendpunkte._dienst(kennung)
        if fehler:
            return fehler
        try:
            return JsonResponse({'ok': True, **dienst.uebernehmen_datei(Mesh3dnetzschnittendpunkte._rumpf(request).get('datei'))})
        except ValueError as grund:
            return JsonResponse({'error': str(grund)}, status=400)

    @staticmethod
    @require_POST
    def zurueck(request, kennung):
        dienst, fehler = Mesh3dnetzschnittendpunkte._dienst(kennung)
        if fehler:
            return fehler
        try:
            return JsonResponse({'ok': True, **dienst.zurueck()})
        except ValueError as grund:
            return JsonResponse({'error': str(grund)}, status=400)

    @staticmethod
    @require_POST
    def wieder(request, kennung):
        dienst, fehler = Mesh3dnetzschnittendpunkte._dienst(kennung)
        if fehler:
            return fehler
        try:
            return JsonResponse({'ok': True, **dienst.wieder()})
        except ValueError as grund:
            return JsonResponse({'error': str(grund)}, status=400)

    @staticmethod
    @require_POST
    def schnitt(request, kennung):
        dienst, fehler = Mesh3dnetzschnittendpunkte._dienst(kennung)
        if fehler:
            return fehler
        rumpf = Mesh3dnetzschnittendpunkte._rumpf(request)
        try:
            return JsonResponse({'ok': True, **dienst.speichern(rumpf.get('schnitte', []), bool(rumpf.get('uebernehmen')))})
        except ValueError as grund:
            return JsonResponse({'error': str(grund)}, status=400)
