# -*- coding: utf-8 -*-
"""SMPL-X-Referenzkoerper: Liste, Netz, Skelett und die vorgegebenen Masse.

WARUM (Edgar, 06.09.2026: „Mit dem SMPL Modell macht das Online tool den
Fit. Baue das als Modell ein"; 15.09.2026: „kannst du die SMPL Modelle auf
SMPL-X umstellen (also inkl. Gesichtsknochen)?"): Diese Koerper sind die
Messlatte — auf ihnen laeuft der GarmentCode-Reiter ohne Messung, mit den
Massen aus GarmentCodes YAML. Geprueft wird, dass die Seite genau das
bekommt:

    1. Die Liste nennt die SMPL-X-Durchschnitte (nicht mehr die
       SMPL-Durchschnitte des Tools) mit Geschlecht und Massen-Flag.
    2. Das Netz kommt in Metern mit Y oben (Hoehe ~1,66 m, Fuesse bei 0),
       10.475 Punkte, Dreiecke — und ein Skelett mit 55 Gelenken: Kiefer,
       Augen, Finger dabei, Handflaechen nicht; Hautgewichte fuer 55 Knochen.
    3. Der alte Name `f_smpl_average_A40` bleibt ladbar (gespeicherte
       Szenen) und bekommt das SMPL-X-Skelett UEBERTRAGEN.
    4. Ein unbekannter Name ist 404, nicht 500.
    5. `/api/garmentcode/masse/` mit `koerper` liefert die YAML-Werte, jede
       Herkunft 'vorgegeben' — nichts wird gemessen.

Ohne Modelldateien (`SMPLX_MODELS_DIR`) fallen 2 und 3 auf Uebersprung.
"""

import json

from django.conf import settings
from django.test import SimpleTestCase

from ...dienste.smplxrig import Smplxrig


class SmplfigurTest(SimpleTestCase):
    databases = set()

    def _modell_noetig(self):
        if not Smplxrig.vorhanden('female'):
            self.skipTest('SMPL-X-Modelldateien fehlen unter %s' % settings.SMPLX_MODELS_DIR)

    def test_die_liste_nennt_mean_all_und_verschweigt_a40(self):
        antwort = self.client.get('/api/character/smpl-figur/')
        self.assertEqual(antwort.status_code, 200)
        figuren = {f['name']: f for f in json.loads(antwort.content)['figuren']}
        self.assertIn('mean_all', figuren)
        self.assertNotIn('f_smpl_average_A40', figuren)
        if Smplxrig.vorhanden('female'):
            self.assertIn('smplx_female', figuren)
            self.assertIn('smplx_male', figuren)
            self.assertEqual(figuren['smplx_female']['geschlecht'], 'female')
            self.assertTrue(figuren['smplx_female']['smpl'])
            self.assertTrue(figuren['smplx_female']['masse_vorhanden'])
            self.assertIn('SMPL-X', figuren['smplx_female']['anzeige'])

    def test_netz_in_metern_y_oben_mit_smplx_skelett(self):
        self._modell_noetig()
        antwort = self.client.get('/api/character/smpl-figur/smplx_female/netz/')
        self.assertEqual(antwort.status_code, 200)
        daten = json.loads(antwort.content)
        self.assertEqual(len(daten['punkte']), 10475)
        self.assertEqual(len(daten['dreiecke']), 20908)
        ys = [p[1] for p in daten['punkte']]
        self.assertAlmostEqual(min(ys), 0.0, delta=0.02, msg='Fuesse nicht am Boden')
        self.assertAlmostEqual(daten['hoehe'], 1.66, delta=0.03)
        self.assertEqual(daten['geschlecht'], 'female')
        self.assertEqual(daten['masse']['bust'], 90)
        skelett = daten['skelett']
        self.assertEqual(skelett['name'], 'SMPL-X (55 Gelenke)')
        namen = [k['name'] for k in skelett['knochen']]
        for gelenk in ('Pelvis', 'Left_wrist', 'Jaw', 'Left_eye', 'Right_eye', 'left_index1', 'right_thumb3'):
            self.assertIn(gelenk, namen)
        self.assertNotIn('Left_palm', namen)
        haut = daten['hautgewichte']
        self.assertEqual(len(haut['knochen']), 55)
        self.assertEqual(haut['knochen'][22:25], ['Jaw', 'Left_eye', 'Right_eye'])

    def test_alter_smpl_name_bleibt_ladbar_und_bekommt_das_skelett_uebertragen(self):
        self._modell_noetig()
        antwort = self.client.get('/api/character/smpl-figur/f_smpl_average_A40/netz/')
        self.assertEqual(antwort.status_code, 200)
        daten = json.loads(antwort.content)
        self.assertEqual(len(daten['punkte']), 6890)
        self.assertEqual(daten['skelett']['name'], 'SMPL-X (55 Gelenke), uebertragen')
        self.assertEqual(len(daten['hautgewichte']['knochen']), 55)

    def test_unbekannter_koerper_ist_404(self):
        antwort = self.client.get('/api/character/smpl-figur/quatsch/netz/')
        self.assertEqual(antwort.status_code, 404)

    def test_garmentcode_masse_sind_vorgegeben(self):
        antwort = self.client.post(
            '/api/garmentcode/masse/',
            {
                'koerper': 'f_smpl_average_A40',
                'smpl': '1',
                'geschlecht': 'female',
                'morphs': '{}',
            },
        )
        self.assertEqual(antwort.status_code, 200)
        daten = json.loads(antwort.content)
        self.assertEqual(daten['masse']['bust'], 90.0)
        self.assertEqual(daten['masse']['arm_pose_angle'], 40.0)
        self.assertEqual(set(daten['herkunft'].values()), {'vorgegeben'})
