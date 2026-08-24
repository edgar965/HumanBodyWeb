"""
Django endpoint for cloth-export: receives the payload from `cloth_export.js`,
runs the chosen collision-engine pipeline, writes the MP4 to the studio
video-output directory, and returns its public URL.

UMBAU 18.08.2026 (Befund `freie-funktionen`, Kriterium 1): sieben Funktionen auf
Modulebene, keine Klasse. Motor, Ausgabeordner, Szene, Zielpfad und Antwort
stehen jetzt in `dienste/stoffexportlauf.Stoffexportlauf`; der Zielpfad selbst
liegt weiterhin in `dienste/stoffexportziel.Stoffexportziel`.
"""
from __future__ import annotations
import json
import os
import sys
import time
import logging

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .dienste.stoffexportlauf import Stoffexportlauf
from .dienste.stoffexportziel import Stoffexportziel


# Make the `collision` package importable (it lives in HumanBody, not HumanBodyWeb)
# KEIN Rueckfall auf das alte Projekt A:\HumanBodyTest mehr (Review
# 12.08.2026): Es liegt noch auf der Platte. Fehlte HUMANBODY_ROOT, hat der
# Export stillschweigend Daten von DORT geladen - ein Fehler, den man am
# Ergebnis nicht erkennt. Jetzt bleibt der Pfad leer und der Import scheitert
# sichtbar.
_HB_ROOT = str(getattr(settings, 'HUMANBODY_ROOT', ''))
_HB_PARENT = os.path.dirname(_HB_ROOT)
if _HB_ROOT and _HB_ROOT not in sys.path:
    sys.path.insert(0, _HB_ROOT)
if _HB_PARENT and _HB_PARENT not in sys.path:
    sys.path.insert(0, _HB_PARENT)

logger = logging.getLogger(__name__)

#: Bisherige Aufrufform — die Liste steht in `Stoffexportlauf`.
MOTOREN = Stoffexportlauf.MOTOREN


def _namensstamm(scene_name):
    """Szenenname -> unbedenklicher Namensstamm (siehe `Stoffexportziel`)."""
    return Stoffexportziel({'scene_name': scene_name}, '').namensstamm()


@csrf_exempt
@require_POST
def export_cloth(request):
    """Kleider-Export: Rumpf entgegennehmen, Motor fahren, MP4 zurueckmelden."""
    try:
        rumpf = json.loads(request.body)
    except Exception as fehler:
        return JsonResponse({'ok': False, 'error': f'bad json: {fehler}'},
                            status=400)

    lauf = Stoffexportlauf(rumpf)
    unbekannt = lauf.motorfehler()
    if unbekannt:
        return unbekannt
    szene, fehlerantwort = lauf.szene()
    if fehlerantwort:
        return fehlerantwort
    ziel, fehlerantwort = lauf.zielpfad()
    if fehlerantwort:
        return fehlerantwort

    beginn = time.time()
    try:
        from collision import export_mp4
        ergebnis = export_mp4(szene, lauf.motor, lauf.guete, ziel,
                              resolution=lauf.ziel.aufloesung())
    except Exception as fehler:
        logger.exception('export_mp4 crashed')
        return JsonResponse({'ok': False, 'error': f'export crashed: {fehler}'},
                            status=500)
    return lauf.antwort(ergebnis, ziel, round(time.time() - beginn, 2))
