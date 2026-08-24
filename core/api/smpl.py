# -*- coding: utf-8 -*-
"""SMPL-Koerper und SMPL-Kleidungsbibliothek.

Aus core/character_api.py herausgeloest (Umbau 15.08.2026) — warum so
geschnitten, steht in `core/api/__init__.py`.
"""

from ..daten.netzantwort import Netzantwort
from ..daten.stoffantwort import Stoffantwort
from ..dienste.charakterdaten import Charakterdaten
from ..models import AppSettings
from django.http import JsonResponse, HttpResponseNotFound
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
import json
import logging


logger = logging.getLogger(__name__)


@require_GET
def smpl_settings_api(request):
    """Return SMPL body default settings."""
    s = AppSettings.load()
    betas = [0.0] * 10
    try:
        parts = s.smpl_default_betas.split(',')
        for i, v in enumerate(parts[:10]):
            betas[i] = float(v.strip())
    except (ValueError, IndexError):
        logger.debug('uebergangen', exc_info=True)
    result = {
        'gender': s.smpl_default_gender,
        'betas': betas,
        'opacity': s.smpl_default_opacity,
        'color': s.smpl_default_color,
        'wireframe': s.smpl_default_wireframe,
        'xoffset': s.smpl_default_xoffset,
        'humanbody_preset': s.smpl_default_humanbody_preset,
    }
    # Include scene settings if saved
    if s.smpl_default_scene:
        try:
            result['scene'] = json.loads(s.smpl_default_scene)
        except (json.JSONDecodeError, TypeError):
            logger.debug('uebergangen', exc_info=True)
    return JsonResponse(result)


@csrf_exempt
@require_POST
def smpl_settings_save(request):
    """Save SMPL body + scene settings from the test-smpl page."""
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

    s = AppSettings.load()

    # Gender
    gender = data.get('gender', 'female')
    if gender not in ('female', 'male', 'neutral'):
        gender = 'female'
    s.smpl_default_gender = gender

    # Betas
    betas = data.get('betas', [])
    if isinstance(betas, list) and len(betas) == 10:
        s.smpl_default_betas = ','.join(f'{b:.2f}' for b in betas)

    # Display
    opacity = data.get('opacity')
    if opacity is not None:
        s.smpl_default_opacity = max(0.0, min(1.0, float(opacity)))

    color = data.get('color', '')
    if color and isinstance(color, str) and color.startswith('#'):
        s.smpl_default_color = color

    s.smpl_default_wireframe = bool(data.get('wireframe', False))

    xoffset = data.get('xoffset')
    if xoffset is not None:
        s.smpl_default_xoffset = max(-2.0, min(2.0, float(xoffset)))

    # Scene settings
    scene_data = data.get('scene')
    if scene_data and isinstance(scene_data, dict):
        s.smpl_default_scene = json.dumps(scene_data)

    s.save()
    return JsonResponse({'ok': True})


@require_GET
def smpl_body_mesh(request):
    """Return SMPL body mesh (vertices + faces + normals) as base64 JSON.

    Query params:
        gender: female/male/neutral (default: female)
        betas: comma-separated floats, e.g. "1.5,-0.3,0,0,0,0,0,0,0,0"
    """
    gender = request.GET.get('gender', 'female')
    betas_str = request.GET.get('betas', '')

    betas = None
    if betas_str:
        try:
            betas = [float(x) for x in betas_str.split(',')]
        except ValueError:
            return JsonResponse({'error': 'Invalid betas format'}, status=400)

    try:
        gen = Charakterdaten.smpl_koerpergenerator()
        mesh = gen.generate(gender=gender, betas=betas)
    except FileNotFoundError as e:
        return JsonResponse({'error': str(e)}, status=404)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({
        'vertices': Netzantwort.feld(mesh['vertices'], 'vertices'),
        'faces': Netzantwort.feld(mesh['faces'], 'faces'),
        'normals': Netzantwort.feld(mesh['normals'], 'normals'),
        'vertex_count': mesh['vertex_count'],
        'face_count': mesh['face_count'],
        'gender': gender,
    })


