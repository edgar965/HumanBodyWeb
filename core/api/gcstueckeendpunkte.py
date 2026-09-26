# -*- coding: utf-8 -*-
"""Endpunkte fuer den Knopf „Neu backen" auf `/settings/kleider/`.

    POST /api/kleider/gcstuecke/starten/   startet den Stapellauf, {gestartet: true}
    GET  /api/kleider/gcstuecke/stand/     Fortschritt: geschafft, gesamt, zeile, fertig, fehler
    POST /api/kleider/gcstuecke/stoppen/   beendet den laufenden Unterprozess

Alles Weitere steht in `core/dienste/gcstueckelauf.py`.
"""

import logging

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from ..daten.anfragerumpf import Anfragerumpf
from ..dienste.gcstueckelauf import Gcstueckelauf

logger = logging.getLogger('core')


class Gcstueckeendpunkte:
    """Start, Stand und Stopp des GC-Stapellaufs."""

    @staticmethod
    @require_POST
    def starten(request):
        # `neu`: auch Stuecke bauen, deren Fingerabdruck noch passt (CLI `--neu`,
        # Checkbox „auch aktuelle Stücke neu bauen"). Leerer Rumpf -> False.
        neu, antwort = Anfragerumpf.feld(request, 'neu', vorgabe=False) if request.body else (False, None)
        if antwort is not None:
            return antwort
        try:
            Gcstueckelauf.starten(neu=bool(neu))
        except ValueError as fehler:
            return JsonResponse({'fehler': str(fehler)}, status=409)
        except Exception as fehler:  # noqa: BLE001
            logger.exception('Gcstueckelauf: Start fehlgeschlagen')
            return JsonResponse({'fehler': '%s: %s' % (type(fehler).__name__, fehler)}, status=500)
        return JsonResponse({'gestartet': True})

    @staticmethod
    @require_GET
    def stand(request):
        try:
            return JsonResponse(Gcstueckelauf.stand())
        except Exception as fehler:  # noqa: BLE001
            logger.exception('Gcstueckelauf: Stand nicht lesbar')
            return JsonResponse({'fehler': str(fehler)}, status=500)

    @staticmethod
    @require_POST
    def stoppen(request):
        Gcstueckelauf.stoppen()
        return JsonResponse({'gestoppt': True})
