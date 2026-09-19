# -*- coding: utf-8 -*-
"""Testfall „Modell aus Bildern": Abstand zur Referenzfigur — an der Daz-Bibliothek (19.09.2026).

Edgar: „Testcase … das Ursula9-Modell zum Vergleich mit dem, was du erzeugt
hast." `Bildmodelltestfall.vergleichen(stellung)` misst das Ergebnis gegen
den Katalogeintrag (`optionen.testfall.figur`):

1. Die Referenz gegen sich selbst: RMS 0, Maximum 0, jedes Teil 0.
2. Die Grundfigur gegen P3D Ursula: RMS deutlich über 0 (die Wahrheitsprobe
   der Anpassung fand 4,76 mm OHNE Ursulas Regler — hier ohne jede Anpassung
   mehr), Höhe beider im Ergebnis, 19 Proportionen je Seite, das schlechteste
   Teil ist nicht das Auge. Sabotage-Gegenprobe: eine falsche Figur → None.
"""

import unittest

from django.test import SimpleTestCase
from Genesis9.pfade import G9pfade

from core.dienste.bildmodelltestfall import Bildmodelltestfall


class _Job:
    kennung = 'pruef'


@unittest.skipUnless(G9pfade.vorhanden(), 'Daz-Bibliothek fehlt')
class TestfallTest(SimpleTestCase):
    def test_referenz_gegen_sich_selbst_und_grundfigur(self):
        t = Bildmodelltestfall(_Job(), {'testfall': {'figur': 'p3d_ursula'}})
        eintrag = t.eintrag()
        self.assertIsNotNone(eintrag)
        gleich = t.vergleichen(eintrag['regler'])
        self.assertEqual((gleich['rms_mm'], gleich['max_mm']), (0.0, 0.0))
        self.assertTrue(all(v == 0.0 for v in gleich['je_teil'].values()))
        self.assertEqual(gleich['punkte'], 25182)
        grund = t.vergleichen({})
        self.assertGreater(grund['rms_mm'], 3.0, 'die Grundfigur ist nicht Ursula')
        self.assertGreater(grund['max_mm'], grund['rms_mm'])
        self.assertEqual(len(grund['proportionen']['referenz']), 19)
        self.assertEqual(len(grund['proportionen']['modell']), 19)
        self.assertGreater(grund['hoehe_cm']['referenz'], 150)
        self.assertNotEqual(grund['hoehe_cm']['referenz'], grund['hoehe_cm']['modell'])
        schlechtestes = max(grund['je_teil'], key=grund['je_teil'].get)
        self.assertNotEqual(schlechtestes, 'auge')
        # Sabotage-Gegenprobe: ohne bekannte Figur kein Vergleich.
        self.assertIsNone(Bildmodelltestfall(_Job(), {'testfall': {'figur': 'gibtsnicht'}}).vergleichen({}))
        self.assertIsNone(Bildmodelltestfall.figur({'testfall': {}}))
