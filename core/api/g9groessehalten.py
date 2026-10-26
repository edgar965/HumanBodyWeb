# -*- coding: utf-8 -*-
u"""G9groessehaltenapi — „Größe halten“ im Genesis-Bedienfeld (R8, 25.10.2026; `Genesis9/groessehalten.py`, Browser `genesis9groessehalten.js`).

    POST /api/character/genesis9-figur/groesse-halten/  {regler: {Name: Wert}, drehung?, ziel_m?}
         mit ziel_m  → {wert, hoehe_m, abweichung_mm, schritte, anschlag, ziel_m, ms}   (Ausgleichsregler `body_bs_ProportionLegsLength` gelöst)
         ohne ziel_m → {wert, hoehe_m, schritte: 0, ms}                                   (nur die aktuelle Größe)

Gerechnet wird im Speicher (`G9formung`), nichts wird abgelegt; `ms` ist die Rechenzeit auf dem Server.
"""
import logging
import math

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from Genesis9.groessehalten import G9groessehalten
from Genesis9.pfade import G9pfade

from .g9figur import FEHLT, G9figur

logger = logging.getLogger('core')

__all__ = ['G9groessehaltenapi']


class G9groessehaltenapi:

    #: Ein Ziel außerhalb davon ist kein Mensch, sondern ein Tippfehler (Meter).
    ZIEL_MIN_M, ZIEL_MAX_M = 0.3, 4.0

    @staticmethod
    def _zahlen(regler):
        u"""{Name: Wert} aus dem Rumpf — nur endliche Zahlen."""
        aus = {}
        for k, v in (regler if isinstance(regler, dict) else {}).items():
            try:
                w = float(v)
            except (TypeError, ValueError):
                continue
            if math.isfinite(w):
                aus[str(k)] = w
        return aus

    @staticmethod
    def _ziel(roh):
        u"""Das Ziel in Metern — None, wenn keins kam; ValueError bei Unsinn."""
        if roh is None or roh == '':
            return None
        ziel = float(roh)
        unten, oben = G9groessehaltenapi.ZIEL_MIN_M, G9groessehaltenapi.ZIEL_MAX_M
        if not (math.isfinite(ziel) and unten <= ziel <= oben):
            raise ValueError(f'ziel_m {roh!r} liegt nicht zwischen {unten} und {oben} m')
        return ziel

    @staticmethod
    @csrf_exempt
    @require_POST
    def halten(request):
        if not G9pfade.vorhanden():
            return JsonResponse({'fehler': FEHLT}, status=404)
        rumpf = G9figur._rumpf(request)
        drehung = {k: dict(v) for k, v in (rumpf.get('drehung') or {}).items() if isinstance(v, dict)}
        try:
            ziel = G9groessehaltenapi._ziel(rumpf.get('ziel_m'))
        except (TypeError, ValueError) as fehler:
            return JsonResponse({'fehler': str(fehler)}, status=400)
        halten = G9groessehalten(G9groessehaltenapi._zahlen(rumpf.get('regler')), drehung)
        try:
            aus = halten.messen() if ziel is None else halten.loesen(ziel)
        except (OSError, KeyError, ValueError) as fehler:
            logger.warning('Größe halten: nicht rechenbar (%s)', fehler)
            return JsonResponse({'fehler': str(fehler)}, status=500)
        if ziel is not None:
            logger.info('Größe halten: Ziel %.4f m, %s = %.4f, Abweichung %.2f mm, %d Schritte, %.0f ms', ziel,
                        G9groessehalten.AUSGLEICH, aus['wert'], aus['abweichung_mm'], aus['schritte'], aus['ms'])
        return JsonResponse(aus)
