# -*- coding: utf-8 -*-
"""Gespeicherte Modelle und Frisuren auflisten, lesen, schreiben.

Aus core/api/netz.py herausgeloest (Umbau 16.08.2026).
"""

from django.conf import settings
from django.http import JsonResponse, FileResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
import json
import os
import re


HAIR_COLORS = {
    "Silken Black":       {"viewport": (0.02, 0.02, 0.02)},
    "Dark Brown":         {"viewport": (0.08, 0.04, 0.02)},
    "Cocoa Brown":        {"viewport": (0.25, 0.12, 0.05)},
    "Light Golden Brown": {"viewport": (0.7, 0.5, 0.25)},
    "Honey Blonde":       {"viewport": (0.6, 0.26, 0.08)},
    "Light Blonde":       {"viewport": (0.6, 0.3, 0.05)},
    "Auburn":             {"viewport": (0.5, 0.2, 0.05)},
    "Natural Black":      {"viewport": (0.05, 0.05, 0.05)},
    "Burgundy":           {"viewport": (0.13, 0.085, 0.08)},
    "Plum":               {"viewport": (0.33, 0.17, 0.05)},
}


@require_GET
def model_files(request):
    """Return list of ALL model files (.json and .scene.json) from models dir."""
    models_dir = str(settings.HUMANBODY_MODELS_DIR)
    files = []
    if os.path.isdir(models_dir):
        for fname in sorted(os.listdir(models_dir)):
            if not fname.endswith('.json'):
                continue
            fpath = os.path.join(models_dir, fname)
            if not os.path.isfile(fpath):
                continue
            is_scene = fname.endswith('.scene.json')
            name = fname[:-len('.scene.json')] if is_scene else fname[:-5]
            ftype = 'scene' if is_scene else 'model'
            stat = os.stat(fpath)
            entry = {
                'name': name,
                'filename': fname,
                'type': ftype,
                'size': stat.st_size,
                'modified': int(stat.st_mtime),
            }
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                entry['label'] = data.get('name', name)
                if is_scene:
                    entry['character_count'] = len(data.get('characters', []))
            except (json.JSONDecodeError, IOError):
                entry['label'] = name
            files.append(entry)
    return JsonResponse({'files': files})


@require_GET
def character_models(request):
    """Return list of available model presets."""
    models_dir = str(settings.HUMANBODY_MODELS_DIR)
    presets = []
    if os.path.isdir(models_dir):
        for fname in sorted(os.listdir(models_dir)):
            if fname.endswith('.json') and not fname.endswith('.scene.json'):
                name = fname[:-5]
                fpath = os.path.join(models_dir, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    presets.append({
                        'name': name,
                        'label': name,
                    })
                except (json.JSONDecodeError, IOError):
                    presets.append({'name': name, 'label': name})
    return JsonResponse({'presets': presets})


@require_GET
def character_model_detail(request, name):
    """Return contents of a model preset JSON file."""
    # Guard against path traversal
    if '/' in name or '\\' in name or '..' in name:
        return JsonResponse({'error': 'Invalid name'}, status=400)
    models_dir = str(settings.HUMANBODY_MODELS_DIR)
    fpath = os.path.normpath(os.path.join(models_dir, f"{name}.json"))
    if not fpath.startswith(os.path.normpath(models_dir)):
        return JsonResponse({'error': 'Invalid path'}, status=400)
    if not os.path.isfile(fpath):
        return HttpResponseNotFound(f'Preset not found: {name}')
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return JsonResponse(data)


@csrf_exempt
@require_POST
def character_model_save(request):
    """Save a model preset JSON file."""
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    name = body.get('name', '').strip()
    data = body.get('data')
    if not name or not data:
        return JsonResponse({'error': 'name and data required'}, status=400)

    # Sanitize filename: keep alphanumeric, spaces, hyphens, underscores
    safe_name = re.sub(r'[^\w\s\-]', '', name).strip()
    if not safe_name:
        return JsonResponse({'error': 'Invalid name'}, status=400)

    # Path traversal protection
    models_dir = str(settings.HUMANBODY_MODELS_DIR)
    fpath = os.path.normpath(os.path.join(models_dir, f"{safe_name}.json"))
    if not fpath.startswith(os.path.normpath(models_dir)):
        return JsonResponse({'error': 'Invalid path'}, status=400)

    # Ensure directory exists
    os.makedirs(models_dir, exist_ok=True)

    # Ensure 'name' field in data matches the filename
    data['name'] = safe_name

    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return JsonResponse({'ok': True, 'filename': f"{safe_name}.json"})


@require_GET
def character_hairstyles(request):
    """Return available hairstyles (GLB files in hairstyles dir)."""
    hairstyles_dir = os.path.join(str(settings.HUMANBODY_DATA_DIR), 'hairstyles')
    styles = []
    if os.path.isdir(hairstyles_dir):
        for fname in sorted(os.listdir(hairstyles_dir)):
            if fname.endswith('.glb'):
                name = fname[:-4]
                label = name.replace('_', ' ').title()
                styles.append({
                    'name': name,
                    'label': label,
                    'url': f'/api/character/hairstyle/{name}/',
                })
    return JsonResponse({
        'hairstyles': styles,
        'colors': {k: v['viewport'] for k, v in HAIR_COLORS.items()},
    })


def character_hairstyle_glb(request, name):
    """Serve a hairstyle GLB file."""
    if '/' in name or '\\' in name or '..' in name:
        return JsonResponse({'error': 'Invalid name'}, status=400)
    hairstyles_dir = os.path.join(str(settings.HUMANBODY_DATA_DIR), 'hairstyles')
    glb_path = os.path.normpath(os.path.join(hairstyles_dir, f"{name}.glb"))
    if not glb_path.startswith(os.path.normpath(hairstyles_dir)):
        return JsonResponse({'error': 'Invalid path'}, status=400)
    if not os.path.isfile(glb_path):
        return HttpResponseNotFound(f'Hairstyle not found: {name}')
    return FileResponse(
        open(glb_path, 'rb'),
        content_type='model/gltf-binary',
        filename=f'{name}.glb',
    )
