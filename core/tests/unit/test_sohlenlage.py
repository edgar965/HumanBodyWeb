# -*- coding: utf-8 -*-
u"""Die Sohle folgt der Fussmitte und bleibt in der Simulation, wo sie liegt.

WARUM (11.09.2026, Edgar am Plateauschuh: „an einer Seite kommt die Haut
durch", dann „bei den Schuhen kommt auch noch die Haut durch")
======================================================================
Zwei Ursachen, beide gemessen an der Ballerina auf „FemaleWithHair":

1. Die Sohle lag symmetrisch um `foot_x` (das Mittel ALLER Fusspunkte,
   0,9 cm aussen von der Umrissmitte); die grosse Zehe liegt 2,9 cm innen
   davon und stand 2,6 cm über den Rand (`schuh/sohle.py`, `versatz`).
2. Das gespannte Oberteil zog die Stoffsohle mit: 1,3 cm zur Seite, Rand
   4–11 mm hoch, an der Ferse 5–7 mm schmaler als der Fuss
   (`schuh/sohlenhalt.py`: Bindung an den Schnitt im Simulator).

Dazu die Falle in pygarment: `Panel.assembly` rundet den ersten Vertex
beim Umhängen des Drehpunkts auf ganze Zentimeter — ein Start in
(-0,94, 0) verschob die ganze Sohle um 0,94 cm. Deshalb beginnt jede
Sohlenkontur in (0, 0).
"""
import numpy as np
from django.test import SimpleTestCase

from . import test_schuhschnitt as _schnitt
from ._schuhbau import Schuhbau


class SohlenlageTest(SimpleTestCase):

    databases = set()
    # Als Modul importiert, nicht die Klasse: Sonst liefe deren Suite hier
    # ein zweites Mal mit.
    FUSS = _schnitt.SchuhschnittTest.FUSS

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Schuhbau.vorbereiten(cls.FUSS)

    def _sohlenkontur(self, muster, name_endet):
        from GarmentCode.schnittvorschau import Schnittvorschau
        spez = muster.assembly().pattern
        vorschau = Schnittvorschau({'pattern': spez})
        for name, panel in spez['panels'].items():
            if name.startswith('probe_l') and name.endswith(name_endet):
                return np.asarray(vorschau.platzieren(vorschau.kontur(panel), panel))
        raise AssertionError('kein Panel %s' % name_endet)

    def test_die_sohle_beginnt_im_ursprung_und_liegt_auf_der_fersenmitte(self):
        from GarmentCode.schuh.sohle import Sohlenpanel
        k = Sohlenpanel.kontur(25.0, 10.0, 8.0, versatz=(-0.5, -2.0))
        self.assertEqual(list(k['ferse_a'].start), [0.0, 0.0])
        # Ballenmitte -0,5, Spitze bei -2,0 gegen die Ferse.
        self.assertAlmostEqual(k['seite_va'].end[0], -0.5 + 5.0)
        self.assertAlmostEqual(k['zehe_i'].start[0], -2.0)
        self.assertAlmostEqual(k['zehe_a'].end[0], -2.0)
        # Innen und aussen sind damit nicht gleich lang.
        p = Sohlenpanel('s', 25.0, 10.0, 8.0, versatz=(-0.5, -2.0))
        self.assertNotAlmostEqual(p.randlaenge_hinten('a'), p.randlaenge_hinten('i'),
                                  delta=0.01)

    def test_die_sohle_folgt_der_fussmitte_im_raum(self):
        u"""An der Ferse liegt die Sohlenmitte auf `foot_heel_x`, die Spitze
        auf `foot_toe_x` — nicht auf `foot_x`."""
        kontur = self._sohlenkontur(Schuhbau.bauen('Halbschuh'), '_sohle')
        hinten = kontur[kontur[:, 2] < kontur[:, 2].min() + 0.3]
        spitze = kontur[np.argmax(kontur[:, 2])]
        self.assertAlmostEqual((hinten[:, 0].min() + hinten[:, 0].max()) / 2.0,
                               self.FUSS['foot_heel_x'], delta=0.3)
        self.assertAlmostEqual(spitze[0], self.FUSS['foot_toe_x'], delta=0.3)
        self.assertGreater(abs(spitze[0] - self.FUSS['foot_x']), 2.0)

    def test_auch_die_zweiteilige_sohle_beginnt_je_panel_im_ursprung(self):
        from GarmentCode.schuh.sohlenteile import Sohlenteile
        teile = Sohlenteile('s', 25.0, 10.0, 8.0, versatz=(-0.5, -2.0))
        for panel in teile.panels():
            self.assertEqual(list(panel.edges[0].start), [0.0, 0.0], panel.name)
        # Die Ballennaht ist auf beiden Seiten zwei Kanten lang.
        self.assertEqual(len(teile.vorn.interfaces['ballen'].edges), 2)
        self.assertEqual(len(teile.hinten.interfaces['ballen'].edges), 2)

    def test_der_sohlenhalt_bindet_innen_an_die_anfangslage_und_den_rand_an_die_kontur(self):
        u"""Ein Sohlenpanel als Quadrat (Punkte 0–3 innen), zwei Nahtpunkte
        (4, 5) daneben, die das Boxmesh in die Luft gesetzt hat: Sie
        landen auf der geplanten Kontur, die inneren bleiben, wo sie sind."""
        from GarmentCode.schuh.sohlenhalt import Sohlenhalt

        class Stoff:
            pass

        stoff = Stoff()
        init = np.array([[0, 0, 0], [1, 0, 0], [1, 0, 1], [0, 0, 1],
                         [1.5, 2.0, 0.5], [-0.5, 2.0, 0.5]], dtype=float)
        flaechen = np.array([[0, 1, 2], [0, 2, 3], [1, 4, 2], [3, 5, 0], [4, 5, 5]])
        kontur = np.array([[-1, 0, -1], [2, 0, -1], [2, 0, 2], [-1, 0, 2]], dtype=float)
        original = Sohlenhalt.__dict__['kontur']
        Sohlenhalt.kontur = classmethod(lambda cls, cloth, name: cls.verdichtet(kontur))
        try:
            ziele = Sohlenhalt.ziele(stoff, {'x_sohle': [0, 1, 2, 3]}, init, flaechen)
        finally:
            Sohlenhalt.kontur = original
        self.assertEqual(sorted(ziele), [0, 1, 2, 3, 4, 5])
        for i in range(4):
            np.testing.assert_allclose(ziele[i], init[i])
        np.testing.assert_allclose(ziele[4], [2.0, 0.0, 0.5], atol=0.01)
        np.testing.assert_allclose(ziele[5], [-1.0, 0.0, 0.5], atol=0.01)

    def test_der_absatz_endpunkt_liefert_die_reinen_fussdeltas(self):
        mit = self.client.get('/api/character/pose/ruhelage/?winkel_grad=25'
                              '&hebung_cm=4.9').json()
        self.assertEqual(sorted(mit['absatz_deltas']),
                         ['DEF-foot.L', 'DEF-foot.R', 'DEF-toe.L', 'DEF-toe.R'])
        ohne = self.client.get('/api/character/pose/ruhelage/').json()
        self.assertEqual(ohne['absatz_deltas'], {})
