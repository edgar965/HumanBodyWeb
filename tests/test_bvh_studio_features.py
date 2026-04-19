#!/usr/bin/env python3
"""Smoke-Tests für neue BVH Studio Features (v0.39+):

- Theatre-Licht-Presets API
- Floor-Texturen API
- Scene-Object-Upload API
- Projekt Save/Load-Roundtrip mit Licht-Eigenschaften
- Client-Log-Endpoint

Run: python tests/test_bvh_studio_features.py
Setzt voraus, dass der Django-Server auf http://localhost:8081 läuft.
"""
import json
import sys
import tempfile
import urllib.request
import urllib.parse
from pathlib import Path

BASE_URL = 'http://localhost:8081'
RESULTS = []


def _req(path, method='GET', data=None, files=None):
    url = BASE_URL + path
    if files:
        # Multipart form data
        import email.mime.multipart as mm
        import email.mime.application as ma
        # Use stdlib: build multipart manually
        boundary = '----WebTestBoundary9876'
        body = b''
        for name, (fname, content, ctype) in files.items():
            body += f'--{boundary}\r\n'.encode()
            body += f'Content-Disposition: form-data; name="{name}"; filename="{fname}"\r\n'.encode()
            body += f'Content-Type: {ctype}\r\n\r\n'.encode()
            body += content
            body += b'\r\n'
        body += f'--{boundary}--\r\n'.encode()
        req = urllib.request.Request(url, data=body, method=method)
        req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
    else:
        if data is not None:
            body = json.dumps(data).encode()
            req = urllib.request.Request(url, data=body, method=method)
            req.add_header('Content-Type', 'application/json')
        else:
            req = urllib.request.Request(url, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, {'error': str(e)}
    except Exception as e:
        return 0, {'error': str(e)}


def _check(name, condition, detail=''):
    status = 'OK' if condition else 'FAIL'
    RESULTS.append((status, name, detail))
    icon = '[OK]  ' if condition else '[FAIL]'
    print(f'{icon} {name}{(" — " + detail) if detail else ""}')


# =========================================================================
# Test 1: Theatre-Presets-Liste
# =========================================================================

def test_theatre_presets_list():
    print('\n=== Theatre-Presets Liste ===')
    code, data = _req('/api/studio/theatre-presets/')
    _check('Theatre-Presets: HTTP 200', code == 200)
    _check('Theatre-Presets: JSON response', isinstance(data, dict) and 'presets' in data)
    presets = data.get('presets', [])
    expected = {'ballett_klassisch', 'club_dancefloor', 'jazz_buehne', 'sonnenuntergang', 'studio_portrait'}
    actual = {p.get('name') for p in presets}
    _check(f'Theatre-Presets: alle 5 Defaults vorhanden (got {len(actual)})', expected.issubset(actual))
    # Jedes Preset hat label + lightCount
    for p in presets:
        _check(f"Preset {p.get('name')} hat label + lightCount > 0",
               'label' in p and p.get('lightCount', 0) > 0)


# =========================================================================
# Test 2: Theatre-Preset-Detail
# =========================================================================

def test_theatre_preset_detail():
    print('\n=== Theatre-Preset Details ===')
    code, data = _req('/api/studio/theatre-preset/ballett_klassisch/')
    _check('Ballett-Preset: HTTP 200', code == 200)
    _check('Ballett-Preset: label = "Ballett (Klassisch)"', data.get('label') == 'Ballett (Klassisch)')
    lights = data.get('lights', [])
    _check(f'Ballett-Preset: 4 Lichter (got {len(lights)})', len(lights) == 4)
    for lg in lights:
        _check(f'Licht "{lg.get("name")}": hat type',
               lg.get('type') in ('spot', 'directional', 'point', 'ambient'))
        _check(f'Licht "{lg.get("name")}": hat position (3 Werte)',
               isinstance(lg.get('position'), list) and len(lg['position']) == 3)
    # Nicht-existentes Preset
    code, data = _req('/api/studio/theatre-preset/nonexistent_xyz/')
    _check('Nicht-existentes Preset: HTTP 404', code == 404)


# =========================================================================
# Test 3: Floor-Texturen
# =========================================================================

def test_floor_textures():
    print('\n=== Floor-Texturen ===')
    code, data = _req('/api/studio/floor-textures/')
    _check('Floor-Texturen: HTTP 200', code == 200)
    textures = data.get('textures', [])
    _check('Floor-Texturen: enthält "none" (Fallback)',
           any(t.get('name') == 'none' for t in textures))


# =========================================================================
# Test 4: Scene-Object-Upload
# =========================================================================

def test_scene_object_upload():
    print('\n=== Scene-Object-Upload ===')
    # Minimale OBJ-Datei (einfaches Dreieck)
    obj_content = b"""# Test OBJ
v 0 0 0
v 1 0 0
v 0 1 0
f 1 2 3
"""
    code, data = _req('/api/studio/scene-object-upload/',
                      method='POST',
                      files={'object': ('test_cube.obj', obj_content, 'text/plain')})
    _check('OBJ-Upload: HTTP 200', code == 200)
    _check('OBJ-Upload: ok=true', data.get('ok') is True)
    _check('OBJ-Upload: url beginnt mit /media/scene_objects/',
           data.get('url', '').startswith('/media/scene_objects/'))
    _check('OBJ-Upload: ext=obj', data.get('ext') == 'obj')
    # Ungültiges Format
    code, data = _req('/api/studio/scene-object-upload/',
                      method='POST',
                      files={'object': ('bad.xyz', b'xyz', 'text/plain')})
    _check('Ungültiges Format: HTTP 400', code == 400)


# =========================================================================
# Test 5: Project Save/Load-Roundtrip mit Licht-Properties
# =========================================================================

def test_project_save_load_roundtrip():
    print('\n=== Project Save/Load-Roundtrip (Licht-Properties) ===')
    # Projekt-Daten simulieren wie sie der Client speichern würde
    project_data = {
        'name': 'TestProject_LightProps',
        'fps': 30,
        'tracks': [
            {
                'name': 'Animation 1', 'type': 'bvh', 'preset': 'Rig2', 'bodyType': 'Female_Caucasian',
                'color': '#7c5cbf', 'muted': False, 'position': [0, 0, 0], 'clips': []
            },
            {
                'name': 'TestSpot', 'type': 'light', 'color': '#ffc107', 'muted': False, 'position': [0, 0, 0],
                'lightColor': '#ff00ff', 'lightIntensity': 7.5,
                'lightPosition': {'x': 1.5, 'y': 3.5, 'z': 2.5},
                'lightTarget':   {'x': 0, 'y': 1, 'z': 0},
                'lightAngle': 0.7854,  # 45°
                'lightPenumbra': 0.42,
                'lightDistance': 30.0,
                'lightVisible': True,
                'lightType': 'spot',
                '_sceneLight': False,
                'clips': [
                    {
                        'type': 'light_kf', 'category': None, 'name': 'Licht 1',
                        'totalFrames': 0, 'fps': 30, 'startFrame': 60,
                        'trimIn': 0, 'trimOut': 0, 'speed': 1,
                        'data': {
                            'position': {'x': 2, 'y': 4, 'z': 1},
                            'target':   {'x': 0, 'y': 1, 'z': 0},
                            'color': '#00ffff',
                            'intensity': 12.0,
                            'angle': 0.5236,  # 30°
                            'penumbra': 0.3,
                            'distance': 40.0,
                            'fade': False  # Sprung, kein Fade
                        }
                    }
                ]
            }
        ]
    }
    # Save to temp file via studio_project_save API
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / 'test_light_roundtrip.studio.json'
        # Client speichert via POST mit path+project
        code, saved = _req('/api/studio/project-save/', method='POST',
                           data={'path': str(tmp_path), 'project': project_data})
        _check('Save: HTTP 200', code == 200)
        _check('Save: ok=true', saved.get('ok') is True)
        # Datei existiert
        _check('Save: Datei existiert', tmp_path.is_file())
        # Laden
        code, loaded = _req(f'/api/studio/project-load/?path={urllib.parse.quote(str(tmp_path))}')
        _check('Load: HTTP 200', code == 200)
        _check('Load: ok=true', loaded.get('ok') is True)
        restored = loaded.get('project', {})
        # Licht-Track finden
        light_tracks = [t for t in restored.get('tracks', []) if t.get('type') == 'light']
        _check(f'Load: 1 Licht-Track (got {len(light_tracks)})', len(light_tracks) == 1)
        if light_tracks:
            lt = light_tracks[0]
            _check('Load: Licht-Farbe erhalten', lt.get('lightColor') == '#ff00ff')
            _check(f'Load: Licht-Intensität = 7.5 (got {lt.get("lightIntensity")})', lt.get('lightIntensity') == 7.5)
            _check('Load: Licht-Position erhalten',
                   lt.get('lightPosition', {}).get('x') == 1.5 and lt.get('lightPosition', {}).get('y') == 3.5)
            _check('Load: Licht-Winkel erhalten', abs(lt.get('lightAngle', 0) - 0.7854) < 0.001)
            _check('Load: Licht-Penumbra erhalten', lt.get('lightPenumbra') == 0.42)
            _check('Load: Licht-Reichweite erhalten', lt.get('lightDistance') == 30.0)
            _check('Load: Licht-Type = spot', lt.get('lightType') == 'spot')
            # Keyframe
            kfs = [c for c in lt.get('clips', []) if c.get('type') == 'light_kf']
            _check(f'Load: 1 Licht-Keyframe (got {len(kfs)})', len(kfs) == 1)
            if kfs:
                kf = kfs[0]
                d = kf.get('data', {})
                _check('Load: Keyframe-Intensität = 12', d.get('intensity') == 12.0)
                _check('Load: Keyframe-Fade = false', d.get('fade') is False)
                _check('Load: Keyframe-Angle erhalten', abs(d.get('angle', 0) - 0.5236) < 0.001)


# =========================================================================
# Test 6: Client-Log Endpoint
# =========================================================================

def test_scene_light_overrides_roundtrip():
    print('\n=== Scene-Light-Overrides Roundtrip ===')
    # Projekt mit Szenen-Licht-Overrides (Key Light mit geänderter Intensität + Aus-State)
    project_data = {
        'name': 'TestProject_SceneLight',
        'fps': 30,
        'tracks': [],
        'sceneLights': {
            'Key Light': {
                'color': '#ff5733', 'intensity': 8.5,
                'position': {'x': 1, 'y': 2, 'z': 3},
                'target': {'x': 0, 'y': 0, 'z': 0},
                'angle': None, 'penumbra': None, 'distance': None,
                'visible': True, 'muted': True,  # User hat Aus geschaltet
                'clips': [
                    {'type': 'light_kf', 'name': 'Licht 1', 'startFrame': 30,
                     'data': {'position': {'x': 2, 'y': 3, 'z': 1},
                              'color': '#ffaa00', 'intensity': 5.0, 'fade': False}}
                ]
            },
            'Ambient': {
                'color': '#aabbcc', 'intensity': 0.5,
                'position': {'x': 0, 'y': 0, 'z': 0},
                'target': None, 'angle': None, 'penumbra': None, 'distance': None,
                'visible': False,  # Helper versteckt
                'muted': False, 'clips': []
            }
        },
        'sceneFloor': {
            'color': '#8b4513', 'texture': 'none',
            'roughness': 0.7, 'metalness': 0.1, 'size': 10.0,
            'muted': False
        }
    }
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / 'test_scene_lights.studio.json'
        code, saved = _req('/api/studio/project-save/', method='POST',
                           data={'path': str(tmp_path), 'project': project_data})
        _check('Save scene-lights: HTTP 200', code == 200)
        code, loaded = _req(f'/api/studio/project-load/?path={urllib.parse.quote(str(tmp_path))}')
        _check('Load scene-lights: HTTP 200', code == 200)
        restored = loaded.get('project', {})
        # sceneLights preserved
        sl = restored.get('sceneLights', {})
        _check(f'SceneLights: Key Light vorhanden', 'Key Light' in sl)
        if 'Key Light' in sl:
            kl = sl['Key Light']
            _check('Key Light: Farbe erhalten (#ff5733)', kl.get('color') == '#ff5733')
            _check(f'Key Light: Intensität = 8.5 (got {kl.get("intensity")})', kl.get('intensity') == 8.5)
            _check('Key Light: muted=true (Aus) erhalten', kl.get('muted') is True)
            _check('Key Light: visible=true (Helper zeigen) erhalten', kl.get('visible') is True)
            _check('Key Light: 1 Keyframe erhalten', len(kl.get('clips', [])) == 1)
            if kl.get('clips'):
                kf = kl['clips'][0]
                _check('Key Light KF: fade=false erhalten', kf.get('data', {}).get('fade') is False)
        # Ambient: lightVisible=false (Helper versteckt) round-trippen
        amb = sl.get('Ambient', {})
        _check('Ambient: Farbe erhalten', amb.get('color') == '#aabbcc')
        _check('Ambient: visible=false (Helper versteckt) erhalten — nicht zu true resettet',
               amb.get('visible') is False)

        # sceneFloor preserved
        sf = restored.get('sceneFloor', {})
        _check('SceneFloor: Farbe erhalten (#8b4513)', sf.get('color') == '#8b4513')
        _check(f'SceneFloor: Größe = 10.0 (got {sf.get("size")})', sf.get('size') == 10.0)
        _check(f'SceneFloor: Rauheit = 0.7 (got {sf.get("roughness")})', sf.get('roughness') == 0.7)


def test_client_log():
    print('\n=== Client-Log Endpoint ===')
    code, data = _req('/api/log/', method='POST',
                      data={'page': 'bvh_studio', 'action': 'test_event', 'detail': 'automated test'})
    _check('Client-Log: HTTP 200', code == 200)


# =========================================================================
# Test 7: UI-Prefs (preload_seconds)
# =========================================================================

def test_ui_prefs_preload():
    print('\n=== UI-Prefs (Preload-Einstellung) ===')
    code, data = _req('/api/ui-prefs/')
    _check('UI-Prefs: HTTP 200', code == 200)
    # preload_seconds sollte ein string oder number sein; kann fehlen (Default 3)
    _check('UI-Prefs: dict-response', isinstance(data, dict))


# =========================================================================
# Main
# =========================================================================

def main():
    try:
        _req('/humanbody/bvh-studio/')
    except Exception as e:
        print(f'Server scheint nicht zu laufen auf {BASE_URL}: {e}')
        sys.exit(1)

    test_theatre_presets_list()
    test_theatre_preset_detail()
    test_floor_textures()
    test_scene_object_upload()
    test_project_save_load_roundtrip()
    test_scene_light_overrides_roundtrip()
    test_client_log()
    test_ui_prefs_preload()

    print('\n' + '=' * 60)
    total = len(RESULTS)
    passed = sum(1 for r in RESULTS if r[0] == 'OK')
    failed = total - passed
    print(f'Ergebnis: {passed}/{total} PASS, {failed} FAIL')
    print('=' * 60)
    if failed:
        print('\nFehlgeschlagene Tests:')
        for status, name, detail in RESULTS:
            if status == 'FAIL':
                print(f'  [FAIL] {name}{(" — " + detail) if detail else ""}')
    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    main()
