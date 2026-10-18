# -*- coding: utf-8 -*-
"""Modellexport — Endpunkt für „Exportieren …" im Kontextmenü der Modellzeile.

Der Browser hat die Formate schon geschrieben (GLB/OBJ/PLY/STL/DAE, siehe
`static/viewer/scene/modellexport.js`); hier werden sie nur noch abgelegt.
Nur `.blend` und `.fbx` laufen durch Blender (`core/dienste/modellexportlauf.py`).
"""

import json
import logging

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from ..dienste.modellexportlauf import Modellexportlauf, ZielAbgelehnt
from ..dienste.modellexportziel import Modellexportziel
from ..dienste.ordnersuche import Ordnersuche

logger = logging.getLogger('core')

#: Was Blender aus der GLB baut — der Rest kommt fertig aus dem Browser.
BLENDER_FORMATE = ('blend', 'fbx')


class Modellexportanfrage:
    """`vorgabe` liefert den Startordner, `vorhanden` was dort liegt, `ordnersuche` das Fenster
    „Ordner suchen", `ablegen` nimmt den Export an."""

    @staticmethod
    @require_GET
    def vorgabe(request):
        """Mit `?name=`: `<Vorgabeordner>/<Modellname>` (Dialog der Szene seit 18.10.2026),
        sonst der Vorgabeordner."""
        name = request.GET.get('name')
        if name is None:
            return JsonResponse({'ordner': str(settings.HUMANBODY_MODELLEXPORT_VORGABE_DIR)})
        return JsonResponse({'ordner': str(Modellexportziel.vorgabe(name))})

    @staticmethod
    @csrf_exempt
    @require_POST
    def vorhanden(request):
        """`{ordner, name, endungen: [".glb", "_vorne.jpg", …]}` → `{vorhanden: [Dateinamen]}`.
        Legt nichts an."""
        try:
            daten = json.loads(request.body or b'{}')
            ordner = Modellexportziel.pruefen(daten.get('ordner'))
        except (json.JSONDecodeError, ValueError) as e:
            return JsonResponse({'vorhanden': [], 'error': str(e)})
        stamm = Modellexportziel.name(daten.get('name'))
        endungen = [str(e) for e in daten.get('endungen') or [] if isinstance(e, str)]
        return JsonResponse({'ordner': str(ordner), 'stamm': stamm,
                             'vorhanden': Modellexportlauf.vorhanden(ordner, stamm, endungen)})

    @staticmethod
    @csrf_exempt
    @require_POST
    def ordnersuche(request):
        """Öffnet das Fenster „Ordner suchen" auf diesem Rechner und wartet auf die Wahl.
        → `{ordner}`, leer bei Abbruch."""
        try:
            daten = json.loads(request.body or b'{}')
        except json.JSONDecodeError:
            daten = {}
        ordner = Ordnersuche.waehlen(daten.get('start') or '', 'Exportordner wählen')
        logger.info('Modellexport: Ordnersuche → %s', ordner or '(abgebrochen)')
        return JsonResponse({'ordner': ordner})

    @staticmethod
    @csrf_exempt
    @require_POST
    def ablegen(request):
        dateien = request.FILES.getlist('dateien')
        if not dateien and 'blend_quelle' not in request.FILES:
            return JsonResponse({'error': 'Keine Datei zum Ablegen'}, status=400)
        lauf = Modellexportlauf(
            ordner_roh=request.POST.get('ordner'),
            name_roh=request.POST.get('name'),
            dateien=dateien,
            blend_quelle=request.FILES.get('blend_quelle'),
            fps=_fps(request.POST.get('fps')),
            polygone=_polygone(request.POST.get('polygone')),
            direkt=request.POST.get('direkt') == '1',
            blender_formate=_blender_formate(request.POST.get('blender_formate')),
        )
        try:
            ergebnis = lauf.ausfuehren()
        except ZielAbgelehnt as e:
            return JsonResponse({'error': str(e)}, status=400)
        warnungen = _liste(request.POST.get('warnungen'))
        if warnungen:
            logger.info('Modellexport: %s — Warnungen: %s', ergebnis['ordner'], '; '.join(warnungen))
        ergebnis['warnungen'] = warnungen
        return JsonResponse(ergebnis)


def _fps(roh):
    """Bildrate aus dem Dialog, 1–120; fehlt sie oder ist sie unbrauchbar: 30."""
    try:
        wert = int(round(float(roh)))
    except (TypeError, ValueError):
        return 30
    return min(120, max(1, wert))


def _polygone(roh):
    """Anteil der Dreiecke im `.blend`-Export, 0,05–1; fehlt er: 1 (Original)."""
    try:
        wert = float(roh)
    except (TypeError, ValueError):
        return 1.0
    return min(1.0, max(0.05, wert))


def _blender_formate(roh):
    """`"blend,fbx"` → `('blend', 'fbx')`; fehlt das Feld (ältere Aufrufer), nur `.blend` wie bisher."""
    gewaehlt = tuple(f for f in BLENDER_FORMATE if f in str(roh or '').split(','))
    return gewaehlt or ('blend',)


def _liste(roh):
    try:
        werte = json.loads(roh or '[]')
    except (json.JSONDecodeError, ValueError):
        return []
    return [str(w) for w in werte] if isinstance(werte, list) else []
