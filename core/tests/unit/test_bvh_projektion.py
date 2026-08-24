# -*- coding: utf-8 -*-
"""Die BVH-nach-Pixel-Kette an einer Miniatur-BVH festnagseln.

WARUM MIT VON HAND GERECHNETEN ZAHLEN (17.08.2026)
=================================================
`_parse_bvh_to_2d` (180 Zeilen) ist in drei Klassen zerlegt worden. Diese Rechnung
muss pixelweise zu `fitOverlayCamera` in `playback.js` passen — das gezeichnete
Skelett wird über das echte Video gelegt. Ein Test, der einfach das Ergebnis des
Codes als Sollwert nimmt, würde jede Verschiebung mitwandern lassen; deshalb
stehen hier nachgerechnete Werte.

DIE MINIATUR
============
Wurzel `Hips` mit 6 Kanälen, Kind `Spine` mit 3, Endpunkt darüber. Zwei Bilder:

    Bild 1: Hips bei (0, 1, 0), keine Drehung   -> Spine bei (0, 11, 0)
    Bild 2: Hips bei (0, 1, 0), Spine 90° um Z  -> Spine bleibt (0, 11, 0),
                                                   seine Kinder kippen

Ausschnitt aus BILD 1 (so macht es der Browser):
    x: min 0, max 0   -> Mitte 0, Größe 0 -> ersetzt durch 1 -> halb_x = 0,75
    y: min 1, max 11  -> Mitte 6, Größe 10          -> halb_y = 7,5
    Video 100x100 -> Seitenverhältnis 1,0; Skelett 0,1 -> also halb_x = 7,5

    Hips  (0, 1):  x = (0-0+7,5)/15*100 = 50 ; y = (6+7,5-1)/15*100 = 83,33
    Spine (0,11):  x = 50               ; y = (6+7,5-11)/15*100 = 16,67
"""

import unittest
from pathlib import Path

from django.test import SimpleTestCase

from core.dienste.bvh_projektion import _parse_bvh_to_2d
from core.dienste.bvhbaum import Bvhbaum
from core.dienste.vorwaertskinematik import Vorwaertskinematik
from core.projekt_temp import ProjektTemp

BVH = '\n'.join([
    'HIERARCHY',
    'ROOT Hips',
    '{',
    '    OFFSET 0.00 0.00 0.00',
    '    CHANNELS 6 Xposition Yposition Zposition Zrotation Xrotation Yrotation',
    '    JOINT Spine',
    '    {',
    '        OFFSET 0.00 10.00 0.00',
    '        CHANNELS 3 Zrotation Xrotation Yrotation',
    '        End Site',
    '        {',
    '            OFFSET 0.00 10.00 0.00',
    '        }',
    '    }',
    '}',
    'MOTION',
    'Frames: 2',
    'Frame Time: 0.040000',
    '',                                  # Leerzeile: kommt in echten Dateien vor
    '0.0 1.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0',
    '0.0 1.0 0.0 0.0 0.0 0.0 90.0 0.0 0.0',
    '',
])


