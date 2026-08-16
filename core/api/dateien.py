# -*- coding: utf-8 -*-
"""Auslieferung von BVH-, Video- und Erkennungsdateien.

Herausgeloest aus core/views.py (Umbau 15.08.2026). Die Datei hatte 3.496 Zeilen
und 43 Endpunkte, dazwischen die Pipeline-Laeufe mit bis zu 304 Zeilen je
Funktion. Getrennt wird nach Aufgabe: Endpunkte in core/api/, Fachlogik in
core/dienste/, die Laeufe in core/pipelines/.
"""

from ..dienste.skelettvideo import _render_video_with_skeleton
from ..dienste.keypoints import _serve_keypoints_2d_impl
from ..models import BVHJob, AppSettings
from django.conf import settings
from django.http import (
    JsonResponse, FileResponse, HttpResponse, HttpResponseNotFound,
    StreamingHttpResponse,
)
from django.shortcuts import get_object_or_404
from pathlib import Path
import os




def _annotate_file_sizes(jobs):
    """Add video_size (bytes) and video_size_display (human-readable) to each job."""
    for job in jobs:
        try:
            video_path = Path(settings.MEDIA_ROOT) / str(job.video_file)
            size = video_path.stat().st_size if video_path.exists() else 0
        except OSError:
            size = 0
        job.video_size = size
        if size < 1024:
            job.video_size_display = f'{size} B'
        elif size < 1024 * 1024:
            job.video_size_display = f'{size / 1024:.1f} KB'
        elif size < 1024 * 1024 * 1024:
            job.video_size_display = f'{size / (1024*1024):.1f} MB'
        else:
            job.video_size_display = f'{size / (1024*1024*1024):.1f} GB'


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

    # Default: raw BVH file
    bvh_path = job.bvh_file
    # Fallback: hybrid partial success — body failed, face succeeded
    if (not bvh_path or not os.path.exists(bvh_path)) and job.bvh_file_face and os.path.exists(job.bvh_file_face):
        bvh_path = job.bvh_file_face
    if not bvh_path or not os.path.exists(bvh_path):
        return HttpResponseNotFound('BVH file not found')
    resp = FileResponse(
        open(bvh_path, 'rb'),
        content_type='text/plain',
        filename=os.path.basename(bvh_path),
    )
    resp['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return resp


def _serve_retarget_job_impl(job, request):
    """Retarget a pipeline job's BVH to Rigify/DEF skeleton."""
    from ..character_api import retarget_bvh_data

    if not job.bvh_file:
        return HttpResponseNotFound('Job has no BVH file')
    bvh_path = job.bvh_file
    if not os.path.isfile(bvh_path):
        return HttpResponseNotFound(f'BVH file not found: {bvh_path}')

    body_height = float(request.GET.get('body_height', 1.68))
    fmt = request.GET.get('format', None)
    foot_correction = request.GET.get('foot_correction', '').lower() in ('1', 'true')

    return JsonResponse(retarget_bvh_data(bvh_path, body_height, fmt, foot_correction))


def serve_bvh_face(request, job_id):
    """Serve the face+hands BVH file for hybrid pipeline jobs."""
    job = get_object_or_404(BVHJob, id=job_id)
    if not job.bvh_file_face or not os.path.exists(job.bvh_file_face):
        return HttpResponseNotFound('Face BVH file not found')
    resp = FileResponse(
        open(job.bvh_file_face, 'rb'),
        content_type='text/plain',
        filename=os.path.basename(job.bvh_file_face),
    )
    resp['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return resp


def _serve_video_with_range(request, file_path):
    """Serve a video file with HTTP Range request support for seeking."""
    import mimetypes
    ct = mimetypes.guess_type(str(file_path))[0] or 'video/mp4'
    file_size = os.path.getsize(file_path)

    range_header = request.META.get('HTTP_RANGE', '')
    if range_header:
        # Parse "bytes=START-END"
        try:
            ranges = range_header.replace('bytes=', '').split('-')
            start = int(ranges[0]) if ranges[0] else 0
            end = int(ranges[1]) if ranges[1] else file_size - 1
        except (ValueError, IndexError):
            start, end = 0, file_size - 1
        end = min(end, file_size - 1)
        length = end - start + 1

        def file_iterator():
            with open(file_path, 'rb') as f:
                f.seek(start)
                remaining = length
                while remaining > 0:
                    chunk = f.read(min(8192, remaining))
                    if not chunk:
                        break
                    remaining -= len(chunk)
                    yield chunk

        resp = StreamingHttpResponse(file_iterator(), status=206, content_type=ct)
        resp['Content-Length'] = length
        resp['Content-Range'] = f'bytes {start}-{end}/{file_size}'
        resp['Accept-Ranges'] = 'bytes'
        return resp

    # No Range header — serve full file with Accept-Ranges
    resp = FileResponse(open(file_path, 'rb'), content_type=ct)
    resp['Accept-Ranges'] = 'bytes'
    resp['Content-Length'] = file_size
    return resp


def serve_video_file(request, job_id):
    """Serve the original uploaded video, with fallback to output directory."""
    job = get_object_or_404(BVHJob, id=job_id)

    # Try the original upload location first
    if job.video_file:
        primary = Path(settings.MEDIA_ROOT) / str(job.video_file)
        if primary.exists():
            return _serve_video_with_range(request, str(primary))

    # Fallback: look in output directory for 0_input_video.mp4
    output_dir = Path(settings.MEDIA_ROOT) / 'output' / str(job.id)
    if output_dir.exists():
        stem = Path(job.video_file.name).stem if job.video_file else job.name
        for candidate in [
            output_dir / stem / '0_input_video.mp4',
            output_dir / f'{stem}.mp4',
            output_dir / f'{stem}.webm',
        ]:
            if candidate.exists():
                return _serve_video_with_range(request, str(candidate))
        # Try any video file in the output subdirectory
        sub = output_dir / stem if (output_dir / stem).is_dir() else output_dir
        for f in sub.iterdir():
            if f.suffix.lower() in ('.mp4', '.webm', '.avi', '.mov') and f.name.startswith('0_'):
                return _serve_video_with_range(request, str(f))

    return HttpResponseNotFound('Video file not found')


def serve_detection_data(request, job_id):
    """Serve per-frame detection flags as JSON for the BVH player."""
    job = get_object_or_404(BVHJob, id=job_id)
    output_dir = Path(settings.MEDIA_ROOT) / 'output' / str(job.id)
    detection_file = output_dir / 'detection.json'
    if detection_file.exists():
        resp = FileResponse(
            open(detection_file, 'rb'),
            content_type='application/json',
        )
        resp['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return resp
    # Backwards compat: old jobs without detection data → empty array
    return JsonResponse([], safe=False)


def video_thumbnail(request, job_id):
    """Extract frame 0 from a job's video and return as JPEG thumbnail."""
    job = get_object_or_404(BVHJob, id=job_id)
    video_path = Path(settings.MEDIA_ROOT) / str(job.video_file)
    try:
        import cv2
        cap = cv2.VideoCapture(str(video_path))
        ret, frame = cap.read()
        cap.release()
        if not ret:
            return HttpResponseNotFound('Could not read video frame')
        h, w = frame.shape[:2]
        target_w, target_h = 160, 90
        scale = min(target_w / w, target_h / h)
        new_w, new_h = int(w * scale), int(h * scale)
        frame = cv2.resize(frame, (new_w, new_h))
        _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
        return HttpResponse(jpeg.tobytes(), content_type='image/jpeg')
    except Exception:
        return HttpResponseNotFound('Thumbnail generation failed')


def _copy_to_output_dir(src_path, filename):
    """Copy a video file to the configured video_output_dir."""
    s = AppSettings.load()
    out_dir = Path(s.video_output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    import shutil
    dest = out_dir / filename
    shutil.copy2(str(src_path), str(dest))
    return dest


def save_rig_video(request, job_id):
    """Render and download skeleton-only video (white skeleton on black)."""
    job = get_object_or_404(BVHJob, id=job_id)
    out_path = _render_video_with_skeleton(job, overlay=False)
    if not out_path or not out_path.exists():
        return HttpResponseNotFound('Could not render rig video')
    filename = f'{job.pipeline}_{Path(job.name).stem}_rig_only.mp4'
    _copy_to_output_dir(out_path, filename)
    return FileResponse(
        open(out_path, 'rb'),
        content_type='video/mp4',
        filename=filename,
    )


def save_overlay_video(request, job_id):
    """Render and download video with skeleton overlay."""
    job = get_object_or_404(BVHJob, id=job_id)
    out_path = _render_video_with_skeleton(job, overlay=True)
    if not out_path or not out_path.exists():
        return HttpResponseNotFound('Could not render overlay video')
    filename = f'{Path(job.name).stem}_skeleton.mp4'
    _copy_to_output_dir(out_path, filename)
    return FileResponse(
        open(out_path, 'rb'),
        content_type='video/mp4',
        filename=filename,
    )


def save_video3d(request, job_id):
    """Save uploaded 3D character video to the configured video_output_dir."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    job = get_object_or_404(BVHJob, id=job_id)
    video_blob = request.FILES.get('video')
    if not video_blob:
        return JsonResponse({'error': 'No video file'}, status=400)
    s = AppSettings.load()
    out_dir = Path(s.video_output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = Path(job.name).stem
    filename = f'{stem}_3d_character.webm'
    dest = out_dir / filename
    with open(dest, 'wb') as f:
        for chunk in video_blob.chunks():
            f.write(chunk)
    return JsonResponse({'ok': True, 'path': str(dest)})


def serve_keypoints_2d(request, job_id):
    """Legacy endpoint — redirects to unified serve_bvh_file(?mode=keypoints2d)."""
    job = get_object_or_404(BVHJob, id=job_id)
    return _serve_keypoints_2d_impl(job)
