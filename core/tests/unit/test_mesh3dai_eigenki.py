# -*- coding: utf-8 -*-
"""Mesh3D-AI, Eigenregler-KI Fassung 1 (26.10.2026, `Eigenkinetz`, `Eigenkidaten`, `Eigenkitraining`) an Kunstdaten, ohne Karte und ohne Figur:

    1  Löser: aus Grundformen B und einem Weg B·e + Verschiebung kommt e zurück; die Verschiebung nehmen die Nebengrößen, nicht die Anfasser
    2  Gewicht: ein Punkt mit Gewicht 0 zählt nicht (ein falscher Weg dort ändert e nicht)
    3  Start des Netzes = geometrische Grundlinie (letzte Schicht 0: gleiches e wie der Löser mit Gewicht 1 auf dem rohen Weg)
    4  Vermehrung: ein Punkt des Eingangs folgt seinem nächsten Körperpunkt, in dessen Haltung gedreht
    5  Prüfzeile: Fehler in mm (1 Einheit = 10 mm), rot ab `ROT_MM`, je Gruppe gezählt
Sabotage (von Hand): in `Eigenkinetz.loesen` die Nebengrößen weglassen (`torch.cat([basis, neben])` → `basis`) → Fall 1 rot; in `loesen` `* wr` streichen → Fall 2 rot;
in `Eigenkinetz.__init__` die Null der letzten Schicht streichen → Fall 3 rot; in `Eigenkidaten.verschoben` `self.R @` streichen → Fall 4 rot; in `Eigenkitraining._zeile` `>` → `>=` → Fall 5 rot.
"""
import sys
import unittest
from types import SimpleNamespace

from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT / 'mesh3dai'))


def _torch():
    try:
        import torch  # noqa: F401
        return True
    except ImportError:
        return False


@unittest.skipUnless(_torch(), 'kein torch')
class EigenkiTest(unittest.TestCase):
    def setUp(self):
        import torch
        from mesh3dai_eigenki_netz import Eigenkinetz
        self.t, self.N = torch, Eigenkinetz
        torch.manual_seed(0)
        self.ruhe = torch.rand(40, 3)
        self.B = torch.zeros(2, 40, 3)
        self.B[0, :10, 0] = 0.01                        # Spalte 0: Punkte 0–9 um 1 cm in x je Einheit
        self.B[1, 20:30, 1] = 0.01                      # Spalte 1: Punkte 20–29 um 1 cm in y je Einheit
        self.neben = Eigenkinetz.neben(self.ruhe)

    def test_1_loeser_mit_nebengroessen(self):
        t = self.t
        e = t.tensor([2.0, -1.0])
        weg = t.einsum('k,kpc->pc', e, self.B) + t.tensor([0.0, 0.0, 0.03])
        r, n = self.N.loesen(self.B, self.neben, weg, lam=1e-8)
        self.assertLess(float((r - e).abs().max()), 1e-3)
        self.assertAlmostEqual(float(n[2]), 3.0, places=2)                 # 3 cm in z über die Nebengröße (1 cm je Einheit)

    def test_2_gewicht_null_zaehlt_nicht(self):
        t = self.t
        e = t.tensor([1.0, 0.0])
        weg = t.einsum('k,kpc->pc', e, self.B)
        falsch = weg.clone()
        falsch[0, 0] += 0.5
        w = t.ones(40)
        w[0] = 0.0
        r, _n = self.N.loesen(self.B, self.neben, falsch, w, lam=1e-8)
        self.assertLess(float((r - e).abs().max()), 1e-3)

    def test_3_start_ist_die_grundlinie(self):
        t = self.t
        m = t.cat([t.randn(40, 3) * 0.2, t.rand(40, 6)], 1)
        netz = self.N(m.shape[1])
        with t.no_grad():
            e, w = netz(m, self.B, self.neben)
        geo, _n = self.N.loesen(self.B, self.neben, m[:, :3] * self.N.SKALA_M)
        self.assertTrue(bool((w == 0.5).all()))
        self.assertLess(float((e - geo).abs().max()), 1e-4)

    def test_4_eingang_folgt_dem_koerper(self):
        t = self.t
        from mesh3dai_eigenki_daten import Eigenkidaten
        d = Eigenkidaten.__new__(Eigenkidaten)
        dreh = t.tensor([[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])   # 90° um z: x der Ruhe → y der Haltung
        d.R = dreh.expand(40, 3, 3)
        d.alle = t.zeros(2, 3)
        d.idx_alle = t.tensor([5, 25])
        d.haut, d.idx_haut = None, None
        alle, haut = d.verschoben(t.tensor([1.0, 0.0]), SimpleNamespace(basis=self.B))
        self.assertIsNone(haut)
        self.assertEqual([round(v, 6) for v in alle[0].tolist()], [0.0, 0.01, 0.0])
        self.assertEqual(alle[1].abs().sum().item(), 0.0)

    def test_5_pruefzeile(self):
        t = self.t
        from mesh3dai_eigenki_training import Eigenkitraining
        tr = Eigenkitraining.__new__(Eigenkitraining)
        tr.B, tr.mm_je_einheit, tr.gruppen = self.B, 10.0, ['Beine', 'Arme']
        tr.b = None
        d = SimpleNamespace(e_ziel=t.tensor([1.0, 0.0]), form_mm=lambda _b, _e: t.tensor(0.0))
        z = tr._zeile(d, t.tensor([1.0, Eigenkitraining.ROT_MM / 10.0]))     # genau an der Schwelle: nicht rot
        self.assertEqual(z['rot'], 0)
        z = tr._zeile(d, t.tensor([3.5, 0.0]))                                 # 25 mm daneben
        self.assertEqual((z['rot'], z['je_gruppe_rot']), (1, {'Beine': [1, 1], 'Arme': [0, 1]}))
        self.assertAlmostEqual(z['eigen_mm'], 25.0 * 10 / 40, places=3)        # 10 von 40 Punkten 25 mm daneben


if __name__ == '__main__':
    unittest.main()
