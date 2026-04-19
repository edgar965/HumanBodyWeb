"""Tests für UI-Prefs Endpoint."""
from .base import TestCategory, http_request


class UiPrefsTests(TestCategory):
    name = 'UI-Prefs'
    description = 'User-Einstellungen (Preload, Projekt-Pfade, etc.)'

    @staticmethod
    def test_ui_prefs_get():
        """/api/ui-prefs/ liefert 200 + dict"""
        code, data = http_request('/api/ui-prefs/')
        if code != 200:
            return False, f'HTTP {code}'
        if not isinstance(data, dict):
            return False, f'Kein dict: {type(data).__name__}'
        return True, f'{len(data)} Felder'
