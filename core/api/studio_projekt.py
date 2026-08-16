# -*- coding: utf-8 -*-
"""Studioprojekte und Szenen auf dem Server ablegen und lesen.

Aus core/api/studio.py herausgeloest (Umbau 16.08.2026).
"""

from ..atomic_write import AtomarSchreiber
from ..safe_paths import SafePath, PfadAbgelehnt
from django.conf import settings
from django.http import JsonResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
import json
import os
import re


@require_GET
def scene_list(request):
    """Return list of available scene files (.scene.json)."""
    models_dir = str(settings.HUMANBODY_MODELS_DIR)
    scenes = []
    if os.path.isdir(models_dir):
        for fname in sorted(os.listdir(models_dir)):
            if fname.endswith('.scene.json'):
                name = fname[:-len('.scene.json')]
                fpath = os.path.join(models_dir, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    scenes.append({
                        'name': name,
                        'label': data.get('name', name),
                        'character_count': len(data.get('characters', [])),
                    })
                except (json.JSONDecodeError, IOError):
                    scenes.append({'name': name, 'label': name, 'character_count': 0})
    return JsonResponse({'scenes': scenes})


@require_GET
def scene_detail(request, name):
    """Return contents of a scene JSON file."""
    if '/' in name or '\\' in name or '..' in name:
        return JsonResponse({'error': 'Invalid name'}, status=400)
    models_dir = str(settings.HUMANBODY_MODELS_DIR)
    fpath = os.path.normpath(os.path.join(models_dir, f"{name}.scene.json"))
    if not fpath.startswith(os.path.normpath(models_dir)):
        return JsonResponse({'error': 'Invalid path'}, status=400)
    if not os.path.isfile(fpath):
        return HttpResponseNotFound(f'Scene not found: {name}')
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return JsonResponse(data)


@csrf_exempt
@require_POST
def scene_save(request):
    """Save a scene JSON file."""
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    name = body.get('name', '').strip()
    data = body.get('data')
    if not name or not data:
        return JsonResponse({'error': 'name and data required'}, status=400)

    safe_name = re.sub(r'[^\w\s\-]', '', name).strip()
    if not safe_name:
        return JsonResponse({'error': 'Invalid name'}, status=400)

    models_dir = str(settings.HUMANBODY_MODELS_DIR)
    fpath = os.path.normpath(os.path.join(models_dir, f"{safe_name}.scene.json"))
    if not fpath.startswith(os.path.normpath(models_dir)):
        return JsonResponse({'error': 'Invalid path'}, status=400)

    os.makedirs(models_dir, exist_ok=True)
    data['name'] = name

    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return JsonResponse({'ok': True, 'filename': f"{safe_name}.scene.json"})


@csrf_exempt
@require_POST
def studio_project_save(request):
    """Save BVH Studio project JSON to a file on disk.

    POST /api/studio/project-save/
    Body JSON: { path: "full/path.studio.json", project: {...} }

    Pfad wird über SafePath geprüft (12.08.2026): vorher schrieb dieser Endpunkt
    an JEDE Stelle der Platte, ohne CSRF-Token und damit auch von einer fremden
    Webseite auslösbar. Geschrieben wird über AtomarSchreiber, damit zwei
    gleichzeitige Speichervorgänge keine halbe Datei hinterlassen.
    """
    import logging
    log = logging.getLogger('core')

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    project_data = data.get('project')
    if not project_data:
        return JsonResponse({'error': 'path + project required'}, status=400)

    try:
        sp = SafePath.fuer_studio_projekte().pruefe(data.get('path'))
    except PfadAbgelehnt as e:
        return JsonResponse({'error': str(e)}, status=403)

    try:
        AtomarSchreiber.json_schreiben(sp, project_data)
        log.info('[studio] Project saved: %s', sp)
        return JsonResponse({'ok': True, 'path': str(sp)})
    except Exception as e:                                       # noqa: BLE001
        log.exception('[studio] Project save failed: %s', sp)
        return JsonResponse({'error': str(e)}, status=500)


@require_GET
def studio_project_load(request):
    """Load BVH Studio project JSON from a file on disk.

    GET /api/studio/project-load/?path=full/path.studio.json
    """
    import logging
    log = logging.getLogger('core')

    try:
        fp = SafePath.fuer_studio_projekte().pruefe(request.GET.get('path'))
    except PfadAbgelehnt as e:
        return JsonResponse({'error': str(e)}, status=403)
    if not fp.is_file():
        # Kein voller Pfad in der Antwort: Das war eine Auskunft darüber, was auf
        # der Platte liegt. Der Pfad steht im Protokoll.
        log.info('[studio] Project not found: %s', fp)
        return JsonResponse({'error': 'File not found'}, status=404)

    try:
        with open(str(fp), 'r', encoding='utf-8') as f:
            data = json.load(f)
        log.info('[studio] Project loaded: %s', fp)
        return JsonResponse({'ok': True, 'project': data, 'path': str(fp)})
    except Exception as e:                                       # noqa: BLE001
        log.exception('[studio] Project load failed: %s', fp)
        return JsonResponse({'error': str(e)}, status=500)


@require_GET
def studio_project_list(request):
    """List project files in the configured project directory.

    GET /api/studio/project-list/?dir=path
    """
    roh = (request.GET.get('dir') or '').strip()
    if not roh:
        return JsonResponse({'files': []})
    try:
        dp = SafePath.fuer_studio_projekte().pruefe(roh)
    except PfadAbgelehnt as e:
        return JsonResponse({'error': str(e)}, status=403)
    if not dp.is_dir():
        return JsonResponse({'files': []})

    files = []
    for f in sorted(dp.glob('*.studio.json')):
        files.append({
            'name': f.stem.replace('.studio', ''),
            'path': str(f),
            'size': f.stat().st_size,
            'modified': f.stat().st_mtime,
        })
    return JsonResponse({'files': files})
