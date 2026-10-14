# -*- coding: utf-8 -*-
"""Kleidungarmprobe: trägt Stoff Armgewicht, obwohl er weit vom Arm liegt? (14.10.2026)

Die Gewebe-Regel (`Kleidunggewebe`) hängt den Rock der Ballerina vom Bund statt an die Hände, hängt aber eine weite Robe (Zauberer) an die Arme — gemessen: Armgewicht bei Stoff ab 25 cm vom Arm 0,9 % → 21 %. Die Animationsprüfung
(`Meshfigurtanzpruefung._gewebe`) übernimmt die Regel deshalb nur, wenn dieses Maß nicht steigt.

    ArmTest      welcher Knochen zählt zum Arm (Fuß, Zehen, Becken nicht); Abstand zum nächsten Arm-Käfigpunkt; gezählt wird, was FERN liegt UND Armgewicht trägt (ein Ärmel am Arm nicht, ein Rock an der Hand ja)
    DrahtTest    Quelltext: die Gewebe-Regel wird mit der Probe geprüft und nennt den Grund

Sabotage: in `Kleidungarmprobe.zaehlen` `fern > self.FERN_M` durch `True` ersetzen → `test_ein_aermel_am_arm_zaehlt_nicht` rot; in `armknochen` das `'foot' not in k` streichen → `test_fuss_und_zehen_sind_kein_arm` rot;
in `Meshfigurtanzpruefung._gewebe` `arm_nachher <= arm_vorher` durch `True` ersetzen → `DrahtTest` rot.
"""

from pathlib import Path

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from Kleidung.kleidungarmprobe import Kleidungarmprobe

WEB = Path(settings.BASE_DIR)

KNOCHEN = ['pelvis', 'spine1', 'l_upperarm', 'l_forearm', 'l_hand', 'l_index1', 'l_foot', 'l_toes', 'l_midfoot', 'head']


def kaefig():
    """Ein Käfig aus 20 Punkten am Arm (x 0,3 … 0,6, y 1,3; ganz am linken Oberarm) und 20 am Rumpf (x −0,1 … 0,1, y 1,0 … 1,4; ganz am Becken)."""
    arm = np.stack([np.linspace(0.3, 0.6, 20), np.full(20, 1.3), np.zeros(20)], axis=1)
    rumpf = np.stack([np.linspace(-0.1, 0.1, 20), np.linspace(1.0, 1.4, 20), np.zeros(20)], axis=1)
    punkte = np.concatenate([arm, rumpf])
    index = np.zeros((40, 4), dtype=np.int64)
    index[:20] = 2
    gewicht = np.zeros((40, 4))
    gewicht[:, 0] = 1.0
    return punkte, index, gewicht


class ArmTest(SimpleTestCase):
    databases = set()

    def test_welche_knochen_zum_arm_zaehlen(self):
        arm = Kleidungarmprobe.armknochen(KNOCHEN)
        self.assertEqual([k for k, a in zip(KNOCHEN, arm, strict=True) if a], ['l_upperarm', 'l_forearm', 'l_hand', 'l_index1'])

    def test_fuss_und_zehen_sind_kein_arm(self):
        arm = Kleidungarmprobe.armknochen(['l_foot', 'l_toes', 'l_midfoot', 'r_index1', 'l_shoulder'])
        self.assertEqual(arm.tolist(), [False, False, False, True, True], '`mid` im Mittelfuß darf nicht als Mittelfinger zählen')

    def test_abstand_zum_naechsten_arm_punkt(self):
        punkte, index, gewicht = kaefig()
        probe = Kleidungarmprobe(punkte, index, gewicht, KNOCHEN)
        fern = probe.fern([[0.45, 1.3, 0.02], [0.0, 0.8, 0.0], [0.3, 1.3, 0.0]])
        np.testing.assert_allclose(fern[0], 0.02, atol=0.01)
        self.assertGreater(fern[1], 0.5, 'unter dem Rumpf, weit weg vom Arm')
        self.assertAlmostEqual(float(fern[2]), 0.0, places=6)

    def test_ein_aermel_am_arm_zaehlt_nicht_ein_rock_an_der_hand_schon(self):
        punkte, index, gewicht = kaefig()
        probe = Kleidungarmprobe(punkte, index, gewicht, KNOCHEN)
        ruhe = [[0.45, 1.3, 0.02], [0.0, 0.8, 0.0], [0.0, 0.8, 0.1], [0.05, 0.7, 0.0]]
        fern = probe.fern(ruhe)
        # Punkt 0: am Arm, Armgewicht 1 (Ärmel) · Punkt 1: weit weg, Armgewicht 0,8 (Rock an der Hand) · Punkt 2: weit weg, nur 0,1 Armgewicht · Punkt 3: weit weg, kein Armgewicht
        ind = np.array([[2, 0, 0, 0], [2, 0, 0, 0], [2, 0, 0, 0], [0, 1, 0, 0]])
        gew = np.array([[1.0, 0, 0, 0], [0.8, 0.2, 0, 0], [0.1, 0.9, 0, 0], [0.5, 0.5, 0, 0]])
        self.assertEqual(probe.zaehlen(fern, ind, gew), 1)

    def test_ein_aermel_am_arm_zaehlt_nicht(self):
        punkte, index, gewicht = kaefig()
        probe = Kleidungarmprobe(punkte, index, gewicht, KNOCHEN)
        fern = probe.fern([[0.45, 1.3, 0.02]])
        self.assertEqual(probe.zaehlen(fern, [[2, 0, 0, 0]], [[1.0, 0, 0, 0]]), 0)

    def test_ohne_arm_im_kaefig_ist_alles_fern(self):
        punkte, index, gewicht = kaefig()
        index[:] = 0
        probe = Kleidungarmprobe(punkte, index, gewicht, KNOCHEN)
        fern = probe.fern([[0.0, 0.0, 0.0]])
        self.assertTrue(np.isinf(fern[0]))


class DrahtTest(SimpleTestCase):
    databases = set()

    def test_die_gewebe_regel_wird_an_der_armprobe_geprueft(self):
        quelle = (WEB / 'core' / 'dienste' / 'meshfigurtanzpruefung.py').read_text(encoding='utf-8')
        self.assertIn('Kleidungarmprobe(kaefig_ruhe, gewichte.index, gewichte.gewicht, gewichte.knochen)', quelle)
        self.assertIn('angewandt = streckung_ok and arm_nachher <= arm_vorher', quelle)
        self.assertIn("'arm_fern_vorher': arm_vorher, 'arm_fern_nachher': arm_nachher", quelle, 'der Bericht nennt beide Zahlen')
        self.assertIn('ruhelage.entposen.ruhe)', quelle, 'der Käfig in Ruhe geht an die Regel')
