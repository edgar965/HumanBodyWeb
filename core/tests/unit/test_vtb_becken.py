# -*- coding: utf-8 -*-
u"""Das Becken der 2D-Ueberlagerung: wo die BVH-Wurzel im Kameraraum landet.

DIE HARTE ZUSICHERUNG
=====================
Statt Pixelzahlen zu vergleichen, prueft `DasBecken`, wo das
Wurzelgelenk landet: Es liegt im Kameraraum auf `transl` PLUS dem
zurueckgedrehten Wurzeloffset — `transl` verschiebt den SMPL-Ursprung,
das Becken sitzt 35 cm darueber. Dieser Vergleich haengt an keiner
Bildgroesse und an keiner Brennweite.

DER ZWEITE ANLASS (12.09.2026)
==============================
Bis dahin verlangte dieser Test das Gegenteil („die Wurzel MUSS genau
auf `transl` liegen") und `Bildpunkte.aus_bvh` zog den Wurzeloffset
ab. Beides war eine Annahme ohne Messung. Gemessen an
`001_ShyrinKurz.mp4` gegen ViTPose (zwoelf Gelenke, 298 Bilder):
mit Abzug 95,9 px daneben, ohne Abzug 23,4 px. Ein gruener Test, der
das Falsche zusichert, ist schlimmer als keiner — deshalb steht die
Messung hier und die Gegenprobe prueft jetzt die andere Richtung.

WAS DIESE PRUEFUNG NICHT IST
============================
Sie startet GVHMR nicht. Ob die Posenschaetzung stimmt, sagt sie nicht
— sie sagt, dass die Umrechnung dazwischen stimmt.

Herausgeloest aus `test_vtb_bvh.py` (Dateigrenze 300 Zeilen).
"""
import unittest

from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

import numpy as np                                          # noqa: E402

from bildpunkte import Bildpunkte                           # noqa: E402
from smplskelett import Smplskelett                         # noqa: E402


class DasBecken(unittest.TestCase):
    u"""Die Wurzel liegt im Kameraraum auf `transl` plus Wurzeloffset."""

    #: Der Wurzeloffset des BVH: die Lage des Beckens ueber dem Ursprung.
    RUHEHOEHE_CM = 35.070

    def _bvh(self, verschiebung):
        u"""Ein BVH-Datensatz ohne Drehungen, nur mit Wurzelbewegung."""
        anzahl = len(verschiebung)
        offsets = np.array(Smplskelett.OFFSETS, dtype=np.float64)
        positionen = np.tile(offsets, (anzahl, 1, 1))
        # So baut `Bvhbau`: Y und Z gespiegelt, in Zentimetern.
        gespiegelt = verschiebung.copy()
        gespiegelt[:, 1] *= -1
        gespiegelt[:, 2] *= -1
        positionen[:, 0] += gespiegelt * Smplskelett.CM_JE_M
        return {'names': list(Smplskelett.NAMEN),
                'parents': list(Smplskelett.ELTERN),
                'offsets': offsets, 'order': 'zyx',
                'rotations': np.zeros((anzahl, 24, 3)),
                'positions': positionen}

    @staticmethod
    def _rueck():
        return np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]], dtype=np.float64)

    def _welt(self, bvh, bild):
        from scipy.spatial.transform import Rotation
        eltern = [int(p) for p in bvh['parents']]
        offsets = np.asarray(bvh['offsets'], dtype=np.float64)
        return Bildpunkte._vorwaerts(bvh, bild, eltern, offsets, Rotation, np)

    def _kameraraum(self, bvh, bild):
        u"""Genau die Umrechnung von `Bildpunkte.aus_bvh`: drehen, teilen."""
        return (self._rueck() @ self._welt(bvh, bild).T).T / Smplskelett.CM_JE_M

    def _beckenlage(self, bvh):
        u"""Der zurueckgedrehte Wurzeloffset in Metern: (0, -0,35, 0,03)."""
        return self._rueck() @ np.asarray(bvh['offsets'][0]) / Smplskelett.CM_JE_M

    def test_die_wurzel_sitzt_ueber_der_verschiebung(self):
        verschiebung = np.array([[0.0, 0.0, 3.0], [0.5, -0.2, 2.5],
                                 [-0.3, 0.1, 4.0]])
        bvh = self._bvh(verschiebung)
        for bild in range(len(verschiebung)):
            with self.subTest(bild=bild):
                becken = self._kameraraum(bvh, bild)[0]
                soll = verschiebung[bild] + self._beckenlage(bvh)
                self.assertTrue(np.allclose(becken, soll, atol=1e-6),
                                '%s != %s' % (becken, soll))

    def test_der_wurzeloffset_zeigt_im_kameraraum_nach_oben(self):
        u"""Y zeigt im Kameraraum nach unten: -0,35 m heisst 35 cm ueber
        dem Ursprung — dort sitzt das Becken eines stehenden Menschen."""
        lage = self._beckenlage(self._bvh(np.zeros((1, 3))))
        self.assertAlmostEqual(lage[1], -self.RUHEHOEHE_CM / 100, places=4)

    def test_mit_abzug_saesse_das_becken_auf_dem_ursprung(self):
        u"""Die Gegenprobe zur alten Fassung: Wer den Offset abzieht, setzt
        das Becken auf `transl` — 35 cm unter die Person (gemessen 96 px
        statt 23 px, siehe Modulkopf)."""
        verschiebung = np.array([[0.0, 0.0, 3.0]])
        bvh = self._bvh(verschiebung)
        offsets = np.asarray(bvh['offsets'], dtype=np.float64)
        mit_abzug = (self._rueck() @ (self._welt(bvh, 0)[0] - offsets[0])
                     / Smplskelett.CM_JE_M)
        self.assertTrue(np.allclose(mit_abzug, verschiebung[0], atol=1e-6))
        abstand = float(np.linalg.norm(self._kameraraum(bvh, 0)[0] - mit_abzug))
        self.assertGreater(abstand, self.RUHEHOEHE_CM / 100)

    def test_die_kette_ist_zusammenhaengend(self):
        u"""Kein Gelenk liegt weiter als einen Knochen vom Elter weg."""
        bvh = self._bvh(np.array([[0.0, 0.0, 3.0]]))
        punkte = self._kameraraum(bvh, 0)
        for kind, elter in enumerate(Smplskelett.ELTERN):
            if elter < 0:
                continue
            laenge = float(np.linalg.norm(punkte[kind] - punkte[elter]))
            soll = float(np.linalg.norm(
                np.array(Smplskelett.OFFSETS[kind]))) / 100
            with self.subTest(gelenk=Smplskelett.NAMEN[kind]):
                self.assertAlmostEqual(laenge, soll, places=6)
