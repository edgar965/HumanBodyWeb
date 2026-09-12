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

from ._smplmodelle import Smplmodelle


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


class SmplkoerperTest(Smplmodelle, unittest.TestCase):

    databases = set()

    def _pruefe(self, geschlecht, datei):
        modell = self.modell(geschlecht)
        pfad = os.path.join(_bodies(), datei)
        if not os.path.isfile(pfad):
            self.skipTest('GarmentCode-Klon ohne %s' % datei)
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
        modell = self.modell('male')
        rest = modell.formen(None)
        a40 = modell.a40(None)

        def spanne(v):
            return float(v[:, 0].max() - v[:, 0].min())

        def hoehe(v):
            return float(v[:, 1].max() - v[:, 1].min())

        self.assertGreater(spanne(rest) - spanne(a40), 0.15,
                           'A-Haltung senkt die Arme nicht')
        self.assertAlmostEqual(hoehe(rest), hoehe(a40), delta=0.02)


class ArmlaengeTest(Smplmodelle, unittest.TestCase):
    u"""Die Armlaenge muss GEMESSEN sein, nicht aus der YAML kommen.

    GarmentCode baut den Aermel als `length * (arm_length - opening)`
    (`sleeves.py`:137). Die SMPL-YAML des Tools fuehrt dort 80 cm bei 165 cm
    Koerpergroesse — ein Platzhalter, der dem Tool nie auffaellt, weil es
    diese Datei nie zum Drapieren nimmt. Uebernommen ergibt er einen 24 cm
    langen Aermel, wo 16 cm gemeint sind.
    """

    databases = set()

    def test_armlaenge_passt_zur_koerpergroesse(self):
        for geschlecht in self.GESCHLECHTER:
            modell = self.modell(geschlecht)
            v = modell.a40(None)
            hoehe = float(v[:, 1].max() - v[:, 1].min()) * 100
            arm = modell.armlaenge(None)
            anteil = arm / hoehe
            wo = '%s: Arm %.1f von %.1f cm' % (geschlecht, arm, hoehe)
            self.assertGreater(anteil, 0.25, wo)
            self.assertLess(anteil, 0.36, wo)
            # Der Platzhalter der Tool-YAML darf nie durchschlagen.
            self.assertLess(arm, 70.0, '%s: 80 cm aus der YAML?' % geschlecht)

    def test_armlaenge_waechst_mit_der_figur(self):
        u"""Eine groessere Figur hat laengere Arme — sonst waere der Wert
        eine Konstante und die Messung wirkungslos."""
        from GarmentCode.smplform import Smplform
        modell = self.modell('male')
        klein = modell.armlaenge(Smplform.betas('male', -70, 0))
        gross = modell.armlaenge(Smplform.betas('male', 70, 0))
        self.assertGreater(gross - klein, 5.0,
                           'klein %.1f, gross %.1f' % (klein, gross))


if __name__ == '__main__':
    unittest.main()