@require_GET
def smpl_garment_library(request):
    """Return SMPL garment catalog grouped by category."""
    lib = Charakterdaten.smpl_bibliothek()
    catalog = lib.get_catalog()
    return JsonResponse(catalog)


@require_GET
def smpl_garment_mesh(request):
    """Return SMPL garment mesh (vertices + faces + normals) as base64 JSON."""
    garment_id = request.GET.get('garment_id', '')
    if not garment_id:
        return JsonResponse({'error': 'garment_id required'}, status=400)

    lib = Charakterdaten.smpl_bibliothek()
    try:
        mesh = lib.get_garment_mesh(garment_id)
    except Exception as e:
        logger.error("Error loading SMPL garment %s: %s", garment_id, e)
        return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({
        'garment_id': garment_id,
        'vertices': Netzantwort.feld(mesh['vertices'], 'vertices'),
        'faces': Netzantwort.feld(mesh['faces'], 'faces'),
        'normals': Netzantwort.feld(mesh['normals'], 'normals'),
        'vertex_count': len(mesh['vertices']) // 3,
        'face_count': len(mesh['faces']) // 3,
    })


@require_GET
def smpl_garment_fit(request):
    """Fit an SMPL garment to the project body and return as base64 binary.

    Query params:
        garment_id  — SMPL garment id from SmplGarmentLibrary
        body_type   — e.g. 'Female_Caucasian'
        offset      — surface offset in meters (default 0.006)
        stiffness   — fabric stiffness 0-1
        color_r/g/b — garment color (0-1 float)
        morph_*     — body morph overrides
        meta_*      — meta slider values (internal -1..1)
    """
    garment_id = request.GET.get('garment_id', '')
    if not garment_id:
        return JsonResponse({'error': 'garment_id required'}, status=400)

    lib = Charakterdaten.smpl_bibliothek()
    try:
        raw = lib.get_garment_mesh_raw(garment_id)
    except Exception as e:
        logger.error("Error loading SMPL garment raw %s: %s", garment_id, e)
        return JsonResponse({'error': str(e)}, status=500)

    # Koerper aus der Anfrage — derselbe Weg wie ueberall
    # (`Charakterdaten.koerper_aus`); der Reglerblock stand hier ein viertes Mal.
    koerper = Charakterdaten.koerper_aus(request.GET)
    gender, body_verts = koerper.geschlecht, koerper.vertices
    if body_verts is None:
        return JsonResponse({'error': 'Failed to compute body mesh'}, status=500)

    body_faces = Charakterdaten.netzdaten(gender).faces

    offset = float(request.GET.get('offset', 0.006))
    stiffness = float(request.GET.get('stiffness', 0.5))

    color = (
        float(request.GET.get('color_r', 0.30)),
        float(request.GET.get('color_g', 0.50)),
        float(request.GET.get('color_b', 0.40)),
    )

    from GarmentFitter import fit_garment
    result = fit_garment(
        raw['vertices'], raw['faces'], body_verts,
        body_faces=body_faces,
        offset=offset,
        stiffness=stiffness,
        color=color,
        coordinate_system='smpl',
    )

    if result is None:
        return JsonResponse({'error': 'Fitting failed'}, status=500)

    return JsonResponse(Stoffantwort.aus(result, body_verts, gender,
                                        farbe=color, garment_id=garment_id))


@require_GET
def smpl_garment_thumbnail(request, garment_path):
    """Return thumbnail PNG for an SMPL garment."""
    # garment_path is the garment_id
    garment_id = garment_path.rstrip('/')
    lib = Charakterdaten.smpl_bibliothek()
    try:
        thumb_data = lib.get_thumbnail(garment_id)
    except Exception as e:
        return HttpResponseNotFound(f'Garment not found: {e}')

    if thumb_data is None:
        return HttpResponseNotFound('No thumbnail')

    from django.http import HttpResponse
    return HttpResponse(thumb_data, content_type='image/png')
