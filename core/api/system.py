# -*- coding: utf-8 -*-
"""Einstellungen, Protokoll und CharMorph-Bestand.

Herausgeloest aus core/character_api.py (Umbau 15.08.2026). Die Datei hatte
6.495 Zeilen und 110 Endpunkte; die Themen darin waren nur durch Reihenfolge
getrennt. Die Endpunkte hier bleiben duenne Funktionen — Django-Dekoratoren,
Stapelspuren und Tests bleiben damit lesbar —, waehrend die Fachlogik in
core/dienste/ als Klassen liegt.
"""

from ..models import AppSettings
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
import json
import logging


logger = logging.getLogger(__name__)


@require_GET
def humanbody_settings_api(request):
    """Return HumanBody default model settings."""
    s = AppSettings.load()
    return JsonResponse({
        'models_dir': str(settings.HUMANBODY_MODELS_DIR),
        'config': s.default_model_config,
        'scene': s.default_model_scene,
        'animations': s.default_model_animations,
        'show_rig_config': s.show_rig_config,
        'show_rig_scene': s.show_rig_scene,
        'show_rig_animations': s.show_rig_animations,
        'default_anim_config': s.default_anim_config,
        'default_anim_scene': s.default_anim_scene,
        'default_anim_animations': s.default_anim_animations,
        'expanded_panels_config': json.loads(s.expanded_panels_config or '[]'),
        'expanded_panels_scene': json.loads(s.expanded_panels_scene or '[]'),
        'selection_opacity': s.selection_opacity,
        'result': s.default_model_result,
        'default_anim_result': s.default_anim_result,
        'ui_prefs': s.ui_prefs or {},
    })


@csrf_exempt
@require_POST
def ui_pref_save(request):
    """Save a single UI preference key/value to AppSettings.ui_prefs."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        data = json.loads(request.body)
        key = data.get('key')
        value = data.get('value')
        if not key:
            return JsonResponse({'error': 'key required'}, status=400)
        s = AppSettings.load()
        prefs = s.ui_prefs or {}
        prefs[key] = value
        s.ui_prefs = prefs
        s.save()
        return JsonResponse({'ok': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def client_log(request):
    """Receive log messages from the browser and write to server log.

    POST /api/log/
    Body JSON: { page: "bvh_studio", action: "gauss_smooth_on", detail: "sigma=2.0" }
    """
    # Routet auf core.client-Logger -> client.log
    log = logging.getLogger('core.client')
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    page = data.get('page', '?')
    action = data.get('action', '?')
    detail = data.get('detail', '')
    level = data.get('level', 'info').lower()

    msg = f'[{page}] {action}'
    if detail:
        msg += f' - {detail}'

    if level == 'error':
        log.error(msg)
    elif level == 'warning':
        log.warning(msg)
    else:
        log.info(msg)

    return JsonResponse({'ok': True})


@require_GET
def charmorph_presets(request):
    """List available CharMorph body type presets."""
    import os as _os
    preset_dir = _os.path.join(str(settings.TOOLS_ROOT), 'tools', 'CharMorphPlugin', 'data', 'characters', 'mb_female', 'presets')
    presets = []
    if _os.path.isdir(preset_dir):
        for f in sorted(_os.listdir(preset_dir)):
            if f.endswith('.json'):
                name = f.replace('.json', '').replace('type_', '').replace('specialtype_', 'special_')
                try:
                    with open(_os.path.join(preset_dir, f)) as fh:
                        data = json.load(fh)
                    meta = data.get('metaproperties', {})
                    structural = data.get('structural', {})
                    presets.append({
                        'name': name,
                        'label': name.replace('_', ' ').title(),
                        'meta': meta,
                        'structural': structural,
                    })
                except Exception:
                    logger.debug('optionaler Schritt fehlgeschlagen', exc_info=True)
    return JsonResponse({'presets': presets})


@require_GET
def charmorph_assets(request):
    """List available CharMorph clothing assets."""
    import os as _os
    try:
        import yaml
    except ImportError:
        return JsonResponse({'assets': [], 'error': 'pyyaml not installed'})
    asset_dir = _os.path.join(str(settings.TOOLS_ROOT), 'tools', 'CharMorphPlugin', 'data', 'characters', 'mb_female', 'assets')
    assets = []
    if _os.path.isdir(asset_dir):
        for entry in sorted(_os.listdir(asset_dir)):
            ep = _os.path.join(asset_dir, entry)
            if _os.path.isdir(ep):
                config_path = _os.path.join(ep, 'config.yaml')
                if _os.path.isfile(config_path):
                    try:
                        with open(config_path) as f:
                            cfg = yaml.safe_load(f)
                        assets.append({
                            'name': entry,
                            'category': cfg.get('category', 'Other'),
                            'tags': cfg.get('tags', []),
                            'fitting': cfg.get('fitting', 'soft'),
                            'parameters': cfg.get('parameters', {}),
                            'material_presets': list(cfg.get('material_presets', {}).keys()),
                        })
                    except Exception:
                        logger.debug('optionaler Schritt fehlgeschlagen', exc_info=True)
            elif entry.endswith('.blend'):
                assets.append({
                    'name': entry.replace('.blend', ''),
                    'category': 'Other',
                    'tags': [],
                    'fitting': 'soft',
                    'parameters': {},
                    'material_presets': [],
                })
    return JsonResponse({'assets': assets})


@require_GET
def charmorph_hairstyles(request):
    """List available CharMorph hairstyles."""
    import os as _os
    hair_dir = _os.path.join(str(settings.TOOLS_ROOT), 'tools', 'CharMorphPlugin',
                             'data', 'characters', 'mb_female', 'hairstyles')
    hairstyles = []
    if _os.path.isdir(hair_dir):
        for f in sorted(_os.listdir(hair_dir)):
            if f.endswith('.npz'):
                name = f.replace('.npz', '')
                hairstyles.append({
                    'name': name,
                    'label': name.replace('_', ' ').replace('1', ' 1').strip().title(),
                    'file': f,
                })
    # Load hair colors from CharMorph
    colors = {}
    colors_file = _os.path.join(str(settings.TOOLS_ROOT), 'tools', 'CharMorphPlugin', 'data', 'hair_colors.yaml')
    if _os.path.isfile(colors_file):
        try:
            import yaml
            with open(colors_file) as f:
                colors_raw = yaml.safe_load(f)
            for name, props in (colors_raw or {}).items():
                if isinstance(props, dict):
                    colors[name] = {
                        'viewport_color': props.get('viewport_color', [0.5, 0.3, 0.1]),
                        'melanin': props.get('melanin', 0.5),
                    }
        except Exception:
            logger.debug('optionaler Schritt fehlgeschlagen', exc_info=True)

    return JsonResponse({'hairstyles': hairstyles, 'colors': colors})
