# -*- coding: utf-8 -*-
"""SMPL-X-Netz und -Textur ausliefern.

Aus core/api/foto.py herausgeloest (Umbau 16.08.2026).
"""

from ..daten.netzantwort import Netzantwort
from ..daten.wrapperpfad import Wrapperpfad
from ..dienste.smplxnetz import SmplxNetz, SmplxNetzFehler
from ..dienste.texturbacken import Texturbacken
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
import json
import os


import logging

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def smplx_mesh(request):
    """Generate SMPL-X mesh from betas.

    Expects JSON: {"betas": [...], "gender": "female"|"male"|"neutral"}
    Returns base64-encoded vertices (float32) and faces (uint32).
    """
    try:
        with Wrapperpfad():
            from smplest_x_wrapper import generate_mesh
    except ImportError:
        logger.warning('SMPL-X-Wrapper nicht importierbar', exc_info=True)
        return JsonResponse({'ok': False, 'error': 'Wrapper not found'})

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

    betas = body.get('betas', [0.0] * 10)
    gender = body.get('gender', 'neutral')

    result = generate_mesh(betas, gender)
    if result is None:
        return JsonResponse({'ok': False, 'error': 'SMPL-X model not available'})

    resp = {
        'ok': True,
        'vertices': Netzantwort.smplx_feld(result['vertices'], 'vertices'),
        'faces': Netzantwort.smplx_feld(result['faces'], 'faces'),
        'joints': Netzantwort.smplx_feld(result['joints'], 'joints'),
        'parents': result['parents'],
        'skin_indices': Netzantwort.smplx_feld(result['skin_indices'], 'skin_indices'),
        'skin_weights': Netzantwort.smplx_feld(result['skin_weights'], 'skin_weights'),
        'n_verts': result['n_verts'],
        'n_faces': result['n_faces'],
        'n_joints': result['n_joints'],
    }

    # Include UV data if available (seam-duplicated vertex arrays)
    if 'uv_coords' in result:
        resp['uv_vertices']     = Netzantwort.smplx_feld(result['uv_vertices'], 'uv_vertices')
        resp['uv_coords']       = Netzantwort.smplx_feld(result['uv_coords'], 'uv_coords')
        resp['uv_faces']        = Netzantwort.smplx_feld(result['uv_faces'], 'uv_faces')
        resp['uv_skin_indices'] = Netzantwort.smplx_feld(result['uv_skin_indices'], 'uv_skin_indices')
        resp['uv_skin_weights'] = Netzantwort.smplx_feld(result['uv_skin_weights'], 'uv_skin_weights')
        resp['n_uv_verts']      = result['n_uv_verts']

    return JsonResponse(resp)


@require_GET
def smplx_texture(request, job_id):
    """Das Foto auf die UV-Karte des SMPL-X-Netzes backen (PNG, 1024x1024).

    Bis zum Umbau am 15.08.2026 standen hier 179 Zeilen mit drei
    Projektionswegen, zwei sys.path-Umwegen und dem Zusammensetzen der
    Teiltexturen. Das liegt jetzt in Texturbacken und SmplxNetz.
    """
    import cv2

    from ..models import PhotoAnalysisJob
    try:
        job = PhotoAnalysisJob.objects.get(id=job_id)
    except PhotoAnalysisJob.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Job not found'}, status=404)

    foto_pfad = os.path.join(str(settings.BASE_DIR), job.photo_file)
    if not os.path.isfile(foto_pfad):
        return JsonResponse({'ok': False, 'error': 'Photo not found'}, status=404)
    foto = cv2.imread(foto_pfad)
    if foto is None:
        return JsonResponse({'ok': False, 'error': 'Could not read photo'}, status=500)

    try:
        daten = json.loads(job.result_json)
    except (json.JSONDecodeError, TypeError):
        logger.exception('smplx_texture: JSONDecodeError/TypeError')
        return JsonResponse({'ok': False, 'error': 'Invalid result data'}, status=500)

    try:
        vertices, faces, _netz = SmplxNetz.erzeugen(
            daten.get('betas', [0.0] * 10), daten.get('gender', 'neutral'))
    except SmplxNetzFehler as e:
        logger.exception('smplx_texture: SmplxNetzFehler')
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)

    region = request.GET.get('region', 'all')
    if region not in Texturbacken.REGIONEN:
        region = 'all'
    backen = Texturbacken(job_id, daten, foto)
    hintergrund = Texturbacken.hintergrundfarbe(daten.get('skin_color', '#ccaa88'))
    try:
        textur = backen.backen(request.GET.get('backend', 'orthographic'),
                               vertices, faces, region, hintergrund)
    except Exception as e:                                        # noqa: BLE001
        logger.exception('Textur backen fehlgeschlagen (Region %s)', region)
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)

    textur = backen.zusammensetzen(cv2, textur, region, hintergrund)
    daten['texture_path'] = backen.speichern(cv2, textur)
    try:
        job.result_json = json.dumps(daten, default=str)
        job.save(update_fields=['result_json'])
    except Exception:                                             # noqa: BLE001
        logger.error('Texturpfad fuer %s nicht speicherbar', job_id, exc_info=True)

    from django.http import HttpResponse
    _, puffer = cv2.imencode('.png', textur)
    return HttpResponse(puffer.tobytes(), content_type='image/png')
