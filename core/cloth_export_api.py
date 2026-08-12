"""
Django endpoint for cloth-export: receives the payload from `cloth_export.js`,
runs the chosen collision-engine pipeline, writes the MP4 to the studio
video-output directory, and returns its public URL.
"""
from __future__ import annotations
import json
import os
import sys
import time
import uuid
import logging

from django.conf import settings
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt

from .safe_paths import SafePath, PfadAbgelehnt


# Make the `collision` package importable (it lives in HumanBody, not HumanBodyWeb)
# KEIN Rueckfall auf das alte Projekt A:\HumanBodyTest mehr (Review
# 12.08.2026): Es liegt noch auf der Platte. Fehlte HUMANBODY_ROOT, hat der
# Export stillschweigend Daten von DORT geladen - ein Fehler, den man am
# Ergebnis nicht erkennt. Jetzt bleibt der Pfad leer und der Import scheitert
# sichtbar.
_HB_ROOT = str(getattr(settings, 'HUMANBODY_ROOT', ''))
_HB_PARENT = os.path.dirname(_HB_ROOT)
if _HB_ROOT and _HB_ROOT not in sys.path:
    sys.path.insert(0, _HB_ROOT)
if _HB_PARENT and _HB_PARENT not in sys.path:
    sys.path.insert(0, _HB_PARENT)

logger = logging.getLogger(__name__)


def _out_dir():
    s = _load_settings()
    vid = (s.ui_prefs or {}).get('studio_video_output') if s else None
    if vid and os.path.isdir(vid):
        return vid
    return os.path.join(str(settings.MEDIA_ROOT), 'cloth_exports')


def _load_settings():
    try:
        from core.models import AppSettings
        return AppSettings.load()
    except Exception:
        return None


@csrf_exempt
def export_cloth(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    try:
        payload = json.loads(request.body)
    except Exception as e:
        return JsonResponse({'ok': False, 'error': f'bad json: {e}'}, status=400)

    engine = payload.get('engine', 'blender_eevee')
    quality = payload.get('quality', 'medium')
    if engine not in ('blender_eevee', 'warp_blender', 'warp_only', 'skinning_blender'):
        return JsonResponse({'ok': False, 'error': f'unknown engine {engine}'}, status=400)

    try:
        from collision.bridge import payload_to_scene_input
        from collision import export_mp4
    except Exception as e:
        return JsonResponse({'ok': False, 'error': f'import failed: {e}'}, status=500)

    try:
        scene = payload_to_scene_input(payload)
    except Exception as e:
        logger.exception('payload_to_scene_input failed')
        return JsonResponse({'ok': False, 'error': f'payload decode failed: {e}'}, status=400)

    # Ziel-Verzeichnis und Dateiname kommen aus dem Payload und werden seit
    # 12.08.2026 über SafePath geprüft. Vorher wurde `output_dir` nur auf
    # "existiert als Verzeichnis" geprüft und `filename` nur auf die Endung —
    # ein Name wie `..\..\x.mp4` landete damit ausserhalb des Ausgabeordners.
    requested_dir = (payload.get('output_dir') or '').strip()
    out_dir = _out_dir()
    if requested_dir:
        try:
            out_dir = str(SafePath.fuer_ausgabe().pruefe(requested_dir))
        except PfadAbgelehnt as e:
            return JsonResponse({'ok': False, 'error': f'output_dir abgelehnt: {e}'}, status=403)
    os.makedirs(out_dir, exist_ok=True)
    requested_name = (payload.get('filename') or '').strip()
    if requested_name:
        try:
            requested_name = SafePath.dateiname(requested_name, '.mp4')
        except PfadAbgelehnt as e:
            return JsonResponse({'ok': False, 'error': f'filename abgelehnt: {e}'}, status=403)
        base, ext = os.path.splitext(requested_name)
        out_name = f"{base}_{engine}{ext}"
    else:
        out_name = f"{payload.get('scene_name', 'scene').replace('/', '_')}_{engine}_{int(time.time())}_{uuid.uuid4().hex[:6]}.mp4"
    out_path = os.path.join(out_dir, out_name)

    # Optional resolution override from client
    try:
        w = int(payload.get('width') or 1920)
        h = int(payload.get('height') or 1080)
        resolution = (max(64, w), max(64, h))
    except Exception:
        resolution = (1920, 1080)

    t0 = time.time()
    try:
        result = export_mp4(scene, engine, quality, out_path, resolution=resolution)
    except Exception as e:
        logger.exception('export_mp4 crashed')
        return JsonResponse({'ok': False, 'error': f'export crashed: {e}'}, status=500)
    elapsed = time.time() - t0

    if not result.get('ok'):
        return JsonResponse({
            'ok': False,
            'engine': engine,
            'quality': quality,
            'elapsed_sec': round(elapsed, 2),
            'log': result.get('log', ''),
            'error': 'engine failed — see log',
        }, status=200)

    # Relative URL if the file landed under MEDIA_ROOT
    url = None
    media_root = str(settings.MEDIA_ROOT)
    if out_path.startswith(media_root):
        rel = out_path[len(media_root):].replace('\\', '/').lstrip('/')
        url = settings.MEDIA_URL.rstrip('/') + '/' + rel
    return JsonResponse({
        'ok': True,
        'engine': engine,
        'quality': quality,
        'elapsed_sec': round(elapsed, 2),
        'output': out_path,
        'url': url,
        'duration_sec': result.get('duration_sec', 0),
    })
