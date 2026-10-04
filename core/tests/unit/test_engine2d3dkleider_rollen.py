# -*- coding: utf-8 -*-
"""Rollen der Bildauswahl von „2D3D Kleider" (03.10.2026): Netz-Pipeline gegen „Nur Iterationen".

Edgar: „Diagonalbilder sind für TRELLIS nicht nützlich — mach einen Bereich, welche Bilder du für die TRELLIS-Pipeline benutzt,
und darunter welche zusätzlichen du für die Iterationen nutzt." Reine Logik, keine Datenbank, kein Dateizugriff.
"""

import unittest

from core.dienste.engine2d3dkleiderrollen import Engine2d3dKleiderrollen
from core.dienste.iterationsreferenz import Iterationsreferenz


class Engine2d3dKleiderrollenTest(unittest.TestCase):
    def test_1_nur_iterationen_steht_in_der_auswahl_vor_nicht_verwenden(self):
        werte = [w for w, _t in Engine2d3dKleiderrollen.liste()]
        self.assertIn('iterationen', werte)
        self.assertLess(werte.index('iterationen'), werte.index('aus'))

    def test_2_unbekannte_rolle_wird_automatisch(self):
        self.assertEqual(Engine2d3dKleiderrollen.pruefen('iterationen'), 'iterationen')
        self.assertEqual(Engine2d3dKleiderrollen.pruefen('seitlich'), 'auto')

    def test_3_das_netz_bekommt_weder_aus_noch_nur_iterationen(self):
        self.assertTrue(Engine2d3dKleiderrollen.fuer_netz({'rolle': 'vorne'}))
        self.assertTrue(Engine2d3dKleiderrollen.fuer_netz({'rolle': 'auto'}))
        self.assertFalse(Engine2d3dKleiderrollen.fuer_netz({'rolle': 'aus'}))
        self.assertFalse(Engine2d3dKleiderrollen.fuer_netz({'rolle': 'iterationen'}))

    def test_4_nur_iterationen_nennt_genau_diese_fotos(self):
        bilder = [{'datei': 'a.png', 'rolle': 'vorne'}, {'datei': 'b.png', 'rolle': 'iterationen'},
                  {'datei': 'c.png', 'rolle': 'aus'}, 'kein Eintrag']
        self.assertEqual(Engine2d3dKleiderrollen.nur_iterationen(bilder), {'b.png'})
        self.assertEqual(Engine2d3dKleiderrollen.nur_iterationen(None), set())

    def test_5_winkel_wird_geprueft_und_in_den_bereich_gebracht(self):
        pruefen = Engine2d3dKleiderrollen.winkel_pruefen
        self.assertEqual(pruefen(45), 45.0)
        self.assertEqual(pruefen('-135'), -135.0)
        self.assertEqual(pruefen(225), -135.0)
        self.assertEqual(pruefen(-180), 180.0)
        for leer in (None, '', 'x', True, float('nan'), float('inf')):
            self.assertIsNone(pruefen(leer), repr(leer))

    def test_7_farbe_am_foto_nur_aus_wenn_ausdruecklich_aus(self):
        pruefen = Engine2d3dKleiderrollen.farbe_pruefen
        for aus in (False, 'false', '0', 'aus'):
            self.assertIs(pruefen(aus), False, repr(aus))
        for an in (True, 'true', '1', 'an'):
            self.assertIs(pruefen(an), True, repr(an))
        self.assertIsNone(pruefen(None))
        self.assertIsNone(pruefen('vielleicht'))

    def test_6_die_iterationen_nehmen_ein_nur_iterationen_foto_mit_seinem_winkel(self):
        eintrag = {'datei': 'randy_2.png', 'rolle': 'iterationen', 'winkel': 45.0}
        self.assertEqual(Iterationsreferenz.winkel_von(eintrag), 45.0)
        # ohne Winkel und ohne Namen im Bogen bleibt es None — die Pose schätzt ihn (`Blickwinkelschaetzung`)
        self.assertIsNone(Iterationsreferenz.winkel_von({'datei': 'randy_2.png', 'rolle': 'iterationen'}))
