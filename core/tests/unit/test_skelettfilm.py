# -*- coding: utf-8 -*-
"""Skelettfilm und Skelettzeichner — Bildzuordnung, Sichtbarkeit, Zielpfad.

WARUM MIT GERECHNETEN ZAHLEN (17.08.2026)
=========================================
`_render_video_with_skeleton` (97 Zeilen) hat keinen Test gehabt: Es braucht ein
Video, OpenCV-Schreiber und eine Pipeline-Ausgabe. Zwei Teile darin sind aber
reine Rechnung, und in ihnen steckt der Fehler, der die teuerste Sorte wäre —
ein Skelett, das dem Video vorausläuft.

DIE ZUORDNUNG
=============
Verhältnismäßig, wie in der Three.js-Wiedergabe:

    Video 101 Bilder, Bewegung 51 Bilder
    Bild 0   -> 0/100 * 50 = 0
    Bild 50  -> 50/100 * 50 = 25
    Bild 100 -> 100/100 * 50 = 50

Ein 1:1-Zähler ergäbe bei Bild 100 den Index 100 — außerhalb der Bewegung.

DIE SICHTBARKEIT
================
Gemalt wird nur, was sicher (> 0,3) UND im Bild ist. Beides einzeln geprüft: ein
Punkt mit Sicherheit 0,3 (Grenze, wird NICHT gemalt) und einer bei x = Breite
(einen Pixel außerhalb).
"""

import numpy as np
from django.test import SimpleTestCase

from core.dienste.skelettvideo import Skelettfilm
from core.dienste.skelettzeichner import Skelettzeichner


class ZuordnungTest(SimpleTestCase):

    def test_verhaeltnismaessig_wie_in_threejs(self):
        for bild, erwartet in ((0, 0), (50, 25), (100, 50)):
            self.assertEqual(Skelettfilm.zuordnen(bild, 101, 51), erwartet,
                             'Bild %d' % bild)

    def test_nie_ueber_das_letzte_bewegungsbild(self):
        self.assertEqual(Skelettfilm.zuordnen(999, 101, 51), 50)

    def test_einzelbild_faellt_auf_null(self):
        """Ein Video mit einem Bild würde sonst durch Null teilen."""
        self.assertEqual(Skelettfilm.zuordnen(0, 1, 51), 0)
        self.assertEqual(Skelettfilm.zuordnen(0, 101, 1), 0)


class ZeichnerTest(SimpleTestCase):

    def bild(self):
        return np.zeros((100, 200, 3), dtype=np.uint8)

    def test_linie_wird_gemalt(self):
        bild = self.bild()
        Skelettzeichner([('a', 'b')]).zeichnen(
            bild, {'a': (10, 50, 0.9), 'b': (190, 50, 0.9)})
        self.assertGreater(int(bild.sum()), 0, 'irgendwas muss gemalt sein')

    def test_unsicherer_punkt_bekommt_keine_linie(self):
        """Die Grenze ist 0,3 — genau 0,3 zählt NICHT.

        Der sichere Nachbar wird weiter als GELENK gemalt (ein Kreis von 3 px);
        nur die Linie zum unsicheren Punkt darf nicht entstehen. Geprüft wird
        deshalb, wo gemalt wurde, nicht ob.
        """
        bild = self.bild()
        Skelettzeichner([('a', 'b')]).zeichnen(
            bild, {'a': (10, 50, 0.3), 'b': (190, 50, 0.9)})
        gemalt = np.argwhere(bild.sum(axis=2) > 0)
        self.assertTrue(len(gemalt))
        self.assertGreater(gemalt[:, 1].min(), 180,
                           'nur um den sicheren Punkt herum, keine Linie nach links')

    def test_punkt_ausserhalb_des_bildes_wird_nicht_gemalt(self):
        bild = self.bild()
        Skelettzeichner([('a', 'b')]).zeichnen(
            bild, {'a': (200, 50, 0.9), 'b': (100, 50, 0.9)})
        # Der zweite Punkt liegt im Bild und wird als Gelenk gemalt; die LINIE
        # zum Punkt ausserhalb darf nicht entstehen.
        gemalt = np.argwhere(bild.sum(axis=2) > 0)
        self.assertTrue(len(gemalt), 'das Gelenk im Bild wird gemalt')
        self.assertLess(gemalt[:, 1].max(), 110, 'keine Linie nach rechts raus')

    def test_farbe_und_dicke_kommen_durch(self):
        bild = self.bild()
        Skelettzeichner([('a', 'b')], farbe=(255, 0, 0), dicke=1).zeichnen(
            bild, {'a': (10, 50, 0.9), 'b': (190, 50, 0.9)})
        self.assertGreater(int(bild[:, :, 0].sum()), 0, 'Blau-Kanal (BGR)')


class ZielpfadTest(SimpleTestCase):

    class Auftrag:
        id = 3
        name = 'tanz.mp4'
        pipeline = 'v4'
        video_file = 'video.mp4'
        bvh_file = ''
        fps = 30

    def test_ueberlagerung_und_rig_haben_eigene_dateien(self):
        auftrag = self.Auftrag()
        ueber = Skelettfilm(auftrag, ueberlagern=True).zielpfad().name
        rig = Skelettfilm(auftrag, ueberlagern=False).zielpfad().name
        self.assertEqual(ueber, 'v4_tanz_overlay.mp4')
        self.assertEqual(rig, 'v4_tanz_rig_only.mp4')

    def test_bvh_rig_ist_eine_dritte_datei(self):
        """Sonst zeigte der Zwischenspeicher das 2D-Rig, wo das BVH-Rig gemeint war."""
        auftrag = self.Auftrag()
        auftrag.bvh_file = __file__          # existiert
        self.assertEqual(Skelettfilm(auftrag, ueberlagern=False).zielpfad().name,
                         'v4_tanz_rig_only_bvh.mp4')
