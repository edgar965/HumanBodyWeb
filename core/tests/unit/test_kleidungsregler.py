# -*- coding: utf-8 -*-
"""`Kleidungsregler` — Anfragewert oder Vorlagenwert?

„Unbrauchbar → Vorgabe" ist die Vorschrift dieser Klasse: Die Regler kommen
aus der Abfragezeichenkette, und `offset=viel` darf keine Fehlerseite
ergeben, sondern den Wert der Vorlage.
"""

from django.test import SimpleTestCase

from core.daten.kleidungsregler import Kleidungsregler
from ._attrappen import Vorlagenattrappe


class KleidungsreglerTest(SimpleTestCase):
    """Welcher Wert gilt: der aus der Anfrage oder der aus der Vorlage?"""

    def test_anfrage_schlaegt_vorlage(self):
        regler = Kleidungsregler.aus_parametern(
            {'offset': '0.02', 'stiffness': '0.9'}, Vorlagenattrappe())
        self.assertAlmostEqual(regler.abstand, 0.02)
        self.assertAlmostEqual(regler.steifigkeit, 0.9)

    def test_ohne_angabe_gilt_die_vorlage(self):
        regler = Kleidungsregler.aus_parametern({}, Vorlagenattrappe())
        self.assertAlmostEqual(regler.abstand, 0.01)
        self.assertAlmostEqual(regler.steifigkeit, 0.4)

    def test_unbrauchbarer_wert_faellt_auf_die_vorgabe_zurueck(self):
        """„unbrauchbar → Vorgabe" ist die Vorschrift dieser Klasse.

        Ein Regler kommt aus der Abfragezeichenkette; `offset=viel` darf keine
        Fehlerseite ergeben, sondern die Vorlage.
        """
        for kaputt in ('viel', '', None, 'NaN?'):
            with self.subTest(wert=kaputt):
                regler = Kleidungsregler.aus_parametern(
                    {'offset': kaputt}, Vorlagenattrappe())
                self.assertAlmostEqual(regler.abstand, 0.01)

    def test_farbe_kanalweise_ueberschreibbar(self):
        regler = Kleidungsregler.aus_parametern({'color_g': '0.75'},
                                                Vorlagenattrappe())
        self.assertAlmostEqual(regler.farbe[0], 0.1)
        self.assertAlmostEqual(regler.farbe[1], 0.75)
        self.assertAlmostEqual(regler.farbe[2], 0.3)

    def test_um_huelle_nur_bei_rig_hull(self):
        self.assertTrue(Kleidungsregler.aus_parametern(
            {'fit_mode': 'rig_hull'}, Vorlagenattrappe()).um_huelle)
        self.assertFalse(Kleidungsregler.aus_parametern(
            {'fit_mode': 'body'}, Vorlagenattrappe()).um_huelle)
        self.assertFalse(Kleidungsregler.aus_parametern(
            {}, Vorlagenattrappe()).um_huelle)
