# -*- coding: utf-8 -*-
"""Kleider-Export: Rumpf entgegennehmen, Motor fahren, MP4 zurueckmelden.

Django endpoint for cloth-export: receives the payload from `cloth_export.js`,
runs the chosen collision-engine pipeline, writes the MP4 to the studio
video-output directory, and returns its public URL.

UMBAU 18.08.2026 (Befund `freie-funktionen`, Kriterium 1): sieben Funktionen auf
Modulebene, keine Klasse. Motor, Ausgabeordner, Szene, Zielpfad und Antwort
stehen jetzt in `dienste/stoffexportlauf.Stoffexportlauf`; der Zielpfad selbst
liegt weiterhin in `dienste/stoffexportziel.Stoffexportziel`.

UMBAU 27.08.2026: Die letzten zwei freien Funktionen sind Methoden von
`Stoffexport` geworden, und der `sys.path`-Eingriff auf Modulebene steht in
`_pfad_bereiten()` — er lief bisher beim IMPORT, also auch dann, wenn niemand
exportiert.
"""
from __future__ import annotations

import json
import logging
import os
import sys
import time

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .dienste.stoffexportlauf import Stoffexportlauf
from .dienste.stoffexportziel import Stoffexportziel

logger = logging.getLogger(__name__)


class Stoffexport:
    """Die HTTP-Schale um `Stoffexportlauf`."""

    #: Bisherige Aufrufform — die Liste steht in `Stoffexportlauf`.
    #: Weiterleitung; die Liste selbst kommt aus `collision`.
    motoren = staticmethod(Stoffexportlauf.motoren)

    @staticmethod
    def _pfad_bereiten():
        """`collision` importierbar machen — es liegt in HumanBody, nicht hier.

        KEIN Rueckfall auf das alte Projekt A:\\HumanBodyTest mehr (Review
        12.08.2026): Es liegt noch auf der Platte. Fehlte HUMANBODY_ROOT, hat
        der Export stillschweigend Daten von DORT geladen — ein Fehler, den man
        am Ergebnis nicht erkennt. Jetzt bleibt der Pfad leer und der Import
        scheitert sichtbar.
        """
        wurzel = str(getattr(settings, 'HUMANBODY_ROOT', ''))
        eltern = os.path.dirname(wurzel)
        for teil in (wurzel, eltern):
            if teil and teil not in sys.path:
                sys.path.insert(0, teil)

    @staticmethod
    def namensstamm(scene_name):
        """Szenenname -> unbedenklicher Namensstamm (siehe `Stoffexportziel`)."""
        return Stoffexportziel({'scene_name': scene_name}, '').namensstamm()

    @staticmethod
    @csrf_exempt
    @require_POST
    def ausfuehren(request):
        """Kleider-Export: Rumpf entgegennehmen, Motor fahren, MP4 melden."""
        try:
            rumpf = json.loads(request.body)
        except Exception as fehler:
            return JsonResponse({'ok': False,
                                 'error': 'bad json: %s' % fehler}, status=400)
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
        ergebnis, fehlerantwort = Stoffexport._motor_fahren(lauf, szene, ziel)
        if fehlerantwort:
            return fehlerantwort
        return lauf.antwort(ergebnis, ziel, round(time.time() - beginn, 2))

    @staticmethod
    def _motor_fahren(lauf, szene, ziel):
        """(Ergebnis, Fehlerantwort) — genau eines der beiden ist gesetzt."""
        Stoffexport._pfad_bereiten()
        try:
            from collision import export_mp4
            return export_mp4(szene, lauf.motor, lauf.guete, ziel,
                              resolution=lauf.ziel.aufloesung()), None
        except Exception as fehler:                              # noqa: BLE001
            logger.exception('export_mp4 crashed')
            return None, JsonResponse(
                {'ok': False, 'error': 'export crashed: %s' % fehler},
                status=500)
