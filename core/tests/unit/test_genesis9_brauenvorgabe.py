# -*- coding: utf-8 -*-
"""Die Brauenstil-Auswahl zeigt, was der Server zeichnet (Edgar, 10.10.2026, Asian: „ändern funktioniert nicht").

Bei leerem `brauenstil` zeichnet der Server Karte 06 (`G9brauen.VORGABE`). Die Auswahl zeigte bis dahin den ERSTEN Eintrag der Liste
(`inst.brauenstil || stile[0].id`, damals „MB Olesia Brows Apply"): angezeigt ein anderer Stil als gezeichnet, und wer den angezeigten
Eintrag wählte, löste kein `change` aus — nichts passierte. Geprüft wird am Quelltext (die Methode baut DOM und hängt an der Szene):
die Vorgabe der Oberfläche ist dieselbe wie die des Servers, und Auswahl wie Farbliste gehen über `stilJetzt()`.
"""
import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from Genesis9.brauen import G9brauen

QUELLE = Path(settings.BASE_DIR) / 'static' / 'viewer' / 'charakter' / 'genesis9' / 'genesis9eigenschaften.js'


class Genesis9brauenvorgabeTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.text = QUELLE.read_text(encoding='utf-8')

    def test_1_vorgabe_der_oberflaeche_ist_die_des_servers(self):
        treffer = re.search(r"static BRAUENVORGABE = '([a-z0-9]+)';", self.text)
        self.assertIsNotNone(treffer, 'BRAUENVORGABE fehlt in genesis9eigenschaften.js')
        self.assertEqual(treffer.group(1), G9brauen.VORGABE)

    def test_2_auswahl_und_farbliste_gehen_ueber_den_gezeichneten_stil(self):
        methode = self.text.split('static _brauen(', 1)[1].split('static _wahl(', 1)[0]
        self.assertNotIn('inst.brauenstil || stile[0].id', methode, 'die Auswahl zeigt wieder den ersten Eintrag statt des gezeichneten')
        self.assertIn('stilJetzt()', methode)
        self.assertIn('artVon(stilJetzt())', methode, 'die Farbliste folgt dem Stil, der gezeichnet wird')
        self.assertNotIn('artVon(inst.brauenstil)', methode)
