# -*- coding: utf-8 -*-
"""Projekt: Szene-Roundtrip

Szenenlichter, geloeschte Keyframes und der Boden im Speichern/Laden-Umlauf

Aus `project_tests.py` herausgeloest (17.08.2026, Befund `dateigroesse`):
Die Datei hatte 426 Zeilen und eine Klasse mit 36 Testmethoden.
"""
from .base import TestCategory
from ._projekt_basis import Projektvorlagen


class ProjektSzeneTests(TestCategory):
    name = 'Projekt: Szene-Roundtrip'
    description = 'Szenenlichter, geloeschte Keyframes und der Boden im Speichern/Laden-Umlauf'

    # --- Scene Light Overrides ---
    @staticmethod
    def test_scene_light_key_exists():
        """sceneLights.Key Light existiert nach Load"""
        r = Projektvorlagen.szenenlichter()
        sl = r.get('project', {}).get('sceneLights', {})
        return 'Key Light' in sl, 'Keys: ' + ', '.join(sl.keys())

    @staticmethod
    def test_scene_light_key_color():
        """Key Light Farbe: '#ff5733' erhalten"""
        r = Projektvorlagen.szenenlichter()
        kl = r.get('project', {}).get('sceneLights', {}).get('Key Light', {})
        return kl.get('color') == '#ff5733', f'got {kl.get("color")}'

    @staticmethod
    def test_scene_light_key_intensity():
        """Key Light Intensität: 8.5 erhalten"""
        r = Projektvorlagen.szenenlichter()
        kl = r.get('project', {}).get('sceneLights', {}).get('Key Light', {})
        return kl.get('intensity') == 8.5, f'got {kl.get("intensity")}'

    @staticmethod
    def test_scene_light_muted_true():
        """Key Light muted=true (Aus) erhalten"""
        r = Projektvorlagen.szenenlichter()
        kl = r.get('project', {}).get('sceneLights', {}).get('Key Light', {})
        return kl.get('muted') is True, f'got {kl.get("muted")}'

    @staticmethod
    def test_scene_light_visible_true():
        """Key Light visible=true (Helper zeigen) erhalten"""
        r = Projektvorlagen.szenenlichter()
        kl = r.get('project', {}).get('sceneLights', {}).get('Key Light', {})
        return kl.get('visible') is True, f'got {kl.get("visible")}'

    @staticmethod
    def test_scene_light_keyframe_preserved():
        """Key Light hat 1 Keyframe nach Load"""
        r = Projektvorlagen.szenenlichter()
        kl = r.get('project', {}).get('sceneLights', {}).get('Key Light', {})
        clips = kl.get('clips', [])
        return len(clips) == 1, f'{len(clips)} Clips'

    @staticmethod
    def test_scene_light_keyframe_fade_false():
        """Key Light KF fade=false erhalten"""
        r = Projektvorlagen.szenenlichter()
        kl = r.get('project', {}).get('sceneLights', {}).get('Key Light', {})
        clips = kl.get('clips', [])
        if not clips:
            return False, 'Kein KF'
        return clips[0].get('data', {}).get('fade') is False, ''

    @staticmethod
    def test_ambient_visible_false_persists():
        """Ambient visible=false bleibt false (kein Reset auf true)"""
        r = Projektvorlagen.szenenlichter()
        amb = r.get('project', {}).get('sceneLights', {}).get('Ambient', {})
        return amb.get('visible') is False, f'got {amb.get("visible")}'

    @staticmethod
    def test_ambient_color_preserved():
        """Ambient Farbe: '#aabbcc' erhalten"""
        r = Projektvorlagen.szenenlichter()
        amb = r.get('project', {}).get('sceneLights', {}).get('Ambient', {})
        return amb.get('color') == '#aabbcc', f'got {amb.get("color")}'

    # --- Deleted KF persists ---
    @staticmethod
    def test_deleted_kf_only_one_clip():
        """Gelöschter Standard Start bleibt weg: nur 1 Clip (Standard Ende)"""
        r = Projektvorlagen.geloeschter_kf()
        kl = r.get('project', {}).get('sceneLights', {}).get('Key Light', {})
        clips = kl.get('clips', [])
        return len(clips) == 1, f'{len(clips)} Clips'

    @staticmethod
    def test_deleted_kf_only_ende():
        """Nur 'Standard Ende' vorhanden, kein 'Standard Start'"""
        r = Projektvorlagen.geloeschter_kf()
        kl = r.get('project', {}).get('sceneLights', {}).get('Key Light', {})
        clips = kl.get('clips', [])
        has_start = any(c.get('name') == 'Standard Start' for c in clips)
        has_ende = any(c.get('name') == 'Standard Ende' for c in clips)
        return not has_start and has_ende, f'start={has_start} ende={has_ende}'

    # --- Scene Floor ---
    @staticmethod
    def test_scene_floor_exists():
        """sceneFloor existiert im Save"""
        r = Projektvorlagen.boden()
        return bool(r.get('project', {}).get('sceneFloor')), ''

    @staticmethod
    def test_scene_floor_color():
        """sceneFloor.color: '#8b4513' erhalten"""
        r = Projektvorlagen.boden()
        sf = r.get('project', {}).get('sceneFloor', {})
        return sf.get('color') == '#8b4513', f'got {sf.get("color")}'

    @staticmethod
    def test_scene_floor_size():
        """sceneFloor.size: 10.0 erhalten"""
        r = Projektvorlagen.boden()
        sf = r.get('project', {}).get('sceneFloor', {})
        return sf.get('size') == 10.0, f'got {sf.get("size")}'

    @staticmethod
    def test_scene_floor_roughness():
        """sceneFloor.roughness: 0.7 erhalten"""
        r = Projektvorlagen.boden()
        sf = r.get('project', {}).get('sceneFloor', {})
        return sf.get('roughness') == 0.7, f'got {sf.get("roughness")}'

    @staticmethod
    def test_scene_floor_metalness():
        """sceneFloor.metalness: 0.15 erhalten"""
        r = Projektvorlagen.boden()
        sf = r.get('project', {}).get('sceneFloor', {})
        return sf.get('metalness') == 0.15, f'got {sf.get("metalness")}'
