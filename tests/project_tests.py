"""Tests für Projekt Save/Load-Roundtrip.

Jede Assertion ist ein eigener Test (granulare Anzeige in der UI).
Helpers cachen Save/Load-Ergebnisse pro Fixture.
"""
import tempfile
import urllib.parse
from pathlib import Path
from .base import TestCategory, http_request


def _save_load(project_data):
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / 'test_project.studio.json'
        code, saved = http_request('/api/studio/project-save/', method='POST',
                                    data={'path': str(tmp_path), 'project': project_data})
        if code != 200 or not saved.get('ok'):
            return {'_save_code': code, '_save_ok': False}
        save_exists = tmp_path.is_file()
        code, loaded = http_request(f'/api/studio/project-load/?path={urllib.parse.quote(str(tmp_path))}')
        if code != 200 or not loaded.get('ok'):
            return {'_save_code': 200, '_save_ok': True, '_file_exists': save_exists,
                    '_load_code': code, '_load_ok': False}
        return {
            '_save_code': 200, '_save_ok': True, '_file_exists': save_exists,
            '_load_code': 200, '_load_ok': True,
            'project': loaded.get('project', {}),
        }


# Fixtures — einmal gebaut, in allen Tests verwendet
_LIGHT_PROPS_FIXTURE = None
_SCENE_OVERRIDES_FIXTURE = None
_DELETED_KF_FIXTURE = None
_SCENE_FLOOR_FIXTURE = None


def _fx_light_props():
    global _LIGHT_PROPS_FIXTURE
    if _LIGHT_PROPS_FIXTURE is None:
        proj = {
            'name': 'T', 'fps': 30, 'tracks': [{
                'name': 'TestSpot', 'type': 'light', 'color': '#ffc107', 'muted': False,
                'position': [0, 0, 0], 'lightColor': '#ff00ff', 'lightIntensity': 7.5,
                'lightPosition': {'x': 1.5, 'y': 3.5, 'z': 2.5},
                'lightTarget':   {'x': 0, 'y': 1, 'z': 0},
                'lightAngle': 0.7854, 'lightPenumbra': 0.42, 'lightDistance': 30.0,
                'lightVisible': True, 'lightType': 'spot',
                'clips': [{
                    'type': 'light_kf', 'name': 'KF1', 'startFrame': 60,
                    'data': {'intensity': 12.0, 'fade': False, 'angle': 0.5236, 'visible': True},
                }]
            }]
        }
        _LIGHT_PROPS_FIXTURE = _save_load(proj)
    return _LIGHT_PROPS_FIXTURE


def _fx_scene_overrides():
    global _SCENE_OVERRIDES_FIXTURE
    if _SCENE_OVERRIDES_FIXTURE is None:
        proj = {
            'name': 'T', 'fps': 30, 'tracks': [],
            'sceneLights': {
                'Key Light': {
                    'color': '#ff5733', 'intensity': 8.5,
                    'position': {'x': 1, 'y': 2, 'z': 3},
                    'visible': True, 'muted': True,
                    'clips': [
                        {'type': 'light_kf', 'name': 'Licht 1', 'startFrame': 30,
                         'data': {'intensity': 5.0, 'fade': False}}
                    ]
                },
                'Ambient': {
                    'color': '#aabbcc', 'intensity': 0.5,
                    'position': {'x': 0, 'y': 0, 'z': 0},
                    'visible': False, 'muted': False, 'clips': []
                }
            }
        }
        _SCENE_OVERRIDES_FIXTURE = _save_load(proj)
    return _SCENE_OVERRIDES_FIXTURE


def _fx_deleted_kf():
    global _DELETED_KF_FIXTURE
    if _DELETED_KF_FIXTURE is None:
        proj = {
            'name': 'T', 'fps': 30, 'tracks': [],
            'sceneLights': {
                'Key Light': {
                    'color': '#fff', 'intensity': 3.0,
                    'position': {'x': 2, 'y': 4, 'z': -5},
                    'visible': True, 'muted': False,
                    'clips': [
                        {'type': 'light_kf', 'name': 'Standard Ende', 'startFrame': 300,
                         'data': {'visible': True, 'fade': True}}
                    ]
                }
            }
        }
        _DELETED_KF_FIXTURE = _save_load(proj)
    return _DELETED_KF_FIXTURE


