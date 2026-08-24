# -*- coding: utf-8 -*-
"""Silhouette und Ausrichtung eines analysierten Fotos — die HTTP-Schale.

Aus core/api/foto.py herausgeloest (Umbau 16.08.2026).

UMBENANNT am 17.08.2026: Die Datei hiess `fotoausrichtung.py` und damit genau
wie `core/dienste/fotoausrichtung.py`, aus der sie ihre Rechenschritte holt.
Zwei Dateien gleichen Namens in einem Projekt sind in einer Stapelspur nicht
auseinanderzuhalten — Befund von `namens-dubletten`. „Abgleich" benennt, was
diese drei Endpunkte tun: Foto und Koerpernetz zur Deckung bringen und das
Ergebnis speichern. Gerechnet wird nebenan in `Fotoausrichtung`.
"""

from ..dienste.fotoausrichtung import Fotoausrichtung
from ..dienste.silhouette import Silhouette
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
import json
import numpy as np
import os


import logging

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def photo_save_projection(request, job_id):
    """Save the client-rendered projection preview as silhouette image."""
    from ..models import PhotoAnalysisJob
    try:
        job = PhotoAnalysisJob.objects.get(id=job_id)
    except PhotoAnalysisJob.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Job not found'}, status=404)

    import base64
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

    img_data = body.get('image', '')
    if not img_data:
        return JsonResponse({'ok': False, 'error': 'No image data'}, status=400)

    if ',' in img_data:
        img_data = img_data.split(',', 1)[1]

    try:
        raw = base64.b64decode(img_data)
    except Exception:
        return JsonResponse({'ok': False, 'error': 'Invalid base64'}, status=400)

    sil_dir = os.path.join(str(settings.BASE_DIR), 'media', 'photo_analysis', 'silhouettes')
    os.makedirs(sil_dir, exist_ok=True)
    fname = f'{job_id}.jpg'
    fpath = os.path.join(sil_dir, fname)
    with open(fpath, 'wb') as f:
        f.write(raw)

    rel_path = f'media/photo_analysis/silhouettes/{fname}'
    try:
        data = json.loads(job.result_json)
        data['silhouette_path'] = rel_path
        job.result_json = json.dumps(data, default=str)
        job.save(update_fields=['result_json'])
    except Exception:
        logger.warning('Job-Ergebnis konnte nicht gespeichert werden — result_json fehlt jetzt', exc_info=True)

    return JsonResponse({'ok': True, 'path': f'/{rel_path}'})


@require_GET
def photo_silhouette_data(request, job_id):
    """Umrisse fuer den Ausrichtungsassistenten: Koerper, Gesicht, Rahmen.

    Bis zum Umbau am 15.08.2026 standen hier 338 Zeilen; am 17.08.2026 waren es
    noch 74. Der Ablauf steht jetzt in
    `dienste/silhouettenauftrag.Silhouettenauftrag` — hier bleibt, was ein
    Endpunkt tut: Auftrag holen, rufen, Statuscode setzen.
    """
    import cv2

    from ..dienste.silhouettenauftrag import Fotofehler, Silhouettenauftrag
    from ..models import PhotoAnalysisJob
    try:
        job = PhotoAnalysisJob.objects.get(id=job_id)
    except PhotoAnalysisJob.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Job not found'}, status=404)
    try:
        auftrag = Silhouettenauftrag(job, _posierte_punkte)
        return JsonResponse(auftrag.ergebnis(cv2))
    except Fotofehler as fehler:
        return JsonResponse({'ok': False, 'error': str(fehler)},
                            status=fehler.code)


def _posierte_punkte(job_id, daten, breite, hoehe):
    """Gespeicherte Pose in Bildkoordinaten, oder None.

    Die .npz kommt aus der Foto-Pipeline; fehlt sie oder fehlt die Kamera, wird
    orthographisch projiziert. Eine kuerzere Punktliste (SMPL statt SMPL-X) wird
    mit NaN aufgefuellt, damit die Indizes der Dreiecke weiter passen."""
    kamera = daten.get('cam_data')
    pfad = os.path.join(str(settings.BASE_DIR), '..', 'HumanBody', 'data',
                        'photoTo3D', 'SMPLX', '%s.npz' % job_id)
    if not (kamera and os.path.isfile(pfad)):
        return None
    try:
        npz = np.load(pfad)
        if 'posed_vertices' not in npz:
            return None
        posiert = npz['posed_vertices']
        punkte = Fotoausrichtung.vertices_projizieren(posiert, kamera, breite, hoehe)
        return punkte, len(posiert)
    except Exception:                                             # noqa: BLE001
        logger.error('Posierte Vertices fuer %s nicht ladbar', job_id,
                     exc_info=True)
        return None


@csrf_exempt
@require_POST
def photo_save_alignment(request, job_id):
    """Save user-confirmed alignment transforms into the job's result_json."""
    from ..models import PhotoAnalysisJob
    try:
        job = PhotoAnalysisJob.objects.get(id=job_id)
    except PhotoAnalysisJob.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Job not found'}, status=404)

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

    body_transform = body.get('body_transform')
    face_transform = body.get('face_transform')
    proj_2d_offset = body.get('proj_2d_offset')
    if not body_transform and not proj_2d_offset:
        return JsonResponse({'ok': False, 'error': 'body_transform or proj_2d_offset required'}, status=400)

    try:
        data = json.loads(job.result_json)
    except (json.JSONDecodeError, TypeError):
        logger.exception('photo_save_alignment: JSONDecodeError/TypeError')
        return JsonResponse({'ok': False, 'error': 'Invalid result data'}, status=500)

    data['alignment_data'] = {
        'body_transform': body_transform,
        'face_transform': face_transform,
        'proj_2d_offset': proj_2d_offset,
        'body_contour_edited': body.get('body_contour_edited'),
        'face_contour_edited': body.get('face_contour_edited'),
    }
    job.result_json = json.dumps(data, default=str)
    job.save(update_fields=['result_json'])

    return JsonResponse({'ok': True})
