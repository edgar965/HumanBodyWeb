# -*- coding: utf-8 -*-
"""MocapNET v4 — 2D-Erkennung und BVH in einem Lauf.

Aus core/pipelines/pipelinelauf.py herausgeloest (Umbau 15.08.2026). Die Datei
war beim Aufteilen von views.py entstanden und hatte selbst 1.228 Zeilen —
darunter Funktionen von 300 Zeilen. Getrennt wird nach Pipeline: Wer an der
OpenPose-Erkennung arbeitet, soll nicht die GVHMR-Nachbereitung mitlesen.
"""

import logging
from .werkzeuge import _get_video_frame_count
from ..dienste.laufende_prozesse import LaufendeProzesse
from ..models import AppSettings
from ..pipeline_process import PipelineProzess
from django.conf import settings
import os


MAX_ERROR_CHARS = 2000  # max stderr chars to include in error messages
logger = logging.getLogger('core')


def _run_v4_pipeline(job, video_path, output_dir):
    """Run MocapNET v4 pipeline: video -> BVH in one step."""
    import time as _time

    total_frames = _get_video_frame_count(video_path)
    job.status = 'v4_processing'
    job.progress = 0
    job.progress_detail = f'0 / {total_frames} frames' if total_frames else 'Starting MocapNET v4...'
    job.save()

    video_stem = job.name.rsplit('.', 1)[0]
    bvh_output = str(output_dir / f'v4_{video_stem}.bvh')

    # Stop-flag file for graceful cancellation
    stop_flag = str(output_dir / 'STOP_FLAG')

    v4_script = str(settings.MOCAPNET_V4_SCRIPT)
    s = AppSettings.load()
    p = job.pipeline_params or {}
    cmd = [
        settings.PIPELINE_PYTHON, v4_script,
        '--from', str(video_path),
        '--output', bvh_output,
        '--headless',
        '--stop-flag', stop_flag,
        '--hcd-iterations', str(p.get('hcd_iterations', s.v4_hcd_iterations)),
        '--hcd-epochs', str(p.get('hcd_epochs', s.v4_hcd_epochs)),
        '--hcd-lr', str(p.get('hcd_learning_rate', s.v4_hcd_learning_rate)),
        '--smooth-sampling', str(p.get('smoothing_sampling', s.v4_smoothing_sampling)),
        '--smooth-cutoff', str(p.get('smoothing_cutoff', s.v4_smoothing_cutoff)),
        '--mp-detection-conf', str(p.get('mp_detection', s.mp_min_detection_confidence)),
        '--mp-tracking-conf', str(p.get('mp_tracking', s.mp_min_tracking_confidence)),
        '--mp-model-complexity', str(s.mp_model_complexity),
        '--flipHorizontal',
    ]
    # Component flags (per-job override, fallback to AppSettings)
    if p.get('body', s.v4_enable_body): cmd.append('--body')
    if p.get('face', s.v4_enable_face): cmd.append('--face')
    if p.get('hands', s.v4_enable_hands): cmd.append('--hands')
    if p.get('mouth', s.v4_enable_mouth): cmd.append('--mouth')
    if p.get('eyes', s.v4_enable_eyes): cmd.append('--eyes')

    # Diese Stelle war die einzige, die Zeichensatz und stderr schon richtig
    # hatte — sie ist die Vorlage für PipelineProzess und nutzt ihn jetzt selbst,
    # damit es nur noch eine Fassung gibt.
    pp = PipelineProzess.starten(cmd, cwd=settings.MOCAPNET_V4_ROOT)
    proc, stderr_lines = pp.proc, pp.stderr_zeilen
    LaufendeProzesse.eintragen(job.id, proc)

    v4_start = _time.time()
    last_update = 0

    # 900 s: Der erste Lauf laedt Modellgewichte, und dabei kommt minutenlang
    # keine Zeile. Kuerzer waere ein Abbruch mitten im Download.
    for line in pp.stdout_zeilen(stille_timeout=900):
        line = line.strip()
        if line.startswith('TOTAL:'):
            try:
                total_frames = int(line[6:])
                job.progress_detail = f'0 / {total_frames} frames'
                job.save()
            except ValueError:
                logger.debug('uebergangen', exc_info=True)
        elif line.startswith('PROGRESS:'):
            now = _time.time()
            if now - last_update < 1.0:
                continue
            last_update = now
            try:
                parts = line[9:].split('/')
                current = int(parts[0])
                total = int(parts[1]) if len(parts) > 1 else total_frames
                if total > 0 and current > 0:
                    pct = int((current / total) * 98)
                    elapsed = now - v4_start
                    fps = current / max(elapsed, 0.1)
                    remaining = int((total - current) / max(fps, 0.01))
                    job.progress = pct
                    job.progress_detail = (
                        f'{current} / {total} frames — '
                        f'{fps:.1f} fps, ~{remaining}s left'
                    )
                    job.save()
            except (ValueError, IndexError):
                logger.debug('uebergangen', exc_info=True)
        elif line.startswith('DETECTION:'):
            pass  # detection.json saved alongside BVH, no action needed
        elif line.startswith('KEYPOINTS:'):
            pass  # 2dJoints_v4.csv saved alongside BVH, no action needed
        elif line.startswith('DONE:'):
            # v4 reports the output path
            reported = line[5:].strip()
            if reported and os.path.exists(reported):
                bvh_output = reported
        elif line.startswith('STOPPED:'):
            # Graceful stop — partial BVH was saved
            reported = line[8:].strip()
            if reported and os.path.exists(reported):
                bvh_output = reported

    pp.warten(timeout=1800)

    # Clean up stop flag if still present
    if os.path.exists(stop_flag):
        try:
            os.remove(stop_flag)
        except OSError:
            logger.debug('uebergangen', exc_info=True)

    if proc.returncode != 0:
        # Check for partial BVH (cancelled / killed)
        if os.path.exists(bvh_output) and os.path.getsize(bvh_output) > 100:
            return bvh_output
        stderr = ''.join(stderr_lines).strip()
        raise RuntimeError(f"MocapNET v4 failed (exit code {proc.returncode}):\n{stderr[-MAX_ERROR_CHARS:]}")

    if not os.path.exists(bvh_output):
        raise RuntimeError(f"BVH file not found at {bvh_output}")

    return bvh_output
