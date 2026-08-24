# -*- coding: utf-8 -*-
"""Kamera: Keyframes speichern und laden

Kamera-Spur im Speichern/Laden-Umlauf — Felder, Flaggen und alte Projekte ohne Quaternion

Aus `camera_track_tests.py` herausgeloest (17.08.2026, Befund `dateigroesse`):
Die Datei hatte 393 Zeilen und eine Klasse mit 18 Testmethoden.
"""
import urllib.parse
from pathlib import Path

from core.projekt_temp import ProjektTemp

from .base import TestCategory, http_request
from ._kamera_basis import _fx_cam_kf_roundtrip


class KameraKeyframeTests(TestCategory):
    name = 'Kamera: Keyframes speichern und laden'
    description = 'Kamera-Spur im Speichern/Laden-Umlauf — Felder, Flaggen und alte Projekte ohne Quaternion'

    # --- BVH Studio: Kamera-Track Projekt Save/Load Roundtrip ---
    @staticmethod
    def test_camera_track_project_save_api_returns_ok():
        """POST /api/studio/project-save/ mit Kamera-Track antwortet ok=true."""
        r = _fx_cam_kf_roundtrip()
        return bool(r.get('_save_ok')), f"save_code={r.get('_save_code')}"

    @staticmethod
    def test_camera_track_project_load_api_returns_ok():
        """GET /api/studio/project-load/ liest den Kamera-Track zurück (ok=true)."""
        r = _fx_cam_kf_roundtrip()
        return bool(r.get('_load_ok')), f"load_code={r.get('_load_code')}"

    @staticmethod
    def test_camera_track_survives_project_save_load_roundtrip():
        """Der Kamera-Track (type='camera') liegt nach Save→Load wieder im Projekt."""
        r = _fx_cam_kf_roundtrip()
        return r.get('track_count') == 1, f"tracks={r.get('track_count')}"

    @staticmethod
    def test_camera_track_cameraactive_flag_preserved_after_load():
        """track.cameraActive=true bleibt nach Save→Load true (sonst fährt der
        Track die Viewport-Kamera während Play nicht mehr an)."""
        r = _fx_cam_kf_roundtrip()
        return r.get('cameraActive') is True, f"cameraActive={r.get('cameraActive')}"

    @staticmethod
    def test_camera_track_both_keyframes_preserved_after_load():
        """Beide Kamera-Keyframes (KF1 + KF2) überleben den Save/Load-Roundtrip."""
        r = _fx_cam_kf_roundtrip()
        return r.get('clip_count') == 2, f"clips={r.get('clip_count')}"

    # --- BVH Studio: einzelne Keyframe-Felder ---
    @staticmethod
    def test_camera_keyframe_position_xyz_preserved_after_load():
        """Keyframe-data.position (x=2.0, y=1.5, z=3.0) bleibt exakt erhalten."""
        r = _fx_cam_kf_roundtrip()
        kf = r.get('kf1') or {}
        pos = kf.get('data', {}).get('position', {})
        ok = (pos.get('x') == 2.0 and pos.get('y') == 1.5 and pos.get('z') == 3.0)
        return ok, f'pos={pos}'

    @staticmethod
    def test_camera_keyframe_quaternion_field_preserved_after_load():
        """Das neue Keyframe-data.quaternion-Feld (x,y,z,w) überlebt Save→Load.
        Das ist der Fix-Kern: ohne gespeicherte Quaternion musste die Playback-
        Seite Euler→Quaternion rekonstruieren und landete im falschen Hemi."""
        r = _fx_cam_kf_roundtrip()
        kf = r.get('kf1') or {}
        q = kf.get('data', {}).get('quaternion')
        if not q:
            return False, 'quaternion-Feld fehlt im restored Projekt'
        ok = (abs(q.get('w', 0) - 0.956) < 1e-3
              and abs(q.get('x', 0) - 0.103) < 1e-3)
        return ok, f'q={q}'

    @staticmethod
    def test_camera_keyframe_fov_preserved_after_load():
        """Keyframe-data.fov=45 bleibt erhalten (sonst zoomt der Export falsch)."""
        r = _fx_cam_kf_roundtrip()
        kf = r.get('kf1') or {}
        return kf.get('data', {}).get('fov') == 45, f"fov={kf.get('data', {}).get('fov')}"

    @staticmethod
    def test_camera_keyframe_interpolation_mode_preserved_after_load():
        """Keyframe-data.interpolation='smooth' bleibt nach Save→Load erhalten."""
        r = _fx_cam_kf_roundtrip()
        kf = r.get('kf1') or {}
        return kf.get('data', {}).get('interpolation') == 'smooth', \
               f"interp={kf.get('data', {}).get('interpolation')}"

    @staticmethod
    def test_camera_keyframe_fade_flag_preserved_after_load():
        """Keyframe-data.fade=true bleibt nach Save→Load erhalten (steuert,
        ob der Vor-Keyframe auf diesen Keyframe interpoliert oder hart springt)."""
        r = _fx_cam_kf_roundtrip()
        kf = r.get('kf1') or {}
        return kf.get('data', {}).get('fade') is True, \
               f"fade={kf.get('data', {}).get('fade')}"

    # --- Backwards-Compat für alte Projekte ohne Quaternion-Feld ---
    @staticmethod
    def test_camera_keyframe_legacy_project_without_quaternion_still_loads():
        """Ein Projekt ohne data.quaternion-Feld (nur rotation x/y/z)
        lädt sauber — Playback fällt auf Euler→Quaternion zurück."""
        proj = {
            'name': 'T', 'fps': 30, 'tracks': [{
                'name': 'Kamera', 'type': 'camera', 'color': '#4caf50', 'muted': False,
                'cameraActive': True,
                'clips': [{
                    'type': 'camera_kf', 'name': 'KF', 'startFrame': 1,
                    'fps': 30, 'totalFrames': 0, 'trimIn': 0, 'trimOut': 0, 'speed': 1.0,
                    'data': {
                        'position': {'x': 1.0, 'y': 2.0, 'z': 3.0},
                        'rotation': {'x': 0.1, 'y': 0.2, 'z': 0.0},
                        'fov': 50,
                        'interpolation': 'linear', 'fade': True,
                    },
                }],
            }],
        }
        # ProjektTemp statt tempfile: SafePath laesst nur MEDIA_ROOT zu
        # (System-Temp gab 403 — 48 Tests rot seit 12.08.2026).
        with ProjektTemp.wegwerfordner() as tmpdir:
            path = Path(tmpdir) / 'legacy_cam.json'
            code_s, saved = http_request('/api/studio/project-save/', method='POST',
                                          data={'path': str(path), 'project': proj})
            if code_s != 200 or not saved.get('ok'):
                return False, f'save failed ({code_s})'
            code_l, loaded = http_request(
                f'/api/studio/project-load/?path={urllib.parse.quote(str(path))}'
            )
        if code_l != 200 or not loaded.get('ok'):
            return False, f'load failed ({code_l})'
        tracks = [t for t in loaded.get('project', {}).get('tracks', []) if t.get('type') == 'camera']
        if not tracks or not tracks[0].get('clips'):
            return False, 'Kein Clip nach Load'
        data = tracks[0]['clips'][0].get('data', {})
        has_rot = data.get('rotation', {}).get('y') == 0.2
        return has_rot, f'rotation.y={data.get("rotation", {}).get("y")}'
