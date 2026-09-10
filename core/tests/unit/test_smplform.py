# -*- coding: utf-8 -*-
u"""Smplform — die Umrechnung Regler <-> SMPL-Betas.

Der Kern dieser Pruefung ist das VORZEICHEN von beta0. Es ist je Geschlecht
verschieden (gemessen: male b0 -1 => +7,8 cm; female b0 +1 => +7,0 cm), und
ein falsches Vorzeichen faellt nirgends auf — der Groessen-Regler laeuft
dann bei jeder zweiten Figur rueckwaerts, ohne Fehler, ohne Warnung.
"""

import unittest

import sys
sys.path.insert(0, r'A:\3DTools\HumanBody')

from GarmentCode.smplform import Smplform  # noqa: E402


class SmplformTest(unittest.TestCase):

    databases = []

    def test_mitte_ist_der_durchschnittskoerper(self):
        self.assertEqual(Smplform.betas('male', 0, 0)[:2], [0.0, 0.0])
        self.assertTrue(Smplform.ist_grundkoerper(0, 0))
        self.assertFalse(Smplform.ist_grundkoerper(10, 0))

    def test_groesser_hat_je_geschlecht_ein_anderes_vorzeichen(self):
        u"""Der eigentliche Befund: dieselbe Zahl macht den Mann groesser
        und die Frau kleiner. Gemessen am SMPL-Modell beider Geschlechter."""
        mann = Smplform.betas('male', 100, 0)
        frau = Smplform.betas('female', 100, 0)
        self.assertLess(mann[0], 0, 'maennlich: groesser heisst beta0 negativ')
        self.assertGreater(frau[0], 0, 'weiblich: groesser heisst beta0 positiv')
        self.assertAlmostEqual(abs(mann[0]), abs(frau[0]))

    def test_schlank_ist_bei_beiden_dasselbe(self):
        u"""Fuer die Fuelle gilt bei beiden Geschlechtern dasselbe Vorzeichen
        (b1 groesser = schlanker) — auch das gemessen."""
        for geschlecht in ('male', 'female'):
            schlank = Smplform.betas(geschlecht, 0, -100)
            kraeftig = Smplform.betas(geschlecht, 0, 100)
            self.assertGreater(schlank[1], 0, geschlecht)
            self.assertLess(kraeftig[1], 0, geschlecht)

    def test_voller_ausschlag_sind_zwei_beta(self):
        self.assertAlmostEqual(abs(Smplform.betas('male', 100, 0)[0]), 2.0)
        self.assertAlmostEqual(abs(Smplform.betas('male', 0, 100)[1]), 2.0)

    def test_zehn_betas_und_nur_die_ersten_zwei_belegt(self):
        b = Smplform.betas('female', 40, -60)
        self.assertEqual(len(b), 10)
        self.assertEqual(b[2:], [0.0] * 8)

    def test_rueckweg_trifft_den_reglerwert(self):
        for geschlecht in ('male', 'female'):
            for groesse, fuelle in ((0, 0), (100, -100), (-35, 60), (12, 7)):
                betas = Smplform.betas(geschlecht, groesse, fuelle)
                zurueck = Smplform.regler(geschlecht, betas)
                self.assertAlmostEqual(zurueck['groesse'], groesse, places=6,
                                       msg='%s %s' % (geschlecht, groesse))
                self.assertAlmostEqual(zurueck['fuelle'], fuelle, places=6,
                                       msg='%s %s' % (geschlecht, fuelle))

    def test_werte_ausserhalb_werden_geklemmt(self):
        self.assertAlmostEqual(abs(Smplform.betas('male', 5000, 0)[0]), 2.0)
        self.assertAlmostEqual(abs(Smplform.betas('male', -5000, 0)[0]), 2.0)

    def test_unsinn_wird_zur_mitte(self):
        u"""Ein leeres Feld darf keinen Koerper verformen."""
        self.assertEqual(Smplform.betas('male', None, 'abc')[:2], [0.0, 0.0])

    def test_unbekanntes_geschlecht_bleibt_bedienbar(self):
        b = Smplform.betas('divers', 100, 0)
        self.assertEqual(len(b), 10)
        self.assertNotEqual(b[0], 0.0)


if __name__ == '__main__':
    unittest.main()
