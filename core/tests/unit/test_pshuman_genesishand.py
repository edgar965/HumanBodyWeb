"""Genesishand: Fingerspitze, Beugung und Strafe gegen Überstreckung mit Kunstpunkten, ohne Karte und ohne Figur."""
import math
import sys
import unittest
from pathlib import Path

import torch
from django.conf import settings

sys.path.insert(0, str(Path(settings.TOOLS_ROOT) / 'pshuman_port14'))
from genesishand import Genesishand  # noqa: E402


def flache_hand():
    """21 Punkte: Handgelenk im Ursprung, vier Finger längs y, Zeigefinger bei x +3, kleiner Finger bei x −3, Glieder je 1 lang."""
    q = torch.zeros(21, 3)
    for i, ansatz in enumerate(Genesishand.ANSAETZE):
        for glied in range(4):
            q[ansatz + glied] = torch.tensor([3.0 - 2.0 * i, 1.0 + glied, 0.0])
    return q


def gebeugt(grad):
    """Flache Hand, der Zeigefinger ab dem Mittelglied um `grad` zu +z geknickt."""
    q = flache_hand()
    w = math.radians(grad)
    richtung = torch.tensor([0.0, math.cos(w), math.sin(w)])
    q[7] = q[6] + richtung
    q[8] = q[7] + richtung
    return q


class SpitzeTest(unittest.TestCase):
    def test_nimmt_nur_punkte_des_endglieds(self):
        """Punkt 2 liegt weiter aussen, gehört aber dem Nachbarfinger: Ohne die Auswahl blieb der Zeigefinger ohne Ziel und rollte sich ein (Edgar_1, 07.11.2026)."""
        p = torch.tensor([[0.0, 0.0, 1.0], [0.0, 0.0, 1.4], [0.0, 0.0, 3.0]])
        nummer = Genesishand._spitze(p, torch.zeros(3), torch.tensor([0.0, 0.0, 1.0]), torch.tensor([0, 1]))
        self.assertEqual(nummer, 1)

    def test_nennt_die_nummer_der_figur_nicht_die_stelle_in_der_auswahl(self):
        p = torch.tensor([[9.0, 9.0, 9.0], [0.0, 0.0, 1.0], [0.0, 0.0, 2.0]])
        nummer = Genesishand._spitze(p, torch.zeros(3), torch.tensor([0.0, 0.0, 1.0]), torch.tensor([1, 2]))
        self.assertEqual(nummer, 2)


class BeugungTest(unittest.TestCase):
    def setUp(self):
        self.hand = Genesishand.__new__(Genesishand)
        self.hand.g = 'cpu'
        self.hand.seiten = ['rechts']

    def test_flache_hand_ist_null(self):
        self.assertAlmostEqual(self.hand._winkel(flache_hand(), 'rechts').abs().max().item(), 0.0, places=5)

    def test_vorzeichen_folgt_der_seite(self):
        rechts = math.degrees(self.hand._winkel(gebeugt(30.0), 'rechts')[0, 1].item())
        links = math.degrees(self.hand._winkel(gebeugt(30.0), 'links')[0, 1].item())
        self.assertAlmostEqual(rechts, 30.0, places=3)
        self.assertAlmostEqual(links, -30.0, places=3)

    def test_nur_das_geknickte_gelenk_zaehlt(self):
        winkel = self.hand._winkel(gebeugt(30.0), 'rechts')
        winkel[0, 1] = 0.0
        self.assertAlmostEqual(winkel.abs().max().item(), 0.0, places=5)

    def test_strafe_nur_bei_ueberstreckung(self):
        self.assertAlmostEqual(self.hand._streck({'rechts': gebeugt(30.0)}).item(), 0.0, places=6)
        erwartet = math.radians(30.0) ** 2 / 12
        self.assertAlmostEqual(self.hand._streck({'rechts': gebeugt(-30.0)}).item(), erwartet, places=5)


if __name__ == '__main__':
    unittest.main()
