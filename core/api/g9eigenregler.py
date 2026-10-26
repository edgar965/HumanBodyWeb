# -*- coding: utf-8 -*-
u"""G9eigenreglerapi — die Eigenregler des Genesis-Bedienfelds (Bereich „Eigen“, `Genesis9/eigenregler.py`; 25.10.2026, Edgar: „Mach zuerst einen einzigen Regler für Profil,
und ein UI dazu, wie ich den bedienen kann“). Das Fenster „… formen“ (`static/viewer/charakter/genesis9/genesis9umrissfenster.js`) holt Umriss und Anfasser und legt den Versatz ab:

    POST /api/character/genesis9-figur/eigenregler/<kennung>/ansicht/  {regler: {Name: Wert}}             → {umriss: [[a, b]], gewichte, anfasser: [{schluessel, anzeige, punkt, versatz}], partner, geschlossen, text, wert}
    POST /api/character/genesis9-figur/eigenregler/<kennung>/formen/   {versatz: {Anfasser: [da, db]}}    → {regler: Reglerzeile}

Umriss und Anfasser stehen in der Figur der übergebenen Regler (die Figur der Szene), ohne den Eigenregler selbst; Versatz in Metern in der Ebene der Ansicht (a nach rechts im Bild, b nach oben).
"""
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from Genesis9.eigenregler import G9eigenregler
from Genesis9.pfade import G9pfade

from .g9figur import FEHLT, G9figur

logger = logging.getLogger('core')

__all__ = ['G9eigenreglerapi']


class G9eigenreglerapi:

    @staticmethod
    def _zahlen(regler):
        u"""{Name: Wert} aus dem Rumpf — nur Zahlen."""
        aus = {}
        for k, v in (regler if isinstance(regler, dict) else {}).items():
            try:
                aus[str(k)] = float(v)
            except (TypeError, ValueError):
                continue
        return aus

    @staticmethod
    @csrf_exempt
    @require_POST
    def ansicht(request, kennung):
        if not G9pfade.vorhanden():
            return JsonResponse({'fehler': FEHLT}, status=404)
        rumpf = G9figur._rumpf(request)
        try:
            return JsonResponse(G9eigenregler.ansicht(kennung, G9eigenreglerapi._zahlen(rumpf.get('regler'))))
        except ValueError as fehler:
            return JsonResponse({'fehler': str(fehler)}, status=400)
        except (OSError, KeyError) as fehler:
            logger.warning('Eigenregler %s: Ansicht nicht lesbar (%s)', kennung, fehler)
            return JsonResponse({'fehler': str(fehler)}, status=500)

    @staticmethod
    @csrf_exempt
    @require_POST
    def formen(request, kennung):
        if not G9pfade.vorhanden():
            return JsonResponse({'fehler': FEHLT}, status=404)
        rumpf = G9figur._rumpf(request)
        versatz = rumpf.get('versatz') if isinstance(rumpf.get('versatz'), dict) else {}
        try:
            zeile = G9eigenregler.formen(kennung, versatz)
        except ValueError as fehler:
            return JsonResponse({'fehler': str(fehler)}, status=400)
        except (OSError, KeyError) as fehler:
            logger.warning('Eigenregler %s: Formen fehlgeschlagen (%s)', kennung, fehler)
            return JsonResponse({'fehler': str(fehler)}, status=500)
        logger.info('Eigenregler %s geformt: %s', kennung, zeile.get('hinweis'))
        return JsonResponse({'regler': zeile})
