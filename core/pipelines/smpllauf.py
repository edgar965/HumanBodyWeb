# -*- coding: utf-8 -*-
"""SMPL-Pipelines (GVHMR, WHAM, PromptHMR, SMPLest-X).

Aus core/pipelines/pipelinelauf.py herausgeloest (Umbau 15.08.2026). Die Datei
war beim Aufteilen von views.py entstanden und hatte selbst 1.228 Zeilen —
darunter Funktionen von 300 Zeilen. Getrennt wird nach Pipeline: Wer an der
OpenPose-Erkennung arbeitet, soll nicht die GVHMR-Nachbereitung mitlesen.
"""

import logging
from .werkzeuge import _monitor_pipeline_log
from .werkzeuge import _get_video_frame_count
from .werkzeuge import _ensure_mp4
from ..dienste.laufende_prozesse import LaufendeProzesse
from ..models import AppSettings
from ..pipeline_process import PipelineProzess
from django.conf import settings
import os
import subprocess


MAX_ERROR_CHARS = 2000  # max stderr chars to include in error messages
logger = logging.getLogger('core')


def _run_smpl_pipeline(job, video_path, output_dir):
    """Run GVHMR / WHAM / PromptHMR 3D pipeline via wrapper scripts."""

    # GVHMR/WHAM use PyAV which doesn't support WebM — convert if needed
    video_path = _ensure_mp4(video_path, output_dir)

    total_frames = _get_video_frame_count(video_path)
    bvh_output = str(output_dir / f'{job.pipeline}_{job.name.rsplit(".", 1)[0]}.bvh')
    wrapper_script = str(settings.WRAPPERS_DIR / 'lift_3d.py')

    s = AppSettings.load()
    job.status = 'processing'
    job.progress = 0
    job.progress_detail = f'0 / {total_frames} frames' if total_frames else f'Starting {job.get_pipeline_display()}...'
    job.save()

    p = job.pipeline_params or {}
    device = p.get('device', s.smpl_device)
    cmd = [
        settings.PIPELINE_PYTHON, wrapper_script,
        '--pipeline', job.pipeline,
        '--video', str(video_path),
        '--output', bvh_output,
        '--device', device,
    ]

    # Pipeline-specific params (per-job override, fallback to AppSettings)
    if job.pipeline == 'gvhmr':
        if p.get('static_cam', s.gvhmr_static_cam):
            cmd.append('--static_cam')
        cmd.extend(['--focal_length_mm', str(p.get('focal_length_mm', s.gvhmr_focal_length_mm))])
        cmd.extend(['--smooth_sigma', str(p.get('smooth_sigma', 2.0))])
        if not p.get('joint_limits', True):
            cmd.append('--no_joint_limits')
        if p.get('use_dpvo', False):
            cmd.append('--use_dpvo')
        if p.get('verbose', False):
            cmd.append('--verbose')
    elif job.pipeline == 'wham':
        if p.get('local_only', s.wham_estimate_local_only):
            cmd.append('--estimate_local_only')
        if p.get('smplify', s.wham_run_smplify):
            cmd.append('--run_smplify')
    elif job.pipeline == 'prompthmr':
        if p.get('static_cam', s.prompthmr_static_camera):
            cmd.append('--static_camera')

    # Write output to log file so subprocess survives server restart
    log_file = output_dir / 'pipeline.log'
    pid_file = output_dir / 'pipeline.pid'

    # stdout geht hier in eine Logdatei (überlebt den Django-Autoreload), deshalb
    # kein PipelineProzess — aber dieselbe Umgebung: PYTHONIOENCODING/PYTHONUTF8
    # bringen den Kindprozess dazu, UTF-8 zu schreiben. Sonst landet cp1252 in
    # einer Datei, die hier als UTF-8 geöffnet wird, und die Umlaute sind kaputt.
    env = PipelineProzess.umgebung()

    log_fh = open(log_file, 'w', encoding='utf-8')
    proc = subprocess.Popen(
        cmd, stdout=log_fh, stderr=subprocess.STDOUT,
        cwd=str(settings.WRAPPERS_DIR.parent), env=env,
    )
    pid_file.write_text(str(proc.pid))

    LaufendeProzesse.eintragen(job.id, proc)

    # Monitor by tailing the log file (survives Django auto-reload)
    _monitor_pipeline_log(job, log_file, total_frames, proc=proc)

    log_fh.close()
    proc.wait(timeout=60)  # Should already be done

    # Clean up PID file
    try:
        pid_file.unlink()
    except (FileNotFoundError, OSError):
        logger.debug('uebergangen', exc_info=True)

    if proc.returncode != 0:
        # Check if BVH was partially written before kill
        if os.path.exists(bvh_output) and os.path.getsize(bvh_output) > 100:
            return bvh_output
        # Check for any BVH in output dir
        import glob as _glob
        bvh_files = _glob.glob(str(output_dir / '*.bvh'))
        if bvh_files:
            return bvh_files[0]
        try:
            error_text = log_file.read_text(encoding='utf-8', errors='replace')
        except Exception:
            error_text = ''
        raise RuntimeError(f"3D pipeline '{job.pipeline}' failed (exit code {proc.returncode}):\n{error_text[-MAX_ERROR_CHARS:]}")

    return bvh_output
