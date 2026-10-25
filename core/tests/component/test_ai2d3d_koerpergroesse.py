# -*- coding: utf-8 -*-
"""Feld „Körpergröße“ oben auf der Testseite von 2d-3d-AI (24.10.2026).

WARUM: Edgar, 24.10.2026: „körpergröße kann ich angeben im Job oben, erstmal, mach ein UI dazu, 1,85 m“. Echte Fotos tragen keinen Maßstab; der dritte Einpass-Lauf schrumpfte die Figur
von 1,710 auf 1,435 m, während die Deckung stieg. Diese Tests halten fest: Die Angabe landet in der job.json (mischend, andere Felder bleiben), steht in Seite und Seitendaten, ein Tippfehler
(185 statt 1,85) wird abgelehnt und nichts geschrieben, leer löscht die Angabe, und ein Export (mit Wahrheit) bekommt keine. Ablage wie `test_ai2d3d_seiten` (nie Edgars 3DObjects).
"""

import json

from django.test import SimpleTestCase

from core.dienste.ai2d3dkoerpergroesse import Ai2d3dkoerpergroesse
from core.tests.component.test_ai2d3d_seiten import Ai2d3dAblageMixin


class Ai2d3dKoerpergroesseFeld(Ai2d3dAblageMixin, SimpleTestCase):
    databases = set()
    ADRESSE = '/api/2d3dai/fototest/koerpergroesse/'

    def _senden(self, rumpf, adresse=None):
        return self.client.post(adresse or self.ADRESSE, json.dumps(rumpf), content_type='application/json')

    def _info(self):
        return json.loads((self.objekte / 'ai2d3d' / 'Fototest' / 'job.json').read_text(encoding='utf-8'))

    def test_angabe_landet_in_der_job_json_und_die_anderen_felder_bleiben(self):
        antwort = self._senden({'koerpergroesse_m': 1.85})
        self.assertEqual(antwort.status_code, 200, antwort.content)
        self.assertEqual(antwort.json()['koerpergroesse_m'], 1.85)
        info = self._info()
        self.assertEqual(info['koerpergroesse_m'], 1.85)
        self.assertEqual(info['name'], 'Fototest')
        self.assertEqual(len(info['fotos']), 2)

    def test_komma_als_dezimalzeichen_wird_verstanden(self):
        self.assertEqual(self._senden({'koerpergroesse_m': '1,85'}).json()['koerpergroesse_m'], 1.85)

    def test_seite_und_seitendaten_zeigen_die_angabe(self):
        self._senden({'koerpergroesse_m': 1.85})
        text = self.client.get('/2d-3d-AI/test/fototest/').content.decode('utf-8')
        self.assertIn('id="ai2d3d-groesse"', text)
        # `unlocalize`: ein deutsches „1,85“ wäre für <input type=number> kein Wert, das Feld bliebe leer
        self.assertIn('value="1.85"', text)
        self.assertIn('"koerpergroesse_m": 1.85', text)

    def test_tippfehler_wird_abgelehnt_und_nichts_geschrieben(self):
        for falsch in (185, 0.5, 'groß', True):
            antwort = self._senden({'koerpergroesse_m': falsch})
            self.assertEqual(antwort.status_code, 400, falsch)
            self.assertNotIn('koerpergroesse_m', self._info())

    def test_leer_loescht_die_angabe(self):
        self._senden({'koerpergroesse_m': 1.85})
        self.assertIsNone(self._senden({'koerpergroesse_m': None}).json()['koerpergroesse_m'])
        self.assertNotIn('koerpergroesse_m', self._info())

    def test_ohne_feld_im_rumpf_400(self):
        self.assertEqual(self._senden({'groesse': 1.85}).status_code, 400)

    def test_export_hat_keine_koerpergroesse(self):
        self.assertEqual(self._senden({'koerpergroesse_m': 1.85}, '/api/2d3dai/probe/koerpergroesse/').status_code, 400)
        self.assertNotIn('id="ai2d3d-groesse"', self.client.get('/2d-3d-AI/probe/').content.decode('utf-8'))

    def test_unbekannter_job_404(self):
        self.assertEqual(self._senden({'koerpergroesse_m': 1.85}, '/api/2d3dai/gibtsnicht/koerpergroesse/').status_code, 404)

    def test_unbrauchbarer_wert_in_der_datei_gilt_als_unbekannt(self):
        self.assertIsNone(Ai2d3dkoerpergroesse.lesen({'koerpergroesse_m': 185}))
        self.assertIsNone(Ai2d3dkoerpergroesse.lesen({}))
        self.assertEqual(Ai2d3dkoerpergroesse.lesen({'koerpergroesse_m': 1.854}), 1.85)
