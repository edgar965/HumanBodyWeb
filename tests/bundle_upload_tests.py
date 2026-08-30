# -*- coding: utf-8 -*-
"""Scene-Object Bundle: Upload und Kette

Hochladen von OBJ, MTL und Textur in EIN Bundle und die Kette OBJ -> MTL -> PNG

Aus `scene_object_bundle_tests.py` herausgeloest (17.08.2026, Befund
`dateigroesse`): Die Datei hatte 422 Zeilen und eine Klasse mit 13 Tests.
"""
from .base import TestCategory
from ._bundle_basis import (Bundelruf, Mtlbezug, _MTL_CONTENT, _OBJ_CONTENT,
                            _PNG_CONTENT)


class BundleUploadTests(TestCategory):
    name = 'Scene-Object Bundle: Upload und Kette'
    #: Eigene Bundle-Kennung je Kategorie — die Tests einer Kategorie
    #: teilen sie, zwei Kategorien duerfen sich nicht ins Bundle fassen.
    _bundle_id = 'pytest_bundle_' + str(id(object()))

    description = (
        'Hochladen von OBJ, MTL und Textur in EIN Bundle und die Kette OBJ -> MTL -> '
        'PNG')

    # --- Upload, Abruf und die Kette OBJ -> MTL -> PNG ---
    # Diese neun Tests haengen aneinander: 01 bis 03 laden hoch und merken die
    # URLs an der Klasse, 04 bis 09 pruefen sie. Sie muessen deshalb in EINER
    # Kategorie bleiben.
    @classmethod
    def test_01_obj_upload_in_bundle(cls):
        """OBJ-Datei mit bundleId: Upload OK, URL enthält bundleId"""
        status, data = Bundelruf.hochladen('/api/studio/scene-object-upload/', [
            ('object', 'bundle_test.obj', _OBJ_CONTENT, 'text/plain'),
            ('bundleId', None, cls._bundle_id, 'text/plain'),
        ])
        if status != 200:
            return False, f'HTTP {status}: {data}'
        if not data.get('ok'):
            return False, f'ok=false: {data.get("error")}'
        url = data.get('url', '')
        if cls._bundle_id not in url:
            return False, f'bundleId fehlt in URL: {url}'
        if 'bundle_test.obj' not in url:
            return False, f'Original-Name fehlt: {url}'
        cls._obj_url = url
        return True, f'URL: {url[-60:]}'

    @classmethod
    def _geprueft(cls, status, daten):
        """Antwort eines Buendel-Uploads pruefen.

        BEFUND `doppelcode` (30.08.2026): Diese fuenf Zeilen standen in
        `test_02` und `test_03`.

        Die Buendelkennung MUSS in der Adresse stehen — daran haengt, dass
        OBJ, MTL und Texturen im selben Ordner landen. Fehlt sie, liegt jede
        Datei fuer sich, und der Loader findet die Textur nicht mehr.

        @return (fehlertext, url) — fehlertext ist leer, wenn alles passt
        """
        if status != 200:
            return f'HTTP {status}', ''
        url = daten.get('url', '')
        if cls._bundle_id not in url:
            return f'bundleId fehlt: {url}', url
        return '', url

    @classmethod
    def test_02_mtl_upload_same_bundle(cls):
        """MTL mit gleicher bundleId landet im gleichen Ordner wie OBJ"""
        status, data = Bundelruf.hochladen('/api/studio/scene-object-upload/', [
            ('object', 'bundle_test.mtl', _MTL_CONTENT, 'text/plain'),
            ('bundleId', None, cls._bundle_id, 'text/plain'),
        ])
        fehler, url = cls._geprueft(status, data)
        if fehler:
            return False, fehler
        obj_dir = getattr(cls, '_obj_url', '').rsplit('/', 1)[0]
        mtl_dir = url.rsplit('/', 1)[0]
        if obj_dir != mtl_dir:
            return (
                False, f'OBJ/MTL in verschiedenen Ordnern: obj={obj_dir} mtl={mtl_dir}')
        cls._mtl_url = url
        return True, 'OBJ+MTL gleicher Bundle-Ordner'

    @classmethod
    def test_03_texture_upload_same_bundle(cls):
        """Textur-PNG mit gleicher bundleId landet im gleichen Ordner"""
        status, data = Bundelruf.hochladen('/api/studio/scene-object-upload/', [
            ('object', 'bundle_tex.png', _PNG_CONTENT, 'image/png'),
            ('bundleId', None, cls._bundle_id, 'text/plain'),
        ])
        fehler, url = cls._geprueft(status, data)
        if fehler:
            return False, fehler
        if 'bundle_tex.png' not in url:
            return False, f'Original-Name fehlt: {url}'
        cls._tex_url = url
        return True, 'Textur-PNG im Bundle-Ordner'

    @classmethod
    def test_04_obj_fetchable(cls):
        """Hochgeladene OBJ ist über /media/ abrufbar und Inhalt intakt"""
        if not hasattr(cls, '_obj_url'):
            return False, 'OBJ-Upload-Test lief nicht'
        status, content = Bundelruf.abrufen(cls._obj_url)
        if status != 200:
            return False, f'OBJ-Download HTTP {status}'
        if b'mtllib bundle_test.mtl' not in content:
            return False, 'mtllib-Referenz fehlt im abgerufenen OBJ'
        return True, f'{len(content)} bytes, mtllib-Ref intakt'

    @classmethod
    def test_05_mtl_fetchable(cls):
        """Hochgeladene MTL abrufbar + referenziert Textur"""
        if not hasattr(cls, '_mtl_url'):
            return False, 'MTL-Upload-Test lief nicht'
        status, content = Bundelruf.abrufen(cls._mtl_url)
        if status != 200:
            return False, f'MTL-Download HTTP {status}'
        if b'map_Kd bundle_tex.png' not in content:
            return False, 'Textur-Referenz fehlt in MTL'
        return True, 'MTL inkl. map_Kd-Referenz abrufbar'

    @classmethod
    def test_06_texture_fetchable(cls):
        """Hochgeladene Textur-PNG abrufbar und als PNG erkannt"""
        if not hasattr(cls, '_tex_url'):
            return False, 'Textur-Upload-Test lief nicht'
        status, content = Bundelruf.abrufen(cls._tex_url)
        if status != 200:
            return False, f'Textur-Download HTTP {status}'
        if not content.startswith(b'\x89PNG'):
            return False, 'PNG-Signature fehlt'
        return True, f'{len(content)} bytes, PNG-Signature OK'

    @classmethod
    def test_07_obj_references_resolve(cls):
        """Die mtllib-Referenz aus OBJ zeigt auf existierende MTL im Bundle-Ordner"""
        if not (hasattr(cls, '_obj_url') and hasattr(cls, '_mtl_url')):
            return False, 'Vorhergehende Tests fehlgeschlagen'
        base = cls._obj_url.rsplit('/', 1)[0]
        resolved_mtl = base + '/bundle_test.mtl'
        if resolved_mtl != cls._mtl_url:
            return False, f'MTL nicht auflösbar: {resolved_mtl} != {cls._mtl_url}'
        # Gleiche Auflösung für map_Kd in MTL → PNG
        resolved_tex = base + '/bundle_tex.png'
        if resolved_tex != cls._tex_url:
            return False, f'Textur nicht auflösbar: {resolved_tex} != {cls._tex_url}'
        return True, 'OBJ→MTL→PNG-Referenzen lösen im Bundle auf'

    @classmethod
    def test_08_without_bundle_id_uses_random(cls):
        """Upload OHNE bundleId landet trotzdem in separatem Ordner —
        nichts wird überschrieben."""
        status1, data1 = Bundelruf.hochladen('/api/studio/scene-object-upload/', [
            ('object', 'solo.obj', b'# a\nv 0 0 0\n', 'text/plain'),
        ])
        status2, data2 = Bundelruf.hochladen('/api/studio/scene-object-upload/', [
            ('object', 'solo.obj', b'# b\nv 1 1 1\n', 'text/plain'),
        ])
        if status1 != 200 or status2 != 200:
            return False, f'Upload HTTP: {status1}/{status2}'
        if data1.get('url') == data2.get('url'):
            return False, f'Beide Uploads lieferten identische URL — kein Bundle-Schutz'
        return True, 'Zwei Uploads → zwei verschiedene URLs'

    @classmethod
    def test_09_mtl_kd_references_texture_in_bundle(cls):
        """MTL-Inhalt referenziert 'map_Kd bundle_tex.png' und die PNG ist unter exakt
        diesem Pfad abrufbar (OBJ→MTL→PNG-Chain komplett)"""
        if not all(hasattr(cls, name)
                   for name in ('_obj_url', '_mtl_url', '_tex_url')):
            return False, 'Vorgänger-Tests fehlgeschlagen'
        status, mtl_content = Bundelruf.abrufen(cls._mtl_url)
        if status != 200 or not mtl_content:
            return False, f'MTL-Fetch HTTP {status}'
        rohangabe, wortteile = Mtlbezug.aus_text(
            mtl_content.decode('utf-8', errors='ignore'))
        if not rohangabe:
            return False, 'map_Kd-Referenz nicht im MTL gefunden'
        name = Mtlbezug.dateiname(rohangabe, wortteile)
        # Die PNG muss unter basePath + Dateiname abrufbar sein.
        basis = cls._obj_url.rsplit('/', 1)[0]
        erwartet = f'{basis}/{name}'
        if erwartet != cls._tex_url:
            return False, (f'MTL zeigt auf "{name}" -> URL "{erwartet}", '
                           f'aber Textur liegt unter "{cls._tex_url}"')
        status2, png = Bundelruf.abrufen(erwartet)
        if status2 != 200:
            return False, f'Referenzierte Textur nicht abrufbar (HTTP {status2})'
        if not png.startswith(b'\x89PNG'):
            return False, 'Referenzierter Textur-Download ist kein PNG'
        return True, f'map_Kd="{name}" -> {len(png)}B PNG OK'
