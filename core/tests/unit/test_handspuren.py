# -*- coding: utf-8 -*-
u"""Handspuren: die Finger einer dritten Quelle über das Hybrid-Gemisch legen.

Die Knochenmenge muss GENAU die Hände sein — Finger, Daumen, Mittelhand —
und kein Gesichtsknochen: Sonst überschriebe GEM-X (das nur Kiefer und
Augen als Gelenke hat, ohne Ausdruck) das Gesicht der v4-Spur. Und was die
dritte Spur nicht hat (`DEF-palm_*`), bleibt aus dem Gemisch stehen.
"""
from django.test import SimpleTestCase

from core.dienste.handspuren import Handspuren


def spuren(tracks, bilder=2):
    from humanbody_core.skeleton.bewegungsspuren import Bewegungsspuren
    return Bewegungsspuren(duration=1.0, times=[0.0, 0.5], tracks=tracks,
                           frame_count=bilder, mapped_bones=sorted(tracks),
                           position_track=[0.0] * 6)


class DieKnochenmenge(SimpleTestCase):

    databases = set()

    def test_nur_haende_keine_gesichter(self):
        knochen = Handspuren.knochen()
        self.assertEqual(len(knochen), 38)
        self.assertTrue(all(k.startswith(Handspuren.ANFAENGE) for k in knochen))
        for gesicht in ('DEF-jaw', 'DEF-lip_T_L', 'DEF-tongue', 'MCH-eye_L'):
            self.assertNotIn(gesicht, knochen)
        for hand in ('DEF-f_index_01_L', 'DEF-thumb_03_R', 'DEF-palm_02_L'):
            self.assertIn(hand, knochen)


class DasMischen(SimpleTestCase):

    databases = set()

    def setUp(self):
        q = lambda w: [w, 0.0, 0.0, 1.0] * 2          # zwei Bilder je Spur
        self.gemischt = spuren({
            'DEF-spine.001': q(0.1), 'DEF-jaw': q(0.2),
            'DEF-f_index.01.L': q(0.3), 'DEF-palm.01.L': q(0.4),
        })
        self.haende = spuren({
            'DEF-spine.001': q(0.9), 'DEF-jaw': q(0.8),
            'DEF-f_index.01.L': q(0.7), 'DEF-thumb.01.R': q(0.6),
        })
        self.ergebnis = Handspuren.mischen(self.gemischt, self.haende)

    def test_finger_kommen_aus_der_dritten_spur(self):
        self.assertEqual(self.ergebnis.tracks['DEF-f_index.01.L'][0], 0.7)
        self.assertEqual(self.ergebnis.tracks['DEF-thumb.01.R'][0], 0.6)

    def test_koerper_und_gesicht_bleiben_wie_sie_waren(self):
        self.assertEqual(self.ergebnis.tracks['DEF-spine.001'][0], 0.1)
        self.assertEqual(self.ergebnis.tracks['DEF-jaw'][0], 0.2)

    def test_was_die_dritte_spur_nicht_hat_bleibt_stehen(self):
        self.assertEqual(self.ergebnis.tracks['DEF-palm.01.L'][0], 0.4)

    def test_bildzahl_und_wurzel_kommen_vom_gemisch(self):
        self.assertEqual(self.ergebnis.frame_count, 2)
        self.assertEqual(self.ergebnis.position_track, [0.0] * 6)
        self.assertEqual(self.ergebnis.mapped_bones, sorted(self.ergebnis.tracks))
