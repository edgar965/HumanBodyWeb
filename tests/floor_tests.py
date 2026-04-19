"""Tests für Boden-Texturen API."""
from .base import TestCategory, http_request


class FloorTests(TestCategory):
    name = 'Boden-Texturen'
    description = 'API für vordefinierte Boden-Texturen'

    @staticmethod
    def test_textures_endpoint():
        """/api/studio/floor-textures/ → HTTP 200"""
        code, data = http_request('/api/studio/floor-textures/')
        if code != 200:
            return False, f'HTTP {code}'
        if 'textures' not in data:
            return False, 'Kein textures-Feld'
        return True, f'{len(data["textures"])} Texturen'

    @staticmethod
    def test_contains_none_fallback():
        """Textur-Liste enthält "none" Fallback (für reine Farbe)"""
        code, data = http_request('/api/studio/floor-textures/')
        if code != 200:
            return False, f'HTTP {code}'
        has_none = any(t.get('name') == 'none' for t in data.get('textures', []))
        if not has_none:
            return False, 'none fehlt'
        return True, 'none-Fallback OK'
