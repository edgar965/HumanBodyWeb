# -*- coding: utf-8 -*-
"""BVH-Bibliothek, Retarget und Bearbeitung der Bewegungen.

Aus core/character_api.py herausgeloest (Umbau 15.08.2026) — warum so
geschnitten, steht in `core/api/__init__.py`.
"""

from ..dienste.bvhverwaltung import Bvhverwaltung, BvhFehler
from ..dienste.retargetdaten import Retargetdaten
from ..dienste.bvhablage import Bvhablage
from ..models import BVHJob
from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
import json
import logging
import os


logger = logging.getLogger(__name__)












@require_GET
def retarget_config(request):
    """Serve BVH-to-Rigify mapping tables, skip-dir-correction lists, and face/hand bone list."""
    from humanbody_core.skeleton import Skeleton, FACE_HAND_BONES
    mappings = {}
    skip_dir_correction = {}
    for fmt, cls in Skeleton._registry.items():
        if cls.BONE_MAP_TO_RIGIFY:
            mappings[fmt] = cls.BONE_MAP_TO_RIGIFY
            skip_dir_correction[fmt] = cls.SKIP_DIR_CORRECTION
    return JsonResponse({
        'mappings': mappings,
        'skip_dir_correction': skip_dir_correction,
        'face_hand_bones': FACE_HAND_BONES,
    })




def retarget_bvh_data(bvh_path, body_height=1.68, fmt=None, foot_correction=False,
                      delta_norm=None):
    """Bisherige Aufrufform — die Rechnung steht in dienste/retargetdaten.py.

    Dorthin ausgelagert am 18.08.2026: Sie ist Fachlogik und hat einen
    Ringimport zwischen `api/retarget.py` und `api/dateien.py` getragen.
    """
    return Retargetdaten(bvh_path, body_height, fmt, foot_correction,
                         delta_norm).holen()

def retarget(request):
    """Unified retarget endpoint — ONE URL for both Job and Library BVH.

    GET /api/retarget/?job=<uuid>                        → job's BVH file
    GET /api/retarget/?category=<cat>&name=<name>        → library BVH file
    Common query params: body_height, format, foot_correction
    """
    job_id = request.GET.get('job')
    category = request.GET.get('category')
    name = request.GET.get('name')

    body_height = float(request.GET.get('body_height', 1.68))
    fmt = request.GET.get('format', None)
    foot_correction = request.GET.get('foot_correction', '').lower() in ('1', 'true')
    delta_norm_str = request.GET.get('delta_norm', '').lower()
    delta_norm = True if delta_norm_str == '1' else (False if delta_norm_str == '0' else None)

    if job_id:
        job = get_object_or_404(BVHJob, id=job_id)
        if not job.bvh_file or not os.path.isfile(job.bvh_file):
            return HttpResponseNotFound('Job has no BVH file')
        bvh_path = job.bvh_file
    elif category and name:
        # Pfadpruefung ueber Bvhablage statt per Zeichenkettenvergleich:
        # `startswith` besteht auch ein Nachbarverzeichnis mit gleichem
        # Namensanfang. Am 16.08.2026 nachgezogen — an den uebrigen Stellen war
        # das schon am 12.08. umgestellt worden, diese hier war uebersehen.
        geprueft = Bvhablage.pfad_pruefen(
            Bvhablage.wurzel() / category / f'{name}.bvh')
        if not geprueft:
            return HttpResponseNotFound('Invalid path')
        bvh_path = str(geprueft)
        if not os.path.isfile(bvh_path):
            return HttpResponseNotFound(f'BVH not found: {category}/{name}')
    else:
        return JsonResponse({'error': 'Provide ?job=<uuid> or ?category=<cat>&name=<name>'}, status=400)

    return JsonResponse(retarget_bvh_data(bvh_path, body_height, fmt, foot_correction, delta_norm))


@require_GET
def retarget_bvh(request, category, name):
    """Legacy — forwards to unified retarget()."""
    request.GET = request.GET.copy()
    request.GET['category'] = category
    request.GET['name'] = name
    return retarget(request)


