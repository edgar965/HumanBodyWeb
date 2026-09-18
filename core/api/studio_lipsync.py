# -*- coding: utf-8 -*-
"""Lippensynchronisation fuer das BVH Studio (18.09.2026, Edgar: „mach Lipsync").

    POST /api/studio/lipsync/   JSON {audioUrl, neu?}
         {ok, dauer, cues: [{start, end, form}], erkenner}
    GET  /api/studio/lipsync/   {verfuegbar, programm}

`audioUrl` ist die Adresse, die der Upload des Studios zurueckgibt
(`/media/studio_audio/<name>.mp3`); nur dieser Ordner wird gelesen
(`Lippensync.pfad_aus_url`). Die Mundformen A–H/X mit Zeiten rechnet
Rhubarb Lip Sync (`core/dienste/lippensync.py`), die Zuordnung zu den
Reglern der Figur (Genesis 9: `Vis AA` …; DEF und SMPL-X: MB-Lab-Einheiten)
macht der Browser (`gemeinsam/lipsyncformen.js`). Ergebnis liegt als
`.lipsync.json` neben der Tondatei — der zweite Aufruf kostet nichts.
"""

import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from core.dienste.lippensync import Lippensync, LipsyncFehler

logger = logging.getLogger("core")

__all__ = ["Studiolipsync"]


class Studiolipsync:
    @staticmethod
    @csrf_exempt
    @require_http_methods(["GET", "POST"])
    def cues(request):
        if request.method == "GET":
            return JsonResponse(
                {"verfuegbar": Lippensync.verfuegbar(), "programm": Lippensync.programm() or ""}
            )
        try:
            rumpf = json.loads(request.body or b"{}")
        except ValueError:
            return JsonResponse({"ok": False, "fehler": "Kein JSON"}, status=400)
        pfad = Lippensync.pfad_aus_url(rumpf.get("audioUrl"))
        if pfad is None:
            return JsonResponse({"ok": False, "fehler": "Keine Tondatei des Studios"}, status=400)
        try:
            daten = Lippensync.cues(pfad, neu=bool(rumpf.get("neu")))
        except LipsyncFehler as fehler:
            logger.warning("[lipsync] %s", fehler)
            return JsonResponse({"ok": False, "fehler": str(fehler)}, status=422)
        logger.info(
            "[lipsync] %s: %d Mundformen, %.1f s",
            pfad.rsplit("\\", 1)[-1],
            len(daten["cues"]),
            daten["dauer"],
        )
        return JsonResponse(dict(daten, ok=True))
