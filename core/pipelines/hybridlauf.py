# -*- coding: utf-8 -*-
"""Hybridlauf: Koerper und Gesicht getrennt, dann zusammengefuehrt.

Aus core/pipelines/pipelinelauf.py herausgeloest (Umbau 15.08.2026). Die Datei
war beim Aufteilen von views.py entstanden und hatte selbst 1.228 Zeilen —
darunter Funktionen von 300 Zeilen. Getrennt wird nach Pipeline: Wer an der
OpenPose-Erkennung arbeitet, soll nicht die GVHMR-Nachbereitung mitlesen.
"""

from .mocapnet4 import _run_v4_pipeline
from .smpllauf import _run_smpl_pipeline
from ..models import AppSettings
from django.conf import settings
import logging
import os
import subprocess
import threading


def _run_hybrid_pipeline(job, video_path, output_dir):
    """Run hybrid pipeline: SMPL body (GPU) + MocapNET v4 face+hands (CPU) in parallel."""
    import time as _time

    p = job.pipeline_params or {}
    s = AppSettings.load()
    video_stem = job.name.rsplit('.', 1)[0]

    # Determine body backend from pipeline name
    body_backend = 'gvhmr' if job.pipeline == 'hybrid_gvhmr' else 'prompthmr'

    # --- Prepare body sub-job (fake job-like object for _run_smpl_pipeline) ---
    # We create a lightweight namespace that _run_smpl_pipeline can use.
    # Each sub-job gets a unique id suffix so the process registry doesn't collide.
    class _SubJob:
        """Minimal job-like object for sub-pipeline calls."""
        def __init__(self, pipeline, params, name, id_suffix):
            self.pipeline = pipeline
            self.pipeline_params = params
            self.name = name
            self.id = f'{job.id}_{id_suffix}'
            self.status = 'processing'
            self.progress = 0
            self.progress_detail = ''
        def save(self, **kw):
            pass  # Don't save sub-job progress directly
        def get_pipeline_display(self):
            return body_backend.upper()

    body_params = dict(p)
    body_params['device'] = p.get('body_device', s.smpl_device)
    body_job = _SubJob(body_backend, body_params, job.name, 'body')

    # --- Prepare v4 params ---
    # NOTE: hcd_iterations forced to 0 in hybrid mode — BVHConverter.dll
    # IK fine-tuning crashes with stack overflow on the face/hands sub-pipeline.
    # The GVHMR body is already high quality; v4 only adds face/hand rotations.
    v4_params = {
        'hcd_iterations': 0,
        'hcd_epochs': p.get('v4_hcd_epochs', s.v4_hcd_epochs),
        'hcd_learning_rate': s.v4_hcd_learning_rate,
        'smoothing_cutoff': s.v4_smoothing_cutoff,
        'smoothing_sampling': s.v4_smoothing_sampling,
        'mp_detection': p.get('v4_mp_detection', s.mp_min_detection_confidence),
        'mp_tracking': p.get('v4_mp_tracking', s.mp_min_tracking_confidence),
        # Always enable body (needed for MediaPipe base pose), plus face+hands
        'body': True,
        'face': p.get('v4_face', s.v4_enable_face),
        'hands': p.get('v4_hands', s.v4_enable_hands),
        'mouth': p.get('v4_mouth', s.v4_enable_mouth),
        'eyes': p.get('v4_eyes', s.v4_enable_eyes),
    }
    v4_job = _SubJob('v4', v4_params, job.name, 'face')

    # Output paths
    body_output_dir = output_dir / 'body'
    face_output_dir = output_dir / 'face'
    body_output_dir.mkdir(parents=True, exist_ok=True)
    face_output_dir.mkdir(parents=True, exist_ok=True)

    # Update job status
    job.status = 'processing'
    job.progress = 0
    job.progress_detail = 'Starting hybrid pipeline...'
    job.save()

    # --- Run both pipelines in parallel threads ---
    body_result = {'bvh': None, 'error': None}
    face_result = {'bvh': None, 'error': None}
    body_progress = [0]
    face_progress = [0]

    def run_body():
        try:
            bvh = _run_smpl_pipeline(body_job, video_path, body_output_dir)
            body_result['bvh'] = bvh
            body_progress[0] = 100
        except Exception as e:
            body_result['error'] = str(e)

    def run_face():
        try:
            bvh = _run_v4_pipeline(v4_job, video_path, face_output_dir)
            face_result['bvh'] = bvh
            face_progress[0] = 100
        except Exception as e:
            face_result['error'] = str(e)

    body_thread = threading.Thread(target=run_body, daemon=True)
    face_thread = threading.Thread(target=run_face, daemon=True)

    t_start = _time.time()
    body_thread.start()
    face_thread.start()

    # Register the v4 subprocess for stop functionality
    # (The body pipeline registers itself via LaufendeProzesse)

    # --- Progress monitoring loop ---
    while body_thread.is_alive() or face_thread.is_alive():
        _time.sleep(2)
        # Read sub-job progress (they write to their .progress fields)
        bp = body_job.progress if hasattr(body_job, 'progress') else 0
        fp = v4_job.progress if hasattr(v4_job, 'progress') else 0
        body_progress[0] = max(body_progress[0], bp)
        face_progress[0] = max(face_progress[0], fp)

        overall = min(body_progress[0], face_progress[0])
        elapsed = _time.time() - t_start
        body_detail = body_job.progress_detail or f'{body_progress[0]}%'
        face_detail = v4_job.progress_detail or f'{face_progress[0]}%'
        job.progress = overall
        job.progress_detail = f'Body: {body_detail} | Face+Hands: {face_detail}'
        job.save()

    body_thread.join(timeout=5)
    face_thread.join(timeout=5)

    # --- Check results ---
    errors = []
    if body_result['error']:
        errors.append(f"Body ({body_backend}): {body_result['error']}")
    if face_result['error']:
        errors.append(f"Face+Hands (v4): {face_result['error']}")

    if errors and not body_result['bvh'] and not face_result['bvh']:
        raise RuntimeError('Hybrid pipeline failed:\n' + '\n'.join(errors))

    # At least one pipeline succeeded — store results
    if body_result['bvh']:
        job.bvh_file = body_result['bvh']
    if face_result['bvh']:
        job.bvh_file_face = face_result['bvh']

    # --- Extract SMPL-X face expressions (replaces noisy v4 face bones) ---
    # Uses batch-mode SMPLest-X: model loaded once, all frames processed in sequence.
    # Output is placed next to the face BVH so retarget_job_merge() finds it.
    face_source = p.get('face_source', 'smplest_x')
    if face_result['bvh'] and face_source == 'smplest_x':
        try:
            face_expr_script = os.path.join(
                str(settings.TOOLS_ROOT), 'VideoToBVH', 'wrappers',
                '_run_smplest_x_video.py')
            face_expr_output = face_result['bvh'].rsplit('.', 1)[0] + '_blendshapes.json'
            job.progress_detail = 'Extracting face expressions (SMPLest-X batch)...'
            job.save()
            subprocess.run(
                [settings.PIPELINE_PYTHON, face_expr_script,
                 str(video_path), face_expr_output],
                check=True, timeout=1200,
            )
            logging.getLogger(__name__).info('Face expressions extracted: %s', face_expr_output)
        except Exception as e:
            logging.getLogger(__name__).warning('Face expression extraction failed: %s', e)

    if errors:
        # Partial success — note which part failed
        job.progress_detail = 'Done (partial: ' + '; '.join(errors)[:200] + ')'
    else:
        job.progress_detail = 'Done'

    return body_result['bvh'], face_result['bvh']
