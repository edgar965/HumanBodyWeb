# -*- coding: utf-8 -*-
"""Vorbilder — die Bibliotheksstücke als Voreinstellungen eines Katalogstücks.

    GET /api/garmentcode/vorbilder/?vorlage=sommerkleid
      -> {vorlage, vorbilder: [{schluessel, titel, hinweis, werte}], gesamt}
    GET /api/garmentcode/vorbildbild/<name>/   Icon eines eigenen Vorbilds

WARUM EIN EIGENER ENDPUNKT (09.09.2026, Edgar: „Mach doch stattdessen neue
buttons unter den Checkboxen … mit den Namen der Garment Fit items"): Die
Passform-Voreinstellungen kommen mit `/api/garmentcode/regler/`. Sie dort
mitzuliefern wäre naheliegend, hiesse aber `api/garmentcode.py` anzufassen —
eine Datei, an der gerade eine zweite Sitzung arbeitet. Ein eigener Endpunkt
kostet nichts und hält beide Arbeiten auseinander.

DIE WERTE SIND GEMESSEN, NICHT GERECHNET. Sie kommen aus `vorbilder.json`,
die `werkzeug/vorbilder_messen.py` schreibt (181 Stücke in 10 s, davon 121
gedeutet). Fehlt die Datei, kommt eine leere Liste und `gesamt: 0` — die
Oberfläche sagt das dann, statt einen leeren Kasten zu zeigen.
"""
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_GET

logger = logging.getLogger('core')

__all__ = ['Garmentvorbilder']


class Garmentvorbilder:
    """Der Endpunkt, der die gemessenen Vorbilder eines Stücks liefert."""

    @staticmethod
    @require_GET
    def vorbilder(request):
        from GarmentCode.vorbildpresets import Vorbildpresets

        vorlage = (request.GET.get('vorlage') or '').strip()
        if not vorlage:
            return JsonResponse({'fehler': 'Kein Kleidungsstück angegeben'},
                                status=400)
        try:
            liste = Vorbildpresets.fuer(vorlage)
            gesamt = Vorbildpresets.anzahl()
        except Exception as fehler:                              # noqa: BLE001
            logger.exception('Vorbilder für %s nicht lesbar', vorlage)
            return JsonResponse(
                {'fehler': '%s: %s' % (type(fehler).__name__, fehler)},
                status=500)
        return JsonResponse({'vorlage': vorlage, 'vorbilder': liste,
                             'gesamt': gesamt})

    @staticmethod
    @require_GET
    def vorbildbild(request, name):
        """Das Icon eines EIGENEN Vorbilds (`eigenevorbilder.py`).

        Die Bibliotheksstuecke haben ihr `.thumb` beim Kleider-Endpunkt;
        ein eigenes Vorbild (Leggings, 11.09.2026) bringt sein Bild als
        Datei unter `Assets/GarmentCode/vorbilder/` mit.
        """
        from django.http import FileResponse, HttpResponseNotFound
        from GarmentCode.vorbildpresets import Vorbildpresets
        pfad = Vorbildpresets.bildpfad(name)
        if not pfad:
            return HttpResponseNotFound('Kein Bild')
        return FileResponse(open(pfad, 'rb'), content_type='image/png')
