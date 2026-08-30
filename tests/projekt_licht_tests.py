# -*- coding: utf-8 -*-
"""Projekt: Licht-Roundtrip

Speichern/Laden von Lichtspuren: Eigenschaften, Keyframes, Szenen-Overrides

Aus `project_tests.py` herausgeloest (17.08.2026, Befund `dateigroesse`):
Die Datei hatte 426 Zeilen und eine Klasse mit 36 Testmethoden.
"""
from .base import TestCategory
from ._projekt_basis import Projektvorlagen


class ProjektLichtTests(TestCategory):
    name = 'Projekt: Licht-Roundtrip'
    description = (
        'Speichern/Laden von Lichtspuren: Eigenschaften, Keyframes, Szenen-Overrides')

    @staticmethod
    def _lichtspuren(antwort):
        """Die Lichtspuren aus einer geladenen Projektantwort.

        Stand am 30.08.2026 zehnmal wortgleich in dieser Datei — vier davon
        meldete `doppelcode` als Block. Wer die Antwortform aendert, aendert
        sie jetzt an einer Stelle.
        """
        spuren = antwort.get('project', {}).get('tracks', [])
        return [s for s in spuren if s.get('type') == 'light']

    # --- Save/Load Mechanik ---
    @staticmethod
    def test_save_http_200():
        """POST /api/studio/project-save/ → HTTP 200"""
        r = Projektvorlagen.licht()
        if r.get('_save_code') != 200:
            return False, f'HTTP {r.get("_save_code")}'
        return True, 'OK'

    @staticmethod
    def test_save_ok_flag():
        """Save response enthält ok=true"""
        r = Projektvorlagen.licht()
        return (
            bool(r.get('_save_ok')), 'ok-Flag OK' if r.get('_save_ok') else 'ok=false')

    @staticmethod
    def test_save_file_exists():
        """Gespeicherte Datei existiert im Dateisystem"""
        r = Projektvorlagen.licht()
        return (
            bool(r.get('_file_exists')),
            'Datei existiert' if r.get('_file_exists') else 'fehlt')

    @staticmethod
    def test_load_http_200():
        """GET /api/studio/project-load/ → HTTP 200"""
        r = Projektvorlagen.licht()
        if r.get('_load_code') != 200:
            return False, f'HTTP {r.get("_load_code")}'
        return True, 'OK'

    @staticmethod
    def test_load_ok_flag():
        """Load response enthält ok=true"""
        r = Projektvorlagen.licht()
        return bool(r.get('_load_ok')), ''

    # --- User-Licht-Properties Roundtrip ---
    @staticmethod
    def test_user_light_track_count():
        """Genau 1 Licht-Track im restored Projekt"""
        r = Projektvorlagen.licht()
        tracks = [t for t in r.get('project', {}).get('tracks',
                                                      []) if t.get('type') == 'light']
        return len(tracks) == 1, f'{len(tracks)} Tracks (erwartet: 1)'

    @staticmethod
    def test_user_light_color_preserved():
        """lightColor: '#ff00ff' bleibt erhalten"""
        r = Projektvorlagen.licht()
        tracks = ProjektLichtTests._lichtspuren(r)
        if not tracks:
            return False, 'Kein Track'
        return (
            tracks[0].get('lightColor') == '#ff00ff',
            f'got {tracks[0].get("lightColor")}')

    @staticmethod
    def test_user_light_intensity_preserved():
        """lightIntensity: 7.5 bleibt erhalten"""
        r = Projektvorlagen.licht()
        tracks = ProjektLichtTests._lichtspuren(r)
        if not tracks:
            return False, 'Kein Track'
        return (
            tracks[0].get('lightIntensity') == 7.5,
            f'got {tracks[0].get("lightIntensity")}')

    @staticmethod
    def test_user_light_position_x():
        """lightPosition.x: 1.5 erhalten"""
        r = Projektvorlagen.licht()
        tracks = ProjektLichtTests._lichtspuren(r)
        if not tracks:
            return False, 'Kein Track'
        x = tracks[0].get('lightPosition', {}).get('x')
        return x == 1.5, f'got {x}'

    @staticmethod
    def test_user_light_position_y():
        """lightPosition.y: 3.5 erhalten"""
        r = Projektvorlagen.licht()
        tracks = ProjektLichtTests._lichtspuren(r)
        if not tracks:
            return False, 'Kein Track'
        y = tracks[0].get('lightPosition', {}).get('y')
        return y == 3.5, f'got {y}'

    @staticmethod
    def test_user_light_position_z():
        """lightPosition.z: 2.5 erhalten"""
        r = Projektvorlagen.licht()
        tracks = ProjektLichtTests._lichtspuren(r)
        if not tracks:
            return False, 'Kein Track'
        z = tracks[0].get('lightPosition', {}).get('z')
        return z == 2.5, f'got {z}'

    @staticmethod
    def test_user_light_target_preserved():
        """lightTarget als Objekt erhalten"""
        r = Projektvorlagen.licht()
        tracks = ProjektLichtTests._lichtspuren(r)
        if not tracks:
            return False, 'Kein Track'
        tgt = tracks[0].get('lightTarget')
        return isinstance(tgt, dict) and tgt.get('y') == 1, 'target OK'

    @staticmethod
    def test_user_light_angle_preserved():
        """lightAngle: 0.7854 (45°) erhalten"""
        r = Projektvorlagen.licht()
        tracks = ProjektLichtTests._lichtspuren(r)
        if not tracks:
            return False, 'Kein Track'
        a = tracks[0].get('lightAngle', 0)
        return abs(a - 0.7854) < 0.001, f'got {a}'

    @staticmethod
    def test_user_light_penumbra_preserved():
        """lightPenumbra: 0.42 erhalten"""
        r = Projektvorlagen.licht()
        tracks = ProjektLichtTests._lichtspuren(r)
        if not tracks:
            return False, 'Kein Track'
        return (
            tracks[0].get('lightPenumbra') == 0.42,
            f'got {tracks[0].get("lightPenumbra")}')

    @staticmethod
    def test_user_light_distance_preserved():
        """lightDistance: 30.0 erhalten"""
        r = Projektvorlagen.licht()
        tracks = ProjektLichtTests._lichtspuren(r)
        if not tracks:
            return False, 'Kein Track'
        return (
            tracks[0].get('lightDistance') == 30.0,
            f'got {tracks[0].get("lightDistance")}')

    @staticmethod
    def test_user_light_type_preserved():
        """lightType='spot' erhalten"""
        r = Projektvorlagen.licht()
        tracks = ProjektLichtTests._lichtspuren(r)
        if not tracks:
            return False, 'Kein Track'
        return tracks[0].get('lightType') == 'spot', f'got {tracks[0].get("lightType")}'

    # --- Licht-Keyframe Roundtrip ---
    @staticmethod
    def test_light_kf_count():
        """1 Licht-Keyframe im restored Track"""
        r = Projektvorlagen.licht()
        tracks = ProjektLichtTests._lichtspuren(r)
        if not tracks:
            return False, 'Kein Track'
        kfs = [c for c in tracks[0].get('clips', []) if c.get('type') == 'light_kf']
        return len(kfs) == 1, f'{len(kfs)} KFs'

    @staticmethod
    def test_light_kf_intensity():
        """Keyframe intensity: 12.0 erhalten"""
        r = Projektvorlagen.licht()
        tracks = [t for t in r.get('project', {}).get('tracks',
                                                      []) if t.get('type') == 'light']
        if not tracks or not tracks[0].get('clips'):
            return False, 'Kein KF'
        return tracks[0]['clips'][0].get('data', {}).get('intensity') == 12.0, ''

    @staticmethod
    def test_light_kf_fade_false():
        """Keyframe fade=false erhalten"""
        r = Projektvorlagen.licht()
        tracks = [t for t in r.get('project', {}).get('tracks',
                                                      []) if t.get('type') == 'light']
        if not tracks or not tracks[0].get('clips'):
            return False, 'Kein KF'
        return tracks[0]['clips'][0].get('data', {}).get('fade') is False, ''

    @staticmethod
    def test_light_kf_angle():
        """Keyframe angle: 0.5236 (30°) erhalten"""
        r = Projektvorlagen.licht()
        tracks = [t for t in r.get('project', {}).get('tracks',
                                                      []) if t.get('type') == 'light']
        if not tracks or not tracks[0].get('clips'):
            return False, 'Kein KF'
        a = tracks[0]['clips'][0].get('data', {}).get('angle', 0)
        return abs(a - 0.5236) < 0.001, f'got {a}'
