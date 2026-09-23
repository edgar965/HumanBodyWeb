# -*- coding: utf-8 -*-
u"""Reglerfelder von Genesis 9 fuer den Browser: Gelenkkorrekturen und Visemes.

    GET /api/character/genesis9-figur/felder/gelenke/?stufen=1
        {stufen, graph: {kanaele, morphe, knochen}, achsen, felder}
    GET /api/character/genesis9-figur/felder/visemes/?stufen=1
        {stufen, visemes: [{id, name}], achsen, felder}
    GET /api/character/genesis9-figur/garderobe/<kennung>/felder/gelenke/?stufen=1
        {kennung, gruppe, stufen, passform, teile: [{kanal: {n, d}}]}   (`G9stueckfelder`)
    … ?kaefig=1   dieselben Felder auf Daz' Kaefigpunkten (`stufen: null`) —
                  fuer den Stoff-Worker (18.09.2026 abends)
    … &laenge=-14.5&weite=-2.7   die Felder des Stuecks MIT Passform (cm,
                  `G9passformhaut`, 20.09.2026) — der Saum liegt ueber anderer Haut

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
Die Stueckfelder (Auto-Follow der JCMs auf die Kleidung, 18.09.2026
nachts) haengen am Stueck: je Teil ein Woerterbuch in der Reihenfolge
von `garderobe/<kennung>/netz/` — leer fuer Props und Stranghaar.
"""
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from core.daten.netzantwort import Netzantwort
from .g9figur import FEHLT
from Genesis9.drehknochen import G9drehknochen
from Genesis9.gelenkkorrekturen import G9gelenkkorrekturen
from Genesis9.netzstufe import G9netzstufe
from Genesis9.pfade import G9pfade
from Genesis9.reglerfelder import G9reglerfelder
from Genesis9.skelett import G9skelett
from Genesis9.stueckfelder import G9stueckfelder
from Genesis9.visemes import G9visemes
from Genesis9.mimik import G9mimik

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
    @require_GET
    def mimik(request):
        u"""Allgemeine Mimik (Braue/Auge/Wange/Mund/Nase/Zunge, `G9mimik`) —
        Mimik- und Script-Spur (22.09.2026: „ich hatte das ALLES in Auftrag
        gegeben", nicht nur Lipsync)."""
        if not G9pfade.vorhanden():
            return JsonResponse({'fehler': FEHLT}, status=404)
        stufen = G9felderapi.stufen(request)
        felder = G9mimik.felder(stufen)
        return JsonResponse({
            'stufen': stufen, 'mimik': G9mimik.liste(),
            'achsen': G9felderapi.achsen(), 'felder': G9felderapi.kodiert(felder),
        })

    @staticmethod
    @require_GET
    def stueck(request, kennung, gruppe):
        if not G9pfade.vorhanden():
            return JsonResponse({'fehler': FEHLT}, status=404)
        kanaele = G9felderapi.kanaele(gruppe)
        if kanaele is None:
            return JsonResponse({'fehler': 'Unbekannte Gruppe %s' % gruppe},
                                status=404)
        stufen = None if request.GET.get('kaefig') else G9felderapi.stufen(request)
        passform = G9felderapi.passform(request)
        try:
            felder = G9stueckfelder.holen(gruppe, kanaele, kennung, stufen, passform)
        except ValueError as fehler:
            return JsonResponse({'fehler': str(fehler)}, status=404)
        return JsonResponse({
            'kennung': kennung, 'gruppe': gruppe, 'stufen': stufen,
            'passform': felder.passform,
            'teile': [{k: G9felderapi.paar(*v) for k, v in teil.items()}
                      for teil in felder.teile],
        })

    @staticmethod
    def passform(request):
        u"""`?laenge=-14.5&weite=-2.7` (cm) — die Passform des Stuecks, dessen
        Felder gefragt sind (`G9passformhaut`, 20.09.2026); None ohne."""
        try:
            laenge = float(request.GET.get('laenge') or 0.0)
            weite = float(request.GET.get('weite') or 0.0)
        except (TypeError, ValueError):
            return None
        return (laenge, weite) if (laenge or weite) else None

    @staticmethod
    def kanaele(gruppe):
        u"""Die Kanaele einer Gruppe — oder None."""
        if gruppe == 'gelenke':
            return G9gelenkkorrekturen.graph()['morphe']
        if gruppe == 'visemes':
            return G9visemes.kennungen()
        return None

    @staticmethod
    def stufen(request):
        try:
            return max(0, min(2, int(request.GET.get('stufen', G9netzstufe.browser()))))
        except (TypeError, ValueError):
            return G9netzstufe.browser()

    @staticmethod
    def achsen():
        u"""`{knochen: {o: [x, y, z] Grad, r: 'XYZ', dreh?}}` aller 138 Knochen.

        `dreh` = `{von, quelle, achse, faktor}` an den 14 Twist-Knochen
        (`G9drehknochen`, 20.09.2026): der Browser stellt sie je Bild aus
        dem Daz-Winkel ihres Glieds — sonst sitzt die ganze Verdrehung am
        Gelenk („der Arm ist kaputt").
        """
        dreh = G9drehknochen.tabelle()
        aus = {}
        for k in G9skelett.roh():
            eintrag = {'o': [round(float(w), 4) for w in k['orientation']],
                       'r': k['reihenfolge']}
            if k['name'] in dreh:
                eintrag['dreh'] = dreh[k['name']]
            aus[k['name']] = eintrag
        return aus

    @staticmethod
    def paar(nummern, deltas):
        return {'n': Netzantwort.feld(nummern, 'n', typ='uint32'),
                'd': Netzantwort.feld(deltas, 'd'), 'anzahl': int(len(nummern))}

    @staticmethod
    def kodiert(felder):
        paar = G9felderapi.paar
        return {
            'koerper': {k: paar(*v) for k, v in felder.koerper.items()},
            'anhaenge': {s: {k: paar(*v) for k, v in kanaele.items()}
                         for s, kanaele in felder.anhaenge.items()},
            'knochen': felder.knochen,
        }
