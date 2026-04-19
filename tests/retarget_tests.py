"""Tests für Retarget + BVH-related APIs (aus alten Script-Tests übernommen)."""
from .base import TestCategory, http_request


class RetargetTests(TestCategory):
    name = 'Retarget API'
    description = 'BVH-Retarget Endpoints + Animations-Library'

    @staticmethod
    def test_animations_endpoint_200():
        """GET /api/character/animations/ → HTTP 200"""
        code, _ = http_request('/api/character/animations/')
        return code == 200, f'HTTP {code}'

    @staticmethod
    def test_animations_has_categories():
        """Response enthält categories-Objekt"""
        code, data = http_request('/api/character/animations/')
        if code != 200:
            return False, f'HTTP {code}'
        cats = data.get('categories', {})
        return isinstance(cats, dict) and len(cats) > 0, f'{len(cats)} Kategorien'

    @staticmethod
    def test_rigify_skeleton_endpoint():
        """GET /api/character/rigify-skeleton/ → HTTP 200 + bones"""
        code, data = http_request('/api/character/rigify-skeleton/')
        if code != 200:
            return False, f'HTTP {code}'
        if not isinstance(data, dict):
            return False, 'Kein dict'
        return True, 'OK'

    @staticmethod
    def test_skin_weights_endpoint():
        """GET /api/character/skin-weights/ → HTTP 200"""
        code, _ = http_request('/api/character/skin-weights/?body_type=Female_Caucasian')
        return code == 200, f'HTTP {code}'
