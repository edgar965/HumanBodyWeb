# -*- coding: utf-8 -*-
"""Clientkanal — die Faelle in-process ueber `django.test.Client`.

Aus `kanal.py` herausgeloest (29.08.2026, Befund `klassen-je-datei`).

DAS IST DER WEG IM TESTLAUF: Testdatenbank, Wegwerf-Medienordner, kein
laufender Server noetig. Bis zum 28.08.2026 gingen die Bundle-Faelle daran
vorbei und redeten mit dem Dev-Server — sie kippten bei Nebenlast um und
schrieben in die echten Mediendaten.
"""

import json
from pathlib import Path

from .kanal import Kanal


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
