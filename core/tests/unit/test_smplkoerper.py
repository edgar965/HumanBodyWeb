# -*- coding: utf-8 -*-
u"""Smplkoerper — die Gegenprobe gegen GarmentCodes eigene A40-Koerper.

Der Generator formt und posiert SMPL selbst (Blendshapes, Kinematik, Linear
Blend Skinning). Bevor er andere Formen liefern darf, muss er den Koerper
reproduzieren, den GarmentCode mitliefert: `f_/m_smpl_average_A40.obj`.
Ohne diese Probe waere jede Variante eine Behauptung — die A-Haltung (40
Grad abgesenkte Arme) haengt an der Wahl des Gelenks und am Vorzeichen der
Drehachse, und beides sieht man einem Netz nicht an.

Gemessen am 06.09.2026: Median 1,8 mm (maennlich) und 2,1 mm (weiblich)
Abstand je Punkt. Die Schwelle steht bei 5 mm Median — enger waere gegen
das Runden der OBJ-Dateien (vier Nachkommastellen) unnoetig scharf.
"""

import os
import unittest

import numpy as np

import sys
sys.path.insert(0, r'A:\3DTools\HumanBody')

from django.conf import settings  # noqa: E402

from GarmentCode.smplkoerper import Smplkoerper  # noqa: E402


def _bodies():
    from GarmentCode.entwurf import Entwurf
    return os.path.join(Entwurf.REPO, 'assets', 'bodies')


def _obj_punkte(pfad):
    punkte = []
    with open(pfad, 'r', encoding='utf-8') as quelle:
        for zeile in quelle:
            if zeile.startswith('v '):
                teile = zeile.split()
                punkte.append([float(teile[1]), float(teile[2]), float(teile[3])])
    return np.asarray(punkte, dtype=np.float64)


class SmplkoerperTest(unittest.TestCase):

    databases = []

    @classmethod
    def setUpClass(cls):
        cls.modelle = str(settings.SMPL_MODELS_DIR)
        cls.vorhanden = all(
            os.path.isfile(os.path.join(cls.modelle, 'SMPL_%s.npz' % g.upper()))
            for g in ('female', 'male'))

    def _pruefe(self, geschlecht, datei):
        if not self.vorhanden:
            self.skipTest('SMPL-Modelldateien nicht vorhanden')
        pfad = os.path.join(_bodies(), datei)
        if not os.path.isfile(pfad):
            self.skipTest('GarmentCode-Klon ohne %s' % datei)
        modell = Smplkoerper.laden(geschlecht, self.modelle)
        eigen = modell.a40(None)
        fremd = _obj_punkte(pfad)
        self.assertEqual(len(eigen), len(fremd), 'Punktzahl')
        abstand = np.linalg.norm(eigen - fremd, axis=1) * 1000.0
        self.assertLess(float(np.median(abstand)), 5.0,
                        'Median %.1f mm' % float(np.median(abstand)))
        self.assertLess(float(np.percentile(abstand, 90)), 12.0)

    def test_weiblicher_a40_wird_reproduziert(self):
        self._pruefe('female', 'f_smpl_average_A40.obj')

    def test_maennlicher_a40_wird_reproduziert(self):
        self._pruefe('male', 'm_smpl_average_A40.obj')

    def test_arme_sind_abgesenkt(self):
        u"""Die Gegenprobe zur Gegenprobe: Ohne die A-Haltung stehen die Arme
        gestreckt, und die Spannweite ist rund 30 cm groesser. Waere die
        Haltung wirkungslos, blieben beide Zahlen gleich."""
        if not self.vorhanden:
            self.skipTest('SMPL-Modelldateien nicht vorhanden')
        modell = Smplkoerper.laden('male', self.modelle)
        rest = modell.formen(None)
        a40 = modell.a40(None)
        spanne = lambda v: float(v[:, 0].max() - v[:, 0].min())   # noqa: E731
        self.assertGreater(spanne(rest) - spanne(a40), 0.15,
                           'A-Haltung senkt die Arme nicht')
        hoehe = lambda v: float(v[:, 1].max() - v[:, 1].min())    # noqa: E731
        self.assertAlmostEqual(hoehe(rest), hoehe(a40), delta=0.02)


class ArmlaengeTest(unittest.TestCase):
    u"""Die Armlaenge muss GEMESSEN sein, nicht aus der YAML kommen.

    GarmentCode baut den Aermel als `length * (arm_length - opening)`
    (`sleeves.py`:137). Die SMPL-YAML des Tools fuehrt dort 80 cm bei 165 cm
    Koerpergroesse — ein Platzhalter, der dem Tool nie auffaellt, weil es
    diese Datei nie zum Drapieren nimmt. Uebernommen ergibt er einen 24 cm
    langen Aermel, wo 16 cm gemeint sind.
    """

    databases = []

    @classmethod
    def setUpClass(cls):
        cls.modelle = str(settings.SMPL_MODELS_DIR)
        cls.vorhanden = all(
            os.path.isfile(os.path.join(cls.modelle, 'SMPL_%s.npz' % g.upper()))
            for g in ('female', 'male'))

    def test_armlaenge_passt_zur_koerpergroesse(self):
        if not self.vorhanden:
            self.skipTest('SMPL-Modelldateien nicht vorhanden')
        for geschlecht in ('female', 'male'):
            modell = Smplkoerper.laden(geschlecht, self.modelle)
            v = modell.a40(None)
            hoehe = float(v[:, 1].max() - v[:, 1].min()) * 100
            arm = modell.armlaenge(None)
            anteil = arm / hoehe
            self.assertGreater(anteil, 0.25, '%s: Arm %.1f von %.1f cm' % (geschlecht, arm, hoehe))
            self.assertLess(anteil, 0.36, '%s: Arm %.1f von %.1f cm' % (geschlecht, arm, hoehe))
            # Der Platzhalter der Tool-YAML darf nie durchschlagen.
            self.assertLess(arm, 70.0, '%s: 80 cm aus der YAML?' % geschlecht)

    def test_armlaenge_waechst_mit_der_figur(self):
        u"""Eine groessere Figur hat laengere Arme — sonst waere der Wert
        eine Konstante und die Messung wirkungslos."""
        if not self.vorhanden:
            self.skipTest('SMPL-Modelldateien nicht vorhanden')
        from GarmentCode.smplform import Smplform
        modell = Smplkoerper.laden('male', self.modelle)
        klein = modell.armlaenge(Smplform.betas('male', -70, 0))
        gross = modell.armlaenge(Smplform.betas('male', 70, 0))
        self.assertGreater(gross - klein, 5.0, 'klein %.1f, gross %.1f' % (klein, gross))


if __name__ == '__main__':
    unittest.main()