def _fx_scene_floor():
    global _SCENE_FLOOR_FIXTURE
    if _SCENE_FLOOR_FIXTURE is None:
        proj = {
            'name': 'T', 'fps': 30, 'tracks': [],
            'sceneFloor': {
                'color': '#8b4513', 'texture': 'none',
                'roughness': 0.7, 'metalness': 0.15, 'size': 10.0,
                'muted': False
            }
        }
        _SCENE_FLOOR_FIXTURE = _save_load(proj)
    return _SCENE_FLOOR_FIXTURE


class ProjectTests(TestCategory):
    name = 'Projekt Save/Load'
    description = 'Roundtrip von Projekten inkl. Licht-Properties, Szenen-Overrides, Boden'

    # --- Save/Load Mechanik ---
    @staticmethod
    def test_save_http_200():
        """POST /api/studio/project-save/ → HTTP 200"""
        r = _fx_light_props()
        if r.get('_save_code') != 200:
            return False, f'HTTP {r.get("_save_code")}'
        return True, 'OK'

    @staticmethod
    def test_save_ok_flag():
        """Save response enthält ok=true"""
        r = _fx_light_props()
        return bool(r.get('_save_ok')), 'ok-Flag OK' if r.get('_save_ok') else 'ok=false'

    @staticmethod
    def test_save_file_exists():
        """Gespeicherte Datei existiert im Dateisystem"""
        r = _fx_light_props()
        return bool(r.get('_file_exists')), 'Datei existiert' if r.get('_file_exists') else 'fehlt'

    @staticmethod
    def test_load_http_200():
        """GET /api/studio/project-load/ → HTTP 200"""
        r = _fx_light_props()
        if r.get('_load_code') != 200:
            return False, f'HTTP {r.get("_load_code")}'
        return True, 'OK'

    @staticmethod
    def test_load_ok_flag():
        """Load response enthält ok=true"""
        r = _fx_light_props()
        return bool(r.get('_load_ok')), ''

    # --- User-Licht-Properties Roundtrip ---
    @staticmethod
    def test_user_light_track_count():
        """Genau 1 Licht-Track im restored Projekt"""
        r = _fx_light_props()
        tracks = [t for t in r.get('project', {}).get('tracks', []) if t.get('type') == 'light']
        return len(tracks) == 1, f'{len(tracks)} Tracks (erwartet: 1)'

    @staticmethod
    def test_user_light_color_preserved():
        """lightColor: '#ff00ff' bleibt erhalten"""
        r = _fx_light_props()
        tracks = [t for t in r.get('project', {}).get('tracks', []) if t.get('type') == 'light']
        if not tracks:
            return False, 'Kein Track'
        return tracks[0].get('lightColor') == '#ff00ff', f'got {tracks[0].get("lightColor")}'

    @staticmethod
    def test_user_light_intensity_preserved():
        """lightIntensity: 7.5 bleibt erhalten"""
        r = _fx_light_props()
        tracks = [t for t in r.get('project', {}).get('tracks', []) if t.get('type') == 'light']
        if not tracks:
            return False, 'Kein Track'
        return tracks[0].get('lightIntensity') == 7.5, f'got {tracks[0].get("lightIntensity")}'

    @staticmethod
    def test_user_light_position_x():
        """lightPosition.x: 1.5 erhalten"""
        r = _fx_light_props()
        tracks = [t for t in r.get('project', {}).get('tracks', []) if t.get('type') == 'light']
        if not tracks:
            return False, 'Kein Track'
        x = tracks[0].get('lightPosition', {}).get('x')
        return x == 1.5, f'got {x}'

    @staticmethod
    def test_user_light_position_y():
        """lightPosition.y: 3.5 erhalten"""
        r = _fx_light_props()
        tracks = [t for t in r.get('project', {}).get('tracks', []) if t.get('type') == 'light']
        if not tracks:
            return False, 'Kein Track'
        y = tracks[0].get('lightPosition', {}).get('y')
        return y == 3.5, f'got {y}'

    @staticmethod
    def test_user_light_position_z():
        """lightPosition.z: 2.5 erhalten"""
        r = _fx_light_props()
        tracks = [t for t in r.get('project', {}).get('tracks', []) if t.get('type') == 'light']
        if not tracks:
            return False, 'Kein Track'
        z = tracks[0].get('lightPosition', {}).get('z')
        return z == 2.5, f'got {z}'

    @staticmethod
    def test_user_light_target_preserved():
        """lightTarget als Objekt erhalten"""
        r = _fx_light_props()
        tracks = [t for t in r.get('project', {}).get('tracks', []) if t.get('type') == 'light']
        if not tracks:
            return False, 'Kein Track'
        tgt = tracks[0].get('lightTarget')
        return isinstance(tgt, dict) and tgt.get('y') == 1, 'target OK'

    @staticmethod
    def test_user_light_angle_preserved():
        """lightAngle: 0.7854 (45°) erhalten"""
        r = _fx_light_props()
        tracks = [t for t in r.get('project', {}).get('tracks', []) if t.get('type') == 'light']
        if not tracks:
            return False, 'Kein Track'
        a = tracks[0].get('lightAngle', 0)
        return abs(a - 0.7854) < 0.001, f'got {a}'

    @staticmethod
    def test_user_light_penumbra_preserved():
        """lightPenumbra: 0.42 erhalten"""
        r = _fx_light_props()
        tracks = [t for t in r.get('project', {}).get('tracks', []) if t.get('type') == 'light']
        if not tracks:
            return False, 'Kein Track'
        return tracks[0].get('lightPenumbra') == 0.42, f'got {tracks[0].get("lightPenumbra")}'

    @staticmethod
    def test_user_light_distance_preserved():
        """lightDistance: 30.0 erhalten"""
        r = _fx_light_props()
        tracks = [t for t in r.get('project', {}).get('tracks', []) if t.get('type') == 'light']
        if not tracks:
            return False, 'Kein Track'
        return tracks[0].get('lightDistance') == 30.0, f'got {tracks[0].get("lightDistance")}'

    @staticmethod
    def test_user_light_type_preserved():
        """lightType='spot' erhalten"""
        r = _fx_light_props()
        tracks = [t for t in r.get('project', {}).get('tracks', []) if t.get('type') == 'light']
        if not tracks:
            return False, 'Kein Track'
        return tracks[0].get('lightType') == 'spot', f'got {tracks[0].get("lightType")}'

    # --- Licht-Keyframe Roundtrip ---
    @staticmethod
    def test_light_kf_count():
        """1 Licht-Keyframe im restored Track"""
        r = _fx_light_props()
        tracks = [t for t in r.get('project', {}).get('tracks', []) if t.get('type') == 'light']
        if not tracks:
            return False, 'Kein Track'
        kfs = [c for c in tracks[0].get('clips', []) if c.get('type') == 'light_kf']
        return len(kfs) == 1, f'{len(kfs)} KFs'

    @staticmethod
    def test_light_kf_intensity():
        """Keyframe intensity: 12.0 erhalten"""
        r = _fx_light_props()
        tracks = [t for t in r.get('project', {}).get('tracks', []) if t.get('type') == 'light']
        if not tracks or not tracks[0].get('clips'):
            return False, 'Kein KF'
        return tracks[0]['clips'][0].get('data', {}).get('intensity') == 12.0, ''

    @staticmethod
    def test_light_kf_fade_false():
        """Keyframe fade=false erhalten"""
        r = _fx_light_props()
        tracks = [t for t in r.get('project', {}).get('tracks', []) if t.get('type') == 'light']
        if not tracks or not tracks[0].get('clips'):
            return False, 'Kein KF'
        return tracks[0]['clips'][0].get('data', {}).get('fade') is False, ''

    @staticmethod
    def test_light_kf_angle():
        """Keyframe angle: 0.5236 (30°) erhalten"""
        r = _fx_light_props()
        tracks = [t for t in r.get('project', {}).get('tracks', []) if t.get('type') == 'light']
        if not tracks or not tracks[0].get('clips'):
            return False, 'Kein KF'
        a = tracks[0]['clips'][0].get('data', {}).get('angle', 0)
        return abs(a - 0.5236) < 0.001, f'got {a}'

    # --- Scene Light Overrides ---
    @staticmethod
    def test_scene_light_key_exists():
        """sceneLights.Key Light existiert nach Load"""
        r = _fx_scene_overrides()
        sl = r.get('project', {}).get('sceneLights', {})
        return 'Key Light' in sl, 'Keys: ' + ', '.join(sl.keys())

    @staticmethod
    def test_scene_light_key_color():
        """Key Light Farbe: '#ff5733' erhalten"""
        r = _fx_scene_overrides()
        kl = r.get('project', {}).get('sceneLights', {}).get('Key Light', {})
        return kl.get('color') == '#ff5733', f'got {kl.get("color")}'

    @staticmethod
    def test_scene_light_key_intensity():
        """Key Light Intensität: 8.5 erhalten"""
        r = _fx_scene_overrides()
        kl = r.get('project', {}).get('sceneLights', {}).get('Key Light', {})
        return kl.get('intensity') == 8.5, f'got {kl.get("intensity")}'

    @staticmethod
    def test_scene_light_muted_true():
        """Key Light muted=true (Aus) erhalten"""
        r = _fx_scene_overrides()
        kl = r.get('project', {}).get('sceneLights', {}).get('Key Light', {})
        return kl.get('muted') is True, f'got {kl.get("muted")}'

    @staticmethod
    def test_scene_light_visible_true():
        """Key Light visible=true (Helper zeigen) erhalten"""
        r = _fx_scene_overrides()
        kl = r.get('project', {}).get('sceneLights', {}).get('Key Light', {})
        return kl.get('visible') is True, f'got {kl.get("visible")}'

    @staticmethod
    def test_scene_light_keyframe_preserved():
        """Key Light hat 1 Keyframe nach Load"""
        r = _fx_scene_overrides()
        kl = r.get('project', {}).get('sceneLights', {}).get('Key Light', {})
        clips = kl.get('clips', [])
        return len(clips) == 1, f'{len(clips)} Clips'

    @staticmethod
    def test_scene_light_keyframe_fade_false():
        """Key Light KF fade=false erhalten"""
        r = _fx_scene_overrides()
        kl = r.get('project', {}).get('sceneLights', {}).get('Key Light', {})
        clips = kl.get('clips', [])
        if not clips:
            return False, 'Kein KF'
        return clips[0].get('data', {}).get('fade') is False, ''

    @staticmethod
    def test_ambient_visible_false_persists():
        """Ambient visible=false bleibt false (kein Reset auf true)"""
        r = _fx_scene_overrides()
        amb = r.get('project', {}).get('sceneLights', {}).get('Ambient', {})
        return amb.get('visible') is False, f'got {amb.get("visible")}'

    @staticmethod
    def test_ambient_color_preserved():
        """Ambient Farbe: '#aabbcc' erhalten"""
        r = _fx_scene_overrides()
        amb = r.get('project', {}).get('sceneLights', {}).get('Ambient', {})
        return amb.get('color') == '#aabbcc', f'got {amb.get("color")}'

    # --- Deleted KF persists ---
    @staticmethod
    def test_deleted_kf_only_one_clip():
        """Gelöschter Standard Start bleibt weg: nur 1 Clip (Standard Ende)"""
        r = _fx_deleted_kf()
        kl = r.get('project', {}).get('sceneLights', {}).get('Key Light', {})
        clips = kl.get('clips', [])
        return len(clips) == 1, f'{len(clips)} Clips'

    @staticmethod
    def test_deleted_kf_only_ende():
        """Nur 'Standard Ende' vorhanden, kein 'Standard Start'"""
        r = _fx_deleted_kf()
        kl = r.get('project', {}).get('sceneLights', {}).get('Key Light', {})
        clips = kl.get('clips', [])
        has_start = any(c.get('name') == 'Standard Start' for c in clips)
        has_ende = any(c.get('name') == 'Standard Ende' for c in clips)
        return not has_start and has_ende, f'start={has_start} ende={has_ende}'

    # --- Scene Floor ---
    @staticmethod
    def test_scene_floor_exists():
        """sceneFloor existiert im Save"""
        r = _fx_scene_floor()
        return bool(r.get('project', {}).get('sceneFloor')), ''

    @staticmethod
    def test_scene_floor_color():
        """sceneFloor.color: '#8b4513' erhalten"""
        r = _fx_scene_floor()
        sf = r.get('project', {}).get('sceneFloor', {})
        return sf.get('color') == '#8b4513', f'got {sf.get("color")}'

    @staticmethod
    def test_scene_floor_size():
        """sceneFloor.size: 10.0 erhalten"""
        r = _fx_scene_floor()
        sf = r.get('project', {}).get('sceneFloor', {})
        return sf.get('size') == 10.0, f'got {sf.get("size")}'

    @staticmethod
    def test_scene_floor_roughness():
        """sceneFloor.roughness: 0.7 erhalten"""
        r = _fx_scene_floor()
        sf = r.get('project', {}).get('sceneFloor', {})
        return sf.get('roughness') == 0.7, f'got {sf.get("roughness")}'

    @staticmethod
    def test_scene_floor_metalness():
        """sceneFloor.metalness: 0.15 erhalten"""
        r = _fx_scene_floor()
        sf = r.get('project', {}).get('sceneFloor', {})
        return sf.get('metalness') == 0.15, f'got {sf.get("metalness")}'
