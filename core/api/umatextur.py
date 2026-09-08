# -*- coding: utf-8 -*-
u"""Die Texturen einer UMA-Python-Figur ausliefern.

    GET /api/umapython/textur/<rasse>/<slot>/<art>/   -> die Bilddatei

WARUM ALS EIGENER ENDPUNKT (Edgar, 08.09.2026: „UMA und UMA Python sehen
noch leicht unterschiedlich aus, z.B. bei der Haut")
=====================================================================
Die Bilder liegen als Dateien im UMA-Projekt (`UMA_Python/texturen.py`).
Sie in die JSON-Antwort zu legen hiesse, fuenf bis acht PNG base64 durch
denselben Kanal zu schicken wie das Netz — die Antwort ist jetzt schon
3,9 MB. Als eigene Adressen kommen sie nebenlaeufig und liegen danach im
Zwischenspeicher des Browsers.

DER PFAD WIRD NICHT AUS DER ANFRAGE GEBAUT
==========================================
`rasse` und `slot` waehlen aus einer LISTE, die der Server selbst
gerechnet hat; die Anfrage darf keinen Pfad beisteuern. Sonst waere der
Endpunkt ein Dateiausleser fuer das ganze Laufwerk — dieselbe Vorsicht
wie bei `/api/garmentcode/schnittnetz/` (07.09.2026).
"""
import logging
import mimetypes

from django.http import FileResponse, JsonResponse
from django.views.decorators.http import require_GET

logger = logging.getLogger('core')

__all__ = ['Umatextur']


class Umatextur:
    u"""Eine Overlay-Textur je Slot."""

    #: Was ausgeliefert werden darf. Ein Wert aus der Anfrage wird nie
    #: zu einem Dateinamen — er waehlt nur einen Eintrag aus.
    ARTEN = ('albedo', 'normalen')

    @staticmethod
    @require_GET
    def bild(request, rasse, slot, art):
        from core.dienste.umapythonfiguren import Umapythonfiguren
        from UMA_Python.szene import Szenenfigur
        if art not in Umatextur.ARTEN:
            return JsonResponse({'fehler': 'Unbekannte Art %r' % art},
                                status=400)
        try:
            gebaut = Umapythonfiguren.bauen(rasse)
        except (OSError, ValueError) as fehler:
            return JsonResponse({'fehler': str(fehler)}, status=404)
        pfad = (Szenenfigur.texturen(gebaut).get(slot) or {}).get(art)
        if pfad is None or not pfad.is_file():
            return JsonResponse(
                {'fehler': 'Keine %s-Textur fuer %s' % (art, slot)},
                status=404)
        typ = mimetypes.guess_type(str(pfad))[0] or 'application/octet-stream'
        antwort = FileResponse(open(str(pfad), 'rb'), content_type=typ)
        # Die Datei aendert sich nur mit dem UMA-Klon. Ein Jahr ist die
        # gleiche Frist wie fuer Statik mit Kennung (siehe CLAUDE.md);
        # die Adresse traegt Rasse und Slot und ist damit eindeutig.
        antwort['Cache-Control'] = 'public, max-age=31536000, immutable'
        return antwort
