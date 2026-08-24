# -*- coding: utf-8 -*-
"""Beiwerk der Projekt-Roundtrip-Tests: Speichern, Laden, vier Vorlagen.

Fuehrender Unterstrich mit Absicht: `testaufbau` erkennt daran, dass das keine
Testdatei ist. Aus `project_tests.py` herausgeloest (17.08.2026, 425 Zeilen).

Die vier `_fx_*`-Vorlagen fahren je EINEN Speichern-Laden-Umlauf und merken sich
das Ergebnis. Alle Tests der beiden Kategorien lesen daraus — deshalb stehen sie
hier und nicht in einer der beiden.
"""

from ._speicherprobe import _save_load   # noqa: F401  (von den Vorlagen benutzt)


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
