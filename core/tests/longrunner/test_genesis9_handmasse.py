# -*- coding: utf-8 -*-
"""Nebenbild-Regler: Fingerlänge aus dem Genesis-Skelett zurückrechnen (19.09.2026).

Wahrheitsprobe: Figur mit `ProportionFingersLength` 0,6 → Verhältnisse
messen → Regler 0,6 (linear, Abweichung < 0,01). Sabotage: `finger`
aus Grundgelenk→Spitze statt Gliedsumme → Fall 2 bleibt grün (gestreckt),
`aus_skelett` mit `index1` statt `mid1` als Handfläche → Fall 1 rot.
Belegt außerdem, dass `breite` kein Proportionsregler ändert (Fall 3) —
der Grund, warum es nur EIN Nebenbild-Regler ist.
"""

import unittest

from django.test import SimpleTestCase
from Genesis9.formung import G9formung
from Genesis9.handmasse import G9handmasse
from Genesis9.pfade import G9pfade


@unittest.skipUnless(G9pfade.vorhanden(), 'Daz-Bibliothek fehlt')
class HandmasseTest(SimpleTestCase):
    databases = set()
    GRUND = {'BaseFeminine_figure_ctrl_Character': 1.0}

    def test_1_regler_kommt_zurueck(self):
        for soll in (0.6, -1.3):
            w = dict(self.GRUND)
            w[G9handmasse.REGLER] = soll
            gemessen = G9handmasse.aus_reglern(w, G9formung)
            werte, erreicht = G9handmasse.regler(gemessen, self.GRUND, G9formung)
            self.assertAlmostEqual(werte[G9handmasse.REGLER], soll, delta=0.01)
            self.assertAlmostEqual(erreicht['finger'], gemessen['finger'], delta=0.002)

    def test_2_grenzen_klemmen(self):
        werte, _ = G9handmasse.regler({'finger': 9.0, 'breite': 0.7}, self.GRUND, G9formung, (-2.0, 2.0))
        self.assertEqual(werte[G9handmasse.REGLER], 2.0)

    def test_3_breite_aendert_kein_proportionsregler(self):
        v0 = G9handmasse.aus_reglern(self.GRUND, G9formung)
        regler = ('body_bs_ProportionFingersLength', 'body_ctrl_ProportionPalmSize',
                  'body_ctrl_ProportionHandSize')
        for name in regler:
            w = dict(self.GRUND)
            w[name] = 1.0
            breite = G9handmasse.aus_reglern(w, G9formung)['breite']
            self.assertAlmostEqual(breite, v0['breite'], places=3, msg=name)
        self.assertGreater(v0['finger'], 1.0, 'BaseFeminine: Mittelfinger länger als die Handfläche')
