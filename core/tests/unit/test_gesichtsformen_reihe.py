# -*- coding: utf-8 -*-
u"""Euler → Quaternion je Knochen in einem Aufruf — bitgleich zum Einzelaufruf.

Gemessen am 12.09.2026 (cProfile, Auftrag 485e51f6, 1.004 Bilder): Ein Abruf
des Retargets brauchte 1,9 s, davon 1,7 s in 37.148 Einzelaufrufen von
`scipy.Rotation.from_euler` (je Bild, je Gesichtsknochen) — die Umrechnung
selbst ist keine 20 ms. `Gesichtsformen.eulerreihe_zu_quat` rechnet alle
Bilder eines Knochens auf einmal; danach 0,29 s je Abruf.

Was hier gilt: dieselben Zahlen wie vorher. Der Einzelaufruf ist die
Referenz, die Reihe muss ihn bis auf Rundung treffen — für die Ausdrucks-
spuren und für die Kieferspuren, die denselben Weg nehmen.
"""
import numpy as np
from django.test import SimpleTestCase
from scipy.spatial.transform import Rotation

from humanbody_core.skeleton.face_blendshapes import Gesichtsformen
from humanbody_core.skeleton.kieferspuren import Kieferspuren

ZUFALL = np.random.default_rng(12)


def einzeln(rx, ry, rz):
    u"""Die Formel vor dem Umbau: Euler(rx, rz, -ry, 'XYZ') → [x, y, z, w]."""
    return Rotation.from_euler('XYZ', [rx, rz, -ry]).as_quat()


class DieReihe(SimpleTestCase):

    databases = set()

    def test_die_reihe_trifft_den_einzelaufruf(self):
        eulers = ZUFALL.uniform(-1.0, 1.0, size=(50, 3))
        reihe = Gesichtsformen.eulerreihe_zu_quat(eulers)
        self.assertEqual(reihe.shape, (50, 4))
        for e, q in zip(eulers, reihe):
            np.testing.assert_allclose(q, einzeln(*e), atol=1e-12)

    def test_der_einzelaufruf_bleibt(self):
        np.testing.assert_allclose(Gesichtsformen._euler_to_threejs_quat(0.3, -0.2, 0.5),
                                   einzeln(0.3, -0.2, 0.5), atol=1e-12)

    def test_eine_leere_reihe_gibt_keine_quaternionen(self):
        self.assertEqual(Gesichtsformen.eulerreihe_zu_quat([]).shape, (0, 4))

    def test_die_ausdrucksspuren_sind_die_alten(self):
        bilder = ZUFALL.uniform(-2.0, 2.0, size=(6, 10)).tolist()
        spuren = Gesichtsformen.expression_to_bone_tracks(bilder, fps=30.0)
        self.assertEqual(spuren.frame_count, 6)
        for name, werte in spuren.tracks.items():
            self.assertEqual(len(werte), 6 * 4)
            for bild, ausdruck in enumerate(bilder):
                euler = Gesichtsformen._expression_to_bone_eulers(ausdruck).get(name, [0, 0, 0])
                np.testing.assert_allclose(werte[bild * 4:bild * 4 + 4],
                                           einzeln(*euler), atol=1e-12)

    def test_die_kieferspuren_sind_die_alten(self):
        spuren = Gesichtsformen.expression_to_bone_tracks([[0.0] * 10] * 5, fps=30.0)
        kiefer = [[0.1, 0, 0], [0.4, 0, 0], [0.9, 0, 0], [-0.2, 0, 0]]   # 4 von 5 Bildern
        Kieferspuren.einsetzen(spuren, kiefer)
        soll = [0.1, 0.4, Kieferspuren.HOECHSTENS, 0.0, 0.0]
        for knochen, anteil in Kieferspuren.ANTEILE:
            for bild, wert in enumerate(soll):
                np.testing.assert_allclose(spuren.tracks[knochen][bild * 4:bild * 4 + 4],
                                           einzeln(wert * anteil, 0.0, 0.0), atol=1e-12)
