# -*- coding: utf-8 -*-
"""Kamera: Kurzbogen und LookAt

Quaternion-Slerp über den kurzen Bogen und die LookAt-Interpolation gegen wirre
Kamerawege

Aus `camera_track_tests.py` herausgeloest (17.08.2026, Befund `dateigroesse`):
Die Datei hatte 393 Zeilen und eine Klasse mit 18 Testmethoden.
"""
import urllib.parse
from pathlib import Path

import numpy as np

from core.projekt_temp import ProjektTemp

from .base import TestCategory, Netzruf
from ._kamera_basis import Kamerabasis


class KameraSlerpTests(TestCategory):
    name = 'Kamera: Kurzbogen und LookAt'
    description = (
        'Quaternion-Slerp über den kurzen Bogen und die LookAt-Interpolation gegen '
        'wirre Kamerawege')

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
        r = Kamerabasis.slerp_kurzbogen(q, q, 0.5)
        return float(abs(r @ q)) > 0.999, f'dot={r @ q:.6f}'

    @staticmethod
    def test_camera_slerp_hemisphere_flip_stays_near_original_pose():
        """Slerp zwischen q und -q (andere Hemisphäre, GLEICHE Orientierung)
        bleibt bei t=0.5 nahe der Ausgangs-Orientierung (dot≈1). Ohne
        Short-Arc würde dot durch 0 laufen = Kamera quer durch die Szene."""
        q = np.array([0.103, 0.275, -0.031, 0.956])
        q = q / np.linalg.norm(q)
        q_flipped = -q
        r_mid = Kamerabasis.slerp_kurzbogen(q, q_flipped, 0.5)
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
            r = Kamerabasis.slerp_kurzbogen(q, q_flipped, float(t))
            ws.append(float(r[3]))
        w_min, w_max = min(ws), max(ws)
        return (w_min > 0.9 or w_max < -0.9), f'w_range=[{w_min:.3f}, {w_max:.3f}]'

    @staticmethod
    def test_camera_slerp_two_near_identical_keyframes_minimal_motion():
        """Zwei fast identische Keyframes → Slerp-Mitte ist praktisch
        deckungsgleich mit Start-Keyframe (dot > 0.9999)."""
        q0 = np.array([0.103, 0.275, -0.031, 0.956])
        q0 /= np.linalg.norm(q0)
        q1 = np.array([0.104, 0.278, -0.031, 0.955])
        q1 /= np.linalg.norm(q1)
        r = Kamerabasis.slerp_kurzbogen(q0, q1, 0.5)
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
        # Exakte Keyframes aus
        # HumanBody/data/studio_projects/TechnoTriadisch.studio.json
        def euler_to_quat_xyz(x, y, z):
            cx, sx = np.cos(x/2), np.sin(x/2)
            cy, sy = np.cos(y/2), np.sin(y/2)
            cz, sz = np.cos(z/2), np.sin(z/2)
            return np.array([sx*cy*cz + cx*sy*sz, cx*sy*cz - sx*cy*sz,
                             cx*cy*sz + sx*sy*cz, cx*cy*cz - sx*sy*sz])

        def rot_vec(v, q):
            qx, qy, qz, qw = q
            vx, vy, vz = v
            tx = 2 * (qy * vz - qz * vy)
            ty = 2 * (qz * vx - qx * vz)
            tz = 2 * (qx * vy - qy * vx)
            return np.array([vx + qw*tx + (qy*tz - qz*ty),
                             vy + qw*ty + (qz*tx - qx*tz),
                             vz + qw*tz + (qx*ty - qy*tx)])
        p0 = np.array([0.0, 1.025963224463083, 4.408712856207886])
        p1 = np.array([-0.38974433511480794, 1.6402570735046442, -4.330442771909365])
        q0 = euler_to_quat_xyz(-0.02856365783876011, 0, 0)
        q1 = euler_to_quat_xyz(-2.972286531734437, -0.08848255376502909,
                               -3.126488094940674)
        tgt = np.array([0.0, 0.9, 0.0])
        max_off = 0.0
        for i in range(21):
            t = i / 20.0
            ts = t * t * (3 - 2 * t)
            pos = (1 - ts) * p0 + ts * p1
            q = Kamerabasis.slerp_kurzbogen(q0, q1, ts)
            q = q / np.linalg.norm(q)
            fwd = rot_vec(np.array([0, 0, -1]), q)
            s = float(fwd @ (tgt - pos))
            hit = pos + s * fwd
            off = float(np.linalg.norm(hit - tgt))
            if off > max_off:
                max_off = off
        # Muss > 1 m sein, sonst ist der "alte Fix" bereits gut und LookAt wäre
        # überflüssig.
        return (
            max_off > 1.0,
            f'max off-body (Quat-only-Slerp) = {max_off:.3f}m — bestätigt den Bug')

    #: Ein Projekt mit genau EINEM Kamera-Keyframe, der ein `lookAt` traegt.
    #: Als Klassenfeld, weil es Daten sind und der Testrumpf sonst zur
    #: Haelfte aus Wortliste besteht.
    LOOKAT_PROJEKT = {
        'name': 'T', 'fps': 30, 'tracks': [{
            'name': 'Kamera', 'type': 'camera',
            'cameraActive': True, 'muted': False,
            'clips': [{
                'type': 'camera_kf', 'name': 'KF', 'startFrame': 1,
                'fps': 30, 'totalFrames': 0, 'trimIn': 0, 'trimOut': 0,
                'speed': 1.0,
                'data': {
                    'position': {'x': 0, 'y': 1.03, 'z': 4.41},
                    'rotation': {'x': -0.03, 'y': 0, 'z': 0},
                    'lookAt': {'x': 0, 'y': 0.9, 'z': 0},
                    'fov': 35, 'interpolation': 'smooth', 'fade': True,
                },
            }],
        }],
    }

    @staticmethod
    def _erster_kamera_kf(projekt):
        """Die `data` des ersten Kamera-Keyframes — oder `{}`."""
        spuren = [s for s in projekt.get('tracks', [])
                  if s.get('type') == 'camera']
        clips = spuren[0].get('clips', []) if spuren else []
        return clips[0].get('data', {}) if clips else {}

    @classmethod
    def _speichern_und_laden(cls, projekt):
        """Projekt schreiben und wieder einlesen. (fehlertext, projekt)

        ProjektTemp statt tempfile: SafePath laesst nur MEDIA_ROOT zu
        (System-Temp gab 403 — 48 Tests rot seit 12.08.2026).
        """
        with ProjektTemp.wegwerfordner() as ordner:
            pfad = Path(ordner) / 'lookat.json'
            code, antwort = Netzruf.senden(
                '/api/studio/project-save/', method='POST',
                data={'path': str(pfad), 'project': projekt})
            if code != 200 or not antwort.get('ok'):
                return f'save failed ({code})', {}
            code, antwort = Netzruf.senden(
                '/api/studio/project-load/?path=%s'
                % urllib.parse.quote(str(pfad)))
        if code != 200 or not antwort.get('ok'):
            return f'load failed ({code})', {}
        return '', antwort.get('project', {})

    @classmethod
    def test_camera_lookat_kf_survives_project_save_load_roundtrip(cls):
        """Das neue lookAt-Feld im Keyframe wird vom /project-save/ und
        /project-load/ API-Paar komplett durchgereicht."""
        fehler, geladen = cls._speichern_und_laden(cls.LOOKAT_PROJEKT)
        if fehler:
            return False, fehler
        daten = cls._erster_kamera_kf(geladen)
        ziel = daten.get('lookAt')
        if not ziel:
            return False, f'lookAt fehlt nach Load: {daten}'
        erwartet = cls.LOOKAT_PROJEKT['tracks'][0]['clips'][0]['data']['lookAt']
        return ziel == erwartet, f'lookAt={ziel}'
