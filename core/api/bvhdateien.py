# -*- coding: utf-8 -*-
"""Die BVH-Bibliothek auflisten und einzelne Dateien ausliefern.

Aus core/api/retarget.py herausgeloest (Umbau 16.08.2026).
"""

from django.conf import settings
from django.http import JsonResponse, FileResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
import json
import os
import re


@require_GET
def character_animations(request):
    """Liste aller BVH-Animationen, gruppiert nach Kategorie — siehe Animationsliste."""
    from ..dienste.animationsliste import Animationsliste
    return JsonResponse({'categories': Animationsliste().nach_kategorie()})


def character_bvh_file(request, name):
    """Serve a BVH animation file (legacy: from MocapNET dir only)."""
    bvh_path = os.path.join(str(settings.HUMANBODY_BVH_DIR), f"{name}.bvh")
    if not os.path.isfile(bvh_path):
        return HttpResponseNotFound(f'BVH not found: {name}')
    return FileResponse(
        open(bvh_path, 'rb'),
        content_type='text/plain',
        filename=f'{name}.bvh',
    )


def character_bvh_file_cat(request, category, name):
    """Serve a BVH animation file from a category subdirectory."""
    bvh_root = os.path.dirname(str(settings.HUMANBODY_BVH_DIR))
    bvh_path = os.path.normpath(os.path.join(bvh_root, category, f"{name}.bvh"))
    # Prevent directory traversal
    if not bvh_path.startswith(os.path.normpath(bvh_root)):
        return HttpResponseNotFound('Invalid path')
    if not os.path.isfile(bvh_path):
        return HttpResponseNotFound(f'BVH not found: {category}/{name}')
    return FileResponse(
        open(bvh_path, 'rb'),
        content_type='text/plain',
        filename=f'{name}.bvh',
    )


@csrf_exempt
@require_POST
def animation_save(request):
    """Save a BVH animation file to its category directory."""
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    category = body.get('category', '').strip()
    name = body.get('name', '').strip()
    bvh_content = body.get('bvh_content', '')

    if not category or not name or not bvh_content:
        return JsonResponse({'error': 'category, name, and bvh_content required'}, status=400)

    # Sanitize name — allow word chars, spaces, hyphens, dots
    name = re.sub(r'[^\w\s\-.]', '', name).strip()
    category = re.sub(r'[^\w\s\-.]', '', category).strip()
    if not name or not category:
        return JsonResponse({'error': 'Invalid name or category'}, status=400)

    bvh_root = os.path.dirname(str(settings.HUMANBODY_BVH_DIR))
    target_dir = os.path.normpath(os.path.join(bvh_root, category))
    target_path = os.path.normpath(os.path.join(target_dir, f"{name}.bvh"))

    # Path traversal check
    if not target_path.startswith(os.path.normpath(bvh_root)):
        return JsonResponse({'error': 'Invalid path'}, status=400)

    os.makedirs(target_dir, exist_ok=True)
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(bvh_content)

    return JsonResponse({'ok': True, 'path': f'{category}/{name}.bvh'})
