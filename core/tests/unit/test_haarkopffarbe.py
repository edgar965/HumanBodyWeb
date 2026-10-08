# -*- coding: utf-8 -*-
"""Haarkopffarbe (06.10.2026): die Haarfarbregel liest die Kopfmessung des Haarabgleichs statt der Teilmaske — Kunstdaten, kein Django, kein Render."""
from django.test import SimpleTestCase
from iterationen2d3d.haarkopffarbe import Haarkopffarbe
from iterationen2d3d.iterationhaare import IterationHaare

KOPF = {'haarabgleich': {'farbe': {'foto': [0.334, 0.324, 0.323], 'render': [0.246, 0.253, 0.256], 'verhaeltnis': 0.77, 'pixel': 22118}}}


class DieKopffarbe(SimpleTestCase):
    def test_1_messen_gibt_die_form_der_teilmaske(self):
        m = Haarkopffarbe.messen(KOPF)
        self.assertEqual(sorted(m), ['foto_farbe', 'pixel', 'render_farbe'])
        self.assertEqual(m['pixel'], 22118)
        self.assertAlmostEqual(m['render_farbe'][0], 0.246)

    def test_2_ohne_messung_oder_mit_zu_wenig_pixeln_keine_kopffarbe(self):
        self.assertIsNone(Haarkopffarbe.messen({}))
        self.assertIsNone(Haarkopffarbe.messen({'haarabgleich': {}}))
        zu_wenig = {'haarabgleich': {'farbe': dict(KOPF['haarabgleich']['farbe'], pixel=10)}}
        self.assertIsNone(Haarkopffarbe.messen(zu_wenig))

    def test_3_grau_ohne_kopfmessung_nur_der_stich_raus(self):
        # wie vor dem 06.10.2026: Helligkeit der jetzigen Tönung (#916e6d → #757575, `test_bart_haarlaenge` Fall 7)
        self.assertEqual(Haarkopffarbe.grau([0x91 / 255, 0x6e / 255, 0x6d / 255]), '#757575')

    def test_4_grau_mit_kopfmessung_zieht_die_helligkeit_nach(self):
        jetzt = [0x46 / 255, 0x48 / 255, 0x49 / 255]
        mit = Haarkopffarbe.messen(KOPF)
        mit['foto_farbe'] = [0.327, 0.327, 0.327]                      # wie `IterationHaare._neutral` es für graues Haar macht
        ohne = Haarkopffarbe.grau(jetzt)
        hell = Haarkopffarbe.grau(jetzt, mit)
        self.assertEqual(ohne, '#484848')
        # Foto ÷ Render der Helligkeit 1,31 → Faktor 1 + 0,7 · 0,31 ≈ 1,22: aus 72 werden rund 88
        self.assertTrue(0x56 <= int(hell[1:3], 16) <= 0x5a, hell)
        self.assertEqual(hell[1:3], hell[3:5])

    def test_5_die_regel_nimmt_die_kopfmessung_vor_der_teilmaske(self):
        teil = {'art': 'haar', 'pixel': 400, 'foto_farbe': [0.33, 0.32, 0.32], 'render_farbe': [0.33, 0.32, 0.32]}      # die Teilmaske sagt „passt"
        befund = dict(KOPF, teile={'herrenhaar_0': teil})

        class _Modell:
            BILD = 'bild.'                     # wie `ModellTextur.BILD`: der Schlüssel der Grauschicht ist '<Frisur>.bild.grau' (ohne den Punkt fiele die Regel auf „erst umfärben" zurück)
            SORTE = 'sorte.'
            haar = {'sorte.herrenhaar': 1.0, 'herrenhaar.bild.grau': 1.0}
            farben = {'haar': '#484848'}

        modell = _Modell()
        regel = IterationHaare(modell, befund)
        regel.getragen = lambda: 'herrenhaar'
        aufrufe = regel.farbe()
        self.assertEqual(len(aufrufe), 1)
        self.assertTrue(aufrufe[0].startswith("m.haar_farbe('#"), aufrufe)
        self.assertGreater(int(aufrufe[0][15:17], 16), 0x48)            # heller als die jetzige Tönung (`m.haar_farbe('#rrggbb')`: Rot steht an Stelle 15–16)
