# -*- coding: utf-8 -*-
"""BVH-Studio und Theatre: Projekte, Ton, Szenenobjekte, Video.

Aus core/character_api.py herausgeloest (Umbau 15.08.2026) — warum so
geschnitten, steht in `core/api/__init__.py`.
"""

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import logging
import os
import uuid


_FLOOR_TEXTURES_DIR = settings.BASE_DIR / 'static' / 'assets' / 'floor_textures'
_SCENE_OBJECTS_DIR = settings.MEDIA_ROOT / 'scene_objects'
_THEATRE_PRESETS_DIR = settings.HUMANBODY_ROOT / 'data' / 'theatre_presets'
logger = logging.getLogger(__name__)


def theatre_settings_api(request):
    """API: Get Theatre default settings (for auto-load)."""
    from core.models import AppSettings
    s = AppSettings.load()
    return JsonResponse({
        'model': s.theatre_default_model or '',
        'animation': s.theatre_default_animation or '',
        'preset': s.theatre_default_preset or 'ballet_stage',
        'video_format': s.theatre_video_format or 'mp4',
        'video_resolution': s.theatre_video_resolution or '1080p',
        'video_fps': s.theatre_video_fps or 30,
        'video_quality': s.theatre_video_quality or 'high',
    })





















@csrf_exempt
@require_POST
def studio_audio_upload(request):
    """Upload audio file for BVH Studio project.

    POST /api/studio/audio-upload/
    Returns: { ok: true, url: '/media/studio_audio/xxx.mp3' }
    """
    log = logging.getLogger('core')

    audio_file = request.FILES.get('audio')
    if not audio_file:
        return JsonResponse({'error': 'No audio file provided'}, status=400)

    # Size check: 50 MB max
    max_size = 50 * 1024 * 1024
    if audio_file.size > max_size:
        return JsonResponse({'error': f'File too large ({audio_file.size // (1024*1024)}MB). Max 50MB.'}, status=400)

    # Extension whitelist
    import pathlib
    ext = pathlib.Path(audio_file.name).suffix.lower()
    allowed = {'.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac', '.webm'}
    if ext not in allowed:
        return JsonResponse({'error': f'Unsupported format: {ext}. Allowed: {", ".join(sorted(allowed))}'}, status=400)

    # Save to media/studio_audio/ with unique name
    dest_dir = os.path.join(settings.MEDIA_ROOT, 'studio_audio')
    os.makedirs(dest_dir, exist_ok=True)

    unique_name = f'{uuid.uuid4().hex}{ext}'
    dest_path = os.path.join(dest_dir, unique_name)

    try:
        with open(dest_path, 'wb') as f:
            for chunk in audio_file.chunks():
                f.write(chunk)
        url = f'{settings.MEDIA_URL}studio_audio/{unique_name}'
        log.info('[studio] Audio uploaded: %s (%d bytes) -> %s', audio_file.name, audio_file.size, unique_name)
        return JsonResponse({'ok': True, 'url': url})
    except Exception as e:
        log.error('[studio] Audio upload failed: %s', e)
        return JsonResponse({'error': str(e)}, status=500)








def studio_theatre_presets(request):
    """Liste aller Theatre-Licht-Presets.

    GET /api/studio/theatre-presets/
    Response: { presets: [{ name, label, lightCount, description }] }
    """
    log = logging.getLogger('core')
    presets = []
    if _THEATRE_PRESETS_DIR.is_dir():
        for f in sorted(_THEATRE_PRESETS_DIR.glob('*.json')):
            try:
                with open(f, 'r', encoding='utf-8') as fh:
                    data = json.load(fh)
                presets.append({
                    'name': f.stem,
                    'label': data.get('label', f.stem),
                    'description': data.get('description', ''),
                    'lightCount': len(data.get('lights', [])),
                })
            except Exception as e:
                log.error(f'[theatre-presets] Failed to read {f}: {e}')
    return JsonResponse({'presets': presets})


def studio_theatre_preset_detail(request, name):
    """Liefert die JSON-Definition eines Theatre-Licht-Presets.

    GET /api/studio/theatre-preset/<name>/
    """
    fp = _THEATRE_PRESETS_DIR / f'{name}.json'
    if not fp.is_file():
        return JsonResponse({'error': 'Preset nicht gefunden'}, status=404)
    try:
        with open(fp, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
        return JsonResponse(data)
    except Exception as e:
        logger.exception('studio_theatre_preset_detail: unerwarteter Fehler')
        return JsonResponse({'error': str(e)}, status=500)


def studio_floor_textures(request):
    """Liste verfügbarer Boden-Texturen.

    GET /api/studio/floor-textures/
    Response: { textures: [{ name, label, url }] }
    """
    textures = [
        {'name': 'none', 'label': 'Keine (Farbe)', 'url': ''},
    ]
    if _FLOOR_TEXTURES_DIR.is_dir():
        for f in sorted(_FLOOR_TEXTURES_DIR.glob('*')):
            if f.suffix.lower() in ('.jpg', '.jpeg', '.png', '.webp'):
                textures.append({
                    'name': f.stem,
                    'label': f.stem.replace('_', ' ').title(),
                    'url': f'/static/assets/floor_textures/{f.name}',
                })
    return JsonResponse({'textures': textures})


@csrf_exempt
@require_POST
def studio_scene_object_upload(request):
    """Upload eines 3D-Objekts für den BVH Studio.

    POST /api/studio/scene-object-upload/
    Form: object=<file>
    Returns: { ok: true, url: "/media/scene_objects/<uuid>.obj", name: "...", ext: "obj" }
    """
    import uuid
    log = logging.getLogger('core')
    if request.method != 'POST' or 'object' not in request.FILES:
        return JsonResponse({'error': 'Kein object File'}, status=400)

    upload = request.FILES['object']
    ext = (upload.name.rsplit('.', 1)[-1] if '.' in upload.name else '').lower()
    allowed = {'obj', 'glb', 'gltf', 'fbx', 'mtl', 'jpg', 'jpeg', 'png', 'webp', 'bmp', 'tga'}
    if ext not in allowed:
        return JsonResponse({'error': f'Format "{ext}" nicht unterstützt'}, status=400)

    # Optional bundleId — alle Dateien des gleichen Imports gehen in denselben Unterordner,
    # damit MTL → Textur-Referenzen per Original-Dateinamen funktionieren.
    bundle_id = request.POST.get('bundleId', '').strip()
    safe_bundle = ''.join(c for c in bundle_id if c.isalnum() or c in '-_')[:32]
    if safe_bundle:
        target_dir = _SCENE_OBJECTS_DIR / safe_bundle
        fname = upload.name.replace(' ', '_')  # Original behalten
    else:
        target_dir = _SCENE_OBJECTS_DIR
        stem = upload.name.rsplit('.', 1)[0].replace(' ', '_')
        fname = f'{stem}_{uuid.uuid4().hex[:8]}.{ext}'
    target_dir.mkdir(parents=True, exist_ok=True)
    fp = target_dir / fname
    try:
        with open(fp, 'wb') as out:
            for chunk in upload.chunks():
                out.write(chunk)
        log.info(f'[scene-object] Uploaded: {fp} ({upload.size} bytes)')
        url_path = f'{settings.MEDIA_URL}scene_objects/' + (f'{safe_bundle}/' if safe_bundle else '') + fname
        return JsonResponse({
            'ok': True,
            'url': url_path,
            'name': upload.name,
            'ext': ext,
        })
    except Exception as e:
        logger.exception('studio_scene_object_upload: unerwarteter Fehler')
        return JsonResponse({'error': str(e)}, status=500)
