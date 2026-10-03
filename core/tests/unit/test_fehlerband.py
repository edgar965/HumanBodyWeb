# -*- coding: utf-8 -*-
"""Das Fehlerband der Auftragsseiten (02.10.2026): eine Meldung bleibt stehen, bis jemand OK klickt.

Edgar: „die Fehlermeldung verschwindet nach ein paar s. Mach die dauerhaft sichtbar, mit OK wegklickbar". Die Ursache war eine
Zeile in `zeigen()`, die bei jedem Abfragetakt das Feld leerte; das Verhalten selbst (11 Fälle) ist im Chrome durchgespielt,
hier steht, dass keine Seite mehr dorthin zurückfällt. Ein Node-Test bräuchte ein DOM — dieser Test liest die Quelltexte.
"""

import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

SEITEN = {
    'engine2d3dkleider': 'engine2d3dkleiderseite.js',
    'meshfigur': 'meshfigurseite.js',
    'blendermodell': 'blendermodellseite.js',
}


class FehlerbandTest(SimpleTestCase):
    def quelle(self, ordner, datei):
        return (Path(settings.BASE_DIR) / 'static' / 'viewer' / ordner / datei).read_text(encoding='utf-8')

    def test_jede_seite_mit_dem_fehlerfeld_nimmt_das_fehlerband(self):
        for ordner, datei in SEITEN.items():
            text = self.quelle(ordner, datei)
            self.assertIn("import { Fehlerband } from '../gemeinsam/fehlerband.js';", text, ordner)
            self.assertIn('this.fehlerband = new Fehlerband();', text, ordner)

    def test_der_abfragetakt_leert_das_feld_nicht_mehr(self):
        """Das war der Fehler: `this.fehler(z.status === 'gescheitert' ? … : '')` in `zeigen()`."""
        for ordner, datei in SEITEN.items():
            text = self.quelle(ordner, datei)
            self.assertNotRegex(text, r"this\.fehler\(\s*z\.status\s*===", ordner)
            self.assertIn('this.fehlerband.auftrag(z)', text, ordner)
            self.assertNotIn("getElementById('fehler')", text, '%s schreibt das Feld an dem Band vorbei' % ordner)

    def test_ein_lesefehler_kommt_nach_ok_nicht_alle_paar_sekunden_zurueck(self):
        for ordner, datei in SEITEN.items():
            text = self.quelle(ordner, datei)
            self.assertIn('this.fehlerband.lesefehler(`Zustand nicht lesbar', text, ordner)
            self.assertNotRegex(text, r"this\.fehler\(`Zustand nicht lesbar", ordner)

    def test_das_band_haengt_am_fenster_damit_man_es_auch_weiter_unten_sieht(self):
        css = (Path(settings.BASE_DIR) / 'static' / 'css' / 'bildmodell.css').read_text(encoding='utf-8')
        regel = re.search(r'\.bildmodell-fehler\.bildmodell-fehler-fest \{(.*?)\}', css, re.S)
        self.assertIsNotNone(regel, 'Regel für das feste Fehlerband fehlt')
        self.assertIn('position: fixed', regel.group(1))
        # Undurchsichtig: sonst schiene der Inhalt hinter dem Band durch.
        self.assertIn('var(--bg-card', regel.group(1))

    def test_das_band_hat_einen_ok_knopf(self):
        text = self.quelle('gemeinsam', 'fehlerband.js')
        self.assertIn("this.ok.textContent = 'OK';", text)
        self.assertIn("this.ok.addEventListener('click'", text)
