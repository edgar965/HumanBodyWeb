# -*- coding: utf-8 -*-
"""Die Simulationsregler als Angaben für den Reiter.

    GET /api/garmentcode/simulationsregler/
      -> {gruppen: [{titel, felder: [{schluessel, titel, vorgabe, min, max,
                                      schritt, hinweis, schalter}]}], anzahl}

WARUM EIN ENDPUNKT UND KEINE VORLAGE (09.09.2026, Edgar: „mach alle an den
Regler … in einem aufklappbaren Bereich unter Bauen"): Es sind 42 Felder.
Stünden sie in der Vorlage, müsste jeder neue Regler an zwei Stellen gepflegt
werden — in `Simulationsfelder` und im HTML —, und die beiden liefen beim
ersten Vergessen auseinander. So gibt es eine Quelle; der Reiter baut, was
sie nennt.

WARUM EINE EIGENE DATEI: `api/garmentcode.py` gehört gerade einer zweiten
Sitzung. Ein eigener Endpunkt kostet nichts und hält beide Arbeiten
auseinander — derselbe Grund wie bei `garmentvorbilder.py`.
"""
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_GET

logger = logging.getLogger('core')

__all__ = ['Garmentsimulation']


class Garmentsimulation:
    """Der Endpunkt, der die Reglerangaben der Simulation liefert."""

    @staticmethod
    @require_GET
    def regler(request):
        from GarmentCode.simulationsfelder import Simulationsfelder

        try:
            gruppen = Simulationsfelder.nach_gruppen()
        except Exception as fehler:                              # noqa: BLE001
            logger.exception('Simulationsregler nicht lesbar')
            return JsonResponse(
                {'fehler': '%s: %s' % (type(fehler).__name__, fehler)},
                status=500)
        anzahl = sum(len(g['felder']) for g in gruppen)
        return JsonResponse({'gruppen': gruppen, 'anzahl': anzahl})
