# -*- coding: utf-8 -*-
"""Meshgenesistestendpunkte — Reiter „Test“ von Mesh-Genesis (16.10.2026): Netze ohne Trainingsdaten, gerechnet mit dem Netz von Ursula1 (`Meshgenesistest`).

GET /mesh-genesis/test/<kennung>/            die Seite eines Tests (Felder Mesh und Ausgabe)
GET /api/meshgenesis/test/<kennung>/          Rig, Drehungen, Ruhezentren, Kennzahlen
GET /api/meshgenesis/test/<kennung>/netz/     das Netz im Rahmen des Datensatzes (GLB, ~100.000 Dreiecke)
POST /api/meshgenesis/test/<kennung>/geschlecht/  {"geschlecht": "weiblich" | "maennlich"} — welche Figuren die Ausgabe nehmen darf (16.10.2026 abends)
POST /api/meshgenesis/test/<kennung>/wahl/    {"name": "haut_ki" | "keine_kleider", "wert": true | false} — Häkchen eines Tests ohne Job (`Meshgenesistestwahl`)
GET /api/meshgenesis/test/<kennung>/figur/<geschlecht>/netz/        Anzeigenetz der vorhergesagten Figur (Binärpaket wie `/api/meshgenesis/<job>/flaeche/netz/`, `Meshgenesisflaechennetz`)
GET /api/meshgenesis/test/<kennung>/linien/0/   Messlinien der Regler-KI aus dem Formschritt (Binärpaket `Meshgenesislinien`, 27.10.2026)
GET /api/meshgenesis/test/<kennung>/linien/flaeche/   das Mesh in der A-Pose im Raum dieser Linien (`Meshgenesislinienflaeche`, 27.10.2026)
GET /api/meshgenesis/test/<kennung>/meshanpassung/    die Genesis-Figur, ohne KI in das Netz eingepasst, mit dem Netz (`Meshgenesistestanpassung`, 28.10.2026)
GET /api/meshgenesis/test/<kennung>/figur/<geschlecht>/bild/<name>  ein Bild dieser Figur (Haut) — die Kachel der KI, wenn Stufe 2 die Haut gerechnet hat (`Meshgenesistesthaut`), sonst die Grundhaut
Die Liste steht im Reiter „Test“ der Seite `/mesh-genesis/` (`Meshgenesisendpunkte.liste`).
"""

import json

from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from ..dienste.auftragsdatei import Auftragsdatei
from ..dienste.meshgenesisflaechennetz import Meshgenesisflaechennetz
from ..dienste.meshgenesistest import Meshgenesistest

__all__ = ['Meshgenesistestendpunkte']


