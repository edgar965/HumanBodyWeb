# -*- coding: utf-8 -*-
u"""Netzpaket — eine Netzantwort als Binärcontainer statt base64-in-JSON.

DAS FORMAT
==========
::

    0 ..  3   b'HBM1'                    Magie
    4 ..  7   uint32 LE                  Länge des JSON-Kopfes in Bytes
    8 ..      JSON-Kopf (UTF-8)          das Antwort-Wörterbuch, Felder ersetzt
              Polsterung mit Leerzeichen auf die nächste 8-Byte-Grenze
    dann      die Felder hintereinander, jedes auf 8 Byte ausgerichtet

Jedes `Netzfeld` im Wörterbuch steht im Kopf als Platzhalter::

    {"__netzfeld__": {"typ": "float32", "pos": 0, "bytes": 850212, "anzahl": 212553}}

Der Browser liest den Kopf, legt für jeden Platzhalter ein `TypedArray` auf den
schon vorhandenen `ArrayBuffer` und **kopiert dabei nichts**
(`gemeinsam/netzpaket.js`).

WARUM 8 BYTE AUSRICHTUNG
========================
`new Float32Array(puffer, versatz, n)` verlangt, dass `versatz` ein Vielfaches
der Elementbreite ist — sonst wirft der Browser `RangeError: start offset of
Float32Array should be a multiple of 4`. Acht statt vier kostet im Schnitt vier
Bytes je Feld und hält auch für float64 offen, falls je eines dazukommt.

WAS DAS BRINGT
==============
base64 bläht jede Nutzlast um ein Drittel auf (3 Bytes → 4 Zeichen). Dazu kam
auf beiden Seiten eine Umwandlung: Der Server maß 0,55 s für base64 und JSON
einer 93-MB-Antwort (`g9antworten.py`), der Browser dekodierte dieselben Daten
noch einmal. Beides fällt hier weg — der Server schreibt die Bytes, die numpy
ohnehin schon im Speicher hat, der Browser legt eine Sicht darauf.

Was NICHT wegfällt: die Zeit, aus den Punkten Three.js-Geometrien zu bauen. Die
lag bei der Messung am 30.09.2026 im Browser-Hauptthread und war der größere
Posten (`~/.claude/rules/` → `szene-ladezeit.md`).

DIE MAGIE IST NICHT SCHMUCK
===========================
Sie ist die Stelle, an der ein falsch geratenes Format LAUT scheitert. Ohne sie
liest der Browser einen HTML-Fehlertext als Float32 und zeigt ein Netz aus
Rauschen — der Fehler wäre dann in der Geometrie zu suchen und nicht in der
Antwort.
"""
import json
import struct

from django.core.serializers.json import DjangoJSONEncoder

from .netzfeld import Netzfeld

__all__ = ['Netzpaket']


class Netzpaket:
    u"""Packt ein Antwort-Wörterbuch mit `Netzfeld`ern in Bytes."""

    MAGIE = b'HBM1'
    #: Der Inhaltstyp der Antwort. Eigener Typ, kein `application/octet-stream`:
    #: So sieht man im Netzwerk-Reiter des Browsers sofort, was da kommt.
    INHALTSTYP = 'application/x-humanbody-netz'
    #: Kopf und jedes Feld beginnen auf einem Vielfachen davon.
    AUSRICHTUNG = 8
    #: Der Schlüssel, an dem der Browser einen Platzhalter erkennt.
    MARKE = '__netzfeld__'

    @classmethod
    def packen(cls, daten):
        u"""`dict` mit Netzfeldern -> Bytes im Format oben."""
        felder = []
        kopf = cls._ersetzen(daten, felder)
        roh = json.dumps(kopf, cls=DjangoJSONEncoder,
                         separators=(',', ':')).encode('utf-8')
        # Die Polsterung steht IM Kopf-Bereich, nicht dahinter: Die gemeldete
        # Kopflänge bleibt die des JSON, der Browser schneidet exakt.
        polster = cls._polster(len(cls.MAGIE) + 4 + len(roh))
        stuecke = [cls.MAGIE, struct.pack('<I', len(roh)), roh, b' ' * polster]
        for feld in felder:
            stuecke.append(feld.rohdaten)
            stuecke.append(b'\0' * cls._polster(len(feld.rohdaten)))
        return b''.join(stuecke)

    @classmethod
    def _polster(cls, laenge):
        rest = laenge % cls.AUSRICHTUNG
        return 0 if rest == 0 else cls.AUSRICHTUNG - rest

    @classmethod
    def _ersetzen(cls, wert, felder, versatz=None):
        u"""Rekursiv jedes Netzfeld durch seinen Platzhalter ersetzen.

        `versatz` zählt die Nutzlast mit — als einelementige Liste, weil die
        Rekursion sonst jeden Zwischenstand zurückreichen müsste.
        """
        if versatz is None:
            versatz = [0]
        if isinstance(wert, Netzfeld):
            marke = {'typ': wert.typ, 'pos': versatz[0],
                     'bytes': len(wert.rohdaten), 'anzahl': wert.anzahl}
            versatz[0] += len(wert.rohdaten) + cls._polster(len(wert.rohdaten))
            felder.append(wert)
            return {cls.MARKE: marke}
        if isinstance(wert, dict):
            return {k: cls._ersetzen(v, felder, versatz) for k, v in wert.items()}
        if isinstance(wert, (list, tuple)):
            return [cls._ersetzen(v, felder, versatz) for v in wert]
        return wert

    # ----------------------------------------------------------- Gegenprobe

    @classmethod
    def auspacken(cls, roh):
        u"""Bytes -> Wörterbuch mit Netzfeldern. Für Tests und Werkzeuge.

        Der Browser hat seinen eigenen Leser (`gemeinsam/netzpaket.js`); diese
        Fassung ist die Gegenprobe, mit der sich „gepackt == ausgepackt" ohne
        einen Browser prüfen lässt.
        """
        if not roh.startswith(cls.MAGIE):
            raise ValueError('Netzpaket: falsche Magie %r' % roh[:4])
        (kopflaenge,) = struct.unpack('<I', roh[4:8])
        kopf = json.loads(roh[8:8 + kopflaenge].decode('utf-8'))
        beginn = 8 + kopflaenge
        beginn += cls._polster(beginn)
        return cls._einsetzen(kopf, roh, beginn)

    @classmethod
    def _einsetzen(cls, wert, roh, beginn):
        if isinstance(wert, dict):
            marke = wert.get(cls.MARKE)
            if isinstance(marke, dict) and len(wert) == 1:
                ab = beginn + marke['pos']
                return Netzfeld(roh[ab:ab + marke['bytes']], marke['typ'],
                                marke['anzahl'])
            return {k: cls._einsetzen(v, roh, beginn) for k, v in wert.items()}
        if isinstance(wert, list):
            return [cls._einsetzen(v, roh, beginn) for v in wert]
        return wert
