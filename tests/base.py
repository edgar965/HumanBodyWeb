"""Basis-Klassen für BVH Studio Tests.

TestCase: repräsentiert einen einzelnen Test.
TestCategory: Sammlung zusammengehöriger Tests.
"""
import json
import urllib.request
import urllib.parse
import urllib.error


BASE_URL = 'http://localhost:8081'


def http_request(path, method='GET', data=None, files=None, timeout=15):
    """Minimaler HTTP-Client. Returns (status_code, json_or_dict)."""
    url = BASE_URL + path
    if files:
        boundary = '----TestBoundary9876xyz'
        body = b''
        for name, (fname, content, ctype) in files.items():
            body += f'--{boundary}\r\n'.encode()
            body += f'Content-Disposition: form-data; name="{name}"; filename="{fname}"\r\n'.encode()
            body += f'Content-Type: {ctype}\r\n\r\n'.encode()
            body += content
            body += b'\r\n'
        body += f'--{boundary}--\r\n'.encode()
        req = urllib.request.Request(url, data=body, method=method)
        req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
    elif data is not None:
        body = json.dumps(data).encode()
        req = urllib.request.Request(url, data=body, method=method)
        req.add_header('Content-Type', 'application/json')
    else:
        req = urllib.request.Request(url, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = resp.read().decode()
            try:
                return resp.status, json.loads(payload)
            except json.JSONDecodeError:
                return resp.status, {'_raw': payload}
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except Exception:
            return e.code, {'error': str(e)}
    except Exception as e:
        return 0, {'error': str(e)}


class TestCase:
    """Ein einzelner Test. Jedes fn sollte einen Bool oder (bool, detail) zurückgeben."""
    def __init__(self, name, fn, description=''):
        self.name = name
        self.fn = fn
        self.description = description

    def run(self):
        """Führt den Test aus; returns dict: {ok, name, description, detail, error}."""
        try:
            result = self.fn()
            if isinstance(result, tuple):
                ok, detail = result[0], result[1] if len(result) > 1 else ''
            else:
                ok, detail = bool(result), ''
            return {
                'ok': ok,
                'name': self.name,
                'description': self.description,
                'detail': detail,
                'error': None,
            }
        except Exception as e:
            import traceback
            return {
                'ok': False,
                'name': self.name,
                'description': self.description,
                'detail': '',
                'error': f'{type(e).__name__}: {e}\n{traceback.format_exc()}',
            }


class TestCategory:
    """Basis-Klasse für Test-Kategorien. Subklassen definieren test_* Methoden."""
    name = 'Unbenannte Kategorie'
    description = ''

    @classmethod
    def cases(cls):
        """Sammelt alle test_* Methoden als TestCase-Objekte."""
        cases = []
        for attr in dir(cls):
            if not attr.startswith('test_'):
                continue
            fn = getattr(cls, attr)
            if not callable(fn):
                continue
            desc = fn.__doc__.strip() if fn.__doc__ else ''
            cases.append(TestCase(
                name=attr.replace('test_', '').replace('_', ' ').title(),
                fn=fn,
                description=desc,
            ))
        return cases

    @classmethod
    def run_all(cls):
        """Führt alle Tests der Kategorie aus; returns list of result dicts."""
        return [c.run() for c in cls.cases()]
