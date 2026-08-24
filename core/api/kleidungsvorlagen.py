# -*- coding: utf-8 -*-
"""Stoffvorlagen der Kleidung: Bereiche, gespeicherte Voreinstellungen.

Aus core/api/kleidung.py herausgeloest (Umbau 16.08.2026).
"""

from django.conf import settings
from django.http import JsonResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from humanbody_core.cloth import TEMPLATE_TYPES, PRIMITIVE_TYPES, BUILDER_REGIONS
import json
import os
import re
import logging

logger = logging.getLogger('core')


_TPL_CATEGORY = {
    'TPL_TSHIRT': 'Top', 'TPL_DRESS': 'Top',
    'TPL_PANTS': 'Pants', 'TPL_SKIRT': 'Pants',
}


@require_GET
def character_cloth_regions(request):
    """Return all cloth options: templates, primitives, builder regions."""
    templates = [{'key': k, 'label': v['label'], 'color': list(v['color'])}
                 for k, v in TEMPLATE_TYPES.items()]
    primitives = [{'key': k, 'label': v['label'], 'color': list(v['color'])}
                  for k, v in PRIMITIVE_TYPES.items()]
    builder = [{'key': k, 'label': k.replace('_', ' ').title(),
                'color': list(v['color'])}
               for k, v in BUILDER_REGIONS.items()]
    return JsonResponse({
        'templates': templates,
        'primitives': primitives,
        'builder_regions': builder,
    })


def _cloth_preset_dir(category):
    """Return Path for cloth template preset directory, creating if needed."""
    d = settings.HUMANBODY_ASSETS_INSTANCE_DIR / category / 'clothFromTemplate'
    d.mkdir(parents=True, exist_ok=True)
    return d


@require_GET
def cloth_preset_list(request):
    """List all cloth template presets for a category (Top or Pants)."""
    category = request.GET.get('category', '')
    if category not in ('Top', 'Pants'):
        return JsonResponse({'error': 'category must be Top or Pants'}, status=400)
    d = _cloth_preset_dir(category)
    presets = []
    for f in sorted(d.glob('*.json')):
        try:
            data = json.loads(f.read_text(encoding='utf-8'))
            presets.append({'name': f.stem, 'label': data.get('name', f.stem)})
        except (json.JSONDecodeError, IOError):
            logger.warning('Kleidervorlage %s nicht lesbar — Dateiname als Bezeichnung', f, exc_info=True)
            presets.append({'name': f.stem, 'label': f.stem})
    return JsonResponse({'presets': presets})


@csrf_exempt
@require_POST
def cloth_preset_save(request):
    """Save a cloth template preset."""
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    name = body.get('name', '').strip()
    data = body.get('data')
    if not name or not data:
        return JsonResponse({'error': 'name and data required'}, status=400)

    template = data.get('template', '')
    category = _TPL_CATEGORY.get(template)
    if not category:
        return JsonResponse({'error': f'Unknown template: {template}'}, status=400)

    safe_name = re.sub(r'[^\w\s\-]', '', name).strip()
    if not safe_name:
        return JsonResponse({'error': 'Invalid name'}, status=400)

    d = _cloth_preset_dir(category)
    fpath = os.path.normpath(os.path.join(str(d), f"{safe_name}.json"))
    if not fpath.startswith(os.path.normpath(str(d))):
        return JsonResponse({'error': 'Invalid path'}, status=400)

    data['name'] = name
    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return JsonResponse({'ok': True, 'filename': f"{safe_name}.json", 'category': category})


@require_GET
def cloth_preset_detail(request, category, name):
    """Load a single cloth template preset."""
    if category not in ('Top', 'Pants'):
        return JsonResponse({'error': 'Invalid category'}, status=400)
    if '/' in name or '\\' in name or '..' in name:
        return JsonResponse({'error': 'Invalid name'}, status=400)

    d = _cloth_preset_dir(category)
    fpath = os.path.normpath(os.path.join(str(d), f"{name}.json"))
    if not fpath.startswith(os.path.normpath(str(d))):
        return JsonResponse({'error': 'Invalid path'}, status=400)
    if not os.path.isfile(fpath):
        return HttpResponseNotFound(f'Preset not found: {category}/{name}')

    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return JsonResponse(data)
