# -*- coding: utf-8 -*-
"""Scene-Object Bundle: MTL-Pfade

MTL-Parser: Optionsflaggen, Unterordner und Backslash-Pfade

Aus `scene_object_bundle_tests.py` herausgeloest (17.08.2026, Befund
`dateigroesse`): Die Datei hatte 422 Zeilen und eine Klasse mit 13 Tests.
"""
from .base import TestCategory
from ._bundle_basis import _PNG_CONTENT, _fetch, _post_multipart


class BundleMtlTests(TestCategory):
    name = 'Scene-Object Bundle: MTL-Pfade'
    description = 'MTL-Parser: Optionsflaggen, Unterordner und Backslash-Pfade'

    # --- MTL-Parser: Optionsflaggen, Unterordner, Backslash-Pfade ---
    # Ab hier baut jeder Test sein eigenes Bundle — kein gemerkter Zustand.
    @classmethod
    def test_10_mtl_options_parser_strips_flags(cls):
        """MTL-Parser muss Optionen wie '-s 1 1 -o 0 0 0' vor dem Dateinamen ignorieren.
        Simuliert via MTL mit Optionen-Zeile + Textur-Upload im gleichen Bundle."""
        bundle = 'pytest_mtlopts_' + str(id(cls))
        mtl_with_opts = (
            b'newmtl Swan\n'
            b'Kd 1.0 1.0 1.0\n'
            b'map_Kd -s 1 1 -o 0 0 0 swan_tex.png\n'
        )
        status1, mtl_data = _post_multipart('/api/studio/scene-object-upload/', [
            ('object', 'swan.mtl', mtl_with_opts, 'text/plain'),
            ('bundleId', None, bundle, 'text/plain'),
        ])
        status2, tex_data = _post_multipart('/api/studio/scene-object-upload/', [
            ('object', 'swan_tex.png', _PNG_CONTENT, 'image/png'),
            ('bundleId', None, bundle, 'text/plain'),
        ])
        if status1 != 200 or status2 != 200:
            return False, f'Upload HTTP: {status1}/{status2}'
        # Simuliere Parser-Logik aus scene_extras.js
        import re
        content = mtl_data.get('_raw', '')  # _post_multipart returns JSON normally
        # Falls JSON OK, MTL-URL aus data.url dann separat fetchen
        mtl_url = mtl_data.get('url')
        if not mtl_url:
            return False, 'Keine MTL-URL geliefert'
        _, mtl_bytes = _fetch(mtl_url)
        mtl_text = mtl_bytes.decode('utf-8', errors='ignore')
        m = re.search(r'^\s*map_Kd\s+(.+?)\s*$', mtl_text, re.IGNORECASE | re.MULTILINE)
        if not m:
            return False, 'map_Kd fehlt'
        raw_ref = m.group(1).strip()
        tokens = [t for t in raw_ref.split() if t and not t.startswith('-')]
        ref_name = (tokens[-1] if tokens else raw_ref).replace('\\', '/').lstrip('./').split('/')[-1]
        if ref_name != 'swan_tex.png':
            return False, f'Parser extrahierte "{ref_name}" (erwartet: "swan_tex.png")'
        # Textur unter demselben Bundle-Ordner muss existieren
        base = mtl_url.rsplit('/', 1)[0]
        status3, _ = _fetch(f"{base}/{ref_name}")
        if status3 != 200:
            return False, f'Referenzierte Textur (mit Options-Flags davor) HTTP {status3}'
        return True, f'Parser ignoriert "-s 1 1 -o 0 0 0" → "{ref_name}" korrekt'

    @classmethod
    def test_11_auto_discover_mtl_from_obj(cls):
        """OBJ enthält 'mtllib X.mtl' → Auto-Discover resolved auf Bundle-URL.
        Das ist die 'Standard-OBJ-Load'-Semantik: User wählt nur OBJ, System fetcht
        MTL+Textur anhand der im OBJ angegebenen Referenzen."""
        bundle = 'pytest_auto_' + str(id(object()))
        obj_with_mtllib = b"mtllib myswan.mtl\nv 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n"
        mtl_content = b"newmtl Swan\nKd 1 1 1\nmap_Kd myswan.png\n"
        # Alle 3 im gleichen Bundle hochladen
        status1, obj_data = _post_multipart('/api/studio/scene-object-upload/', [
            ('object', 'myswan.obj', obj_with_mtllib, 'text/plain'),
            ('bundleId', None, bundle, 'text/plain'),
        ])
        status2, _ = _post_multipart('/api/studio/scene-object-upload/', [
            ('object', 'myswan.mtl', mtl_content, 'text/plain'),
            ('bundleId', None, bundle, 'text/plain'),
        ])
        status3, _ = _post_multipart('/api/studio/scene-object-upload/', [
            ('object', 'myswan.png', _PNG_CONTENT, 'image/png'),
            ('bundleId', None, bundle, 'text/plain'),
        ])
        if status1 != 200 or status2 != 200 or status3 != 200:
            return False, f'Upload HTTP: {status1}/{status2}/{status3}'
        # Simuliere _autoDiscoverMtl-Logik: OBJ-Content parsen, mtllib extrahieren,
        # URL aus basePath + mtllib-filename bauen, HEAD-Check.
        import re
        _, obj_bytes = _fetch(obj_data['url'])
        obj_text = obj_bytes.decode('utf-8', errors='ignore')
        m = re.search(r'^\s*mtllib\s+(.+?)\s*$', obj_text, re.IGNORECASE | re.MULTILINE)
        if not m:
            return False, 'mtllib-Zeile nicht im OBJ gefunden'
        mtllib_ref = m.group(1).strip().replace('\\', '/').lstrip('./')
        base = obj_data['url'].rsplit('/', 1)[0]
        expected_mtl_url = f"{base}/{mtllib_ref}"
        status4, mtl_bytes = _fetch(expected_mtl_url)
        if status4 != 200:
            return False, f'Auto-discover Ziel "{expected_mtl_url}" HTTP {status4}'
        if b'map_Kd' not in mtl_bytes:
            return False, 'Aufgelöstes MTL enthält keine map_Kd-Zeile'
        return True, f'mtllib "{mtllib_ref}" → {expected_mtl_url} (200)'

    @classmethod
    def test_12_subdirectory_texture_ref(cls):
        """MTL-Referenz 'map_Kd textures/swan.png' — Parser versucht Sub-Pfad zuerst,
        fällt auf Dateiname zurück wenn Sub-Pfad nicht existiert (Bundle ist flach)"""
        bundle = 'pytest_subdir_' + str(id(cls))
        # MTL mit Sub-Pfad, aber PNG wird FLACH ins Bundle gelegt (typisch für unseren Upload-Flow)
        mtl_sub = b'newmtl Swan\nmap_Kd textures/swan.png\n'
        status1, mtl_data = _post_multipart('/api/studio/scene-object-upload/', [
            ('object', 'sub.mtl', mtl_sub, 'text/plain'),
            ('bundleId', None, bundle, 'text/plain'),
        ])
        status2, _ = _post_multipart('/api/studio/scene-object-upload/', [
            ('object', 'swan.png', _PNG_CONTENT, 'image/png'),
            ('bundleId', None, bundle, 'text/plain'),
        ])
        if status1 != 200 or status2 != 200:
            return False, f'Upload HTTP: {status1}/{status2}'
        # Simuliere Parser: probiere "textures/swan.png" (fehlt), dann "swan.png" (OK)
        import re
        _, mtl_bytes = _fetch(mtl_data['url'])
        mtl_text = mtl_bytes.decode('utf-8', errors='ignore')
        m = re.search(r'^\s*map_Kd\s+(.+?)\s*$', mtl_text, re.IGNORECASE | re.MULTILINE)
        raw_ref = m.group(1).strip()
        tokens = [t for t in raw_ref.split() if t and not t.startswith('-')]
        candidate = (tokens[-1] if tokens else raw_ref).replace('\\', '/').lstrip('./')
        filename = candidate.split('/')[-1]
        candidates = [candidate] if candidate != filename else []
        candidates.append(filename)
        base = mtl_data['url'].rsplit('/', 1)[0]
        found_url = None
        for c in candidates:
            s, _ = _fetch(f"{base}/{c}")
            if s == 200:
                found_url = f"{base}/{c}"
                break
        if not found_url:
            return False, f'Keiner der Kandidaten auflösbar: {candidates}'
        if not found_url.endswith('/swan.png'):
            return False, f'Unerwarteter Resolve: {found_url}'
        return True, f'Sub-Pfad-Fallback → {found_url.rsplit("/", 1)[-1]}'

    @classmethod
    def test_13_mtl_backslash_paths_normalized(cls):
        """MTL mit Backslash-Pfad (Windows-Export): 'map_Kd textures\\swan.png' muss auf
        den reinen Dateinamen 'swan.png' im Bundle-Ordner resolved werden"""
        bundle = 'pytest_bs_' + str(id(object()))
        mtl_bs = b'newmtl Swan\nmap_Kd textures\\swan.png\n'
        status1, mtl_data = _post_multipart('/api/studio/scene-object-upload/', [
            ('object', 'bs.mtl', mtl_bs, 'text/plain'),
            ('bundleId', None, bundle, 'text/plain'),
        ])
        status2, _ = _post_multipart('/api/studio/scene-object-upload/', [
            ('object', 'swan.png', _PNG_CONTENT, 'image/png'),
            ('bundleId', None, bundle, 'text/plain'),
        ])
        if status1 != 200 or status2 != 200:
            return False, f'Upload HTTP: {status1}/{status2}'
        import re
        _, mtl_bytes = _fetch(mtl_data['url'])
        mtl_text = mtl_bytes.decode('utf-8', errors='ignore')
        m = re.search(r'^\s*map_Kd\s+(.+?)\s*$', mtl_text, re.IGNORECASE | re.MULTILINE)
        raw_ref = m.group(1).strip()
        tokens = [t for t in raw_ref.split() if t and not t.startswith('-')]
        ref_name = (tokens[-1] if tokens else raw_ref).replace('\\', '/').lstrip('./').split('/')[-1]
        if ref_name != 'swan.png':
            return False, f'Parser extrahierte "{ref_name}" (erwartet: "swan.png")'
        base = mtl_data['url'].rsplit('/', 1)[0]
        status3, _ = _fetch(f"{base}/{ref_name}")
        if status3 != 200:
            return False, f'Pfad-Normalisierung ergibt HTTP {status3}'
        return True, 'Backslash → Dateiname korrekt aufgelöst'
