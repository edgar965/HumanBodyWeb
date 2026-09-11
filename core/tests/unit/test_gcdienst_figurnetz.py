# -*- coding: utf-8 -*-
u"""`GarmentcodeDienst.figurnetz` rechnet die Morphs WIRKLICH ein (11.09.2026).

Vom 08.09. bis 11.09.2026 rief die Methode `zustand.set_morph_value` —
einen Namen, den `CharacterState` nicht hat. Das `except Exception`
darunter meldete jeden Morph auf DEBUG als „uebergangen", und jedes
GarmentCode-Stueck wurde fuer den GRUNDKOERPER geschnitten. Aufgefallen
ist es an einer Hose, die auf einer Figur mit duennen Beinen 20 cm Luft
hatte. Gemessen: Figurnetz mit 12 Morphs gegen Grundnetz, 0,0000 m.

Der Fall hier ist die Probe, die das sofort gezeigt haette: Ein Morph, der
die Oberschenkel schmaler macht, MUSS das Netz aendern.

Sabotage-Gegenprobe: `set_morph` -> `set_morph_value` macht den Fall rot.
"""
import numpy as np
from django.test import SimpleTestCase

from GarmentCode.dienst import GarmentcodeDienst


class FigurnetzMorphsTest(SimpleTestCase):

    databases = []

    def test_morph_veraendert_das_netz(self):
        grund = np.asarray(GarmentcodeDienst.figurnetz('female', {}, None))
        duenn = np.asarray(GarmentcodeDienst.figurnetz(
            'female', {'Legs_UpperlegsMass': -1.0}, None))
        self.assertEqual(grund.shape, duenn.shape)
        abweichung = float(np.abs(grund - duenn).max())
        self.assertGreater(abweichung, 0.005, 'Morph wirkt nicht: %.4f m'
                           % abweichung)
