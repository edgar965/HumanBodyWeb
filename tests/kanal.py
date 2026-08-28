# -*- coding: utf-8 -*-
"""Kanal — wie ein Oberflächenfall den Server erreicht.

WARUM (Ansage 17.08.2026: „Halte dich an die djangoBase test implementierung und
baue nichts neues, leite nur ab")
=====================================================================
Die 127 Oberflächenfälle liefen über einen EIGENEN Läufer: eine eigene API
(`/api/tests/run/`), eine eigene Seite und `urllib`-Aufrufe an den laufenden
Server. Damit standen sie außerhalb von `manage.py test` — und außerhalb von
allem, was djangoBase an Testseite, Laufzeiten und Deckung mitbringt.

Jetzt sind sie reguläre Django-Tests (`core/tests/ui/test_oberflaeche.py`), und
diese Klasse ist die eine Stelle, die den Unterschied kennt:

    ClientKanal   im Testlauf: `django.test.Client`, in-process, Testdatenbank
    NetzKanal     außerhalb: `urllib` an den laufenden Server (127.0.0.1:8081)

DER NETZKANAL BLEIBT, WEIL ES IHN NOCH BRAUCHT
==============================================
`Docu/umbau/server_neu.py` und die Werkzeuge fahren die Fälle gegen den ECHTEN
Server mit den echten Daten — das ist eine andere Aussage als der in-process-Lauf
(dort ist die Datenbank leer). Beides soll möglich bleiben; die Fälle selbst
merken davon nichts.

**`127.0.0.1`, nicht `localhost`** (gemessen 17.08.2026, je dreimal):

    http://localhost:8081/api/ui-prefs/   2,113 / 2,062 / 2,058 s
    http://127.0.0.1:8081/api/ui-prefs/   0,019 / 0,015 / 0,025 s

Die zwei Sekunden sind kein Django, sondern die IPv6-Auflösung im Client:
Windows liefert für `localhost` erst `::1`, der Server hört auf IPv4, der Versuch
läuft in einen Timeout, dann kommt `127.0.0.1`. Ein verdächtig runder, über
Wiederholungen konstanter Wert ist fast nie Last, sondern ein Timeout.
"""

import json
import logging
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request

#: Adresse des laufenden Dev-Servers (siehe Modul-Docstring).
BASE_URL = 'http://127.0.0.1:8081'


class Kanal:
    """Basis: wer eine Anfrage schickt, liefert `(status, wörterbuch)`."""

    #: Der gerade gültige Kanal. Der Testlauf setzt ihn auf `ClientKanal`.
    _aktiv = None

    @classmethod
    def aktueller(cls):
        if cls._aktiv is None:
            cls._aktiv = NetzKanal()
        return cls._aktiv

    @classmethod
    def setzen(cls, kanal):
        """Kanal wechseln; liefert den vorherigen zurück (für `finally`)."""
        vorher = cls._aktiv
        cls._aktiv = kanal
        return vorher

    def senden(self, pfad, method='GET', data=None, files=None, timeout=15):
        raise NotImplementedError

    # ---------------------------------------------------------------- Hilfen

    @staticmethod
    def _mehrteilig(files, grenze='----TestBoundary9876xyz'):
        """`multipart/form-data` — von beiden Kanälen gebraucht.

        `files` ist entweder ein Wörterbuch
        ``{name: (dateiname, inhalt, typ)}`` oder eine LISTE aus
        ``(name, dateiname|None, inhalt, typ)``. Die Listenform gibt es seit
        dem 28.08.2026: Ein Bundle-Upload schickt neben der Datei ein
        normales Textfeld (`bundleId`) mit, und dafür muss `filename`
        fehlen dürfen — mit `filename` macht Django daraus eine Datei, und
        `request.POST` bleibt leer.
        """
        eintraege = (files if isinstance(files, (list, tuple))
                     else [(name, wert[0], wert[1], wert[2])
                           for name, wert in files.items()])
        rumpf = b''
        for name, dateiname, inhalt, typ in eintraege:
            rumpf += ('--%s\r\n' % grenze).encode()
            if dateiname is None:
                rumpf += ('Content-Disposition: form-data; name="%s"\r\n\r\n'
                          % name).encode()
            else:
                rumpf += ('Content-Disposition: form-data; name="%s"; '
                          'filename="%s"\r\n' % (name, dateiname)).encode()
                rumpf += ('Content-Type: %s\r\n\r\n' % typ).encode()
            rumpf += (inhalt if isinstance(inhalt, bytes)
                      else str(inhalt).encode()) + b'\r\n'
        rumpf += ('--%s--\r\n' % grenze).encode()
        return rumpf, 'multipart/form-data; boundary=%s' % grenze

    def rohabruf(self, pfad, timeout=10):
        """Den Inhalt einer Adresse als BYTES — für Dateien, nicht für JSON.

        Ein Bundle-Test lädt eine `.mtl` hoch und liest sie danach zurück;
        `senden()` würde daraus ein Wörterbuch machen wollen.
        """
        raise NotImplementedError

    @staticmethod
    def _lesen(status, text):
        """Antworttext als Wörterbuch — Rohtext, wenn es kein JSON ist.

        Der Rohtext geht als `_raw` in den Bericht: Er sagt mehr als
        „Expecting value: line 1 column 1".
        """
        try:
            return status, json.loads(text)
        except (json.JSONDecodeError, TypeError):
            # Kein Fehlerfall, sondern der Normalfall bei HTML-Antworten (eine
            # Seite, eine Fehlerseite, eine Datei). Der Rohtext geht als `_raw`
            # in den Bericht — er sagt mehr als „Expecting value: line 1".
            # Auf `debug`, weil die Pruefungen absichtlich auch Seiten abrufen.
            logging.getLogger('core').debug('Antwort ist kein JSON (%d Zeichen)',
                                            len(text or ''))
            return status, {'_raw': text}