@csrf_exempt
@require_POST
def retarget_merge(request):
    """Server-side hybrid merge: retarget body + face BVHs and merge.

    POST /api/character/retarget-merge/
    Body JSON: { body_bvh: "category/name", face_bvh: "category/name",
                 body_height: 1.68, foot_correction: false }
    """
    from humanbody_core.skeleton import SkeletonRigify

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    body_bvh_key = data.get('body_bvh', '')
    face_bvh_key = data.get('face_bvh', '')
    if not body_bvh_key or not face_bvh_key:
        return JsonResponse({'error': 'body_bvh and face_bvh are required'}, status=400)

    body_height = float(data.get('body_height', 1.68))
    foot_correction = bool(data.get('foot_correction', False))

    # Pfadpruefung ueber Bvhablage — siehe Begruendung in `retarget`.
    body_path = Bvhablage.pfad_pruefen(Bvhablage.wurzel() / f'{body_bvh_key}.bvh')
    if not body_path:
        return HttpResponseNotFound('Invalid body_bvh path')
    if not body_path.is_file():
        return HttpResponseNotFound(f'Body BVH not found: {body_bvh_key}')

    face_path = Bvhablage.pfad_pruefen(Bvhablage.wurzel() / f'{face_bvh_key}.bvh')
    if not face_path:
        return HttpResponseNotFound('Invalid face_bvh path')
    if not face_path.is_file():
        return HttpResponseNotFound(f'Face BVH not found: {face_bvh_key}')

    body_path, face_path = str(body_path), str(face_path)

    body_result = retarget_bvh_data(body_path, body_height=body_height,
                                     foot_correction=foot_correction)
    face_result = retarget_bvh_data(face_path, body_height=body_height)

    merged = SkeletonRigify.merge_retargeted_clips(body_result, face_result)
    return JsonResponse(merged)


@require_GET
def retarget_job_bvh(request, job_id):
    """Legacy endpoint — now handled by serve_bvh_file(?mode=retarget) in views.py."""
    from .dateien import serve_bvh_file
    # Forward to unified handler with mode=retarget
    request.GET = request.GET.copy()
    request.GET['mode'] = 'retarget'
    return serve_bvh_file(request, job_id)


@require_GET
def retarget_job_merge(request, job_id):
    """Server-side retarget + merge for a hybrid pipeline job (body + face BVH).

    GET /api/character/retarget-job-merge/<job_id>/
    Optional query params: body_height, foot_correction
    """
    from humanbody_core.skeleton import SkeletonRigify

    job = get_object_or_404(BVHJob, id=job_id)
    if not job.bvh_file:
        return HttpResponseNotFound('Job has no body BVH file')
    if not job.bvh_file_face:
        return HttpResponseNotFound('Job has no face BVH file')

    for path in (job.bvh_file, job.bvh_file_face):
        if not os.path.isfile(path):
            return HttpResponseNotFound(f'BVH file not found: {path}')

    body_height = float(request.GET.get('body_height', 1.68))
    foot_correction = request.GET.get('foot_correction', '').lower() in ('1', 'true')

    body_result = retarget_bvh_data(job.bvh_file, body_height=body_height,
                                     foot_correction=foot_correction)

    # Always retarget v4 BVH (has hand bones)
    face_result = retarget_bvh_data(job.bvh_file_face, body_height=body_height)

    # Merge body + v4 (hands), filter ALL noisy v4 face bones → neutral face
    merged = SkeletonRigify.merge_retargeted_clips(
        body_result, face_result, filter_noisy_face=True)
    return JsonResponse(merged)










@csrf_exempt
@require_POST
def bvh_manage(request):
    """Dateien und Ordner der BVH-Bibliothek verwalten.

    POST /api/character/bvh-manage/ mit JSON-Feld `action`:
      delete, rename, move, copy, create_folder, rename_folder, delete_folder

    Die Arbeit macht Bvhverwaltung; hier steht nur die HTTP-Schale. Bis zum
    16.08.2026 waren beides 149 Zeilen in einer Funktion.
    """
    try:
        daten = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    try:
        return JsonResponse(Bvhverwaltung.ausfuehren(daten))
    except BvhFehler as e:
        return JsonResponse({'error': e.text}, status=e.kennzahl)










