# -*- coding: utf-8 -*-
"""Die flachen Panels eines Schnitts als Netz für die Szene.

WARUM EIGENE DATEI: `core/api/garmentcode.py` stand bei 199 Zeilen, und
die Regel ist, dass eine Datei beim Anfassen nicht über ihre Grenze wächst
(`~/.claude/rules/struktur.md`).

WARUM ES DEN ENDPUNKT GIBT (Edgar, 07.09.2026: „der 2D button könnte das
Schnittmuster gleich aufs Modell tun, so wie die Online version") — die
Rechnung steht in `GarmentCode/schnittvorschau.py` und ist dort gegen das
`boxmesh.obj` des Upstream geprüft. Hier wird nur der Pfad abgesichert und
das Netz verpackt.

DER PFAD KOMMT AUS DEM BROWSER, ALSO WIRD ER GEPRÜFT. Ohne die Prüfung
könnte eine erfundene Anfrage jede lesbare JSON-Datei des Rechners durch
den Leser schicken und aus der Fehlermeldung erfahren, ob es sie gibt.
Erlaubt ist ausschließlich, was unterhalb des Ausgabeordners liegt.
"""
import logging
import os

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from ..daten.netzantwort import Netzantwort

logger = logging.getLogger('core')


class Schnittvorschauendpunkte:
    """Ein Endpunkt: aus einer Spezifikation die Panels im Raum."""

    @staticmethod
    @require_POST
    def netz(request):
        """Panels als Netz — Punkte in Metern, Y oben (Three-Achsen)."""
        from GarmentCode.schnittvorschau import Schnittvorschau
        pfad = Schnittvorschauendpunkte._pfad(
            request.POST.get('spezifikation') or '')
        if not pfad:
            return JsonResponse(
                {'fehler': 'Keine gültige Spezifikation angegeben'}, status=400)
        try:
            netz = Schnittvorschau(pfad).netz()
        except Exception as fehler:                       # noqa: BLE001
            logger.exception('Schnittvorschau: %s', pfad)
            return JsonResponse(
                {'fehler': '%s: %s' % (type(fehler).__name__, fehler)},
                status=500)
        if not len(netz['punkte']):
            return JsonResponse(
                {'fehler': 'Der Schnitt enthält keine baubaren Panels'},
                status=400)
        return JsonResponse({
            'vertex_count': int(len(netz['punkte'])),
            'face_count': int(len(netz['dreiecke'])),
            'vertices': Netzantwort.feld(netz['punkte'], 'vertices'),
            'faces': Netzantwort.feld(netz['dreiecke'], 'faces'),
            'panels': netz['panels'],
        })

    @staticmethod
    def _pfad(angabe):
        """Der geprüfte Pfad, oder `None`.

        `Entwurf.AUSGABE` ist die Wurzel aller Ergebnisordner. Verglichen
        wird nach `abspath` — sonst käme `…/ausgabe/../../geheim.json`
        durch, und der Vergleich sähe trotzdem richtig aus.
        """
        from GarmentCode.entwurf import Entwurf
        if not angabe or not angabe.lower().endswith('.json'):
            return None
        wurzel = os.path.abspath(str(Entwurf.AUSGABE))
        pfad = os.path.abspath(str(angabe))
        if not pfad.startswith(wurzel + os.sep) or not os.path.isfile(pfad):
            return None
        return pfad
