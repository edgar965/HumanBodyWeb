"""Tests für Character-API Endpoints."""

from .base import Netzruf, TestCategory


class CharacterApiTests(TestCategory):
    name = 'Character API'
    description = 'Mesh, Morphs, Modelle, Hairstyles, Garments'

    @staticmethod
    def test_models_endpoint():
        """GET /api/character/models/ → HTTP 200 + presets-Array"""
        code, data = Netzruf.senden('/api/character/models/')
        if code != 200:
            return False, f'HTTP {code}'
        presets = data.get('presets', [])
        return isinstance(presets, list) and len(presets) > 0, f'{len(presets)} Presets'

    @staticmethod
    def _studio_standard():
        """Das Standardmodell des BVH-Studios (Vorgabe der Einstellungsseite) — seit 12.10.2026 statt des festen Namens `Rig2`:
        `Rig1/2/3/5` wurden mit „13 alte Modelle entfernt“ gelöscht, die Vorgabe zeigte weiter auf `Rig2` (404)."""
        from core.api.seite_bvhstudio_einstellungen import BvhStudioEinstellungenSeite

        return BvhStudioEinstellungenSeite.VORGABEN['studio_default_model']

    @staticmethod
    def test_models_contains_studio_default():
        """Das Standardmodell des Studios steht in der models-Liste"""
        code, data = Netzruf.senden('/api/character/models/')
        if code != 200:
            return False, f'HTTP {code}'
        name = CharacterApiTests._studio_standard()
        names = {p.get('name') for p in data.get('presets', [])}
        return name in names, f'{name} fehlt' if name not in names else ''

    @staticmethod
    def test_model_detail_studio_default():
        """GET /api/character/model/<Standardmodell des Studios>/ → HTTP 200"""
        code, _ = Netzruf.senden(f'/api/character/model/{CharacterApiTests._studio_standard()}/')
        return code == 200, f'HTTP {code}'

    @staticmethod
    def test_mesh_endpoint():
        """GET /api/character/mesh/ → HTTP 200"""
        code, _ = Netzruf.senden('/api/character/mesh/?body_type=Female_Caucasian')
        return code == 200, f'HTTP {code}'

    @staticmethod
    def test_morphs_endpoint():
        """GET /api/character/morphs/ → HTTP 200"""
        code, _ = Netzruf.senden('/api/character/morphs/')
        return code == 200, f'HTTP {code}'

    @staticmethod
    def test_hairstyles_endpoint():
        """GET /api/character/hairstyles/ → HTTP 200"""
        code, _ = Netzruf.senden('/api/character/hairstyles/')
        return code == 200, f'HTTP {code}'

    @staticmethod
    def test_scenes_endpoint():
        """GET /api/character/scenes/ → HTTP 200"""
        code, _ = Netzruf.senden('/api/character/scenes/')
        return code == 200, f'HTTP {code}'
