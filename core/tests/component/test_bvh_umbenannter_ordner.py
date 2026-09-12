# -*- coding: utf-8 -*-
u"""Ein umbenannter Bibliotheksordner lässt gespeicherte Projekte nicht stumm.

Edgar (12.09.2026, BVH Studio): „animation abspielen funktioniert nicht" —
„siehe logs": `GET /api/retarget/?category=Results&name=00001_Dance1 404`.
Der Ordner hieß seit 22:20 `A_Results`; das Projekt TechnoDance nannte
seinen Clip weiter `Results/00001_Dance1`, der Retarget kam nie, die Figur
stand. Die Bibliothek bietet das Umbenennen selbst an
(`Bvhverwaltung._ordner_umbenennen`), also müssen die LESENDEN Wege einen
Umzug verkraften: `Bvhablage.finden` nimmt die Datei aus einem anderen
Ordner, wenn es genau einen mit diesem Namen gibt.

Mehrdeutig (zwei Ordner mit derselben Datei) bleibt 404 — raten wäre die
falsche Bewegung ohne Fehler. Schreibende Endpunkte (`save-bvh-text`,
`save-bvh-effects`) folgen NICHT: Sie schreiben nur, wo sie sollen.
Die Bibliothek der Prüfung liegt in der Prüfablage, nie unter 3DObjects.
"""
import shutil
from pathlib import Path

from django.test import Client, TestCase, override_settings

from core.dienste.bvhablage import Bvhablage
from core.tests.unit._pruefablage import Pruefablage

BVH = """HIERARCHY
ROOT Hips
{
\tOFFSET 0.0 0.0 0.0
\tCHANNELS 6 Xposition Yposition Zposition Zrotation Xrotation Yrotation
\tEnd Site
\t{
\t\tOFFSET 0.0 20.0 0.0
\t}
}
MOTION
Frames: 2
Frame Time: 0.033333
0.0 90.0 0.0 0.0 0.0 0.0
1.0 90.0 0.0 0.0 0.0 0.0
"""


class DerUmzug(TestCase):

    def setUp(self):
        self.ordner = self.enterContext(Pruefablage.ordner('umzug_'))
        self.wurzel = Path(self.ordner) / 'bvh'
        for kategorie in ('A_Results', 'Mixamo'):
            (self.wurzel / kategorie).mkdir(parents=True)
        (self.wurzel / 'A_Results' / 'tanz.bvh').write_text(BVH, encoding='utf-8')
        (self.wurzel / 'Mixamo' / 'gehen.bvh').write_text(BVH, encoding='utf-8')
        self.enterContext(override_settings(HUMANBODY_BVH_DIR=str(self.wurzel / 'MocapNET')))
        self.client = Client()

    def tearDown(self):
        shutil.rmtree(self.ordner, ignore_errors=True)

    def geprueft(self, kategorie, name):
        return Bvhablage.pfad_pruefen(self.wurzel / kategorie / ('%s.bvh' % name))

    def test_die_datei_am_alten_ort_ist_sie_selbst(self):
        pfad = self.geprueft('A_Results', 'tanz')
        self.assertEqual(Bvhablage.finden(pfad), pfad)

    def test_der_umgezogene_ordner_wird_gefunden(self):
        gefunden = Bvhablage.finden(self.geprueft('Results', 'tanz'))
        self.assertEqual(gefunden, (self.wurzel / 'A_Results' / 'tanz.bvh').resolve())

    def test_was_es_nirgends_gibt_bleibt_none(self):
        self.assertIsNone(Bvhablage.finden(self.geprueft('Results', 'gibtsnicht')))
        self.assertIsNone(Bvhablage.finden(None))

    def test_zwei_ordner_mit_derselben_datei_sind_mehrdeutig(self):
        (self.wurzel / 'Mixamo' / 'tanz.bvh').write_text(BVH, encoding='utf-8')
        self.assertIsNone(Bvhablage.finden(self.geprueft('Results', 'tanz')))

    def test_der_retarget_findet_den_clip_des_projekts(self):
        antwort = self.client.get('/api/retarget/?category=Results&name=tanz&body_height=1.68')
        self.assertEqual(antwort.status_code, 200, antwort.content[:200])
        self.assertEqual(antwort.json()['frame_count'], 2)

    def test_die_bvh_datei_kommt_auch_vom_alten_ort(self):
        antwort = self.client.get('/api/character/bvh/Results/tanz/')
        self.assertEqual(antwort.status_code, 200)
        self.assertIn(b'ROOT Hips', b''.join(antwort.streaming_content))
        self.assertEqual(self.client.get('/api/character/bvh/Results/gibtsnicht/').status_code, 404)

    def test_schreiben_folgt_dem_umzug_nicht(self):
        u"""Sonst landete „Boden richten" in einem Ordner, den niemand genannt hat."""
        antwort = self.client.post('/api/retarget/save-bvh-effects/',
                                   data={'category': 'Results', 'name': 'tanz', 'fixed_radius': 0.5},
                                   content_type='application/json')
        self.assertEqual(antwort.status_code, 404)
        self.assertFalse((self.wurzel / 'Results').exists())
