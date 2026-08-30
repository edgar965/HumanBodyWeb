# -*- coding: utf-8 -*-
"""Netzkanal — die Faelle ueber das Netz an den laufenden Server.

Aus `kanal.py` herausgeloest (29.08.2026, Befund `klassen-je-datei`): Dort
standen drei eigenstaendige Klassen in einer Datei.

DIESE FASSUNG BLEIBT, WEIL ES SIE BRAUCHT: `Docu/umbau/server_neu.py` und
die Werkzeuge fahren die Faelle gegen den ECHTEN Server mit den echten
Daten — das ist eine andere Aussage als der in-process-Lauf, wo die
Datenbank leer ist.
"""

import json
import urllib.error
import urllib.request

from .kanal import BASE_URL, Kanal


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
