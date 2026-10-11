# -*- coding: utf-8 -*-
"""Einstellungen → Charakter → „Backen" (`/settings/charakter/`): womit der Blender-Import die Haut bäckt — „Lokal" (GPU, ohne Blender) oder „Blender" (Cycles).

Edgar (10.10.2026): „Die Pipeline soll einstellbar sein, mach dazu ein Option Backen bei Einstellungen - Charakter, mit Option ‚Lokal' und ‚Blender'." Die Wahl liegt in
`AppSettings.ui_prefs['blendimport_backen']` (`Blendimportbackenwahl`), Vorgabe `lokal`; gelesen wird sie, wenn der Schritt „haut" beginnt.

1. Die Seite bietet beide Wahlen an und wählt ohne gespeicherten Wert „Lokal" vor.
2. Speichern merkt „Blender" und die Seite zeigt es wieder; `Blendimportbackenwahl.gewaehlt()` liest es.
3. Ein unbekannter Wert wird nicht gespeichert (die alte Wahl bleibt); ein Formular ohne das Feld lässt sie ebenfalls stehen.
4. Zurück auf „Lokal" geht.

Sabotage-Gegenprobe (11.10.2026): in `szenenseite.py` `if wahl in Blendimportbackenwahl.WAHLEN:` → `if wahl:` → Fall 3 rot (ein unbekannter Wert wurde gespeichert), danach rückgängig.
"""

import re

from django.test import Client, TestCase
from django.urls import reverse

from core.dienste.blendimportbackenwahl import Blendimportbackenwahl
from core.models import AppSettings


class BackenWahlTest(TestCase):
    def setUp(self):
        self.client = Client(HTTP_HOST='127.0.0.1')
        s = AppSettings.load()
        s.ui_prefs = {k: v for k, v in (s.ui_prefs or {}).items() if k != Blendimportbackenwahl.SCHLUESSEL}
        s.save()

    def _seite(self):
        return self.client.get(reverse('settings_scene')).content.decode('utf-8')

    def _gewaehlt_in_seite(self):
        """Der Wert der `<option selected>` im Feld `blendimport_backen`."""
        text = self._seite()
        feld = re.search(r'<select[^>]*name="blendimport_backen".*?</select>', text, re.S)
        self.assertIsNotNone(feld, 'Das Feld „Backen" fehlt auf der Seite')
        optionen = re.findall(r'<option value="([^"]*)"([^>]*)>', feld.group(0))
        return [w for w, rest in optionen if 'selected' in rest], [w for w, _ in optionen]

    def _speichern(self, **felder):
        antwort = self.client.post(reverse('settings_scene'), felder)
        self.assertEqual(antwort.status_code, 302)

    def test_1_die_seite_bietet_beide_wahlen_an_und_waehlt_lokal_vor(self):
        gewaehlt, alle = self._gewaehlt_in_seite()
        self.assertEqual(alle, ['lokal', 'blender'])
        self.assertEqual(gewaehlt, ['lokal'])
        self.assertEqual(Blendimportbackenwahl.gewaehlt(), 'lokal')

    def test_2_blender_wird_gemerkt_und_gelesen(self):
        self._speichern(blendimport_backen='blender')
        self.assertEqual(self._gewaehlt_in_seite()[0], ['blender'])
        self.assertEqual(AppSettings.load().ui_prefs[Blendimportbackenwahl.SCHLUESSEL], 'blender')
        self.assertEqual(Blendimportbackenwahl.gewaehlt(), 'blender')

    def test_3_unbekanntes_und_fehlendes_aendern_die_wahl_nicht(self):
        self._speichern(blendimport_backen='blender')
        self._speichern(blendimport_backen='unsinn')
        self.assertEqual(Blendimportbackenwahl.gewaehlt(), 'blender')
        self._speichern()
        self.assertEqual(Blendimportbackenwahl.gewaehlt(), 'blender')

    def test_4_zurueck_auf_lokal(self):
        self._speichern(blendimport_backen='blender')
        self._speichern(blendimport_backen='lokal')
        self.assertEqual(Blendimportbackenwahl.gewaehlt(), 'lokal')
        self.assertEqual(self._gewaehlt_in_seite()[0], ['lokal'])
