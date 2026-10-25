# -*- coding: utf-8 -*-
"""Einstellungen → 2d-3d-AI (24.10.2026): die Seite, das Speichern über `/api/ui-prefs/` und der Weg bis zum Rechenlauf (`Fotogelenke`).

WARUM: Edgar, 24.10.2026: „Mach auch du eine Seite Einstellungen - 2d-3d-KI wo du sowas einstellen kannst, damit man das später beides ausprobieren kann?“. Ein Wert, der auf der Seite
steht, aber beim Lauf nicht ankommt, sähe aus wie gewählt und rechnete doch mit der Vorgabe — darum geht der Test durch alle Schichten: Seite lesen, speichern, Seite wieder lesen, Lauf.
"""
import json
import sys

from django.conf import settings
from django.test import TestCase

sys.path.insert(0, str(settings.TOOLS_ROOT))

from KoerperKI_Fotos.fotogelenke import Fotogelenke  # noqa: E402

from core.dienste.ai2d3dposewahl import Ai2d3dposewahl  # noqa: E402


class DieEinstellungsseite(TestCase):
    ADRESSE = '/settings/2d-3d-ai/'

    def _speichern(self, wert):
        antwort = self.client.post('/api/ui-prefs/', json.dumps({Ai2d3dposewahl.SCHLUESSEL: wert}), content_type='application/json')
        self.assertEqual(antwort.status_code, 200)

    def _seite(self):
        antwort = self.client.get(self.ADRESSE)
        self.assertEqual(antwort.status_code, 200)
        return antwort.content.decode('utf-8')

    def test_beide_quellen_und_die_vorgabe_gewaehlt(self):
        html = self._seite()
        self.assertIn('id="ai2d3d-settings-form"', html)
        self.assertIn('name="%s"' % Ai2d3dposewahl.SCHLUESSEL, html)
        self.assertIn('<option value="vitpose" selected>', html)
        self.assertIn('<option value="sam3dbody">', html)
        for _w, text in Ai2d3dposewahl.WERTE:
            self.assertIn(text, html)

    def test_gespeicherte_quelle_gilt_fuer_seite_und_lauf(self):
        self._speichern('sam3dbody')
        html = self._seite()
        self.assertIn('<option value="sam3dbody" selected>', html)
        self.assertIn('<option value="vitpose">', html)
        self.assertEqual(Ai2d3dposewahl.gewaehlt(), 'sam3dbody')
        self.assertEqual(Fotogelenke().quelle, 'sam3dbody')

    def test_unbekannter_wert_faellt_auf_die_vorgabe(self):
        self._speichern('sapiens')
        self.assertIn('<option value="vitpose" selected>', self._seite())
        self.assertEqual(Fotogelenke().quelle, 'vitpose')

    def test_im_menue_der_einstellungen(self):
        self.assertIn('href="%s"' % self.ADRESSE, self._seite())
