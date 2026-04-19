"""Tests für Character-API Endpoints."""
from .base import TestCategory, http_request


class CharacterApiTests(TestCategory):
    name = 'Character API'
    description = 'Mesh, Morphs, Modelle, Hairstyles, Garments'

    @staticmethod
    def test_models_endpoint():
        """GET /api/character/models/ → HTTP 200 + presets-Array"""
        code, data = http_request('/api/character/models/')
        if code != 200:
            return False, f'HTTP {code}'
        presets = data.get('presets', [])
        return isinstance(presets, list) and len(presets) > 0, f'{len(presets)} Presets'

    @staticmethod
    def test_models_contains_rig2():
        """Rig2 in models-Liste vorhanden"""
        code, data = http_request('/api/character/models/')
        if code != 200:
            return False, f'HTTP {code}'
        names = {p.get('name') for p in data.get('presets', [])}
        return 'Rig2' in names, 'Rig2 fehlt' if 'Rig2' not in names else ''

    @staticmethod
    def test_model_detail_rig2():
        """GET /api/character/model/Rig2/ → HTTP 200"""
        code, _ = http_request('/api/character/model/Rig2/')
        return code == 200, f'HTTP {code}'

    @staticmethod
    def test_mesh_endpoint():
        """GET /api/character/mesh/ → HTTP 200"""
        code, _ = http_request('/api/character/mesh/?body_type=Female_Caucasian')
        return code == 200, f'HTTP {code}'

    @staticmethod
    def test_morphs_endpoint():
        """GET /api/character/morphs/ → HTTP 200"""
        code, _ = http_request('/api/character/morphs/')
        return code == 200, f'HTTP {code}'

    @staticmethod
    def test_hairstyles_endpoint():
        """GET /api/character/hairstyles/ → HTTP 200"""
        code, _ = http_request('/api/character/hairstyles/')
        return code == 200, f'HTTP {code}'

    @staticmethod
    def test_scenes_endpoint():
        """GET /api/character/scenes/ → HTTP 200"""
        code, _ = http_request('/api/character/scenes/')
        return code == 200, f'HTTP {code}'
