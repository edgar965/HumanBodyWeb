# -*- coding: utf-8 -*-
"""GEM-X-Finger auf SMPL-X: jeder Knochen zeigt dorthin, wohin SOMA ihn schickt.

DER ANLASS (24.09.2026, Edgar an Auftrag 2026.09.24.13.39.32: „die Finger der
Haende im Ursprungsvideo sind zusammen, im BVH sind die Finger
auseinandergespreizt"): SOMAs Fingerglieder liegen in der T-Pose parallel
zur Handachse, SMPL-X' gestreckte Hand ist gefaechert (kleiner Finger 37,8
Grad daneben). `Somahaende` uebertrug die Drehungen 1:1 — Zeige- gegen
Kleinfinger-Grundglied 46,6 Grad statt 12,6 wie im SOMA. Seither gleicht
`_angleichen` die Ruhelagen an (gemessen danach 0,0 Grad je Glied).

BDD - GEGEBEN / DANN
====================
    DieAngleichung  ... Ruhe und gebeugte Finger: SMPL-X-Knochen = SOMA-Knochen
                    ... ohne tpose bleibt es 1:1 (alte Aufrufer, mit Warnung)
"""

import unittest

from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

import numpy as np  # noqa: E402
from scipy.spatial.transform import Rotation  # noqa: E402
from SMPL.finger import Smplxfinger  # noqa: E402
from somahaende import Somahaende  # noqa: E402


class DieAngleichung(unittest.TestCase):
    N = 2
    FINGER = ('Thumb', 'Index', 'Middle', 'Ring', 'Pinky')

    def _skelett(self):
        """Namen und T-Pose: alle Fingerglieder entlang ±x, der Daumen schraeg nach vorn."""
        namen, tpose = ['Hips'], [[0.0, 0.0, 0.0]]
        for seite, vz in (('Left', 1.0), ('Right', -1.0)):
            namen.append('%sHand' % seite)
            tpose.append([vz * 50.0, 0.0, 0.0])
            for k, finger in enumerate(self.FINGER):
                glieder = ('1', '2', '3', 'End') if finger == 'Thumb' else ('1', '2', '3', '4', 'End')
                z = 2.0 - k
                for i, g in enumerate(glieder):
                    namen.append('%sHand%s%s' % (seite, finger, g))
                    if finger == 'Thumb':
                        tpose.append([vz * (50.0 + 1.5 * (i + 1)), -0.5, 2.0 + 1.5 * (i + 1)])
                    else:
                        tpose.append([vz * (50.0 + 2.5 + 2.5 * i), 0.0, z])
        return namen, np.asarray(tpose) / 100.0

    def _params(self, drehung, mit_tpose=True):
        namen, tpose = self._skelett()
        koerper = np.zeros((self.N, len(namen) - 1, 3), np.float32)
        for name, rv in drehung.items():
            koerper[:, namen.index(name) - 1] = rv
        params = {'names': np.array(namen), 'body_pose': koerper}
        if mit_tpose:
            params['tpose'] = tpose
        return params, namen, tpose, koerper

    @staticmethod
    def _smplx_knochen(hand, seite, finger):
        i = Smplxfinger.FINGER.index(finger)
        basis = Smplxfinger.NAMEN.index('%s_%s1' % (seite, finger))
        G = Rotation.identity()
        aus = []
        for k in range(3):
            G = G * Rotation.from_rotvec(hand[i * 3 + k].astype(np.float64))
            d = np.asarray(Smplxfinger.OFFSETS[basis + min(k + 1, 2)], dtype=np.float64)
            aus.append(G.apply(d / np.linalg.norm(d)))
        return aus

    @staticmethod
    def _soma_knochen(namen, tpose, koerper, seite, finger):
        vs = Somahaende.SEITEN[seite] + Somahaende.FINGER[finger]
        kette = ('1', '2', '3') if finger == 'thumb' else ('1', '2', '3', '4')
        G, welt = Rotation.identity(), {}
        for g in kette:
            G = G * Rotation.from_rotvec(koerper[0, namen.index(vs + g) - 1].astype(np.float64))
            welt[g] = G
        aus = []
        for gelenk, kind in Somahaende.KNOCHEN['thumb' if finger == 'thumb' else 'finger']:
            d = tpose[namen.index(vs + kind)] - tpose[namen.index(vs + gelenk)]
            aus.append(welt[gelenk].apply(d / np.linalg.norm(d)))
        return aus

    def _vergleichen(self, drehung):
        params, namen, tpose, koerper = self._params(drehung)
        links, rechts = Somahaende(params, np).haende(self.N)
        for seite, hand in (('left', links[0]), ('right', rechts[0])):
            for finger in Smplxfinger.FINGER:
                soll = self._soma_knochen(namen, tpose, koerper, seite, finger)
                ist = self._smplx_knochen(hand, seite, finger)
                for k, (a, b) in enumerate(zip(soll, ist)):
                    with self.subTest(seite=seite, finger=finger, glied=k + 1):
                        np.testing.assert_allclose(b, a, atol=1e-5)

    def test_ruhe_bleibt_geschlossen(self):
        """Keine Drehung im SOMA -> kein gefaecherter SMPL-X-Kleinfinger."""
        self._vergleichen({})

    def test_gebeugte_finger_zeigen_wie_im_soma(self):
        self._vergleichen({
            'LeftHandIndex1': [0.0, 0.1, 0.05], 'LeftHandIndex2': [0.0, 0.0, -0.9],
            'LeftHandPinky3': [0.0, 0.0, -1.2], 'RightHandRing2': [0.2, 0.0, 0.7],
            'RightHandThumb2': [0.3, 0.4, 0.0],
        })

    def test_ohne_tpose_bleibt_es_eins_zu_eins(self):
        params, _namen, _tpose, _k = self._params({'LeftHandIndex3': [0.0, 0.0, 0.5]}, mit_tpose=False)
        links, _ = Somahaende(params, np).haende(self.N)
        np.testing.assert_allclose(links[0, 1], [0.0, 0.0, 0.5], atol=1e-6)
        np.testing.assert_allclose(links[0, 0], 0.0, atol=1e-6)
