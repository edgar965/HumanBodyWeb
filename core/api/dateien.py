# -*- coding: utf-8 -*-
"""Auslieferung von BVH-, Video- und Erkennungsdateien.

Herausgeloest aus core/views.py (Umbau 15.08.2026). Die Datei hatte 3.496 Zeilen
und 43 Endpunkte, dazwischen die Pipeline-Laeufe mit bis zu 304 Zeilen je
Funktion. Getrennt wird nach Aufgabe: Endpunkte in core/api/, Fachlogik in
core/dienste/, die Laeufe in core/pipelines/.

UMBAU 18.08.2026 (Befund `freie-funktionen`, Kriterium 1): 13 Funktionen, keine
Klasse. Die Arbeit steht jetzt in

    dienste/videoauslieferung.py  Video finden und mit `Range` ausliefern
    dienste/videoablage.py        fertige Videos in den Ausgabeordner
    daten/dateigroessen.py        Groessenangabe fuer die Auftragsliste

Hier bleiben die Endpunkte -- Django routet auf Aufrufbares, das ist ihre Form.

DABEI GEFUNDEN: `_serve_retarget_job_impl` holte `retarget_bvh_data` aus
`core.character_api` -- die Datei ist beim Umbau am 15.08.2026 in `core/api/`
aufgegangen und existiert nicht mehr. Belegt am 18.08.2026:
`ModuleNotFoundError: No module named 'core.character_api'`. Damit war
`/api/bvh/<auftrag>/?mode=retarget` tot. Ein Import IN einer Funktion faellt
weder beim Start noch dem Werkzeug `tote-importe` auf -- nur beim Aufruf.
"""

import os
from pathlib import Path

from django.conf import settings
from django.http import (
    FileResponse, HttpResponse, HttpResponseNotFound, JsonResponse,
)
from django.shortcuts import get_object_or_404

from ..daten.dateigroessen import Dateigroessen
from ..dienste.keypoints import _serve_keypoints_2d_impl
from ..dienste.skelettvideo import _render_video_with_skeleton
from ..dienste.videoablage import Videoablage
from ..dienste.videoauslieferung import Videoauslieferung
from ..models import BVHJob
from ..dienste.retargetdaten import Retargetdaten


def _annotate_file_sizes(jobs):
    """Bisherige Aufrufform (core/api/auftrag_upload.py)."""
    return Dateigroessen.anhaengen(jobs)