class BvhProjektionTest(SimpleTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ordner = ProjektTemp.ordner(prefix='bvhproj_')
        cls.pfad = Path(cls.ordner) / 'mini.bvh'
        cls.pfad.write_text(BVH, encoding='utf-8')

    @classmethod
    def tearDownClass(cls):
        ProjektTemp.weg(cls.ordner)
        super().tearDownClass()

    # ------------------------------------------------------------------ lesen

    def test_hierarchie_gelesen(self):
        baum = Bvhbaum(self.pfad)
        self.assertEqual(baum.gelenke, ['Hips', 'Spine'])
        self.assertEqual(baum.eltern, {'Hips': None, 'Spine': 'Hips'})
        self.assertEqual(baum.verbindungen(), [('Hips', 'Spine')])

    def test_kanalfolge_in_dateireihenfolge(self):
        """Die Reihenfolge entscheidet über die Drehung — sie darf nicht sortiert
        werden."""
        baum = Bvhbaum(self.pfad)
        self.assertEqual(baum.kanalfolge[:6],
                         [('Hips', 'Xposition'), ('Hips', 'Yposition'),
                          ('Hips', 'Zposition'), ('Hips', 'Zrotation'),
                          ('Hips', 'Xrotation'), ('Hips', 'Yrotation')])
        self.assertEqual(baum.kanalfolge[6:],
                         [('Spine', 'Zrotation'), ('Spine', 'Xrotation'),
                          ('Spine', 'Yrotation')])

    def test_leerzeilen_zaehlen_nicht_als_bild(self):
        """Zwei Bewegungszeilen, obwohl drei Leerzeilen dazwischen stehen."""
        self.assertEqual(len(Bvhbaum(self.pfad).bilder), 2)

    def test_endpunkt_verschiebt_die_hierarchie_nicht(self):
        """`End Site` hat keinen Namen — es darf nicht Eltern von Spine werden."""
        self.assertNotIn(Bvhbaum.ENDPUNKT, Bvhbaum(self.pfad).eltern.values())

    # ---------------------------------------------------------------- Kinematik

    def test_weltpositionen_erstes_bild(self):
        stellen = Vorwaertskinematik(Bvhbaum(self.pfad)).positionen()
        self.assertAlmostEqual(stellen[0]['Hips'][1], 1.0, places=6)
        self.assertAlmostEqual(stellen[0]['Spine'][1], 11.0, places=6)

    def test_drehung_des_kindes_verschiebt_es_nicht(self):
        """Spine dreht um sich selbst — seine POSITION bleibt (0, 11, 0)."""
        stellen = Vorwaertskinematik(Bvhbaum(self.pfad)).positionen()
        self.assertAlmostEqual(stellen[1]['Spine'][0], 0.0, places=6)
        self.assertAlmostEqual(stellen[1]['Spine'][1], 11.0, places=6)

    def test_achsendrehung_um_z(self):
        """90° um Z schickt (1,0,0) nach (0,1,0)."""
        matrix = Vorwaertskinematik.achsendrehung('Z', 90)
        gedreht = matrix @ [1.0, 0.0, 0.0]
        self.assertAlmostEqual(gedreht[0], 0.0, places=6)
        self.assertAlmostEqual(gedreht[1], 1.0, places=6)

    # --------------------------------------------------------------- Projektion

    def test_pixel_wie_von_hand_gerechnet(self):
        punkte, verbindungen = _parse_bvh_to_2d(self.pfad, 100, 100)
        self.assertEqual(len(punkte), 2)
        self.assertEqual(verbindungen, [('Hips', 'Spine')])
        hips = punkte[0]['Hips']
        spine = punkte[0]['Spine']
        self.assertAlmostEqual(hips[0], 50.0, places=3)
        self.assertAlmostEqual(hips[1], 83.333, places=2)
        self.assertAlmostEqual(spine[0], 50.0, places=3)
        self.assertAlmostEqual(spine[1], 16.667, places=2)
        self.assertEqual(hips[2], 1.0)

    def test_y_ist_gespiegelt(self):
        """Der höhere Punkt (Spine) muss den KLEINEREN Pixelwert haben."""
        punkte, _ = _parse_bvh_to_2d(self.pfad, 100, 100)
        self.assertLess(punkte[0]['Spine'][1], punkte[0]['Hips'][1])

    def test_breites_video_zieht_den_ausschnitt_in_die_breite(self):
        """Bei 200x100 verdoppelt sich halb_x — die Y-Werte bleiben."""
        schmal, _ = _parse_bvh_to_2d(self.pfad, 100, 100)
        breit, _ = _parse_bvh_to_2d(self.pfad, 200, 100)
        self.assertAlmostEqual(breit[0]['Hips'][1], schmal[0]['Hips'][1],
                               places=3)
        self.assertAlmostEqual(breit[0]['Hips'][0], 100.0, places=3)

    def test_bvh_ohne_bewegung_ergibt_leere_listen(self):
        pfad = Path(self.ordner) / 'ohne.bvh'
        pfad.write_text('HIERARCHY\nROOT Hips\n{\n}\nMOTION\n', encoding='utf-8')
        self.assertEqual(_parse_bvh_to_2d(pfad, 100, 100), ([], []))


if __name__ == '__main__':
    unittest.main()
