# -*- coding: utf-8 -*-
"""`Retargetwahl` — die Wahl des Retarget-Verfahrens aus der Anfrage.

`delta_norm` ist DREIWERTIG — das ist der ganze Punkt: „1" heisst ja,
„0" heisst nein, und KEINE Angabe heisst „das Format entscheidet". Mit
einem `bool()` waeren der dritte und der zweite Fall dasselbe.
"""

from django.test import SimpleTestCase

from core.daten.retargetwahl import Retargetwahl


class RetargetwahlTest(SimpleTestCase):
    """`delta_norm` ist DREIWERTIG — das ist der ganze Punkt."""

    def test_drei_zustaende(self):
        self.assertIs(Retargetwahl({'delta_norm': '1'}, 1.68).delta_norm, True)
        self.assertIs(Retargetwahl({'delta_norm': '0'}, 1.68).delta_norm, False)
        self.assertIsNone(Retargetwahl({}, 1.68).delta_norm,
                          'ohne Angabe entscheidet das Format')
        self.assertIsNone(Retargetwahl({'delta_norm': 'vielleicht'},
                                       1.68).delta_norm)

    def test_groesse_und_fusskorrektur(self):
        wahl = Retargetwahl({'body_height': '1.80',
                             'foot_correction': 'TRUE'}, 1.68)
        self.assertAlmostEqual(wahl.groesse, 1.80)
        self.assertTrue(wahl.fusskorrektur)

    def test_vorgabe_greift(self):
        wahl = Retargetwahl({}, 1.68)
        self.assertAlmostEqual(wahl.groesse, 1.68)
        self.assertFalse(wahl.fusskorrektur)
        self.assertIsNone(wahl.format)