class Meshgenesistestendpunkte:
    @staticmethod
    @require_GET
    def seite(request, kennung):
        ordner = Meshgenesistest.pfad(kennung) or Meshgenesistest.angelegt(kennung)
        if ordner is None:
            raise Http404('Kein Test %s' % kennung)
        # mit den Tripo-Jobs (Ordner mit `ziel/`): sonst fiel ihre Seite auf `anlage` zurück und zeigte die Kennung statt des Namens (27.10.2026)
        info = next((t for t in Meshgenesistest.alle(mit_tripo=True) if t.get('kennung') == kennung), None) or Meshgenesistest.anlage(ordner)
        # Die Animation der Ausgabe baut eine Genesis-Figur (22.10.2026): Bilder wie auf der Jobseite (`Meshgenesistexturwahl`).
        from ..dienste.meshgenesistestwahl import Meshgenesistestwahl
        from ..dienste.meshgenesistexturwahl import Meshgenesistexturwahl
        return render(request, 'meshgenesis_test.html', {'test': info, 'wahl': Meshgenesistestwahl.lesen(kennung), 'texturweg': Meshgenesistexturwahl.gewaehlt(), 'texturkante': Meshgenesistexturwahl.KANTE})

    @staticmethod
    @require_GET
    def daten(request, kennung):
        daten = Meshgenesistest.daten(kennung)
        if daten is None:
            return JsonResponse({'error': 'Test %s fehlt oder ist noch nicht gerechnet' % kennung}, status=404)
        return JsonResponse(daten)

    @staticmethod
    @require_POST
    def geschlecht(request, kennung):
        try:
            wert = json.loads(request.body or b'{}').get('geschlecht')
        except (ValueError, AttributeError):
            wert = None
        if not Meshgenesistest.geschlecht_setzen(kennung, wert):
            return JsonResponse({'error': 'Test %s fehlt oder „%s“ ist weder weiblich noch maennlich' % (kennung, wert)}, status=400)
        return JsonResponse({'ok': True, 'geschlecht': wert})

    @staticmethod
    @require_POST
    def wahl(request, kennung):
        from ..dienste.meshgenesistestwahl import Meshgenesistestwahl
        try:
            daten = json.loads(request.body or b'{}')
            name, wert = daten.get('name'), daten.get('wert')
        except (ValueError, AttributeError):
            name, wert = None, None
        if not Meshgenesistestwahl.setzen(kennung, name, wert):
            return JsonResponse({'error': 'Test %s oder Wahl „%s“ nicht änderbar' % (kennung, name)}, status=400)
        return JsonResponse({'ok': True, 'wahl': Meshgenesistestwahl.lesen(kennung)})

    @staticmethod
    @require_GET
    def netz(request, kennung):
        datei = Meshgenesistest.vorschau(kennung)
        if datei is None:
            raise Http404('Kein Netz für Test %s' % kennung)
        return Auftragsdatei.antwort(request, datei, kennung=request.GET.get('v'))

    @staticmethod
    @require_GET
    def linien(request, kennung, nr):
        from ..dienste.meshgenesislinien import Meshgenesislinien
        ordner = Meshgenesistest.pfad(kennung)
        paket = Meshgenesislinien.test(ordner, kennung) if ordner is not None and int(nr) == 0 else None
        if paket is None:
            raise Http404('Keine Messlinien für Test %s — der Formschritt der Kette schreibt sie (Regler-KI, seit 27.10.2026)' % kennung)
        return HttpResponse(paket, content_type='application/octet-stream')

    @staticmethod
    @require_GET
    def linienflaeche(request, kennung):
        from ..dienste.meshgenesislinienflaeche import Meshgenesislinienflaeche
        ordner = Meshgenesistest.pfad(kennung)
        paket = Meshgenesislinienflaeche.paket(ordner) if ordner is not None else None
        if paket is None:
            raise Http404('Kein Mesh in der A-Pose unter den Messlinien für Test %s' % kennung)
        return HttpResponse(paket, content_type='application/octet-stream')

    @staticmethod
    @require_GET
    def meshanpassung(request, kennung):
        from ..dienste.meshgenesistestanpassung import Meshgenesistestanpassung
        ordner = Meshgenesistest.pfad(kennung)
        # `?netz=0`: ohne das Netz (Jobseite „Foto-Genesis“, nur die Figur; 08.11.2026)
        paket = Meshgenesistestanpassung.paket(ordner, ohne_netz=request.GET.get('netz') == '0') if ordner is not None else None
        if paket is None:
            raise Http404('Keine Genesis-Anpassung für Test %s — python14 meshgenesis/meshgenesis_meshanpassung.py --nur %s' % (kennung, kennung))
        return HttpResponse(paket, content_type='application/octet-stream')

    @staticmethod
    @require_GET
    def figurnetz(request, kennung, geschlecht):
        ordner = Meshgenesistest.form_ordner(kennung, geschlecht)
        # `?stufe=1` (09.11.2026, Edgar: „das ganze Anzeigenetz in Stufe 1“): Körper auf Netzstufe 1, `&matrix=1` mit der Unterteilungsmatrix (`Fotogenesiszeile1`)
        paket = Meshgenesisflaechennetz.paket(ordner, stufe=1 if request.GET.get('stufe') == '1' else 0, matrix=request.GET.get('matrix') == '1') if ordner else None
        if paket is None:
            raise Http404('Keine vorhergesagte Figur für Test %s (%s)' % (kennung, geschlecht))
        return HttpResponse(paket, content_type='application/octet-stream')

    @staticmethod
    @require_GET
    def figurbild(request, kennung, geschlecht, name):
        from ..dienste.meshgenesistesthaut import Meshgenesistesthaut
        ordner = Meshgenesistest.form_ordner(kennung, geschlecht)
        pfad = (Meshgenesistesthaut.bild(kennung, geschlecht, name) or Meshgenesisflaechennetz.bild(ordner, name)) if ordner else None
        if pfad is None:
            raise Http404('Kein Bild %s für Test %s (%s)' % (name, kennung, geschlecht))
        return Auftragsdatei.antwort(request, pfad)
