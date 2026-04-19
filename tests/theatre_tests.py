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

    @staticmethod
    def test_bvh_studio_default_exists():
        """BVH Studio Default Preset vorhanden (Ersatz für alte Auto-Szenen-Lichter)"""
        code, data = http_request('/api/studio/theatre-preset/bvh_studio_default/')
        if code != 200:
            return False, f'HTTP {code}'
        if data.get('label') != 'BVH Studio Default':
            return False, f'Label: "{data.get("label")}"'
        return True, 'Label OK'

    @staticmethod
    def test_bvh_studio_default_has_full_light_set():
        """BVH Studio Default hat Key + Fill + Back + Ambient (wie Original-BVH-Studio-Setup)"""
        code, data = http_request('/api/studio/theatre-preset/bvh_studio_default/')
        if code != 200:
            return False, f'HTTP {code}'
        names = {lg.get('name') for lg in data.get('lights', [])}
        expected = {'Key Light', 'Fill Light', 'Back Light', 'Ambient'}
        missing = expected - names
        if missing:
            return False, f'Fehlende Lichter: {", ".join(missing)}'
        return True, f'Alle 4 Lichter vorhanden'

    @staticmethod
    def test_bvh_studio_default_light_types():
        """BVH Studio Default: 3× directional + 1× ambient (native Typen, keine Approximation)"""
        code, data = http_request('/api/studio/theatre-preset/bvh_studio_default/')
        if code != 200:
            return False, f'HTTP {code}'
        types = [lg.get('type') for lg in data.get('lights', [])]
        n_dir = sum(1 for t in types if t == 'directional')
        n_amb = sum(1 for t in types if t == 'ambient')
        if n_dir != 3 or n_amb != 1:
            return False, f'Typen: {n_dir}× directional, {n_amb}× ambient (erwartet 3+1)'
        return True, '3× directional + 1× ambient'

    @staticmethod
    def test_every_preset_renderable_as_timeline():
        """Jedes Preset-Licht hat Position + Intensität — Grundlage für durchgehende
        Timeline-Einträge (Start/Ende-KFs beim Preset-Apply)"""
        code, presets = http_request('/api/studio/theatre-presets/')
        if code != 200:
            return False, f'Liste HTTP {code}'
        errors = []
        for p in presets.get('presets', []):
            pname = p['name']
            code2, detail = http_request(f'/api/studio/theatre-preset/{pname}/')
            if code2 != 200:
                errors.append(f'{pname}: HTTP {code2}')
                continue
            for i, lg in enumerate(detail.get('lights', [])):
                # Ambient braucht keine Position; alle anderen schon
                if lg.get('type') != 'ambient':
                    pos = lg.get('position')
                    if not isinstance(pos, list) or len(pos) != 3:
                        errors.append(f'{pname}/{i}: Position ungültig')
                # Jedes Licht muss Intensität haben (sonst wäre Timeline-KF sinnlos)
                if not isinstance(lg.get('intensity'), (int, float)):
                    errors.append(f'{pname}/{i}: Intensität fehlt')
        if errors:
            return False, '; '.join(errors[:3]) + (f' (+{len(errors)-3})' if len(errors) > 3 else '')
        return True, f'{len(presets.get("presets", []))} Presets komplett'

    @staticmethod
    def test_all_presets_have_labels_and_descriptions():
        """Jedes Preset hat Label + Beschreibung (UI-Anzeige im Theatre-Menü)"""
        code, presets = http_request('/api/studio/theatre-presets/')
        if code != 200:
            return False, f'HTTP {code}'
        missing = []
        for p in presets.get('presets', []):
            if not p.get('label'):
                missing.append(f'{p.get("name")}: kein label')
            if not p.get('description'):
                missing.append(f'{p.get("name")}: keine description')
        if missing:
            return False, '; '.join(missing[:3])
        return True, f'{len(presets.get("presets", []))} Presets vollständig'
