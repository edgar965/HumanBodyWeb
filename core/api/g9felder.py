# -*- coding: utf-8 -*-
u"""Reglerfelder von Genesis 9 fuer den Browser: Gelenkkorrekturen und Visemes.

    GET /api/character/genesis9-figur/felder/gelenke/?stufen=1
        {stufen, graph: {kanaele, morphe, knochen}, achsen, felder}
    GET /api/character/genesis9-figur/felder/visemes/?stufen=1
        {stufen, visemes: [{id, name}], achsen, felder}

`felder` = {koerper: {kanal: {n, d}}, anhaenge: {schluessel: {kanal: {n, d}}},
knochen: {kanal: {knochen: {'rotation/x': Grad, …}}}} — `n` Punktnummern
(uint32), `d` Verschiebungen (float32, Meter, xyz je Punkt), beide base64
(`Netzantwort.feld`). `achsen` = je Knochen Daz' `orientation` (Grad, XYZ)
und `rotation_order`: damit rechnet der Browser aus der Bewegung die
Daz-Winkel (`gemeinsam/dazachsen.js`) und stellt Viseme-Knochen.

Die Antwort haengt nur an der Stufe, nicht an der Figur oder ihren
Reglern (die Unterteilung ist linear): der Browser holt sie einmal je
Stufe fuer alle Genesis-9-Figuren (`gemeinsam/genesis9felder.js`).
Gemessen (Stufe 1): 117 JCMs rund 7 s beim ersten Mal, danach Ablage.
"""
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from core.daten.netzantwort import Netzantwort
from .g9figur import FEHLT
from Genesis9.gelenkkorrekturen import G9gelenkkorrekturen
from Genesis9.netzstufe import G9netzstufe
from Genesis9.pfade import G9pfade
from Genesis9.reglerfelder import G9reglerfelder
from Genesis9.skelett import G9skelett
from Genesis9.visemes import G9visemes

__all__ = ['G9felderapi']


class G9felderapi:
    u"""Lesende Endpunkte auf die Felder je Stufe."""

    @staticmethod
    @require_GET
    def gelenke(request):
        if not G9pfade.vorhanden():
            return JsonResponse({'fehler': FEHLT}, status=404)
        stufen = G9felderapi.stufen(request)
        graph = G9gelenkkorrekturen.graph()
        felder = G9reglerfelder.holen('gelenke', graph['morphe'], stufen)
        return JsonResponse({
            'stufen': stufen, 'graph': graph, 'achsen': G9felderapi.achsen(),
            'felder': G9felderapi.kodiert(felder),
        })

    @staticmethod
    @require_GET
    def visemes(request):
        if not G9pfade.vorhanden():
            return JsonResponse({'fehler': FEHLT}, status=404)
        stufen = G9felderapi.stufen(request)
        felder = G9visemes.felder(stufen)
        return JsonResponse({
            'stufen': stufen, 'visemes': G9visemes.liste(),
            'achsen': G9felderapi.achsen(), 'felder': G9felderapi.kodiert(felder),
        })

    @staticmethod
    def stufen(request):
        try:
            return max(0, min(2, int(request.GET.get('stufen', G9netzstufe.browser()))))
        except (TypeError, ValueError):
            return G9netzstufe.browser()

    @staticmethod
    def achsen():
        u"""`{knochen: {o: [x, y, z] Grad, r: 'XYZ'}}` aller 138 Knochen."""
        return {k['name']: {'o': [round(float(w), 4) for w in k['orientation']],
                            'r': k['reihenfolge']}
                for k in G9skelett.roh()}

    @staticmethod
    def kodiert(felder):
        def paar(nummern, deltas):
            return {'n': Netzantwort.feld(nummern, 'n', typ='uint32'),
                    'd': Netzantwort.feld(deltas, 'd'), 'anzahl': int(len(nummern))}
        return {
            'koerper': {k: paar(*v) for k, v in felder.koerper.items()},
            'anhaenge': {s: {k: paar(*v) for k, v in kanaele.items()}
                         for s, kanaele in felder.anhaenge.items()},
            'knochen': felder.knochen,
        }