class NetzKanal(Kanal):
    """Über das Netz an den laufenden Server."""

    def senden(self, pfad, method='GET', data=None, files=None, timeout=15):
        adresse = BASE_URL + pfad
        if files:
            rumpf, typ = self._mehrteilig(files)
            anfrage = urllib.request.Request(adresse, data=rumpf, method=method)
            anfrage.add_header('Content-Type', typ)
        elif data is not None:
            anfrage = urllib.request.Request(adresse,
                                             data=json.dumps(data).encode(),
                                             method=method)
            anfrage.add_header('Content-Type', 'application/json')
        else:
            anfrage = urllib.request.Request(adresse, method=method)
        try:
            with urllib.request.urlopen(anfrage, timeout=timeout) as antwort:
                return self._lesen(antwort.status, antwort.read().decode())
        except urllib.error.HTTPError as fehler:
            try:
                return fehler.code, json.loads(fehler.read().decode())
            except Exception as roh:                              # noqa: BLE001
                # Beide Gruende in den Bericht: der Statuscode UND warum sein
                # Rumpf nicht lesbar war.
                return fehler.code, {
                    'error': '%s (Fehlerrumpf unlesbar: %s)' % (fehler, roh)}
        except Exception as fehler:                               # noqa: BLE001
            return 0, {'error': str(fehler)}


    def rohabruf(self, pfad, timeout=10):
        adresse = pfad if pfad.startswith('http') else BASE_URL + pfad
        try:
            with urllib.request.urlopen(adresse, timeout=timeout) as antwort:
                return antwort.status, antwort.read()
        except urllib.error.HTTPError as fehler:
            return fehler.code, b''
        except Exception as fehler:                               # noqa: BLE001
            # Der Grund gehoert in den Bericht: Ein Aufrufer sieht sonst nur
            # „HTTP 0" und weiss nicht, ob der Server aus war, der Name nicht
            # aufloeste oder die Zeit ablief.
            return 0, str(fehler).encode('utf-8', 'replace')


class ClientKanal(Kanal):
    """In-process über `django.test.Client` — im `manage.py test`-Lauf."""

    def __init__(self, client):
        self.client = client

    def senden(self, pfad, method='GET', data=None, files=None, timeout=15):
        try:
            antwort = self._anfahren(pfad, method, data, files)
        except Exception as fehler:                               # noqa: BLE001
            # Eine Ausnahme in der View ist das Ergebnis des Falls, nicht ein
            # Abbruch des Laufs — genauso wie beim Netzkanal (dort waere es 500).
            return 0, {'error': '%s: %s' % (type(fehler).__name__, fehler)}
        text = antwort.content.decode('utf-8', errors='replace')
        return self._lesen(antwort.status_code, text)

    def _anfahren(self, pfad, method, data, files):
        if files:
            rumpf, typ = self._mehrteilig(files)
            return self.client.generic(method, pfad, rumpf, content_type=typ)
        if data is not None:
            return self.client.generic(method, pfad, json.dumps(data),
                                       content_type='application/json')
        return self.client.generic(method, pfad)

    def rohabruf(self, pfad, timeout=10):
        """In-process — die Datei kommt aus der Antwort des Testclients.

        `MEDIA_URL`-Adressen bedient der Testclient NICHT: Statik und Medien
        liefert im Testlauf niemand aus. Deshalb wird eine Medienadresse
        direkt von der Platte gelesen; das ist dieselbe Datei, die die
        Ansicht gerade geschrieben hat.
        """
        from django.conf import settings
        if pfad.startswith(str(settings.MEDIA_URL)):
            rest = pfad[len(str(settings.MEDIA_URL)):].split('?')[0]
            datei = Path(settings.MEDIA_ROOT) / rest
            if not datei.is_file():
                return 404, b''
            return 200, datei.read_bytes()
        try:
            antwort = self.client.get(pfad)
        except Exception as fehler:                               # noqa: BLE001
            return 0, str(fehler).encode('utf-8', 'replace')
        return antwort.status_code, antwort.content
