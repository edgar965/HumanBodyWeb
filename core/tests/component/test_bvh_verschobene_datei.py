# -*- coding: utf-8 -*-
"""Eine verschobene BVH-Datei wird NICHT gesucht — sie ist 404, und das Studio
nimmt ihren Clip aus der Zeitleiste.

Edgar (13.09.2026, BVH Studio): „bei jedem Refresh soll der Ordner neu
refresht werden, so dass ich nicht auf eine Animation klicken kann die es
nicht gibt. Falls in der Timeline etwas ist was es nicht gibt, dann
entfernen." Vorher (12.09. und der erste Anlauf am 13.09.) suchte
`Bvhablage.finden` die Datei in anderen Ordnern und Unterordnern — der
falsche Ansatz: Das Projekt spielte Bewegung aus einer Datei, die niemand
genannt hatte, und der Umzug blieb unsichtbar.

Jetzt: Genau `<Kategorie>/<Name>.bvh`, sonst 404 — für den Retarget, die
Datei selbst und die schreibenden Endpunkte gleichermaßen. Das Aufräumen
der Zeitleiste prüft `test_js_clipfehlt.py`. Die Bibliothek der Prüfung
liegt in der Prüfablage, nie unter 3DObjects.
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


class DieVerschobeneDatei(TestCase):
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

    def test_die_datei_an_ihrem_ort_wird_umgesetzt(self):
        antwort = self.client.get('/api/retarget/?category=A_Results&name=tanz&body_height=1.68')
        self.assertEqual(antwort.status_code, 200, antwort.content[:200])
        self.assertEqual(antwort.json()['frame_count'], 2)
        antwort = self.client.get('/api/character/bvh/A_Results/tanz/')
        self.assertEqual(antwort.status_code, 200)
        self.assertIn(b'ROOT Hips', b''.join(antwort.streaming_content))

    def test_der_alte_ordnername_bleibt_404(self):
        antwort = self.client.get('/api/retarget/?category=Results&name=tanz&body_height=1.68')
        self.assertEqual(antwort.status_code, 404)
        self.assertIn(b'BVH not found: Results/tanz', antwort.content)
        self.assertEqual(self.client.get('/api/character/bvh/Results/tanz/').status_code, 404)

    def test_ein_unterordner_bleibt_404(self):
        alt = self.wurzel / 'A_Results' / 'alt'
        alt.mkdir()
        (self.wurzel / 'A_Results' / 'tanz.bvh').rename(alt / 'tanz.bvh')
        antwort = self.client.get('/api/retarget/?category=A_Results&name=tanz&body_height=1.68')
        self.assertEqual(antwort.status_code, 404)
        self.assertEqual(self.client.get('/api/character/bvh/A_Results/tanz/').status_code, 404)

    def test_die_pfadpruefung_bleibt(self):
        self.assertIsNone(Bvhablage.pfad_pruefen(self.wurzel / '..' / 'settings.py'))
        self.assertEqual(self.client.get('/api/character/bvh/..%2F..%2Fx/tanz/').status_code, 404)

    def test_schreiben_folgt_keinem_umzug(self):
        """Sonst landete „Boden richten“ in einem Ordner, den niemand genannt hat."""
        antwort = self.client.post(
            '/api/retarget/save-bvh-effects/',
            data={'category': 'Results', 'name': 'tanz', 'fixed_radius': 0.5},
            content_type='application/json',
        )
        self.assertEqual(antwort.status_code, 404)
        self.assertFalse((self.wurzel / 'Results').exists())
