"""Tests für Theatre-Licht-Presets API."""
from .base import TestCategory, http_request


class TheatreTests(TestCategory):
    name = 'Theatre-Presets'
    description = 'API für Theatre-Licht-Presets (Liste, Details, 404)'

    @staticmethod
    def test_list_returns_200():
        """/api/studio/theatre-presets/ liefert HTTP 200 + presets-Array"""
        code, data = http_request('/api/studio/theatre-presets/')
        if code != 200:
            return False, f'HTTP {code}'
        if 'presets' not in data:
            return False, 'Kein presets-Feld'
        return True, f'{len(data["presets"])} Presets'

    @staticmethod
    def test_list_contains_defaults():
        """Liste enthält alle 5 Default-Presets (Ballett, Jazz, Club, Studio, Sonnenuntergang)"""
        code, data = http_request('/api/studio/theatre-presets/')
        if code != 200:
            return False, f'HTTP {code}'
        names = {p.get('name') for p in data.get('presets', [])}
        expected = {'ballett_klassisch', 'club_dancefloor', 'jazz_buehne',
                    'sonnenuntergang', 'studio_portrait'}
        missing = expected - names
        if missing:
            return False, f'Fehlend: {", ".join(missing)}'
        return True, f'Alle 5 gefunden'

    @staticmethod
    def test_ballett_details():
        """Ballett-Preset hat 4 Lichter + korrektes Label"""
        code, data = http_request('/api/studio/theatre-preset/ballett_klassisch/')
        if code != 200:
            return False, f'HTTP {code}'
        lights = data.get('lights', [])
        if len(lights) != 4:
            return False, f'{len(lights)} Lichter (erwartet: 4)'
        if data.get('label') != 'Ballett (Klassisch)':
            return False, f'Label: "{data.get("label")}"'
        return True, 'Label + 4 Lichter OK'

    @staticmethod
    def test_light_structure():
        """Jedes Licht hat type + position (3 Werte)"""
        code, data = http_request('/api/studio/theatre-preset/ballett_klassisch/')
        if code != 200:
            return False, f'HTTP {code}'
        for lg in data.get('lights', []):
            if lg.get('type') not in ('spot', 'directional', 'point', 'ambient'):
                return False, f'Ungültiger type: {lg.get("type")}'
            pos = lg.get('position')
            if not isinstance(pos, list) or len(pos) != 3:
                return False, f'Position ungültig: {pos}'
        return True, '4/4 Lichter OK'

    @staticmethod
    def test_nonexistent_returns_404():
        """Nicht-existentes Preset → HTTP 404"""
        code, _ = http_request('/api/studio/theatre-preset/nonexistent_xyz/')
        if code != 404:
            return False, f'HTTP {code} (erwartet 404)'
        return True, '404 korrekt'
