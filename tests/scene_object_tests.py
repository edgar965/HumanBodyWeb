"""Tests für Scene-Object (3D-Objekt) Upload API."""
from .base import TestCategory, http_request


class SceneObjectTests(TestCategory):
    name = 'Scene-Objects'
    description = '3D-Objekt-Upload (OBJ/GLB/MTL/Texturen)'

    @staticmethod
    def test_obj_upload_ok():
        """OBJ Upload → HTTP 200 + URL in /media/scene_objects/"""
        obj = b"# Test OBJ\nv 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n"
        code, data = http_request('/api/studio/scene-object-upload/', method='POST',
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
        """Upload mit bundleId behält Original-Dateinamen (für MTL→Textur-Referenzen)"""
        import io
        boundary = '----TestBoundary9876xyz'
        body = b''
        body += f'--{boundary}\r\n'.encode()
        body += b'Content-Disposition: form-data; name="object"; filename="my_model.obj"\r\n'
        body += b'Content-Type: text/plain\r\n\r\n'
        body += b'v 0 0 0\n'
        body += b'\r\n'
        body += f'--{boundary}\r\n'.encode()
        body += b'Content-Disposition: form-data; name="bundleId"\r\n\r\n'
        body += b'testbundle123\r\n'
        body += f'--{boundary}--\r\n'.encode()
        import urllib.request
        req = urllib.request.Request('http://localhost:8081/api/studio/scene-object-upload/',
                                     data=body, method='POST')
        req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
        try:
            import json as _json
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = _json.loads(resp.read().decode())
            if 'testbundle123' not in data.get('url', ''):
                return False, f'bundleId fehlt in URL: {data.get("url")}'
            if 'my_model.obj' not in data.get('url', ''):
                return False, f'Original-Name fehlt: {data.get("url")}'
            return True, 'Bundle-Pfad + Original-Name OK'
        except Exception as e:
            return False, str(e)

    @staticmethod
    def test_mtl_upload_ok():
        """MTL-Datei kann hochgeladen werden"""
        mtl = b"newmtl Default\nKd 0.8 0.8 0.8\n"
        code, data = http_request('/api/studio/scene-object-upload/', method='POST',
                                  files={'object': ('test.mtl', mtl, 'text/plain')})
        if code != 200:
            return False, f'HTTP {code}'
        if data.get('ext') != 'mtl':
            return False, f'ext={data.get("ext")}'
        return True, 'MTL Upload OK'

    @staticmethod
    def test_invalid_extension_rejected():
        """Unerlaubte Extension → HTTP 400"""
        code, _ = http_request('/api/studio/scene-object-upload/', method='POST',
                               files={'object': ('bad.xyz', b'junk', 'text/plain')})
        if code != 400:
            return False, f'HTTP {code} (erwartet 400)'
        return True, '400 korrekt'
