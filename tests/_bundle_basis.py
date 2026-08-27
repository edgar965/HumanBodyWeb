# -*- coding: utf-8 -*-
"""Beiwerk der Bundle-Tests: Multipart-Upload, Abruf und drei Kunstdateien.

Fuehrender Unterstrich mit Absicht: `testaufbau` erkennt daran, dass das keine
Testdatei ist. Aus `scene_object_bundle_tests.py` herausgeloest (17.08.2026,
416 Zeilen).

Die drei Kunstdateien (`OBJ`, `MTL`, `PNG`) sind absichtlich winzig und
trotzdem gueltig: Ein OBJ mit `mtllib`-Verweis, ein MTL mit `map_Kd`-Verweis
und ein 1x1-PNG. Damit laesst sich die ganze Kette OBJ -> MTL -> PNG pruefen,
ohne ein echtes Modell hochzuladen.

UMBAU 27.08.2026 (Befund `freie-funktionen`): Die beiden Sende-Funktionen
stehen jetzt als `Bundelruf`; die Kunstdateien sind Klassenfelder daneben.
"""

# `io` stand hier und wurde nie benutzt (Befund `tote-importe`).
import json
import urllib.error
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


class Bundelruf:
    """Multipart-Upload und Abruf — von Hand gebaut, absichtlich am Kanal vorbei."""

    #: Wie lange auf eine Antwort gewartet wird.
    FRIST_UPLOAD_S = 15
    FRIST_ABRUF_S = 10

    @classmethod
    def hochladen(cls, pfad, felder):
        """Sendet ein Multipart-Formular.

        `felder` = [(name, dateiname|None, inhalt, inhaltstyp)];
        `dateiname=None` -> normales Textfeld, sonst Datei.
        Rueckgabe: `(Status, JSON oder {'_raw': Text})`.
        """
        grenze = '----BundleBoundary' + str(id(felder))
        anfrage = urllib.request.Request(
            BASE_URL + pfad, data=cls._rumpf(grenze, felder), method='POST')
        anfrage.add_header('Content-Type',
                           'multipart/form-data; boundary=%s' % grenze)
        try:
            with urllib.request.urlopen(
                    anfrage, timeout=cls.FRIST_UPLOAD_S) as antwort:
                text = antwort.read().decode()
                try:
                    return antwort.status, json.loads(text)
                # stumm gewollt: Der Rohtext geht als `_raw` in den Bericht —
                # er sagt mehr als die Parser-Meldung.
                except json.JSONDecodeError:
                    return antwort.status, {'_raw': text}
        except urllib.error.HTTPError as fehler:
            return fehler.code, {'error': str(fehler)}
        except Exception as fehler:                              # noqa: BLE001
            return 0, {'error': str(fehler)}

    @staticmethod
    def _rumpf(grenze, felder):
        """Der Multipart-Rumpf als Bytes."""
        teile = b''
        for name, dateiname, inhalt, inhaltstyp in felder:
            teile += ('--%s\r\n' % grenze).encode()
            if dateiname is not None:
                teile += ('Content-Disposition: form-data; name="%s"; '
                          'filename="%s"\r\n' % (name, dateiname)).encode()
                teile += ('Content-Type: %s\r\n\r\n' % inhaltstyp).encode()
            else:
                teile += ('Content-Disposition: form-data; name="%s"\r\n\r\n'
                          % name).encode()
            teile += (inhalt if isinstance(inhalt, (bytes, bytearray))
                      else inhalt.encode())
            teile += b'\r\n'
        return teile + ('--%s--\r\n' % grenze).encode()

    @classmethod
    def abrufen(cls, adresse):
        """Laedt den Inhalt einer Adresse (absolut oder relativ)."""
        if adresse.startswith('/'):
            adresse = BASE_URL + adresse
        try:
            with urllib.request.urlopen(
                    adresse, timeout=cls.FRIST_ABRUF_S) as antwort:
                return antwort.status, antwort.read()
        except urllib.error.HTTPError as fehler:
            return fehler.code, b''
        except Exception as fehler:                              # noqa: BLE001
            # Der Grund gehoert in den Bericht: Ein Aufrufer sieht sonst nur
            # „HTTP 0" und weiss nicht, ob der Server aus war, der Name nicht
            # aufloeste oder die Zeit ablief. Die Bytes sind hier frei — beim
            # Statuscode 0 prueft niemand den Inhalt.
            return 0, str(fehler).encode('utf-8', 'replace')


# Synthetische Test-Dateien — minimal, aber syntaktisch gültig. Sie bleiben
# Modulkonstanten: Das sind DATEN, kein Verhalten.
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
