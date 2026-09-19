# -*- coding: utf-8 -*-
u"""Die HumanBody-Frisuren auf dem Genesis-9-Kopf — gegen die ECHTEN Dateien
(`hairstyles/*.glb`, Ursula1), nicht gegen Kunstköpfe.

ANLASS (19.09.2026 spät, Edgar: „HumanBody Haar: Ballerina Dutt funktioniert
nicht auf Genesis Modell"): Der Dutt (`ballerina_dutt.glb`, 219 Punkte) ist
eine Kugel von 9 cm, die auf HumanBody zur Hälfte im Hinterkopf steckt —
75 Punkte bis 47 mm tief, gewollt. `G9frisur.bauen` hob jeden dieser Punkte
einzeln über die Genesis-Kopfhaut: aus 10 × 7 × 10 cm wurden 12 × 8 × 6,5 cm,
Hub bis 54 mm (`_wegwerf/mess_dutt_genesis.py`) — eine plattgedrückte
Scheibe. Seither bekommt jeder Punkt als Ziel seine Tiefe auf HumanBody,
wenn er dort in der Haut lag (`G9frisur.zieltiefe`); gemessen danach
10,2 × 7,2 × 9,4 cm, Hub 5,3 mm.

1. Der Dutt bleibt eine Kugel: Tiefe (z) mindestens 90 % der Breite (x);
   vor dem Fix 54 %. Hub höchstens 15 mm (vorher 54).
2. Kein Punkt, der auf HumanBody außerhalb der Haut lag, steckt auf Genesis
   in der Haut — für Dutt und Ballerina.
3. Der Dutt ragt hinter den Genesis-Kopf wie hinter den HumanBody-Kopf
   (4,3 cm dort; hier 3–6 cm).

Sabotage-Gegenprobe: `zieltiefe` -> `np.full(len(punkte), ABSTAND)` (das alte
Verhalten) -> Fall 1 rot (54 %, 54 mm), Fälle 2 und 3 grün.
"""
import os
import unittest

import numpy as np
from django.test import SimpleTestCase

from Genesis9.pfade import G9pfade

from ..unit._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()
Humanbodypfad.assets()

REGLER = {'P3DUrsula_figure_ctrl_Character': 1}


def bibliothek_da():
    try:
        from core.dienste.g9frisur import G9frisur
        return G9pfade.vorhanden() and os.path.isfile(G9frisur.pfad('ballerina_dutt'))
    except Exception:  # noqa: BLE001 — ohne Bibliothek oder Frisur: kein Test
        return False


@unittest.skipUnless(bibliothek_da(), 'Daz-Bibliothek oder hairstyles/ballerina_dutt.glb fehlt')
class Genesis9FrisurSitz(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from core.dienste.g9frisur import G9frisur
        from core.dienste.hbtraeger import Hbtraeger
        from Genesis9.kollision import G9kollision
        from Genesis9.koerpernetz import G9koerpernetz
        cls.frisur = G9frisur(REGLER)
        fein, normalen, baum = G9koerpernetz(cls.frisur.figur.formung, stufen=1).koerperflaeche()
        cls.g9 = (fein, normalen, baum)
        hb = Hbtraeger.laden('female', None, {}, {})
        cls.hb = (np.asarray(hb['fein']), np.asarray(hb['fein_normalen']),
                  G9kollision.baum(hb['fein']))
        cls.netze, cls.roh = {}, {}
        for name in ('ballerina_dutt', 'ballerina'):
            cls.roh[name] = G9frisur.laden(G9frisur.pfad(name))[0]
            cls.netze[name] = cls.frisur.bauen(name, stufen=1)

    @classmethod
    def tiefe(cls, punkte, figur):
        from Genesis9.kollision import G9kollision
        fein, normalen, baum = figur
        return G9kollision.tiefe(punkte, fein, normalen, baum)

    def test_1_der_dutt_bleibt_eine_kugel(self):
        p = self.netze['ballerina_dutt']['punkte']
        breite, tiefe = np.ptp(p[:, 0]), np.ptp(p[:, 2])
        self.assertGreaterEqual(tiefe / breite, 0.90, 'Dutt %.1f x %.1f cm' % (breite * 100, tiefe * 100))
        self.assertLessEqual(self.netze['ballerina_dutt']['hub_mm'], 15.0)

    def test_2_was_auf_humanbody_aussen_lag_liegt_auch_hier_aussen(self):
        from core.dienste.g9frisur import G9frisur
        for name in ('ballerina_dutt', 'ballerina'):
            aussen_hb = self.tiefe(self.roh[name], self.hb) >= G9frisur.ABSTAND
            tiefe_g9 = self.tiefe(self.netze[name]['punkte'], self.g9)
            self.assertGreater(aussen_hb.sum(), 100, name)
            self.assertEqual(int((tiefe_g9[aussen_hb] < 0).sum()), 0, name)

    def test_3_der_dutt_ragt_hinter_den_kopf(self):
        kopf = self.frisur.kopf_g9()
        hinten = kopf['min'][2] - self.netze['ballerina_dutt']['punkte'][:, 2].min()
        self.assertGreater(hinten, 0.03)
        self.assertLess(hinten, 0.06)
