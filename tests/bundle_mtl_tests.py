# -*- coding: utf-8 -*-
"""Scene-Object Bundle: MTL-Pfade

MTL-Parser: Optionsflaggen, Unterordner und Backslash-Pfade

Aus `scene_object_bundle_tests.py` herausgeloest (17.08.2026, Befund
`dateigroesse`): Die Datei hatte 422 Zeilen und eine Klasse mit 13 Tests.
"""
from .base import TestCategory
from ._bundle_basis import Bundelruf, Mtlbezug, _PNG_CONTENT


class BundleMtlTests(TestCategory):
    name = 'Scene-Object Bundle: MTL-Pfade'
    description = 'MTL-Parser: Optionsflaggen, Unterordner und Backslash-Pfade'

    # --- MTL-Parser: Optionsflaggen, Unterordner, Backslash-Pfade ---
    # Ab hier baut jeder Test sein eigenes Bundle — kein gemerkter Zustand.
    # ------------------------------------------------------------- Bausteine
    #
    # BEFUND `doppelcode` (30.08.2026): Die beiden Bloecke unten standen in
    # `test_12` und `test_13` zeichengleich. Ein Test, der seinen Aufbau
    # kopiert, laeuft beim naechsten Umbau der Schnittstelle nur zur Haelfte
    # mit — und der zurueckgebliebene wird gruen, weil er etwas anderes prueft
    # als sein Name sagt.

    @classmethod
    def _mtl_und_textur(cls, bundle, mtl_name, mtl_inhalt,
                        textur='swan.png'):
        """MTL und PNG in DASSELBE Buendel legen.

        Die Textur kommt FLACH ins Buendel, auch wenn die MTL einen Unterpfad
        nennt — genau so laedt der Upload-Weg der Anwendung hoch. Darauf beruht
        die Rueckfall-Suche, die beide Faelle pruefen.

        @param textur Name der Bilddatei; `test_10` braucht einen anderen
        @return (fehlertext, mtl_daten) — fehlertext ist leer, wenn es klappte
        """
        status1, mtl_daten = Bundelruf.hochladen(
            '/api/studio/scene-object-upload/', [
                ('object', mtl_name, mtl_inhalt, 'text/plain'),
                ('bundleId', None, bundle, 'text/plain'),
            ])
        status2, _ = Bundelruf.hochladen(
            '/api/studio/scene-object-upload/', [
                ('object', textur, _PNG_CONTENT, 'image/png'),
                ('bundleId', None, bundle, 'text/plain'),
            ])
        if status1 != 200 or status2 != 200:
            return f'Upload HTTP: {status1}/{status2}', None
        return '', mtl_daten

    @classmethod
    def test_10_mtl_options_parser_strips_flags(cls):
        """Optionen wie `-s 1 1 -o 0 0 0` stehen VOR dem Dateinamen.

        Der Parser muss sie ueberspringen. Bis zum 30.08.2026 baute dieser
        Test Upload und MTL-Auswertung selbst nach — Zeile fuer Zeile das,
        was `_mtl_und_textur` und `_map_kd` daneben schon konnten (elf
        Verzweigungen, Rang C).
        """
        bundle = 'pytest_mtlopts_' + str(id(cls))
        mtl = (b'newmtl Swan\n'
               b'Kd 1.0 1.0 1.0\n'
               b'map_Kd -s 1 1 -o 0 0 0 swan_tex.png\n')
        fehler, mtl_daten = cls._mtl_und_textur(bundle, 'swan.mtl', mtl,
                                                textur='swan_tex.png')
        if fehler:
            return False, fehler
        rohangabe, wortteile = Mtlbezug.aus_adresse(mtl_daten['url'])
        name = Mtlbezug.dateiname(rohangabe, wortteile)
        if name != 'swan_tex.png':
            return False, (f'Parser extrahierte "{name}" '
                           f'(erwartet: "swan_tex.png")')
        basis = mtl_daten['url'].rsplit('/', 1)[0]
        status, _ = Bundelruf.abrufen(f'{basis}/{name}')
        if status != 200:
            return False, (f'Referenzierte Textur (mit Options-Flags davor) '
                           f'HTTP {status}')
        return True, f'Parser ignoriert "-s 1 1 -o 0 0 0" -> "{name}" korrekt'

    @classmethod
    def test_11_auto_discover_mtl_from_obj(cls):
        """OBJ enthält 'mtllib X.mtl' → Auto-Discover resolved auf Bundle-URL.
        Das ist die 'Standard-OBJ-Load'-Semantik: User wählt nur OBJ, System fetcht
        MTL+Textur anhand der im OBJ angegebenen Referenzen."""
        bundle = 'pytest_auto_' + str(id(object()))
        obj_with_mtllib = b"mtllib myswan.mtl\nv 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n"
        mtl_content = b"newmtl Swan\nKd 1 1 1\nmap_Kd myswan.png\n"
        # Alle 3 im gleichen Bundle hochladen
        status1, obj_data = Bundelruf.hochladen('/api/studio/scene-object-upload/', [
            ('object', 'myswan.obj', obj_with_mtllib, 'text/plain'),
            ('bundleId', None, bundle, 'text/plain'),
        ])
        status2, _ = Bundelruf.hochladen('/api/studio/scene-object-upload/', [
            ('object', 'myswan.mtl', mtl_content, 'text/plain'),
            ('bundleId', None, bundle, 'text/plain'),
        ])
        status3, _ = Bundelruf.hochladen('/api/studio/scene-object-upload/', [
            ('object', 'myswan.png', _PNG_CONTENT, 'image/png'),
            ('bundleId', None, bundle, 'text/plain'),
        ])
        if status1 != 200 or status2 != 200 or status3 != 200:
            return False, f'Upload HTTP: {status1}/{status2}/{status3}'
        # Simuliere _autoDiscoverMtl-Logik: OBJ-Content parsen, mtllib extrahieren,
        # URL aus basePath + mtllib-filename bauen, HEAD-Check.
        import re
        _, obj_bytes = Bundelruf.abrufen(obj_data['url'])
        obj_text = obj_bytes.decode('utf-8', errors='ignore')
        m = re.search(r'^\s*mtllib\s+(.+?)\s*$', obj_text, re.IGNORECASE | re.MULTILINE)
        if not m:
            return False, 'mtllib-Zeile nicht im OBJ gefunden'
        mtllib_ref = m.group(1).strip().replace('\\', '/').lstrip('./')
        base = obj_data['url'].rsplit('/', 1)[0]
        expected_mtl_url = f"{base}/{mtllib_ref}"
        status4, mtl_bytes = Bundelruf.abrufen(expected_mtl_url)
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
        # MTL mit Sub-Pfad, aber PNG wird FLACH ins Bundle gelegt (typisch für unseren
        # Upload-Flow)
        mtl_sub = b'newmtl Swan\nmap_Kd textures/swan.png\n'
        fehler, mtl_data = cls._mtl_und_textur(bundle, 'sub.mtl', mtl_sub)
        if fehler:
            return False, fehler
        # Simuliere Parser: probiere "textures/swan.png" (fehlt), dann "swan.png" (OK)
        raw_ref, tokens = Mtlbezug.aus_adresse(mtl_data['url'])
        candidate = ((tokens[-1] if tokens else raw_ref)
                     .replace('\\', '/').lstrip('./'))
        filename = candidate.split('/')[-1]
        candidates = [candidate] if candidate != filename else []
        candidates.append(filename)
        base = mtl_data['url'].rsplit('/', 1)[0]
        found_url = None
        for c in candidates:
            s, _ = Bundelruf.abrufen(f"{base}/{c}")
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
        fehler, mtl_data = cls._mtl_und_textur(bundle, 'bs.mtl', mtl_bs)
        if fehler:
            return False, fehler
        raw_ref, tokens = Mtlbezug.aus_adresse(mtl_data['url'])
        ref_name = Mtlbezug.dateiname(raw_ref, tokens)
        if ref_name != 'swan.png':
            return False, f'Parser extrahierte "{ref_name}" (erwartet: "swan.png")'
        base = mtl_data['url'].rsplit('/', 1)[0]
        status3, _ = Bundelruf.abrufen(f"{base}/{ref_name}")
        if status3 != 200:
            return False, f'Pfad-Normalisierung ergibt HTTP {status3}'
        return True, 'Backslash → Dateiname korrekt aufgelöst'
