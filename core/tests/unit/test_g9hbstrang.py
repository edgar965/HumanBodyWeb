# -*- coding: utf-8 -*-
u"""Stranghaar auf einer HumanBody-Figur (`core/dienste/g9hbstrang.py`, 30.09.2026).

Bis dahin fiel Stranghaar auf HumanBody ganz weg — in der Mischung von „Haar – Generisch" taten
drei der achtzehn Sortenregler dort nichts. Die Strähnen haben keine Unterteilung, jeder Punkt
wäre übertragen worden (Viola: 477.720); deshalb eine Stichprobe. Geprüft mit Kunstdaten: Die
Stichprobe deckt die ganze Punktfolge, das Verschiebungsfeld kommt auf allen Punkten an, und die
Haut eines Punkts ist die seines nächsten Stichprobenpunkts.
"""
from unittest import mock

import numpy as np
from django.test import SimpleTestCase

from core.dienste.g9hbstrang import G9hbstrang


class Verschiebend:
    u"""Attrappe eines `G9aufhumanbody`: `uebertragen` = eine bekannte Verschiebung."""

    def __init__(self, feld):
        self.feld = feld
        self.gefragt = 0

    def uebertragen(self, punkte_g9, bindung=None):
        self.gefragt = len(punkte_g9)
        return punkte_g9 + self.feld(punkte_g9)

    def figur(self):
        return {'name': 'attrappe'}


def straehnen(anzahl=40, je=25):
    u"""`anzahl` senkrechte Strähnen mit je `je` Punkten, hintereinander abgelegt wie bei Daz."""
    x = np.repeat(np.linspace(-0.1, 0.1, anzahl), je)
    y = np.tile(np.linspace(1.7, 1.4, je), anzahl)
    return np.column_stack([x, y, np.zeros_like(x)])


class Signatur(SimpleTestCase):
    databases = set()

    def test_0_die_attrappe_hat_die_signatur_des_traegers(self):
        import inspect

        from core.dienste.g9aufhumanbody import G9aufhumanbody

        for name in ('uebertragen', 'figur'):
            echt = set(inspect.signature(getattr(G9aufhumanbody, name)).parameters)
            attrappe = set(inspect.signature(getattr(Verschiebend, name)).parameters)
            self.assertEqual(echt, attrappe, name)


class Stichprobe(SimpleTestCase):
    databases = set()

    def test_1_klein_bleibt_ganz(self):
        np.testing.assert_array_equal(G9hbstrang.stichprobe(10), np.arange(10))

    def test_2_gross_ist_gleichmaessig_verteilt(self):
        with mock.patch.object(G9hbstrang, 'STICHPROBE', 100):
            wahl = G9hbstrang.stichprobe(1000)
        self.assertEqual(len(wahl), 100)
        self.assertEqual(int(wahl[0]), 0)
        self.assertEqual(int(wahl[-1]), 999)
        self.assertLess(int(np.diff(wahl).max()), 12)          # keine Lücke über eine Strähne


class Uebertragung(SimpleTestCase):
    databases = set()

    def test_3_verschiebung_kommt_auf_allen_punkten_an(self):
        punkte = straehnen()
        traeger = Verschiebend(lambda p: np.tile([0.02, -0.01, 0.03], (len(p), 1)))
        with mock.patch.object(G9hbstrang, 'STICHPROBE', 120):
            aus = G9hbstrang.uebertragen(traeger, punkte)
        self.assertEqual(traeger.gefragt, 120)                   # nur die Stichprobe voll
        np.testing.assert_allclose(aus, punkte + [0.02, -0.01, 0.03], atol=1e-9)

    def test_4_glattes_feld_wird_glatt_verteilt(self):
        punkte = straehnen()
        traeger = Verschiebend(lambda p: np.column_stack([np.zeros(len(p)), 0.05 * p[:, 0],
                                                          np.zeros(len(p))]))
        with mock.patch.object(G9hbstrang, 'STICHPROBE', 200):
            aus = G9hbstrang.uebertragen(traeger, punkte)
        soll = punkte + traeger.feld(punkte)
        # Das Feld ändert sich über die 20 cm Breite um 10 mm; die vier gemittelten Probenpunkte
        # liegen bis drei Strähnen (15 mm) daneben. Erster Lauf: 1,13 mm größter Fehler.
        self.assertLess(float(np.abs(aus - soll).max()), 2e-3)

    def test_5_kleine_netze_gehen_ganz_durch(self):
        punkte = straehnen(4, 5)
        traeger = Verschiebend(lambda p: np.tile([0.0, 0.1, 0.0], (len(p), 1)))
        aus = G9hbstrang.uebertragen(traeger, punkte)
        self.assertEqual(traeger.gefragt, len(punkte))
        np.testing.assert_allclose(aus, punkte + [0.0, 0.1, 0.0])


class Haut(SimpleTestCase):
    databases = set()

    def test_6_jeder_punkt_traegt_die_haut_seines_naechsten_stichprobenpunkts(self):
        # Ein Hauch Rauschen: Im regelmäßigen Gitter gäbe es gleich weite Nachbarn, und
        # KD-Baum und `argmin` dürften verschieden wählen.
        punkte = straehnen() + np.random.default_rng(7).normal(0.0, 1e-5, (1000, 3))

        class Teilhaut:
            def haut(self, p, teil):
                index = np.zeros((len(p), 4), dtype=np.int64)
                index[:, 0] = np.arange(len(p))                  # die Nummer des Probenpunkts
                gewicht = np.tile([1.0, 0.0, 0.0, 0.0], (len(p), 1))
                return {'knochen': ['DEF-spine.006'], 'index': index, 'gewicht': gewicht}

        folger = mock.Mock(haut=None)                            # ohne Daz-Bindung: ganze Figur
        with mock.patch.object(G9hbstrang, 'STICHPROBE', 400), \
                mock.patch('core.dienste.g9hbstrang.G9hbteilhaut.fuer', return_value=Teilhaut()):
            wahl = G9hbstrang.stichprobe(len(punkte))
            haut = G9hbstrang.haut(Verschiebend(lambda p: 0 * p), folger, punkte)
        self.assertEqual(haut['index'].shape, (len(punkte), 4))
        abstand = np.linalg.norm(punkte[:, None, :] - punkte[wahl][None, :, :], axis=2)
        np.testing.assert_array_equal(haut['index'][:, 0], abstand.argmin(axis=1))
        np.testing.assert_allclose(haut['gewicht'].sum(axis=1), 1.0)
