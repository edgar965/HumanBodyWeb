# -*- coding: utf-8 -*-
"""2D-Keypoints aus den verschiedenen Pipeline-Ausgaben lesen.

Aus core/dienste/keypoints.py herausgeloest (Umbau 16.08.2026).
"""

from django.conf import settings
from pathlib import Path
import json


BODY_JOINT_NAMES = [
    'head', 'neck', 'rshoulder', 'relbow', 'rhand',
    'lshoulder', 'lelbow', 'lhand', 'hip',
    'rhip', 'rknee', 'rfoot', 'lhip', 'lknee', 'lfoot',
    'endsite_eye.r', 'endsite_eye.l', 'rear', 'lear',
]
import logging

logger = logging.getLogger('core')


def _try_generate_smpl_2d_keypoints(job, output_dir):
    """Try to retroactively generate 2D keypoints from GVHMR hmr4d_results.pt.

    Returns the keypoints dict if successful, None otherwise.
    Caches the result as _keypoints2d.json for future requests.
    """
    try:
        import sys as _sys
        video_stem = Path(job.video_file.name).stem
        pt_path = output_dir / video_stem / 'hmr4d_results.pt'
        if not pt_path.exists():
            return None

        import torch
        pred = torch.load(str(pt_path), map_location='cpu', weights_only=False)
        if 'smpl_params_incam' not in pred or 'K_fullimg' not in pred:
            return None

        video_path = str(Path(settings.MEDIA_ROOT) / str(job.video_file))
        bvh_stem = Path(job.bvh_file).stem
        kp2d_path = str(output_dir / f'{bvh_stem}_keypoints2d.json')

        # Import _save_2d_keypoints from gvhmr_lift wrapper
        wrapper_dir = str(Path(settings.BASE_DIR).parent / 'VideoToBVH' / 'wrappers')
        if wrapper_dir not in _sys.path:
            _sys.path.insert(0, wrapper_dir)
        from gvhmr_lift import _save_2d_keypoints
        _save_2d_keypoints(pred, kp2d_path, video_path)

        with open(kp2d_path) as f:
            return json.load(f)
    except Exception as e:
        import traceback
        logger.error('[serve_keypoints_2d] Retroactive SMPL 2D keypoints failed: %s', e)
        traceback.print_exc()
        return None


