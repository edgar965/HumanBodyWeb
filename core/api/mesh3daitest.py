# -*- coding: utf-8 -*-
"""Mesh3daitestendpunkte — Reiter „Test“ von Mesh3D-AI (16.10.2026): Netze ohne Trainingsdaten, gerechnet mit dem Netz von Ursula1 (`Mesh3daitest`).

GET /mesh-3D-AI/test/<kennung>/            die Seite eines Tests (Felder Mesh und Ausgabe)
GET /api/mesh3dai/test/<kennung>/          Rig, Drehungen, Ruhezentren, Kennzahlen
GET /api/mesh3dai/test/<kennung>/netz/     das Netz im Rahmen des Datensatzes (GLB, ~100.000 Dreiecke)
POST /api/mesh3dai/test/<kennung>/geschlecht/  {"geschlecht": "weiblich" | "maennlich"} — welche Figuren die Ausgabe nehmen darf (16.10.2026 abends)
GET /api/mesh3dai/test/<kennung>/figur/<geschlecht>/netz/        Anzeigenetz der vorhergesagten Figur (Binärpaket wie `/api/mesh3dai/<job>/flaeche/netz/`, `Mesh3daiflaechennetz`)
GET /api/mesh3dai/test/<kennung>/figur/<geschlecht>/bild/<name>  ein Bild dieser Figur (Haut) — die Kachel der KI, wenn Stufe 2 die Haut gerechnet hat (`Mesh3daitesthaut`), sonst die Grundhaut
Die Liste steht im Reiter „Test“ der Seite `/mesh-3D-AI/` (`Mesh3daiendpunkte.liste`).
"""

import json

from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from ..dienste.auftragsdatei import Auftragsdatei
from ..dienste.mesh3daiflaechennetz import Mesh3daiflaechennetz
from ..dienste.mesh3daitest import Mesh3daitest

__all__ = ['Mesh3daitestendpunkte']


class Mesh3daitestendpunkte:
    @staticmethod
    @require_GET
    def seite(request, kennung):
        ordner = Mesh3daitest.pfad(kennung) or Mesh3daitest.angelegt(kennung)
        if ordner is None:
            raise Http404('Kein Test %s' % kennung)
        info = next((t for t in Mesh3daitest.alle() if t.get('kennung') == kennung), None) or Mesh3daitest.anlage(ordner)
        # Die Animation der Ausgabe baut eine Genesis-Figur (22.10.2026): Bilder wie auf der Jobseite (`Mesh3daitexturwahl`).
        from ..dienste.mesh3daitexturwahl import Mesh3daitexturwahl
        return render(request, 'mesh3dai_test.html', {'test': info, 'texturweg': Mesh3daitexturwahl.gewaehlt(), 'texturkante': Mesh3daitexturwahl.KANTE})

    @staticmethod
    @require_GET
    def daten(request, kennung):
        daten = Mesh3daitest.daten(kennung)
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
        if not Mesh3daitest.geschlecht_setzen(kennung, wert):
            return JsonResponse({'error': 'Test %s fehlt oder „%s“ ist weder weiblich noch maennlich' % (kennung, wert)}, status=400)
        return JsonResponse({'ok': True, 'geschlecht': wert})

    @staticmethod
    @require_GET
    def netz(request, kennung):
        datei = Mesh3daitest.vorschau(kennung)
        if datei is None:
            raise Http404('Kein Netz für Test %s' % kennung)
        return Auftragsdatei.antwort(request, datei, kennung=request.GET.get('v'))

    @staticmethod
    @require_GET
    def figurnetz(request, kennung, geschlecht):
        ordner = Mesh3daitest.form_ordner(kennung, geschlecht)
        paket = Mesh3daiflaechennetz.paket(ordner) if ordner else None
        if paket is None:
            raise Http404('Keine vorhergesagte Figur für Test %s (%s)' % (kennung, geschlecht))
        return HttpResponse(paket, content_type='application/octet-stream')

    @staticmethod
    @require_GET
    def figurbild(request, kennung, geschlecht, name):
        from ..dienste.mesh3daitesthaut import Mesh3daitesthaut
        ordner = Mesh3daitest.form_ordner(kennung, geschlecht)
        pfad = (Mesh3daitesthaut.bild(kennung, geschlecht, name) or Mesh3daiflaechennetz.bild(ordner, name)) if ordner else None
        if pfad is None:
            raise Http404('Kein Bild %s für Test %s (%s)' % (name, kennung, geschlecht))
        return Auftragsdatei.antwort(request, pfad)
