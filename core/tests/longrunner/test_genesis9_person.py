# -*- coding: utf-8 -*-
"""Gewicht, Außenmaße und Handmaße an der Bibliothek (19.09.2026).

1. `G9koerpergewicht`: SMPL-X neutral wiegt bei 1,719 m 75,4 kg (Dichte 1000);
   60 kg bei 170 cm werden über Beta 1 in unter 12 Sekantenschritten getroffen.
2. `G9silhouettenmasse.vom_kaefig`: Feminine/Masculine/Ursula/Kat — Schulter
   breiter als Hüfte breiter als Taille; Masculine an der Schulter breiter
   als Feminine, an der Hüfte nicht. Sabotage (`_maske` ohne Alpha) → rot.
"""

import unittest

import numpy as np
from django.test import SimpleTestCase
from Genesis9.formung import G9formung
from Genesis9.koerpergewicht import G9koerpergewicht
from Genesis9.pfade import G9pfade
from Genesis9.silhouettenmasse import G9silhouettenmasse
from Genesis9.vorschaubild import G9vorschaubild
from Genesis9.zielnetz import G9zielnetz

from core.tests.unit._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()


def bereit():
    return G9pfade.vorhanden() and G9zielnetz.vorhanden()


@unittest.skipUnless(bereit(), 'Daz-Bibliothek oder SMPL-X-Modelle fehlen')
class PersonTest(SimpleTestCase):
    databases = set()

    def test_1_gewicht_ueber_beta_1(self):
        z = G9zielnetz.aus([0.0] * 10, symmetrisch=False)
        self.assertAlmostEqual(G9koerpergewicht.gewicht_kg(z), 75.4, delta=0.5)
        betas, beleg = G9koerpergewicht.betas_fuer_gewicht([0.0] * 10, 170.0, 60.0)
        self.assertAlmostEqual(beleg['gewicht_nachher'], 60.0, delta=G9koerpergewicht.GENAU_KG)
        self.assertLess(betas[1], -0.5)
        self.assertEqual([round(b, 6) for i, b in enumerate(betas) if i != 1], [0.0] * 9, 'nur Beta 1')

    def _masse(self, regler):
        f = G9formung(regler)
        p = np.asarray(f.punkte(), dtype=float)
        p = p - np.array([0.0, p[:, 1].min(), 0.0])
        gelenke = {e['name']: e['kopf'] for e in f.skelett().gelenkknochen()}
        hoehe = float(p[:, 1].max() - p[:, 1].min()) * 100.0
        return G9silhouettenmasse.vom_kaefig(p, G9vorschaubild(p)._dreiecke(), gelenke, hoehe)

    def test_2_aussenmasse_der_grundfiguren(self):
        f = self._masse({'BaseFeminine_figure_ctrl_Character': 1.0})
        m = self._masse({'BaseMasculine_figure_ctrl_Character': 1.0})
        for masse in (f, m):
            self.assertGreater(masse['schulter'], masse['huefte'], masse)
            self.assertGreater(masse['huefte'], masse['taille'], masse)
        self.assertGreater(m['schulter_cm'], f['schulter_cm'] + 4)
        self.assertLess(m['huefte_cm'], f['huefte_cm'])
        self.assertAlmostEqual(f['taille_cm'], 23.4, delta=1.5, msg='Wert vom 19.09.2026')