def _get_2d_keypoints(job):
    """Extract 2D keypoints per frame from OpenPose JSON or MediaPipe CSV.

    Returns list of dicts: [{joint_name: (x_px, y_px, conf), ...}, ...]
    and the (width, height) of the original video.
    """
    import cv2
    video_path = Path(settings.MEDIA_ROOT) / str(job.video_file)
    cap = cv2.VideoCapture(str(video_path))
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    output_dir = Path(settings.MEDIA_ROOT) / 'output' / str(job.id)
    frames = []

    if job.pipeline == 'openpose':
        json_dir = output_dir / 'openpose_json'
        if not json_dir.exists():
            return [], (w, h)
        json_files = sorted(json_dir.glob('*_keypoints.json'))
        for jf in json_files:
            with open(jf) as f:
                data = json.load(f)
            kp = {}
            if data.get('people'):
                pts = data['people'][0].get('pose_keypoints_2d', [])
                # BODY_25: 25 keypoints, each (x, y, confidence)
                names = ['nose', 'neck', 'rshoulder', 'relbow', 'rhand',
                         'lshoulder', 'lelbow', 'lhand', 'midhip',
                         'rhip', 'rknee', 'rfoot', 'lhip', 'lknee', 'lfoot',
                         'reye', 'leye', 'rear', 'lear',
                         'lbigtoe', 'lsmalltoe', 'lheel',
                         'rbigtoe', 'rsmalltoe', 'rheel']
                for i, name in enumerate(names):
                    idx = i * 3
                    if idx + 2 < len(pts):
                        kp[name] = (pts[idx], pts[idx+1], pts[idx+2])
            frames.append(kp)
    else:
        # v4 or MediaPipe CSV or new detector CSV
        if job.pipeline == 'v4':
            # 2dJoints_v4.csv has aspect-ratio-corrected values for MocapNET
            # input — not suitable for video overlay. Use raw MediaPipe coords.
            csv_path = output_dir / '2dJoints_v4_raw.csv'
            if not csv_path.exists():
                csv_path = _extract_v4_keypoints(job)
        elif job.pipeline in ('rtmpose', 'vitpose', 'yolo11'):
            # New 2D detectors write MocapNET-compatible CSV
            csv_path = output_dir / f'{job.pipeline}_2d.csv'
        else:
            csv_path = output_dir / 'frames-mpdata' / '2dJoints_mediapipe.csv'

        if not csv_path or not csv_path.exists():
            return [], (w, h)
        import csv
        with open(csv_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                kp = {}
                # Body joints from CSV header (2DX_name, 2DY_name, visible_name)
                body_joints = BODY_JOINT_NAMES
                for jname in body_joints:
                    xk, yk, vk = f'2DX_{jname}', f'2DY_{jname}', f'visible_{jname}'
                    if xk in row and row[xk]:
                        try:
                            x = float(row[xk]) * w
                            y = float(row[yk]) * h
                            v = float(row[vk]) if row.get(vk) else 0
                            kp[jname] = (x, y, v)
                        except (ValueError, KeyError):
                            logger.debug('uebergangen', exc_info=True)
                frames.append(kp)

    return frames, (w, h)


def _extract_v4_keypoints(job):
    """Re-extract raw 2D keypoints from video for v4 overlay rendering.

    Saves normalized (0-1) MediaPipe coordinates to 2dJoints_v4_raw.csv.
    (The pipeline's 2dJoints_v4.csv has aspect-ratio-corrected values for
    MocapNET input and cannot be used for direct video overlay.)
    """
    import cv2
    try:
        from mediapipe_compat import PoseCompat
    except ImportError:
        import mediapipe as mp
        PoseCompat = None

    video_path = Path(settings.MEDIA_ROOT) / str(job.video_file)
    output_dir = Path(settings.MEDIA_ROOT) / 'output' / str(job.id)
    csv_path = output_dir / '2dJoints_v4_raw.csv'

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return None

    # Use mediapipe pose
    if PoseCompat:
        pose = PoseCompat()
    else:
        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose(static_image_mode=False, model_complexity=1,
                            min_detection_confidence=0.5)

    joint_map = {
        0: 'head', 11: 'lshoulder', 12: 'rshoulder',
        13: 'lelbow', 14: 'relbow', 15: 'lhand', 16: 'rhand',
        23: 'lhip', 24: 'rhip', 25: 'lknee', 26: 'rknee',
        27: 'lfoot', 28: 'rfoot',
    }
    joint_names = sorted(set(joint_map.values()) | {'neck', 'hip'})

    rows = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if PoseCompat:
            result = pose.process(rgb)
            landmarks = result.pose_landmarks.landmark if result.pose_landmarks else None
        else:
            result = pose.process(rgb)
            landmarks = result.pose_landmarks.landmark if result.pose_landmarks else None

        row = {}
        if landmarks:
            for idx, jname in joint_map.items():
                lm = landmarks[idx]
                row[f'2DX_{jname}'] = lm.x
                row[f'2DY_{jname}'] = lm.y
                row[f'visible_{jname}'] = lm.visibility
            # Derived: neck = midpoint of shoulders
            ls, rs = landmarks[11], landmarks[12]
            row['2DX_neck'] = (ls.x + rs.x) / 2
            row['2DY_neck'] = (ls.y + rs.y) / 2
            row['visible_neck'] = min(ls.visibility, rs.visibility)
            # Derived: hip = midpoint of hips
            lh, rh = landmarks[23], landmarks[24]
            row['2DX_hip'] = (lh.x + rh.x) / 2
            row['2DY_hip'] = (lh.y + rh.y) / 2
            row['visible_hip'] = min(lh.visibility, rh.visibility)
        rows.append(row)

    cap.release()

    if not rows:
        return None

    with open(csv_path, 'w', newline='') as f:
        header_parts = ['frameNumber']
        for jn in joint_names:
            header_parts.extend([f'2DX_{jn}', f'2DY_{jn}', f'visible_{jn}'])
        f.write(','.join(header_parts) + '\n')
        for i, row in enumerate(rows):
            parts = [str(i)]
            for jn in joint_names:
                parts.extend([
                    str(row.get(f'2DX_{jn}', '')),
                    str(row.get(f'2DY_{jn}', '')),
                    str(row.get(f'visible_{jn}', '')),
                ])
            f.write(','.join(parts) + '\n')

    return csv_path
