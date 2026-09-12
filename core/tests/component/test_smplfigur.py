# -*- coding: utf-8 -*-
u"""SMPL-Referenzkoerper: Liste, Netz, und die vorgegebenen Masse im GarmentCode-Weg.

WARUM (Edgar, 06.09.2026: „Mit dem SMPL Modell macht das Online tool den
Fit. Baue das als Modell ein"): Diese Koerper sind die Messlatte — auf ihnen
laeuft der GarmentCode-Reiter ohne Messung, mit den Massen aus GarmentCodes
YAML. Geprueft wird, dass die Seite genau das bekommt:

    1. Die Liste nennt beide Koerper mit Geschlecht und Massen-Flag.
    2. Das Netz kommt in Metern mit Y oben (Hoehe ~1,66 m, Fuesse bei 0),
       6.890 Punkte, Dreiecke — kein Achsentausch, den Three.js nicht
       erwartet.
    3. Ein unbekannter Name ist 404, nicht 500.
    4. `/api/garmentcode/masse/` mit `koerper` liefert die YAML-Werte, jede
       Herkunft 'vorgegeben' — nichts wird gemessen.
"""
import json

from django.test import SimpleTestCase


class SmplfigurTest(SimpleTestCase):

    databases = set()

    def test_liste(self):
        antwort = self.client.get('/api/character/smpl-figur/')
        self.assertEqual(antwort.status_code, 200)
        figuren = {f['name']: f for f in json.loads(antwort.content)['figuren']}
        self.assertIn('f_smpl_average_A40', figuren)
        self.assertIn('m_smpl_average_A40', figuren)
        self.assertEqual(figuren['f_smpl_average_A40']['geschlecht'], 'female')
        self.assertTrue(figuren['f_smpl_average_A40']['masse_vorhanden'])

    def test_netz_in_metern_y_oben(self):
        antwort = self.client.get('/api/character/smpl-figur/f_smpl_average_A40/netz/')
        self.assertEqual(antwort.status_code, 200)
        daten = json.loads(antwort.content)
        self.assertEqual(len(daten['punkte']), 6890)
        self.assertGreater(len(daten['dreiecke']), 13000)
        ys = [p[1] for p in daten['punkte']]
        self.assertAlmostEqual(min(ys), 0.0, delta=0.02, msg='Fuesse nicht am Boden')
        self.assertAlmostEqual(daten['hoehe'], 1.66, delta=0.03)
        self.assertEqual(daten['geschlecht'], 'female')
        self.assertEqual(daten['masse']['bust'], 90)

    def test_unbekannter_koerper_ist_404(self):
        antwort = self.client.get('/api/character/smpl-figur/quatsch/netz/')
        self.assertEqual(antwort.status_code, 404)

    def test_garmentcode_masse_sind_vorgegeben(self):
        antwort = self.client.post('/api/garmentcode/masse/', {
            'koerper': 'f_smpl_average_A40', 'smpl': '1',
            'geschlecht': 'female', 'morphs': '{}',
        })
        self.assertEqual(antwort.status_code, 200)
        daten = json.loads(antwort.content)
        self.assertEqual(daten['masse']['bust'], 90.0)
        self.assertEqual(daten['masse']['arm_pose_angle'], 40.0)
        self.assertEqual(set(daten['herkunft'].values()), {'vorgegeben'})
