# -*- coding: utf-8 -*-
"""Tests für `KoerperKI_alle.koerpernetz.Koerpernetz` (24.10.2026, Besitzer 2d-3d-AI) an einer echten gebauten Figur (`unit/_gebautefigur.py`) — im LongRunner (Genesis laden ~3 s).

WARUM: Das Einpassen in die Fotos häutet den Käfig mit dieser Klasse. Hautgewichte und Gelenkzentren kommen aus der gebauten Figur, die Ruhelage aus der Formung der Regler — passen beide
nicht zusammen, rechnet alles stumm mit einer anderen Figur (zweiter Einpass-Lauf 24.10.2026 15:02: Figur noch mit den Reglern aus Runde 1, Start mit anderen Reglern). Die Häutung muss in Ruhe
die Ruhelage geben, eine starre Bewegung starr übertragen und eine Beugung nur die Glieder dahinter bewegen.
"""
import math
import unittest

import torch

from ..unit._gebautefigur import Gebautefigur


class DasKoerpernetz(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not Gebautefigur.da():
            raise unittest.SkipTest('keine gebaute Figur unter %s' % Gebautefigur.QUELLE)
        from KoerperKI_alle.kinematik import Kinematik
        from KoerperKI_alle.koerpernetz import Koerpernetz
        cls.ordner, cls.regler = Gebautefigur.kopieren()
        cls.n = Koerpernetz(cls.ordner, cls.regler, geraet='cpu')
        cls.kin = Kinematik(cls.n.kin)

    @classmethod
    def tearDownClass(cls):
        Gebautefigur.weg(cls.ordner)

    def ruhehaltung(self):
        j = len(self.n.namen)
        return self.kin.vorwaerts(torch.zeros((1, j, 3)), torch.eye(3)[None], self.n.zentren[:1])

    def test_anzeige_passt_zur_formung_ihrer_regler(self):
        self.assertLess(self.n.abweichung_mm, 0.5)

    def test_ruhehaltung_haeutet_auf_die_ruhelage(self):
        x = self.n.haeuten(self.n.zentren, torch.eye(3).expand(len(self.n.namen), 3, 3))
        self.assertLess(float((x - self.n.ruhe).abs().max()), 1e-6)

    def test_kinematik_ohne_winkel_ist_die_ruhe(self):
        p, d, _enden = self.ruhehaltung()
        self.assertLess(float((p[0] - self.n.zentren).abs().max()), 1e-5)
        self.assertLess(float((self.n.haeuten(p[0], d[0]) - self.n.ruhe).abs().max()), 1e-5)

    def test_starre_bewegung_bleibt_starr(self):
        r = torch.tensor([[math.cos(0.7), 0, math.sin(0.7)], [0, 1, 0], [-math.sin(0.7), 0, math.cos(0.7)]]) @ torch.tensor(
            [[1, 0, 0], [0, math.cos(0.2), -math.sin(0.2)], [0, math.sin(0.2), math.cos(0.2)]])
        t = torch.tensor([0.3, -0.1, 2.0])
        p = self.n.zentren @ r.T + t
        x = self.n.haeuten(p, r.expand(len(self.n.namen), 3, 3))
        self.assertLess(float((x - (self.n.ruhe @ r.T + t)).abs().max()), 1e-5)

    def test_beugung_bewegt_nur_die_glieder_dahinter(self):
        j = len(self.n.namen)
        unterarm = self.n.index('l_forearm')
        hinten = {unterarm}
        for b, e in enumerate(self.kin.eltern):
            if e in hinten:
                hinten.add(b)
        winkel = torch.zeros((1, j, 3))
        winkel[0, unterarm] = torch.tensor([0.0, 1.0, 0.5])
        p, d, _e = self.kin.vorwaerts(winkel, torch.eye(3)[None], self.n.zentren[:1])
        x = self.n.haeuten(p[0], d[0])
        weg = (x - self.n.ruhe).norm(dim=1)
        betroffen = torch.zeros(len(self.n.ruhe), dtype=torch.bool)
        for b in hinten:
            betroffen |= ((self.n.knochen == b) & (self.n.gewicht > 0)).any(1)
        self.assertLess(float(weg[~betroffen].max()), 1e-5)
        self.assertGreater(float((p[0, self.n.index('l_hand')] - self.n.zentren[self.n.index('l_hand')]).norm()), 0.1)
        self.assertGreater(float(weg[betroffen].max()), 0.1)

    def test_gewichte_je_punkt_summe_eins(self):
        s = self.n.gewicht.sum(1)
        self.assertEqual(int((s <= 1e-9).sum()), 0)
        self.assertLess(float((s - 1).abs().max()), 0.01)          # Gewichte als Byte gespeichert (/255)

    def test_dreiecke_geschlossen_nach_aussen(self):
        x, d = self.n.ruhe.double(), self.n.dreiecke
        self.assertGreaterEqual(int(d.min()), 0)
        self.assertLess(int(d.max()), len(x))
        volumen = float((x[d[:, 0]] * torch.cross(x[d[:, 1]], x[d[:, 2]], dim=1)).sum() / 6)
        self.assertGreater(volumen, 0.01)
        oben = int(self.n.ruhe[:, 1].argmax())
        self.assertGreater(float(self.n.normalen(self.n.ruhe)[oben, 1]), 0.5)

    def test_fuesse_auf_dem_boden(self):
        self.assertLess(abs(float(self.n.ruhe[:, 1].min())), 0.005)
