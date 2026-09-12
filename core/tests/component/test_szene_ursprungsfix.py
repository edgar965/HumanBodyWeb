# -*- coding: utf-8 -*-
u"""Szene → Animation → „Animation immer auf Ursprungspunkt".

Edgar (12.09.2026): „es gab eine Funktion: Animation immer auf Ursprungspunkt,
findest du die noch? ich brauche die in /humanbody/scene/ im Menü Animation".
Das war „Feste Position" im BVH Studio (Werkzeuge): die Wurzel bleibt in
jedem Bild innerhalb eines Radius um ihren Startpunkt — Vorgabe 0,5 m, seit
„mach den Radius einstellbar" (Edgar, 12.09.2026) im Dialog wählbar, 0 = genau
auf dem Startpunkt. Die Szene ruft dafür denselben Server-Weg wie das Studio beim Speichern mit Effekten
(`/api/retarget/save-bvh-effects/`, `BvhDatei.wurzel_festhalten`) und lädt
die Datei neu — wie „Animation immer auf Bodenniveau".

Die BVH liegt in einer Prüfablage (`HUMANBODY_BVH_DIR` umgebogen), nie in
der Bibliothek unter 3DObjects. Wahrheit des Eichfalls: ein Wurzelgelenk,
das 3 m nach +X und 2 m nach −Z läuft — danach bleibt jedes Bild innerhalb
von 50 cm (BVH-Zentimeter) um Bild 0, Y bleibt, die Drehungen bleiben.
"""
import math
import shutil
from pathlib import Path

from django.test import Client, TestCase, override_settings

from core.tests.unit._pruefablage import Pruefablage

KOPF = """HIERARCHY
ROOT Hips
{
\tOFFSET 0.0 0.0 0.0
\tCHANNELS 6 Xposition Yposition Zposition Zrotation Xrotation Yrotation
\tJOINT Spine
\t{
\t\tOFFSET 0.0 20.0 0.0
\t\tCHANNELS 3 Zrotation Xrotation Yrotation
\t\tEnd Site
\t\t{
\t\t\tOFFSET 0.0 20.0 0.0
\t\t}
\t}
}
MOTION
Frames: %d
Frame Time: 0.033333
"""
BILDER = 30
RADIUS_M = 0.5


def bewegung():
    u"""Die Wurzel wandert in 30 Bildern 300 cm nach +X und 200 cm nach −Z."""
    zeilen = []
    for b in range(BILDER):
        x = 300.0 * b / (BILDER - 1)
        z = -200.0 * b / (BILDER - 1)
        zeilen.append('%.4f 90.0000 %.4f 0.0 0.0 %.4f 5.0 0.0 0.0' % (x, z, b * 2.0))
    return zeilen


def bilder(text):
    zeilen = text.split('\n')
    start = zeilen.index('Frame Time: 0.033333') + 1
    return [[float(w) for w in z.split()] for z in zeilen[start:] if z.strip()]


