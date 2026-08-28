# -*- coding: utf-8 -*-
"""Einstellungen der Anwendung und das Protokoll aus dem Browser.

Aus core/character_api.py herausgeloest (Umbau 15.08.2026) — warum so
geschnitten, steht in `core/api/__init__.py`.

UMBAU 27.08.2026 (Befunde `freie-funktionen`, `klassen-je-datei`): sechs freie
Funktionen aus ZWEI Themen. Der CharMorph-Bestand steht jetzt in
`api/charmorph_bestand.py`; hier bleiben die Einstellungen.
"""

import json
import logging

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from ..models import AppSettings
from ..daten.anfragerumpf import Anfragerumpf

logger = logging.getLogger(__name__)


class Systemendpunkte:
    """Vorgaben der Oberflaeche lesen und schreiben, Browsermeldungen loggen."""

    #: Stufen, die eine Browsermeldung tragen darf.
    STUFEN = ('error', 'warning', 'info')

    @staticmethod
    @require_GET
    def vorgaben(request):
        """Alle Vorgaben des HumanBody-Teils in einer Antwort."""
        gespeichert = AppSettings.load()
        return JsonResponse({
            'models_dir': str(settings.HUMANBODY_MODELS_DIR),
            'config': gespeichert.default_model_config,
            'scene': gespeichert.default_model_scene,
            'animations': gespeichert.default_model_animations,
            'show_rig_config': gespeichert.show_rig_config,
            'show_rig_scene': gespeichert.show_rig_scene,
            'show_rig_animations': gespeichert.show_rig_animations,
            'default_anim_config': gespeichert.default_anim_config,
            'default_anim_scene': gespeichert.default_anim_scene,
            'default_anim_animations': gespeichert.default_anim_animations,
            'expanded_panels_config': json.loads(
                gespeichert.expanded_panels_config or '[]'),
            'expanded_panels_scene': json.loads(
                gespeichert.expanded_panels_scene or '[]'),
            'selection_opacity': gespeichert.selection_opacity,
            'result': gespeichert.default_model_result,
            'default_anim_result': gespeichert.default_anim_result,
            'ui_prefs': gespeichert.ui_prefs or {},
        })

    @staticmethod
    @csrf_exempt
    @require_POST
    def vorgabe_sichern(request):
        """EINEN Schluessel in `AppSettings.ui_prefs` schreiben."""
        try:
            daten = json.loads(request.body)
            schluessel = daten.get('key')
            if not schluessel:
                return JsonResponse({'error': 'key required'}, status=400)
            gespeichert = AppSettings.load()
            vorgaben = gespeichert.ui_prefs or {}
            vorgaben[schluessel] = daten.get('value')
            gespeichert.ui_prefs = vorgaben
            gespeichert.save()
            return JsonResponse({'ok': True})
        except Exception as fehler:
            logger.exception('ui_pref_save: unerwarteter Fehler')
            return JsonResponse({'error': str(fehler)}, status=500)

    @staticmethod
    @csrf_exempt
    @require_POST
    def browsermeldung(request):
        """Eine Meldung aus dem Browser ins Serverprotokoll schreiben.

        POST /api/log/
        JSON: { page: "bvh_studio", action: "gauss_smooth_on",
                detail: "sigma=2.0", level: "info" }
        """
        # Routet auf den Logger `core.client` -> client.log
        protokoll = logging.getLogger('core.client')
        daten, fehler = Anfragerumpf.lesen(request)
        if fehler:
            return fehler
        text = '[%s] %s' % (daten.get('page', '?'), daten.get('action', '?'))
        einzelheit = daten.get('detail', '')
        if einzelheit:
            text += ' - %s' % einzelheit
        stufe = daten.get('level', 'info').lower()
        if stufe == 'error':
            protokoll.error(text)
        elif stufe == 'warning':
            protokoll.warning(text)
        else:
            protokoll.info(text)
        return JsonResponse({'ok': True})
