# -*- coding: utf-8 -*-
"""Beiwerk der Bundle-Tests: Multipart-Upload, Abruf und drei Kunstdateien.

Fuehrender Unterstrich mit Absicht: `testaufbau` erkennt daran, dass das keine
Testdatei ist. Aus `scene_object_bundle_tests.py` herausgeloest (17.08.2026,
416 Zeilen).

Die drei Kunstdateien (`_OBJ_CONTENT`, `_MTL_CONTENT`, `_PNG_CONTENT`) sind
absichtlich winzig und trotzdem gueltig: Ein OBJ mit `mtllib`-Verweis, ein MTL
mit `map_Kd`-Verweis und ein 1x1-PNG. Damit laesst sich die ganze Kette
OBJ -> MTL -> PNG pruefen, ohne ein echtes Modell hochzuladen.
"""

# `io` stand hier und wurde nie benutzt (Befund `tote-importe`).
import json
import urllib.request

# EINE Adresse für alle Tests. Hier stand eine zweite Kopie mit `localhost` —
# die kostete 2 s je Anfrage. Sie kommt aus `kanal.py`, wo auch der Netzkanal
# sie liest; `base.py` reicht sie nicht mehr durch (Befund `tote-importe`,
# 18.08.2026 — und dieser Import hier war der Beleg, dass sie doch gebraucht
# wird: der Testlauf brach danach mit ImportError ab).
#
# DIESE DATEI SCHICKT SELBST (multipart) und nicht über `Kanal`: Sie prüft den
# Upload-Weg mit einem von Hand gebauten Rumpf. Im in-process-Lauf greift sie
# damit ins Netz — deshalb steht sie in der Oberflächen-Suite, die gegen den
# laufenden Server fährt.
from .kanal import BASE_URL


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
            # stumm gewollt: Der Rohtext geht als `_raw` in den Bericht — er
            # sagt mehr als die Parser-Meldung.
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
    except Exception as e:                                    # noqa: BLE001
        # Der Grund gehoert in den Bericht: Ein Aufrufer sieht sonst nur
        # „HTTP 0" und weiss nicht, ob der Server aus war, der Name nicht
        # aufloeste oder die Zeit ablief. Die Bytes sind hier frei — beim
        # Statuscode 0 prueft niemand den Inhalt.
        return 0, str(e).encode('utf-8', 'replace')


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

