# -*- coding: utf-8 -*-
"""Skelett in ein Video zeichnen.

Herausgeloest aus core/views.py (Umbau 15.08.2026). Die Datei hatte 3.496 Zeilen
und 43 Endpunkte, dazwischen die Pipeline-Laeufe mit bis zu 304 Zeilen je
Funktion. Getrennt wird nach Aufgabe: Endpunkte in core/api/, Fachlogik in
core/dienste/, die Laeufe in core/pipelines/.
"""

from .keypoints_quellen import _get_2d_keypoints
from .bvh_projektion import _parse_bvh_to_2d
from django.conf import settings
from pathlib import Path
import os


_BODY_CONNECTIONS = [
    ('neck', 'rshoulder'), ('rshoulder', 'relbow'), ('relbow', 'rhand'),
    ('neck', 'lshoulder'), ('lshoulder', 'lelbow'), ('lelbow', 'lhand'),
    ('neck', 'midhip'), ('neck', 'hip'),  # OpenPose uses midhip, MediaPipe/MocapNET uses hip
    ('midhip', 'rhip'), ('hip', 'rhip'),
    ('rhip', 'rknee'), ('rknee', 'rfoot'),
    ('midhip', 'lhip'), ('hip', 'lhip'),
    ('lhip', 'lknee'), ('lknee', 'lfoot'),
    ('nose', 'neck'), ('head', 'neck'),  # OpenPose: nose, MocapNET: head
    ('nose', 'reye'), ('nose', 'leye'),
    ('reye', 'rear'), ('leye', 'lear'),
    # MocapNET eye/ear names (for RTMPose/ViTPose/YOLO CSV)
    ('head', 'endsite_eye.r'), ('head', 'endsite_eye.l'),
    ('endsite_eye.r', 'rear'), ('endsite_eye.l', 'lear'),
]


def _draw_skeleton(frame, keypoints, connections=None, color=(0, 255, 0),
                   thickness=2):
    """Draw skeleton on a frame using 2D keypoints."""
    import cv2
    h, w = frame.shape[:2]
    min_conf = 0.3

    if connections is None:
        connections = _BODY_CONNECTIONS

    # Draw connections
    for j1, j2 in connections:
        p1 = keypoints.get(j1)
        p2 = keypoints.get(j2)
        if p1 and p2 and p1[2] > min_conf and p2[2] > min_conf:
            pt1 = (int(p1[0]), int(p1[1]))
            pt2 = (int(p2[0]), int(p2[1]))
            if 0 <= pt1[0] < w and 0 <= pt1[1] < h and 0 <= pt2[0] < w and 0 <= pt2[1] < h:
                cv2.line(frame, pt1, pt2, color, thickness, cv2.LINE_AA)

    # Draw joints
    for name, (x, y, conf) in keypoints.items():
        if conf > min_conf and 0 <= x < w and 0 <= y < h:
            cv2.circle(frame, (int(x), int(y)), 3, (0, 200, 255), -1, cv2.LINE_AA)

    return frame


def _render_video_with_skeleton(job, overlay=True):
    """Render a video with skeleton overlay (or skeleton-only on black bg).

    For v4: uses BVH 3D skeleton projected to 2D (full MocapNET v4 rig).
    For v2.1: uses 2D MediaPipe/OpenPose keypoints.

    Returns path to the rendered mp4 file (cached in output dir).
    """
    import cv2
    import numpy as np

    # BVH reprojection only for rig-only mode (black bg) — for overlay
    # we need the original 2D keypoints so they match the video camera
    use_bvh = (not overlay and job.pipeline == 'v4' and job.bvh_file
               and os.path.exists(job.bvh_file))
    suffix = '_overlay' if overlay else '_rig_only'
    if use_bvh:
        suffix += '_bvh'
    stem = Path(job.name).stem
    prefix = job.pipeline
    output_dir = Path(settings.MEDIA_ROOT) / 'output' / str(job.id)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f'{prefix}_{stem}{suffix}.mp4'

    if out_path.exists():
        return out_path

    # Get video dimensions
    video_path = Path(settings.MEDIA_ROOT) / str(job.video_file)
    cap_probe = cv2.VideoCapture(str(video_path))
    w = int(cap_probe.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap_probe.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap_probe.release()

    connections = _BODY_CONNECTIONS
    keypoints_list = None

    # Rig-only for v4: parse BVH and project 3D skeleton to 2D
    if use_bvh:
        try:
            keypoints_list, bvh_conns = _parse_bvh_to_2d(job.bvh_file, w, h)
            if keypoints_list and bvh_conns:
                connections = bvh_conns
        except Exception:
            keypoints_list = None

    # 2D keypoints: always for overlay, fallback for rig-only
    if not keypoints_list:
        result = _get_2d_keypoints(job)
        keypoints_list, (w, h) = result
        connections = _BODY_CONNECTIONS

    if not keypoints_list:
        return None

    cap = cv2.VideoCapture(str(video_path))
    video_fps = cap.get(cv2.CAP_PROP_FPS) or (job.fps or 30)
    total_video_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if not overlay:
        cap.release()
        cap = None

    fps = job.fps or 30
    n_bvh = len(keypoints_list)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(out_path), fourcc, video_fps, (w, h))

    # Proportional mapping: video frame i → BVH frame
    # Matches Three.js: (currentTime / duration) * clipDuration
    for vi in range(total_video_frames):
        if overlay and cap:
            ret, frame = cap.read()
            if not ret:
                frame = np.zeros((h, w, 3), dtype=np.uint8)
        else:
            frame = np.zeros((h, w, 3), dtype=np.uint8)

        # Map video frame to BVH frame proportionally
        if total_video_frames > 1:
            bvh_idx = int(vi / (total_video_frames - 1) * (n_bvh - 1))
        else:
            bvh_idx = 0
        bvh_idx = max(0, min(bvh_idx, n_bvh - 1))
        kp = keypoints_list[bvh_idx]

        color = (0, 255, 0) if overlay else (255, 255, 255)
        _draw_skeleton(frame, kp, connections=connections, color=color,
                       thickness=3)
        writer.write(frame)

    writer.release()
    if cap:
        cap.release()

    return out_path
