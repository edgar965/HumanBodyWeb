"""Tests für den BVH Studio Kamera-Track (Keyframe-Interpolation + Save/Load).

Die eigentliche Slerp-Logik läuft im Browser. Hier spiegeln wir das Verhalten
in Python wider (Numpy-Quaternion-Slerp ist identisch zur Three.js-Implementierung)
und verifizieren zusätzlich, dass das Projekt-Save/Load das Quaternion-Feld
durch-reicht — das war der Fix gegen die "wilden Kamera-Bewegungen" zwischen
fast identischen Keyframes.
"""
from __future__ import annotations

import tempfile
import urllib.parse
from pathlib import Path

import numpy as np

from .base import TestCategory, http_request


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


def _fx_cam_kf_roundtrip():
    global _CAM_KF_ROUNDTRIP
    if _CAM_KF_ROUNDTRIP is not None:
        return _CAM_KF_ROUNDTRIP
    proj = {
        'name': 'T', 'fps': 30,
        'tracks': [{
            'name': 'Kamera', 'type': 'camera', 'color': '#4caf50', 'muted': False,
            'position': [0, 0, 0], 'cameraActive': True,
            'clips': [
                {
                    'type': 'camera_kf', 'name': 'KF1', 'startFrame': 1,
                    'fps': 30, 'totalFrames': 0, 'trimIn': 0, 'trimOut': 0, 'speed': 1.0,
                    'data': {
                        'position': {'x': 2.0, 'y': 1.5, 'z': 3.0},
                        'rotation': {'x': -0.12, 'y': 0.55, 'z': 0.06},
                        'quaternion': {'x': 0.103, 'y': 0.275, 'z': -0.031, 'w': 0.956},
                        'fov': 45,
                        'interpolation': 'smooth', 'fade': True,
                    },
                },
                {
                    'type': 'camera_kf', 'name': 'KF2', 'startFrame': 200,
                    'fps': 30, 'totalFrames': 0, 'trimIn': 0, 'trimOut': 0, 'speed': 1.0,
                    'data': {
                        'position': {'x': 2.05, 'y': 1.51, 'z': 3.02},
                        'rotation': {'x': -0.12, 'y': 0.56, 'z': 0.06},
                        # Zweites KF: Hemisphäre gespiegelt (negiert).
                        # Der Short-Arc-Fix in applyCameraTrack darf nicht
                        # durchdrehen.
                        'quaternion': {'x': -0.104, 'y': -0.280, 'z': 0.031, 'w': -0.955},
                        'fov': 45,
                        'interpolation': 'smooth', 'fade': True,
                    },
                },
            ],
        }],
    }
    with tempfile.TemporaryDirectory() as tmpdir:
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


