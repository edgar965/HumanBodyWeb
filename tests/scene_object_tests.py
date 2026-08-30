"""Tests für Scene-Object (3D-Objekt) Upload API."""
from .base import TestCategory, Netzruf
from ._bundle_basis import Bundelruf


class SceneObjectTests(TestCategory):
    name = 'Scene-Objects'
    description = '3D-Objekt-Upload (OBJ/GLB/MTL/Texturen)'

    @staticmethod
    def test_obj_upload_ok():
        """OBJ Upload → HTTP 200 + URL in /media/scene_objects/"""
        obj = b"# Test OBJ\nv 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n"
        code, data = Netzruf.senden('/api/studio/scene-object-upload/', method='POST',
                                    files={'object': ('test.obj', obj, 'text/plain')})
        if code != 200:
            return False, f'HTTP {code}'
        if not data.get('ok'):
            return False, f'ok=false: {data.get("error")}'
        if not data.get('url', '').startswith('/media/scene_objects/'):
            return False, f'Falscher URL: {data.get("url")}'
        return True, f'ext={data.get("ext")}, URL OK'

    @staticmethod
    def test_bundle_preserves_filename():
        """Upload mit bundleId behält Original-Dateinamen (für MTL→Textur-Referenzen)

        DURCH DEN KANAL, seit dem 28.08.2026: Dieser Fall baute seinen
        Multipart-Rumpf selbst und schickte ihn per `urllib` an
        `http://localhost:8081`. Er brauchte damit einen laufenden
        Dev-Server — ohne ihn stand „Es konnte keine Verbindung hergestellt
        werden" als Fehlschlag da. Und `localhost` statt `127.0.0.1` kostet
        unter Windows 2 s je Aufruf (gemessen, siehe `tests/kanal.py`).
        """
        status, daten = Bundelruf.hochladen(
            '/api/studio/scene-object-upload/',
            [('object', 'my_model.obj', b'v 0 0 0\n', 'text/plain'),
             ('bundleId', None, b'testbundle123', 'text/plain')])
        if status != 200:
            return False, f'HTTP {status}: {daten.get("error", daten)}'
        adresse = daten.get('url', '')
        if 'testbundle123' not in adresse:
            return False, f'bundleId fehlt in URL: {adresse}'
        if 'my_model.obj' not in adresse:
            return False, f'Original-Name fehlt: {adresse}'
        return True, 'Bundle-Pfad + Original-Name OK'

    @staticmethod
    def test_mtl_upload_ok():
        """MTL-Datei kann hochgeladen werden"""
        mtl = b"newmtl Default\nKd 0.8 0.8 0.8\n"
        code, data = Netzruf.senden('/api/studio/scene-object-upload/', method='POST',
                                    files={'object': ('test.mtl', mtl, 'text/plain')})
        if code != 200:
            return False, f'HTTP {code}'
        if data.get('ext') != 'mtl':
            return False, f'ext={data.get("ext")}'
        return True, 'MTL Upload OK'

    @staticmethod
    def test_invalid_extension_rejected():
        """Unerlaubte Extension → HTTP 400"""
        code, _ = Netzruf.senden('/api/studio/scene-object-upload/', method='POST',
                                 files={'object': ('bad.xyz', b'junk', 'text/plain')})
        if code != 400:
            return False, f'HTTP {code} (erwartet 400)'
        return True, '400 korrekt'
