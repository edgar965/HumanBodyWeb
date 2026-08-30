# -*- coding: utf-8 -*-
"""Kamera: Keyframes speichern und laden

Kamera-Spur im Speichern/Laden-Umlauf — Felder, Flaggen und alte Projekte ohne
Quaternion

Aus `camera_track_tests.py` herausgeloest (17.08.2026, Befund `dateigroesse`):
Die Datei hatte 393 Zeilen und eine Klasse mit 18 Testmethoden.
"""
from .base import TestCategory
from ._kamera_basis import Kamerabasis
from ._kameraumlauf import Kameraumlauf


class KameraKeyframeTests(TestCategory):
    name = 'Kamera: Keyframes speichern und laden'
    description = (
        'Kamera-Spur im Speichern/Laden-Umlauf — Felder, Flaggen und alte Projekte '
        'ohne Quaternion')

    # --- BVH Studio: Kamera-Track Projekt Save/Load Roundtrip ---
    @staticmethod
    def test_camera_track_project_save_api_returns_ok():
        """POST /api/studio/project-save/ mit Kamera-Track antwortet ok=true."""
        r = Kamerabasis.umlauf_ergebnis()
        return bool(r.gespeichert), 'save_code=%d' % r.speichercode

    @staticmethod
    def test_camera_track_project_load_api_returns_ok():
        """GET /api/studio/project-load/ liest den Kamera-Track zurück (ok=true)."""
        r = Kamerabasis.umlauf_ergebnis()
        return bool(r.geladen), 'load_code=%d' % r.ladecode

    @staticmethod
    def test_camera_track_survives_project_save_load_roundtrip():
        """Der Kamera-Track (type='camera') liegt nach Save→Load wieder im Projekt."""
        r = Kamerabasis.umlauf_ergebnis()
        return r.spuren == 1, 'tracks=%d' % r.spuren

    @staticmethod
    def test_camera_track_cameraactive_flag_preserved_after_load():
        """track.cameraActive=true bleibt nach Save→Load true (sonst fährt der
        Track die Viewport-Kamera während Play nicht mehr an)."""
        r = Kamerabasis.umlauf_ergebnis()
        return r.kamera_aktiv is True, 'cameraActive=%s' % (r.kamera_aktiv,)

    @staticmethod
    def test_camera_track_both_keyframes_preserved_after_load():
        """Beide Kamera-Keyframes (KF1 + KF2) überleben den Save/Load-Roundtrip."""
        r = Kamerabasis.umlauf_ergebnis()
        return r.klips == 2, 'clips=%d' % r.klips

    # --- BVH Studio: einzelne Keyframe-Felder ---
    @staticmethod
    def test_camera_keyframe_position_xyz_preserved_after_load():
        """Keyframe-data.position (x=2.0, y=1.5, z=3.0) bleibt exakt erhalten."""
        r = Kamerabasis.umlauf_ergebnis()
        pos = Kameraumlauf.feld(r.kf1, 'position', {})
        ok = (pos.get('x') == 2.0 and pos.get('y') == 1.5 and pos.get('z') == 3.0)
        return ok, f'pos={pos}'

    @staticmethod
    def test_camera_keyframe_quaternion_field_preserved_after_load():
        """Das neue Keyframe-data.quaternion-Feld (x,y,z,w) überlebt Save→Load.
        Das ist der Fix-Kern: ohne gespeicherte Quaternion musste die Playback-
        Seite Euler→Quaternion rekonstruieren und landete im falschen Hemi."""
        r = Kamerabasis.umlauf_ergebnis()
        q = Kameraumlauf.feld(r.kf1, 'quaternion')
        if not q:
            return False, 'quaternion-Feld fehlt im restored Projekt'
        ok = (abs(q.get('w', 0) - 0.956) < 1e-3
              and abs(q.get('x', 0) - 0.103) < 1e-3)
        return ok, f'q={q}'

    @staticmethod
    def test_camera_keyframe_fov_preserved_after_load():
        """Keyframe-data.fov=45 bleibt erhalten (sonst zoomt der Export falsch)."""
        r = Kamerabasis.umlauf_ergebnis()
        fov = Kameraumlauf.feld(r.kf1, 'fov')
        return fov == 45, 'fov=%s' % (fov,)

    @staticmethod
    def test_camera_keyframe_interpolation_mode_preserved_after_load():
        """Keyframe-data.interpolation='smooth' bleibt nach Save→Load erhalten."""
        r = Kamerabasis.umlauf_ergebnis()
        art = Kameraumlauf.feld(r.kf1, 'interpolation')
        return art == 'smooth', 'interp=%s' % (art,)

    @staticmethod
    def test_camera_keyframe_fade_flag_preserved_after_load():
        """Keyframe-data.fade=true bleibt nach Save→Load erhalten (steuert,
        ob der Vor-Keyframe auf diesen Keyframe interpoliert oder hart springt)."""
        r = Kamerabasis.umlauf_ergebnis()
        blende = Kameraumlauf.feld(r.kf1, 'fade')
        return blende is True, 'fade=%s' % (blende,)

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
                    'fps': 30, 'totalFrames': 0, 'trimIn': 0, 'trimOut': 0,
                    'speed': 1.0,
                    'data': {
                        'position': {'x': 1.0, 'y': 2.0, 'z': 3.0},
                        'rotation': {'x': 0.1, 'y': 0.2, 'z': 0.0},
                        'fov': 50,
                        'interpolation': 'linear', 'fade': True,
                    },
                }],
            }],
        }
        # `Kameraumlauf` statt einer dritten handgeschriebenen Runde:
        # Speichern, Laden und die Auswertung der Kamera-Spur standen hier
        # noch einmal Zeile fuer Zeile (Befund `doppelcode`, 27.08.2026).
        umlauf = Kameraumlauf.fahren(proj)
        if not umlauf.gespeichert:
            return False, 'save failed (%d)' % umlauf.speichercode
        if not umlauf.geladen:
            return False, 'load failed (%d)' % umlauf.ladecode
        if not umlauf.klips:
            return False, 'Kein Clip nach Load'
        drehung = Kameraumlauf.feld(umlauf.kf1, 'rotation', {})
        return drehung.get('y') == 0.2, 'rotation.y=%s' % (drehung.get('y'),)
