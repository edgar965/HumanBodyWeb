# -*- coding: utf-8 -*-
"""Gemeinsame Handgriffe aller Pipeline-Laeufe.

Aus core/pipelines/pipelinelauf.py herausgeloest (Umbau 15.08.2026). Die Datei
war beim Aufteilen von views.py entstanden und hatte selbst 1.228 Zeilen —
darunter Funktionen von 300 Zeilen. Getrennt wird nach Pipeline: Wer an der
OpenPose-Erkennung arbeitet, soll nicht die GVHMR-Nachbereitung mitlesen.
"""

from ..models import AppSettings
from django.conf import settings
from pathlib import Path
import logging
import os
import subprocess


logger = logging.getLogger('core')
pipeline_logger = logging.getLogger('core.pipeline')


def _get_video_frame_count(video_path):
    """Get total frame count from a video file using OpenCV."""
    try:
        import cv2
        cap = cv2.VideoCapture(str(video_path))
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        return total if total > 0 else 0
    except Exception:
        return 0


def _is_pid_alive(pid):
    """Check if a process with the given PID is still running (Windows)."""
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        SYNCHRONIZE = 0x00100000
        handle = kernel32.OpenProcess(SYNCHRONIZE, False, pid)
        if handle:
            kernel32.CloseHandle(handle)
            return True
        return False
    except Exception:
        return False


def _monitor_pipeline_log(job, log_file, total_frames, *, proc=None, pid=None):
    """Monitor a pipeline subprocess by tailing its log file.

    Pass *proc* (Popen) for normal monitoring or *pid* (int) for re-monitoring
    after server restart.
    """
    import time as _time
    import re as _re

    def _alive():
        if proc is not None:
            return proc.poll() is None
        return _is_pid_alive(pid)

    pct_re = _re.compile(r'(\d+)%\|')
    frac_re = _re.compile(r'(\d+)\s*/\s*(\d+)')

    last_pos = 0
    last_update = 0

    while _alive():
        _time.sleep(1)
        try:
            with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
                f.seek(last_pos)
                new_data = f.read()
                last_pos = f.tell()
        except (FileNotFoundError, OSError):
            continue

        if not new_data:
            continue

        now = _time.time()
        if now - last_update < 0.5:
            continue
        last_update = now

        lines = [l.strip() for l in new_data.splitlines() if l.strip()]
        if not lines:
            continue

        line = lines[-1]
        pct_match = pct_re.search(line)
        frac_match = frac_re.search(line)

        if pct_match:
            job.progress = min(int(pct_match.group(1)), 95)
        elif frac_match:
            cur, tot = int(frac_match.group(1)), int(frac_match.group(2))
            if tot > 0:
                job.progress = min(int(cur / tot * 95), 95)

        detail = line[:80]
        if total_frames:
            detail = f'{detail} — {total_frames} frames'
        job.progress_detail = detail[:100]
        job.save(update_fields=['progress', 'progress_detail', 'updated_at'])


def remonitor_smpl_job(job_id, pid):
    """Re-monitor a still-running SMPL pipeline after server restart.

    Called from CoreConfig.ready() in apps.py.
    """
    import time as _time
    import glob as _glob
    from core.models import BVHJob

    try:
        job = BVHJob.objects.get(id=job_id)
    except BVHJob.DoesNotExist:
        return

    output_dir = Path(settings.MEDIA_ROOT) / 'output' / str(job_id)
    log_file = output_dir / 'pipeline.log'
    video_path = Path(settings.MEDIA_ROOT) / str(job.video_file)
    total_frames = _get_video_frame_count(video_path) if video_path.exists() else 0

    # Monitor until process finishes
    _monitor_pipeline_log(job, log_file, total_frames, pid=pid)

    # Give a moment for final writes
    _time.sleep(1)

    # Refresh from DB — may have been updated elsewhere (cancel, etc.)
    job.refresh_from_db()
    if job.status not in ('processing', 'v4_processing'):
        return

    # Check for BVH output
    bvh_files = _glob.glob(str(output_dir / '*.bvh'))
    valid_bvh = [f for f in bvh_files if os.path.getsize(f) > 100]

    if valid_bvh:
        job.bvh_file = valid_bvh[0]
        job.status = 'complete'
        job.progress = 100
        job.progress_detail = 'Complete'
        job.error_message = ''
        try:
            import cv2
            cap = cv2.VideoCapture(str(video_path))
            job.fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            cap.release()
        except Exception:
            job.fps = 30.0
        job.save()
        pipeline_logger.info('[remonitor] Job %s: BVH found, marked complete.', job_id)
    else:
        # Try to read error from log
        try:
            log_text = log_file.read_text(encoding='utf-8', errors='replace')
            job.error_message = f'Pipeline finished but no BVH output found.\n{log_text[-500:]}'
        except Exception:
            job.error_message = 'Pipeline finished but no BVH output was found.'
        job.status = 'failed'
        job.save()
        pipeline_logger.error('[remonitor] Job %s: no BVH found, marked failed.', job_id)

    # Clean up PID file
    try:
        (output_dir / 'pipeline.pid').unlink()
    except (FileNotFoundError, OSError):
        logger.debug('uebergangen', exc_info=True)


def _ensure_mp4(video_path, output_dir):
    """Convert non-MP4 video to MP4 (GVHMR/WHAM need PyAV-compatible input).
    Returns the MP4 path (may be the original if already MP4)."""
    vp = Path(video_path)
    if vp.suffix.lower() == '.mp4':
        return video_path
    mp4_path = output_dir / (vp.stem + '.mp4')
    if mp4_path.exists():
        return str(mp4_path)
    pipeline_logger.info('[SMPL] Converting %s -> MP4 for SMPL pipeline...', vp.name)
    proc = subprocess.run(
        ['ffmpeg', '-y', '-i', str(video_path), '-c:v', 'libx264',
         '-preset', 'fast', '-crf', '18', '-an', str(mp4_path)],
        capture_output=True, text=True, timeout=600,
    )
    if proc.returncode != 0 or not mp4_path.exists():
        raise RuntimeError(f'ffmpeg conversion failed: {proc.stderr[-500:]}')
    pipeline_logger.info('[SMPL] Converted to %s', mp4_path)
    return str(mp4_path)


def _copy_gvhmr_render_videos(job, output_dir):
    """Copy GVHMR render videos (incam, global, combined) to the user-configured output dir."""
    import shutil
    p = job.pipeline_params or {}
    s = AppSettings.load()
    dest_dir = Path(p.get('video_output_dir', s.video_output_dir))
    if not dest_dir or not str(dest_dir).strip():
        return
    dest_dir.mkdir(parents=True, exist_ok=True)
    video_stem = job.name.rsplit('.', 1)[0]
    gvhmr_dir = output_dir / video_stem
    if not gvhmr_dir.is_dir():
        return
    suffixes = ['incam.mp4', 'global.mp4', 'incam_global_horiz.mp4']
    for f in gvhmr_dir.iterdir():
        if f.suffix == '.mp4':
            dest = dest_dir / f'{video_stem}_{f.stem}.mp4'
            try:
                shutil.copy2(str(f), str(dest))
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f'GVHMR video copy failed: {e}')
