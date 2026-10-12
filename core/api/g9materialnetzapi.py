# -*- coding: utf-8 -*-
u"""G9materialnetzapi — nur die Materialien einer Genesis-9-Figur.

    POST /api/character/genesis9-figur/<name>/material/[?stufen=N]
         Rumpf wie bei `…/netz/` (haut, augen, brauen, brauenstil, praesets, …) — gelesen wird nur, was
         Materialien bestimmt (`G9materialwahl`).
         {stufen, gruppen[{name, index_ab, index_anzahl, kachel, bilder}], anhaenge[{schluessel, gruppen}]}

Der Browser nimmt sie bei einem reinen Materialwechsel (Haut, Augen, Brauenfarbe, Presets) statt der
10-MB-Netzantwort (`G9materialnetz`, `static/viewer/gemeinsam/genesis9materialabruf.js`). Nicht ueber
`G9antworten`: Die Antwort ist klein und wird nicht auf die Platte gelegt.
"""
import logging

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from Genesis9.koerpernetz import G9koerpernetz
from Genesis9.materialnetz import G9materialnetz
from Genesis9.pfade import G9pfade

from ..daten.netzausgabe import Netzausgabe
from .g9figur import FEHLT, G9figur
from .g9materialwahl import G9materialwahl

logger = logging.getLogger('core')

__all__ = ['G9materialnetzapi']


class G9materialnetzapi:
    u"""Die Materialien einer Figur, ohne Punkte."""

    @staticmethod
    @csrf_exempt
    @require_POST
    def antwort(request, name):
        if not G9pfade.vorhanden():
            return JsonResponse({'fehler': FEHLT}, status=404)
        eintrag = G9figur._eintrag(name)
        if eintrag is None:
            return JsonResponse({'fehler': u'Unbekannte Genesis-9-Figur'}, status=404)
        rumpf = G9figur._rumpf(request)
        try:
            netz = G9koerpernetz(None, eintrag, anhaenge=rumpf.get('anhaenge', True) is not False,
                                 **G9materialwahl.aus(rumpf, eintrag))
            aus = G9materialnetz.aus(netz)
        except (OSError, ValueError, KeyError) as fehler:
            logger.warning('Genesis 9: Materialien nicht baubar: %s', fehler)
            return JsonResponse({'fehler': str(fehler)}, status=500)
        return HttpResponse(Netzausgabe.kodieren(aus, False)[0], content_type='application/json')
