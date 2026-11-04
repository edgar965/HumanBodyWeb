# -*- coding: utf-8 -*-
"""Combo-Boxen „Normalen“ oben auf der Testseite von 2d-3d-AI (03.11.2026).

WARUM: Edgar, 03.11.2026: „bei den jobs möchte ich eine Combo box haben, wo ich die engine auswählen kann. Default: Econ“, „aus einem Foto (per UI wählbar) oder aus mehreren“,
„zu Econs registrierung - auch hier beides“. Diese Tests halten fest: ohne Angabe gilt ECON aus allen Fotos mit Chamfer und die Seite zeigt genau das; die Wahl landet in der
job.json (mischend); ein Foto, das der Job nicht hat, eine unbekannte Engine oder Zusammenführung werden abgelehnt und nichts geschrieben; ein Export hat keine Wahl.
Ablage wie `test_ai2d3d_seiten` (nie Edgars 3DObjects).
"""

import json
from pathlib import Path

from django.test import SimpleTestCase

from core.dienste.ai2d3dnormalen import Ai2d3dnormalen
from core.tests.component.test_ai2d3d_seiten import Ai2d3dAblageMixin


class Ai2d3dNormalenWahl(Ai2d3dAblageMixin, SimpleTestCase):
    databases = set()
    ADRESSE = '/api/2d3dai/fototest/normalen/'

    def _senden(self, rumpf, adresse=None):
        return self.client.post(adresse or self.ADRESSE, json.dumps(rumpf), content_type='application/json')

    def _info(self):
        return json.loads((self.objekte / 'ai2d3d' / 'Fototest' / 'job.json').read_text(encoding='utf-8'))

    def test_vorgabe_econ_alle_fotos_chamfer_auf_der_seite(self):
        self.assertEqual(Ai2d3dnormalen.lesen({}), {'engine': 'econ', 'foto': None, 'zusammen': 'chamfer'})
        text = self.client.get('/2d-3d-AI/test/fototest/').content.decode('utf-8')
        self.assertIn('id="ai2d3d-normalen"', text)
        self.assertIn('<option value="econ" ', text)
        self.assertRegex(text, r'<option value="econ"[^>]* selected>')
        self.assertRegex(text, r'<option value=""[^>]*>aus allen Fotos')

    def test_wahl_landet_in_der_job_json_und_die_anderen_felder_bleiben(self):
        foto = Path(self._info()['fotos'][1]['datei']).name
        antwort = self._senden({'engine': 'econ', 'foto': foto, 'zusammen': 'register'})
        self.assertEqual(antwort.status_code, 200, antwort.content)
        info = self._info()
        self.assertEqual(info['normalen'], {'engine': 'econ', 'foto': foto, 'zusammen': 'register'})
        self.assertEqual(info['name'], 'Fototest')
        self.assertRegex(self.client.get('/2d-3d-AI/test/fototest/').content.decode('utf-8'), r'<option value="register" selected>')

    def test_falsches_wird_abgelehnt_und_nichts_geschrieben(self):
        for rumpf in ({'engine': 'zauber'}, {'engine': 'econ', 'zusammen': 'poisson'}, {'engine': 'econ', 'foto': 'gibtsnicht.jpg'}):
            self.assertEqual(self._senden(rumpf).status_code, 400, rumpf)
            self.assertNotIn('normalen', self._info())

    def test_export_hat_keine_wahl(self):
        self.assertEqual(self._senden({'engine': 'econ'}, '/api/2d3dai/probe/normalen/').status_code, 400)
        self.assertNotIn('id="ai2d3d-normalen"', self.client.get('/2d-3d-AI/probe/').content.decode('utf-8'))

    def test_unbrauchbares_in_der_datei_gilt_als_vorgabe(self):
        self.assertEqual(Ai2d3dnormalen.lesen({'normalen': {'engine': 'zauber'}})['engine'], 'econ')
        self.assertEqual(Ai2d3dnormalen.lesen({'normalen': {'engine': 'pshuman', 'foto': '1.jpg'}}), {'engine': 'pshuman', 'foto': '1.jpg', 'zusammen': 'chamfer'})
