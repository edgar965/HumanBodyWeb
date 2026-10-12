# -*- coding: utf-8 -*-
"""Einstellungen → Charakter → „Netzantworten der Genesis-Figuren" (`/settings/charakter/`): im RAM halten (Vorgabe) oder jedes Mal vom Server holen.

Edgar (12.10.2026): „mach das einstellbar im RAM, einstellbar unter Einstellungen - Charakter. Default: RAM." Die Wahl liegt in `AppSettings.ui_prefs['netzantworten']`
(`Netzantwortwahl`), Vorgabe `ram`; die Szene liest sie über `/api/settings/humanbody/` (`Starteinstellungen` → `Genesis9antwortspeicher.einstellen`).

1. Die Seite bietet beide Wahlen an und wählt ohne gespeicherten Wert „RAM" vor.
2. Speichern merkt „server", die Seite zeigt es wieder, und die Schnittstelle der Szene liefert es in `ui_prefs`.
3. Ein unbekannter Wert wird nicht gespeichert (die alte Wahl bleibt); ein Formular ohne das Feld lässt sie ebenfalls stehen.
4. Zurück auf „ram" geht.

Sabotage-Gegenprobe (nicht gefahren): in `szenenseite.py` `if halten in Netzantwortwahl.WAHLEN:` → `if halten:` → Fall 3 rot.
"""

import re

from django.test import Client, TestCase
from django.urls import reverse

from core.dienste.netzantwortwahl import Netzantwortwahl
from core.models import AppSettings


class NetzantwortenWahlTest(TestCase):
    def setUp(self):
        self.client = Client(HTTP_HOST='127.0.0.1')
        s = AppSettings.load()
        s.ui_prefs = {k: v for k, v in (s.ui_prefs or {}).items() if k != Netzantwortwahl.SCHLUESSEL}
        s.save()

    def _gewaehlt_in_seite(self):
        """Die `<option selected>`-Werte und alle Werte im Feld `netzantworten`."""
        text = self.client.get(reverse('settings_scene')).content.decode('utf-8')
        feld = re.search(r'<select[^>]*name="netzantworten".*?</select>', text, re.S)
        self.assertIsNotNone(feld, 'Das Feld „Netzantworten" fehlt auf der Seite')
        optionen = re.findall(r'<option value="([^"]*)"([^>]*)>', feld.group(0))
        return [w for w, rest in optionen if 'selected' in rest], [w for w, _ in optionen]

    def _speichern(self, **felder):
        antwort = self.client.post(reverse('settings_scene'), felder)
        self.assertEqual(antwort.status_code, 302)

    def _gespeichert(self):
        return Netzantwortwahl.aus(AppSettings.load().ui_prefs)

    def test_1_die_seite_bietet_beide_wahlen_an_und_waehlt_ram_vor(self):
        gewaehlt, alle = self._gewaehlt_in_seite()
        self.assertEqual(alle, ['ram', 'server'])
        self.assertEqual(gewaehlt, ['ram'])
        self.assertEqual(self._gespeichert(), 'ram')

    def test_2_server_wird_gemerkt_und_der_szene_geliefert(self):
        self._speichern(netzantworten='server')
        self.assertEqual(self._gewaehlt_in_seite()[0], ['server'])
        self.assertEqual(self._gespeichert(), 'server')
        daten = self.client.get('/api/settings/humanbody/').json()
        self.assertEqual(daten['ui_prefs'][Netzantwortwahl.SCHLUESSEL], 'server')

    def test_3_unbekanntes_und_fehlendes_aendern_die_wahl_nicht(self):
        self._speichern(netzantworten='server')
        self._speichern(netzantworten='unsinn')
        self.assertEqual(self._gespeichert(), 'server')
        self._speichern()
        self.assertEqual(self._gespeichert(), 'server')

    def test_4_zurueck_auf_ram(self):
        self._speichern(netzantworten='server')
        self._speichern(netzantworten='ram')
        self.assertEqual(self._gespeichert(), 'ram')
        self.assertEqual(self._gewaehlt_in_seite()[0], ['ram'])