class CameraTrackTests(TestCategory):
    name = 'Kamera-Track'
    description = 'Keyframe Save/Load + Short-Arc Slerp (Fix gegen "wilde Kamera-Sprünge")'

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

    # --- Playback: applyCameraTrack Short-Arc Quaternion-Slerp ---
    # Der "Kamera bewegt sich wild durch die Szene"-Bug: wenn zwei Keyframes
    # fast gleiche Orientierungen haben, aber ihre Quaternionen in
    # entgegengesetzten Hemisphären liegen (q vs. -q), nimmt ein naiver Slerp
    # den Langbogen (~360°). Der Short-Arc-Fix negiert qNext wenn nötig.
    @staticmethod
    def test_camera_slerp_identical_quaternions_produce_no_drift():
        """slerp(q, q, 0.5) == q — ohne Drift bei wirklich identischen Keyframes."""
        q = np.array([0.1, 0.27, -0.03, 0.96])
        q = q / np.linalg.norm(q)
        r = _slerp_short_arc(q, q, 0.5)
        return float(abs(r @ q)) > 0.999, f'dot={r @ q:.6f}'

    @staticmethod
    def test_camera_slerp_hemisphere_flip_stays_near_original_pose():
        """Slerp zwischen q und -q (andere Hemisphäre, GLEICHE Orientierung)
        bleibt bei t=0.5 nahe der Ausgangs-Orientierung (dot≈1). Ohne
        Short-Arc würde dot durch 0 laufen = Kamera quer durch die Szene."""
        q = np.array([0.103, 0.275, -0.031, 0.956])
        q = q / np.linalg.norm(q)
        q_flipped = -q
        r_mid = _slerp_short_arc(q, q_flipped, 0.5)
        return float(abs(r_mid @ q)) > 0.999, f'dot={abs(r_mid @ q):.6f}'

    @staticmethod
    def test_camera_slerp_hemisphere_flip_w_never_crosses_zero():
        """Über 21 Slerp-Schritte zwischen q und -q darf die Quaternion-
        w-Komponente nie durch 0 laufen — sonst überschlägt sich die Kamera."""
        q = np.array([0.103, 0.275, -0.031, 0.956])
        q = q / np.linalg.norm(q)
        q_flipped = -q
        ws = []
        for t in np.linspace(0, 1, 21):
            r = _slerp_short_arc(q, q_flipped, float(t))
            ws.append(float(r[3]))
        w_min, w_max = min(ws), max(ws)
        return (w_min > 0.9 or w_max < -0.9), f'w_range=[{w_min:.3f}, {w_max:.3f}]'

    @staticmethod
    def test_camera_slerp_two_near_identical_keyframes_minimal_motion():
        """Zwei fast identische Keyframes → Slerp-Mitte ist praktisch
        deckungsgleich mit Start-Keyframe (dot > 0.9999)."""
        q0 = np.array([0.103, 0.275, -0.031, 0.956]); q0 /= np.linalg.norm(q0)
        q1 = np.array([0.104, 0.278, -0.031, 0.955]); q1 /= np.linalg.norm(q1)
        r = _slerp_short_arc(q0, q1, 0.5)
        return float(abs(r @ q0)) > 0.9999, f'dot={abs(r @ q0):.6f}'

    # --- LookAt-Interpolation (echter Fix für "wirre Kamera durch die Szene") ---
    # Reproduziert das Symptom aus dem TechnoTriadisch-Standardprojekt:
    # KF1 bei Z=+4.41 schaut auf Body (0, 0.9, 0); KF2 bei Z=-4.33 auf der
    # anderen Seite schaut auch auf Body. Reine Quaternion-Slerp lässt die
    # Kamera während des Flugs 1-1.5m am Body vorbeischauen. Die LookAt-
    # Interpolation hält den Body mittig.
    @staticmethod
    def test_camera_lookat_interpolation_keeps_body_centered_mid_flight():
        """Linear-Lerp Position + Target + camera.lookAt(target) → Body bleibt
        während des ganzen Flugs zentriert (< 5 cm Abweichung)."""
        p0 = np.array([0.0, 1.026, 4.409])
        p1 = np.array([-0.390, 1.640, -4.330])
        tgt = np.array([0.0, 0.9, 0.0])  # Body-Center, für beide Keyframes gleich
        max_off = 0.0
        for i in range(21):
            t = i / 20.0
            ts = t * t * (3 - 2 * t)  # smoothstep
            pos = (1 - ts) * p0 + ts * p1
            target = (1 - ts) * tgt + ts * tgt  # konstant
            # Kamera-Forward = normalize(target - pos)
            fwd = target - pos
            fwd = fwd / np.linalg.norm(fwd)
            # Ray-Hit auf Body-Center: wo minimal Abstand zum Body?
            # pos + s * fwd so dass (pos + s*fwd - tgt) minimal → s = fwd . (tgt - pos)
            s = float(fwd @ (tgt - pos))
            hit = pos + s * fwd
            off = float(np.linalg.norm(hit - tgt))
            if off > max_off:
                max_off = off
        # Bei konstantem Target MUSS der Hit exakt auf dem Target landen
        return max_off < 0.05, f'max off-body = {max_off:.4f}m'

    @staticmethod
    def test_camera_quaternion_slerp_technotriadisch_misses_body_midflight():
        """Nachweis, dass der alte (nur-Quaternion) Pfad für die TechnoTriadisch-
        Keyframes tatsächlich am Body vorbeischaut — das ist der Bug, den der
        Fix löst. Max off-body muss deutlich > 1 m sein."""
        # Exakte Keyframes aus HumanBody/data/studio_projects/TechnoTriadisch.studio.json
        def euler_to_quat_xyz(x, y, z):
            cx, sx = np.cos(x/2), np.sin(x/2)
            cy, sy = np.cos(y/2), np.sin(y/2)
            cz, sz = np.cos(z/2), np.sin(z/2)
            return np.array([sx*cy*cz + cx*sy*sz, cx*sy*cz - sx*cy*sz,
                              cx*cy*sz + sx*sy*cz, cx*cy*cz - sx*sy*sz])
        def rot_vec(v, q):
            qx, qy, qz, qw = q; vx, vy, vz = v
            tx = 2*(qy*vz - qz*vy); ty = 2*(qz*vx - qx*vz); tz = 2*(qx*vy - qy*vx)
            return np.array([vx + qw*tx + (qy*tz - qz*ty),
                              vy + qw*ty + (qz*tx - qx*tz),
                              vz + qw*tz + (qx*ty - qy*tx)])
        p0 = np.array([0.0, 1.025963224463083, 4.408712856207886])
        p1 = np.array([-0.38974433511480794, 1.6402570735046442, -4.330442771909365])
        q0 = euler_to_quat_xyz(-0.02856365783876011, 0, 0)
        q1 = euler_to_quat_xyz(-2.972286531734437, -0.08848255376502909, -3.126488094940674)
        tgt = np.array([0.0, 0.9, 0.0])
        max_off = 0.0
        for i in range(21):
            t = i / 20.0
            ts = t * t * (3 - 2 * t)
            pos = (1 - ts) * p0 + ts * p1
            q = _slerp_short_arc(q0, q1, ts)
            q = q / np.linalg.norm(q)
            fwd = rot_vec(np.array([0, 0, -1]), q)
            s = float(fwd @ (tgt - pos))
            hit = pos + s * fwd
            off = float(np.linalg.norm(hit - tgt))
            if off > max_off:
                max_off = off
        # Muss > 1 m sein, sonst ist der "alte Fix" bereits gut und LookAt wäre überflüssig.
        return max_off > 1.0, f'max off-body (Quat-only-Slerp) = {max_off:.3f}m — bestätigt den Bug'

    @staticmethod
    def test_camera_lookat_kf_survives_project_save_load_roundtrip():
        """Das neue lookAt-Feld im Keyframe wird vom /project-save/ und
        /project-load/ API-Paar komplett durchgereicht."""
        proj = {
            'name': 'T', 'fps': 30, 'tracks': [{
                'name': 'Kamera', 'type': 'camera', 'cameraActive': True, 'muted': False,
                'clips': [{
                    'type': 'camera_kf', 'name': 'KF', 'startFrame': 1,
                    'fps': 30, 'totalFrames': 0, 'trimIn': 0, 'trimOut': 0, 'speed': 1.0,
                    'data': {
                        'position': {'x': 0, 'y': 1.03, 'z': 4.41},
                        'rotation': {'x': -0.03, 'y': 0, 'z': 0},
                        'lookAt': {'x': 0, 'y': 0.9, 'z': 0},
                        'fov': 35, 'interpolation': 'smooth', 'fade': True,
                    },
                }],
            }],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / 'lookat.json'
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
        clips = tracks[0].get('clips', []) if tracks else []
        la = clips[0].get('data', {}).get('lookAt') if clips else None
        if not la:
            return False, f'lookAt fehlt nach Load: {clips[0].get("data") if clips else None}'
        ok = (la.get('x') == 0 and la.get('y') == 0.9 and la.get('z') == 0)
        return ok, f'lookAt={la}'

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
        with tempfile.TemporaryDirectory() as tmpdir:
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