def _textantwort(pfad):
    """BVH-Text ohne Zwischenspeicher -- er aendert sich beim Bearbeiten."""
    antwort = FileResponse(open(pfad, 'rb'), content_type='text/plain',
                           filename=os.path.basename(pfad))
    antwort['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return antwort


def serve_bvh_file(request, job_id):
    """Unified animation data endpoint for pipeline jobs.

    GET /api/bvh/<job_id>/                     → raw BVH file (default)
    GET /api/bvh/<job_id>/?mode=retarget       → retargeted Rigify/DEF quaternion tracks
    GET /api/bvh/<job_id>/?mode=keypoints2d    → 2D keypoint overlay data

    Query params for retarget mode:
        body_height: float (default 1.68)
        format: str (auto-detected if omitted)
        foot_correction: bool (default false)
    """
    mode = request.GET.get('mode', 'bvh')
    job = get_object_or_404(BVHJob, id=job_id)

    if mode == 'keypoints2d':
        return _serve_keypoints_2d_impl(job)
    if mode == 'retarget':
        return _serve_retarget_job_impl(job, request)

    pfad = job.bvh_file
    # Rueckfall: Beim Hybridlauf kann der Koerper scheitern und das Gesicht
    # gelingen — dann ist die Gesichtsdatei alles, was es gibt.
    if (not pfad or not os.path.exists(pfad)) and job.bvh_file_face \
            and os.path.exists(job.bvh_file_face):
        pfad = job.bvh_file_face
    if not pfad or not os.path.exists(pfad):
        return HttpResponseNotFound('BVH file not found')
    return _textantwort(pfad)


def _serve_retarget_job_impl(job, request):
    """Retarget a pipeline job's BVH to Rigify/DEF skeleton."""
    if not job.bvh_file:
        return HttpResponseNotFound('Job has no BVH file')
    if not os.path.isfile(job.bvh_file):
        return HttpResponseNotFound(f'BVH file not found: {job.bvh_file}')
    hoehe = float(request.GET.get('body_height', 1.68))
    format_ = request.GET.get('format', None)
    fusskorrektur = request.GET.get('foot_correction', '').lower() in ('1', 'true')
    return JsonResponse(Retargetdaten(job.bvh_file, hoehe, format_,
                                       fusskorrektur).holen())


def serve_bvh_face(request, job_id):
    """Serve the face+hands BVH file for hybrid pipeline jobs."""
    job = get_object_or_404(BVHJob, id=job_id)
    if not job.bvh_file_face or not os.path.exists(job.bvh_file_face):
        return HttpResponseNotFound('Face BVH file not found')
    return _textantwort(job.bvh_file_face)


def _serve_video_with_range(request, file_path):
    """Bisherige Aufrufform — siehe dienste/videoauslieferung.py."""
    return Videoauslieferung.mit_bereich(request, file_path)


def serve_video_file(request, job_id):
    """Serve the original uploaded video, with fallback to output directory."""
    job = get_object_or_404(BVHJob, id=job_id)
    return Videoauslieferung(job).antwort(request)


def serve_detection_data(request, job_id):
    """Serve per-frame detection flags as JSON for the BVH player."""
    job = get_object_or_404(BVHJob, id=job_id)
    datei = Path(settings.MEDIA_ROOT) / 'output' / str(job.id) / 'detection.json'
    if not datei.exists():
        # Alte Auftraege haben keine Erkennungsdaten — leere Liste statt 404,
        # damit der Spieler nicht in den Fehlerzweig laeuft.
        return JsonResponse([], safe=False)
    antwort = FileResponse(open(datei, 'rb'), content_type='application/json')
    antwort['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return antwort


def video_thumbnail(request, job_id):
    """Extract frame 0 from a job's video and return as JPEG thumbnail."""
    job = get_object_or_404(BVHJob, id=job_id)
    pfad = Path(settings.MEDIA_ROOT) / str(job.video_file)
    try:
        import cv2
        aufnahme = cv2.VideoCapture(str(pfad))
        gelesen, bild = aufnahme.read()
        aufnahme.release()
        if not gelesen:
            return HttpResponseNotFound('Could not read video frame')
        hoehe, breite = bild.shape[:2]
        faktor = min(160 / breite, 90 / hoehe)
        bild = cv2.resize(bild, (int(breite * faktor), int(hoehe * faktor)))
        _, jpeg = cv2.imencode('.jpg', bild, [cv2.IMWRITE_JPEG_QUALITY, 75])
        return HttpResponse(jpeg.tobytes(), content_type='image/jpeg')
    except Exception:
        return HttpResponseNotFound('Thumbnail generation failed')


def _copy_to_output_dir(src_path, filename):
    """Bisherige Aufrufform — siehe dienste/videoablage.py."""
    return Videoablage.kopieren(src_path, filename)


def _skelettvideo(job, overlay, dateiname):
    """Video rendern, in den Ausgabeordner legen und herunterladen."""
    pfad = _render_video_with_skeleton(job, overlay=overlay)
    if not pfad or not pfad.exists():
        art = 'overlay' if overlay else 'rig'
        return HttpResponseNotFound(f'Could not render {art} video')
    Videoablage.kopieren(pfad, dateiname)
    return FileResponse(open(pfad, 'rb'), content_type='video/mp4',
                        filename=dateiname)


def save_rig_video(request, job_id):
    """Render and download skeleton-only video (white skeleton on black)."""
    job = get_object_or_404(BVHJob, id=job_id)
    return _skelettvideo(job, False,
                         f'{job.pipeline}_{Path(job.name).stem}_rig_only.mp4')


def save_overlay_video(request, job_id):
    """Render and download video with skeleton overlay."""
    job = get_object_or_404(BVHJob, id=job_id)
    return _skelettvideo(job, True, f'{Path(job.name).stem}_skeleton.mp4')


def save_video3d(request, job_id):
    """Save uploaded 3D character video to the configured video_output_dir."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    job = get_object_or_404(BVHJob, id=job_id)
    hochgeladen = request.FILES.get('video')
    if not hochgeladen:
        return JsonResponse({'error': 'No video file'}, status=400)
    ziel = Videoablage.schreiben(hochgeladen,
                                 f'{Path(job.name).stem}_3d_character.webm')
    return JsonResponse({'ok': True, 'path': str(ziel)})


def serve_keypoints_2d(request, job_id):
    """Legacy endpoint — redirects to unified serve_bvh_file(?mode=keypoints2d)."""
    job = get_object_or_404(BVHJob, id=job_id)
    return _serve_keypoints_2d_impl(job)
