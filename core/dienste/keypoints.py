# -*- coding: utf-8 -*-
"""Zweidimensionale Gelenkpunkte fuer die Ueberlagerung.

Herausgeloest aus core/views.py (Umbau 15.08.2026). Die Datei hatte 3.496 Zeilen
und 43 Endpunkte, dazwischen die Pipeline-Laeufe mit bis zu 304 Zeilen je
Funktion. Getrennt wird nach Aufgabe: Endpunkte in core/api/, Fachlogik in
core/dienste/, die Laeufe in core/pipelines/.
"""

from django.conf import settings
from django.http import JsonResponse
from pathlib import Path
from .keypoints_quellen import _extract_v4_keypoints, _try_generate_smpl_2d_keypoints
import json
import logging


BODY_JOINT_NAMES = [
    'head', 'neck', 'rshoulder', 'relbow', 'rhand',
    'lshoulder', 'lelbow', 'lhand', 'hip',
    'rhip', 'rknee', 'rfoot', 'lhip', 'lknee', 'lfoot',
    'endsite_eye.r', 'endsite_eye.l', 'rear', 'lear',
]
logger = logging.getLogger('core')






def _serve_keypoints_2d_impl(job):
    """Serve per-frame 2D keypoints as JSON for the Canvas2D overlay.

    Returns {joints: [...], connections: [...], frames: [{name: [x,y,conf]}, ...]}
    with normalized (0-1) coordinates.
    """
    import csv as _csv

    output_dir = Path(settings.MEDIA_ROOT) / 'output' / str(job.id)

    body_joints = BODY_JOINT_NAMES

    connections = [
        ['head', 'neck'],
        ['neck', 'rshoulder'], ['rshoulder', 'relbow'], ['relbow', 'rhand'],
        ['neck', 'lshoulder'], ['lshoulder', 'lelbow'], ['lelbow', 'lhand'],
        ['neck', 'hip'],
        ['hip', 'rhip'], ['rhip', 'rknee'], ['rknee', 'rfoot'],
        ['hip', 'lhip'], ['lhip', 'lknee'], ['lknee', 'lfoot'],
    ]

    frames = []

    if job.pipeline == 'v4':
        csv_path = output_dir / '2dJoints_v4_raw.csv'
        if not csv_path.exists():
            csv_path = _extract_v4_keypoints(job)
    elif job.pipeline == 'openpose':
        # OpenPose: read JSON files, normalize to 0-1
        import cv2
        video_path = Path(settings.MEDIA_ROOT) / str(job.video_file)
        cap = cv2.VideoCapture(str(video_path))
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 1
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 1
        cap.release()

        json_dir = output_dir / 'openpose_json'
        if json_dir.exists():
            op_names = ['nose', 'neck', 'rshoulder', 'relbow', 'rhand',
                        'lshoulder', 'lelbow', 'lhand', 'midhip',
                        'rhip', 'rknee', 'rfoot', 'lhip', 'lknee', 'lfoot']
            for jf in sorted(json_dir.glob('*_keypoints.json')):
                with open(jf) as f:
                    data = json.load(f)
                kp = {}
                if data.get('people'):
                    pts = data['people'][0].get('pose_keypoints_2d', [])
                    for i, name in enumerate(op_names):
                        idx = i * 3
                        if idx + 2 < len(pts):
                            kp[name] = [pts[idx] / w, pts[idx+1] / h, pts[idx+2]]
                    # Map OpenPose names to our joint names
                    if 'nose' in kp:
                        kp['head'] = kp.pop('nose')
                    if 'midhip' in kp:
                        kp['hip'] = kp.pop('midhip')
                frames.append(kp)
        return JsonResponse({'joints': body_joints, 'connections': connections,
                             'frames': frames})
    elif job.pipeline in ('rtmpose', 'vitpose', 'yolo11'):
        csv_path = output_dir / f'{job.pipeline}_2d.csv'
    elif job.pipeline in ('gvhmr', 'wham', 'prompthmr', 'hybrid_gvhmr', 'hybrid_prompthmr'):
        # SMPL pipelines: prefer MediaPipe 2D detection (accurate screen positions)
        # over SMPL camera projection (which can have offset errors)
        mp_csv = output_dir / '2dJoints_v4_raw.csv'
        if not mp_csv.exists():
            try:
                mp_csv = _extract_v4_keypoints(job)
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning('MediaPipe extraction failed: %s', e)
                mp_csv = None
        if mp_csv and mp_csv.exists():
            csv_path = mp_csv
        else:
            # Fallback: pre-computed SMPL camera projection
            if job.bvh_file:
                bvh_path = Path(job.bvh_file)
                bvh_stem = bvh_path.stem
                kp2d_json = bvh_path.parent / f'{bvh_stem}_keypoints2d.json'
                if not kp2d_json.exists():
                    kp2d_json = output_dir / f'{bvh_stem}_keypoints2d.json'
                if kp2d_json.exists():
                    with open(kp2d_json) as f:
                        return JsonResponse(json.load(f))

                data = _try_generate_smpl_2d_keypoints(job, output_dir)
                if data:
                    return JsonResponse(data)

            return JsonResponse({'joints': body_joints, 'connections': connections,
                                 'frames': []})
    else:
        csv_path = output_dir / 'frames-mpdata' / '2dJoints_mediapipe.csv'

    if not csv_path or not csv_path.exists():
        return JsonResponse({'joints': body_joints, 'connections': connections,
                             'frames': []})

    with open(csv_path) as f:
        reader = _csv.DictReader(f)
        for row in reader:
            kp = {}
            for jname in body_joints:
                xk, yk, vk = f'2DX_{jname}', f'2DY_{jname}', f'visible_{jname}'
                if xk in row and row[xk]:
                    try:
                        kp[jname] = [float(row[xk]), float(row[yk]),
                                     float(row[vk]) if row.get(vk) else 0]
                    except (ValueError, KeyError):
                        logger.debug('uebergangen', exc_info=True)
            frames.append(kp)

    return JsonResponse({'joints': body_joints, 'connections': connections,
                         'frames': frames})






