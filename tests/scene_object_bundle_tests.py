"""Tests für Scene-Object OBJ+MTL+Textur-Bundle-Upload und -Abruf."""
import io
import json
import urllib.request


BASE_URL = 'http://localhost:8081'


def _post_multipart(path, fields):
    """Sendet ein Multipart-Form-Upload. fields = list[(name, filename|None, content, ctype)].

    filename=None → normales Text-Feld. Sonst → Datei.
    Returns (status, json_or_raw).
    """
    boundary = '----BundleBoundary' + str(id(fields))
    body = b''
    for name, fname, content, ctype in fields:
        body += f'--{boundary}\r\n'.encode()
        if fname is not None:
            body += f'Content-Disposition: form-data; name="{name}"; filename="{fname}"\r\n'.encode()
            body += f'Content-Type: {ctype}\r\n\r\n'.encode()
        else:
            body += f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode()
        body += content if isinstance(content, (bytes, bytearray)) else content.encode()
        body += b'\r\n'
    body += f'--{boundary}--\r\n'.encode()
    req = urllib.request.Request(BASE_URL + path, data=body, method='POST')
    req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            payload = resp.read().decode()
            try:
                return resp.status, json.loads(payload)
            except json.JSONDecodeError:
                return resp.status, {'_raw': payload}
    except urllib.error.HTTPError as e:
        return e.code, {'error': str(e)}
    except Exception as e:
        return 0, {'error': str(e)}


def _fetch(url):
    """Lädt den Inhalt einer URL (absolut oder relativ). Returns (status, bytes)."""
    if url.startswith('/'):
        url = BASE_URL + url
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, b''
    except Exception as e:
        return 0, b''


# Synthetische Test-Dateien — minimal, aber syntaktisch gültig.
_OBJ_CONTENT = b"""# Bundle-Test OBJ
mtllib bundle_test.mtl
v 0.0 0.0 0.0
v 1.0 0.0 0.0
v 0.0 1.0 0.0
vt 0.0 0.0
vt 1.0 0.0
vt 0.0 1.0
usemtl Mat01
f 1/1 2/2 3/3
"""

_MTL_CONTENT = b"""# Bundle-Test MTL
newmtl Mat01
Kd 0.8 0.8 0.8
map_Kd bundle_tex.png
"""

# 1x1 PNG (rot) — minimales gültiges PNG
_PNG_CONTENT = bytes([
    0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
    0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
    0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # 1x1
    0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
    0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,
    0x54, 0x08, 0x99, 0x63, 0xF8, 0xCF, 0xC0, 0x00,
    0x00, 0x00, 0x03, 0x00, 0x01, 0x5B, 0xFC, 0x2A,
    0x73, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,
    0x44, 0xAE, 0x42, 0x60, 0x82,
])


# Diese Klasse wird von tests/__init__.py automatisch erkannt
from .base import TestCategory


class SceneObjectBundleTests(TestCategory):
    name = 'Scene-Object Bundle (OBJ+MTL+Textur)'
    description = 'Upload und Abruf eines OBJ-Bundles mit Material und Textur'

    _bundle_id = 'pytest_bundle_' + str(id(object()))

    @classmethod
    def test_01_obj_upload_in_bundle(cls):
        """OBJ-Datei mit bundleId: Upload OK, URL enthält bundleId"""
        status, data = _post_multipart('/api/studio/scene-object-upload/', [
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
    def test_02_mtl_upload_same_bundle(cls):
        """MTL mit gleicher bundleId landet im gleichen Ordner wie OBJ"""
        status, data = _post_multipart('/api/studio/scene-object-upload/', [
            ('object', 'bundle_test.mtl', _MTL_CONTENT, 'text/plain'),
            ('bundleId', None, cls._bundle_id, 'text/plain'),
        ])
        if status != 200:
            return False, f'HTTP {status}'
        url = data.get('url', '')
        if cls._bundle_id not in url:
            return False, f'bundleId fehlt: {url}'
        obj_dir = getattr(cls, '_obj_url', '').rsplit('/', 1)[0]
        mtl_dir = url.rsplit('/', 1)[0]
        if obj_dir != mtl_dir:
            return False, f'OBJ/MTL in verschiedenen Ordnern: obj={obj_dir} mtl={mtl_dir}'
        cls._mtl_url = url
        return True, 'OBJ+MTL gleicher Bundle-Ordner'

    @classmethod
    def test_03_texture_upload_same_bundle(cls):
        """Textur-PNG mit gleicher bundleId landet im gleichen Ordner"""
        status, data = _post_multipart('/api/studio/scene-object-upload/', [
            ('object', 'bundle_tex.png', _PNG_CONTENT, 'image/png'),
            ('bundleId', None, cls._bundle_id, 'text/plain'),
        ])
        if status != 200:
            return False, f'HTTP {status}'
        url = data.get('url', '')
        if cls._bundle_id not in url:
            return False, f'bundleId fehlt: {url}'
        if 'bundle_tex.png' not in url:
            return False, f'Original-Name fehlt: {url}'
        cls._tex_url = url
        return True, 'Textur-PNG im Bundle-Ordner'

    @classmethod
    def test_04_obj_fetchable(cls):
        """Hochgeladene OBJ ist über /media/ abrufbar und Inhalt intakt"""
        if not hasattr(cls, '_obj_url'):
            return False, 'OBJ-Upload-Test lief nicht'
        status, content = _fetch(cls._obj_url)
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
        status, content = _fetch(cls._mtl_url)
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
        status, content = _fetch(cls._tex_url)
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
        """Upload OHNE bundleId landet trotzdem in separatem Ordner (kein Überschreiben)"""
        status1, data1 = _post_multipart('/api/studio/scene-object-upload/', [
            ('object', 'solo.obj', b'# a\nv 0 0 0\n', 'text/plain'),
        ])
        status2, data2 = _post_multipart('/api/studio/scene-object-upload/', [
            ('object', 'solo.obj', b'# b\nv 1 1 1\n', 'text/plain'),
        ])
        if status1 != 200 or status2 != 200:
            return False, f'Upload HTTP: {status1}/{status2}'
        if data1.get('url') == data2.get('url'):
            return False, f'Beide Uploads lieferten identische URL — kein Bundle-Schutz'
        return True, 'Zwei Uploads → zwei verschiedene URLs'
