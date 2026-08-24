# -*- coding: utf-8 -*-
"""Beiwerk der Kamera-Tests: Kurzbogen-Slerp und der Speichern-Laden-Umlauf.

Fuehrender Unterstrich mit Absicht: `testaufbau` erkennt daran, dass das keine
Testdatei ist. Aus `camera_track_tests.py` herausgeloest (17.08.2026, 393 Zeilen).

`_slerp_short_arc` ist die PRUEFFASSUNG der Rechnung, die im Browser in
`playback.js` steht: Sie dreht das Ziel-Quaternion um, wenn das Skalarprodukt
negativ ist — sonst nimmt die Kamera den langen Weg um die Kugel („wilde
Spruenge"). Die Tests dazu stehen in `kamera_slerp_tests.py`.
"""

from __future__ import annotations

import urllib.parse
from pathlib import Path

import numpy as np

from core.projekt_temp import ProjektTemp

from .base import http_request


# ---------------------------------------------------------------------------
# Pure-Python Short-Arc Slerp: identische Semantik zum Browser-Fix
# ---------------------------------------------------------------------------
def _slerp_short_arc(q0, q1, t):
    q0 = np.asarray(q0, dtype=np.float64)
    q1 = np.asarray(q1, dtype=np.float64)
    if q0 @ q1 < 0:
        q1 = -q1
    dot = float(np.clip(q0 @ q1, -1.0, 1.0))
    if dot > 0.9995:
        # Degenerate → linear lerp
        q = (1 - t) * q0 + t * q1
        return q / np.linalg.norm(q)
    omega = np.arccos(dot)
    s0 = np.sin((1 - t) * omega) / np.sin(omega)
    s1 = np.sin(t * omega) / np.sin(omega)
    return s0 * q0 + s1 * q1


# ---------------------------------------------------------------------------
# Save/Load Roundtrip Fixture: Kamera-Track mit zwei Keyframes (inkl. Quaternion)
# ---------------------------------------------------------------------------
_CAM_KF_ROUNDTRIP = None


def _kamera_kf_projekt():
    """Das Studio-Projekt der Roundtrip-Pruefung — zwei Kamera-Keyframes.

    Als eigene Funktion, weil es reine DATEN sind: Der Ablauf darunter
    (speichern, laden, vergleichen) ist die Pruefung, das hier ist ihr Aufbau.

    Der Kniff steckt im zweiten Keyframe: Sein Quaternion ist auf der
    GESPIEGELTEN Hemisphaere (alle Vorzeichen umgedreht). Mathematisch ist das
    dieselbe Drehung; ein Slerp ohne Short-Arc-Korrektur dreht die Kamera
    trotzdem einmal fast ganz herum. Genau das soll die Pruefung sehen.
    """
    # Dictionary gewollt: geht unveraendert als JSON an /api/studio/project-save/.
    return {
        'name': 'T', 'fps': 30,
        'tracks': [{
            'name': 'Kamera', 'type': 'camera', 'color': '#4caf50',
            'muted': False, 'position': [0, 0, 0], 'cameraActive': True,
            'clips': [
                _kamera_kf(1, {'x': 2.0, 'y': 1.5, 'z': 3.0},
                           {'x': -0.12, 'y': 0.55, 'z': 0.06},
                           {'x': 0.103, 'y': 0.275, 'z': -0.031, 'w': 0.956},
                           'KF1'),
                _kamera_kf(200, {'x': 2.05, 'y': 1.51, 'z': 3.02},
                           {'x': -0.12, 'y': 0.56, 'z': 0.06},
                           {'x': -0.104, 'y': -0.280, 'z': 0.031, 'w': -0.955},
                           'KF2'),
            ],
        }],
    }


def _kamera_kf(bild, position, drehung, quaternion, name):
    """Ein Kamera-Keyframe-Clip in der Form, die das Studio speichert."""
    return {
        'type': 'camera_kf', 'name': name, 'startFrame': bild,
        'fps': 30, 'totalFrames': 0, 'trimIn': 0, 'trimOut': 0, 'speed': 1.0,
        'data': {
            'position': position, 'rotation': drehung,
            'quaternion': quaternion, 'fov': 45,
            'interpolation': 'smooth', 'fade': True,
        },
    }


def _fx_cam_kf_roundtrip():
    global _CAM_KF_ROUNDTRIP
    if _CAM_KF_ROUNDTRIP is not None:
        return _CAM_KF_ROUNDTRIP
    proj = _kamera_kf_projekt()
    # ProjektTemp statt tempfile: SafePath laesst nur MEDIA_ROOT zu
    # (System-Temp gab 403 — 48 Tests rot seit 12.08.2026).
    with ProjektTemp.wegwerfordner() as tmpdir:
        path = Path(tmpdir) / 'cam_proj.studio.json'
        code_s, saved = http_request('/api/studio/project-save/', method='POST',
                                      data={'path': str(path), 'project': proj})
        if code_s != 200 or not saved.get('ok'):
            _CAM_KF_ROUNDTRIP = {'_save_code': code_s, '_save_ok': False}
            return _CAM_KF_ROUNDTRIP
        code_l, loaded = http_request(f'/api/studio/project-load/?path={urllib.parse.quote(str(path))}')
    if code_l != 200 or not loaded.get('ok'):
        _CAM_KF_ROUNDTRIP = {'_save_ok': True, '_load_code': code_l, '_load_ok': False}
        return _CAM_KF_ROUNDTRIP
    project = loaded.get('project', {})
    tracks = [t for t in project.get('tracks', []) if t.get('type') == 'camera']
    clips = tracks[0].get('clips', []) if tracks else []
    _CAM_KF_ROUNDTRIP = {
        '_save_ok': True, '_load_ok': True,
        'track_count': len(tracks),
        'clip_count': len(clips),
        'kf1': clips[0] if len(clips) > 0 else None,
        'kf2': clips[1] if len(clips) > 1 else None,
        'cameraActive': tracks[0].get('cameraActive') if tracks else None,
    }
    return _CAM_KF_ROUNDTRIP