class DerUrsprungsfix(TestCase):

    URL = '/api/retarget/save-bvh-effects/'

    def setUp(self):
        self.ordner = self.enterContext(Pruefablage.ordner('ursprung_'))
        self.wurzel = Path(self.ordner) / 'bvh'
        (self.wurzel / 'Test').mkdir(parents=True)
        self.datei = self.wurzel / 'Test' / 'probe.bvh'
        self.datei.write_text(KOPF % BILDER + '\n'.join(bewegung()) + '\n',
                              encoding='utf-8')
        self.enterContext(override_settings(HUMANBODY_BVH_DIR=str(self.wurzel / 'MocapNET')))
        self.client = Client()

    def anwenden(self, radius_m=RADIUS_M):
        antwort = self.client.post(self.URL, data={
            'category': 'Test', 'name': 'probe', 'fixed_radius': radius_m},
            content_type='application/json')
        self.assertEqual(antwort.status_code, 200, antwort.content[:200])
        return antwort.json()

    def abstaende(self):
        u"""Abstand jedes Bildes zu Bild 0 in der Bodenebene (BVH-Zentimeter)."""
        b = bilder(self.datei.read_text(encoding='utf-8'))
        return [math.hypot(x[0] - b[0][0], x[2] - b[0][2]) for x in b]

    def test_die_wurzel_bleibt_im_kreis_um_bild_null(self):
        vorher = bilder(self.datei.read_text(encoding='utf-8'))
        self.assertGreater(math.hypot(vorher[-1][0], vorher[-1][2]), 300.0)
        daten = self.anwenden()
        self.assertTrue(daten['ok'])
        self.assertIn('fixed r=0.50m', daten['applied'])
        nachher = bilder(self.datei.read_text(encoding='utf-8'))
        self.assertEqual(len(nachher), BILDER)
        for bild in nachher:
            self.assertLessEqual(math.hypot(bild[0] - nachher[0][0], bild[2] - nachher[0][2]),
                                 RADIUS_M * 100 + 1e-3)
        # Das letzte Bild liegt AUF dem Rand, in der Laufrichtung (+X, −Z)
        self.assertAlmostEqual(math.hypot(nachher[-1][0], nachher[-1][2]), 50.0, places=2)
        self.assertGreater(nachher[-1][0], 0)
        self.assertLess(nachher[-1][2], 0)

    def test_ein_anderer_radius_gilt_wie_gewaehlt(self):
        daten = self.anwenden(1.0)
        self.assertIn('fixed r=1.00m', daten['applied'])
        abstaende = self.abstaende()
        self.assertLessEqual(max(abstaende), 100.0 + 1e-3)
        self.assertAlmostEqual(abstaende[-1], 100.0, places=2)

    def test_radius_null_haelt_die_wurzel_auf_bild_null(self):
        u"""0 hieß auf dem Server „nichts tun" — jetzt ist es der engste Radius."""
        daten = self.anwenden(0)
        self.assertIn('fixed r=0.00m', daten['applied'])
        self.assertEqual(max(self.abstaende()), 0.0)

    def test_hoehe_und_drehungen_bleiben(self):
        vorher = bilder(self.datei.read_text(encoding='utf-8'))
        self.anwenden()
        nachher = bilder(self.datei.read_text(encoding='utf-8'))
        for v, n in zip(vorher, nachher):
            self.assertAlmostEqual(n[1], v[1], places=3)          # Y
            for i in range(3, 9):                                  # Drehungen
                self.assertAlmostEqual(n[i], v[i], places=2)

    def test_die_bibliothek_bleibt_unberuehrt(self):
        u"""Die Prüfung schreibt nur in die Prüfablage."""
        from core.dienste.bvhablage import Bvhablage
        self.assertEqual(Bvhablage.wurzel(), self.wurzel.resolve())
        self.anwenden()
        self.assertFalse((self.wurzel / 'MocapNET').exists())

    def tearDown(self):
        shutil.rmtree(self.ordner, ignore_errors=True)


class DasDrahtformat(TestCase):
    u"""Menüeintrag, Dispatch und Modul gehören zusammen."""

    databases = set()

    def quelle(self, *teile):
        from django.conf import settings
        return Path(settings.BASE_DIR).joinpath(*teile).read_text(encoding='utf-8')

    def test_das_menue_animation_hat_den_eintrag_neben_bodenniveau(self):
        text = self.quelle('templates', 'scene_config.html')
        boden = text.index('data-action="anim-ground-fix"')
        ursprung = text.index('data-action="anim-origin-fix">Animation immer auf Ursprungspunkt')
        self.assertLess(boden, ursprung)
        self.assertLess(ursprung - boden, 300)

    def test_der_dispatch_ruft_den_ursprungsfix(self):
        text = self.quelle('static', 'viewer', 'scene', 'menubar.js')
        self.assertIn("case 'anim-origin-fix': Ursprungsfix.fragen(); break;", text)
        self.assertIn("import { Ursprungsfix } from './ursprungsfix.js';", text)

    def test_die_vorgabe_ist_der_radius_des_studios(self):
        text = self.quelle('static', 'viewer', 'scene', 'ursprungsfix.js')
        self.assertIn('static VORGABE_CM = 50;', text)
        self.assertIn("ENDPUNKT = '/api/retarget/save-bvh-effects/'", text)
        studio = self.quelle('static', 'viewer', 'bvh_studio', 'werkzeug_position.js')
        self.assertIn('radius: 0.5', studio)

    def test_der_dialog_fragt_den_radius_von_null_an(self):
        u"""Regler, Anzeige und Knopf des Dialogs heißen so, wie das Modul sie ruft."""
        self.assertIn('{% include "_ursprungsfix_dialog.html" %}',
                      self.quelle('templates', 'scene_config.html'))
        dialog = self.quelle('templates', '_ursprungsfix_dialog.html')
        modul = self.quelle('static', 'viewer', 'scene', 'ursprungsfix.js')
        self.assertIn('id="ursprungsfix-radius" min="0" max="200"', dialog)
        for kennung in ('ursprungsfix-dialog', 'ursprungsfix-radius',
                        'ursprungsfix-radius-val', 'ursprungsfix-confirm'):
            self.assertIn('id="%s"' % kennung, dialog)
            self.assertIn("getElementById('%s')" % kennung, modul)
