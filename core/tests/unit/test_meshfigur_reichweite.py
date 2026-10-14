# -*- coding: utf-8 -*-
"""Mesh to 3D, 12.10.2026: Reichweite des Stoffzugs (`kleidung = nah`) — der Rechenfall mit torch und pytorch3d (python10): `python10 -m unittest core.tests.unit.test_meshfigur_reichweite`.

Festgelegt wird nach der GRUNDFIGUR, nicht nach dem laufenden Stand: Der erste Versuch (Reichweite 7 cm gegen die aktuelle Figur) ließ die Zauberer-Figur trotzdem auf Oberschenkel 96,1 cm wachsen (`weich`
103,5, ohne Zug 51,4) — ein Stück Robe nahe am Oberschenkel zog den Regler, der Oberschenkel wuchs, mehr Robe kam in Reichweite. Kunstdaten: zwei Käfigpunkte, Stoffproben 5 cm und 12 cm davor.
Sabotage-Gegenprobe: in `meshto3d/meshfigur_abstandstoff.py` die Zeile `passt = passt & self.kleid_nah` streichen → `test_der_zug_waechst_nicht_mit_der_figur_mit` wird rot. Ohne torch/pytorch3d (python14) übersprungen.
"""

import importlib.util
import unittest

from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

HAT_TORCH = importlib.util.find_spec('torch') is not None and importlib.util.find_spec('pytorch3d') is not None


@unittest.skipUnless(HAT_TORCH, 'braucht torch und pytorch3d (python10)')
class ReichweiteTest(unittest.TestCase):
    """Zwei Käfigpunkte (z = 0), davor zwei Stoffproben bei z = 0,05 und z = 0,12."""

    def _abstand(self, kleidung):
        import torch

        from meshfigur_abstand import Meshfigurabstand

        a = Meshfigurabstand.__new__(Meshfigurabstand)
        a.kleidung, a.kleid_reichweite, a.kleid_abstand = kleidung, 0.07, 0.008
        a.kleid_zieht = torch.ones(2, dtype=torch.bool)
        a.kleid_nah = a._nah_haut = None
        a.haut = torch.zeros(2, dtype=torch.bool)
        proben = torch.tensor([[0.0, 0.0, 0.05], [0.0, 0.0, 0.12]])
        normalen = torch.tensor([[0.0, 0.0, 1.0]] * 2)
        a._haut_stand = a.haut                                    # die Haut-/Stoffteilung, wie `_haut_teile` sie gemerkt hätte: beide Proben sind Stoff
        a._haut_teile_gemerkt = (proben[:0], normalen[:0], proben, normalen, True)
        return a

    def _zug(self, a, v):
        import torch

        vn = torch.tensor([[0.0, 0.0, 1.0]] * 2)
        # jede Probe zieht ihren eigenen Käfigpunkt: Probe 0 → Punkt 0, Probe 1 → Punkt 1
        return float(a._stoffzug(v, vn, torch.tensor([0, 1]), 0.05, None))

    def _zwei_punkte(self, z0, z1):
        import torch

        return torch.tensor([[0.0, 0.0, z0], [0.0, 0.0, z1]])

    def test_festlegen_trennt_anliegenden_und_lockeren_stoff(self):
        a = self._abstand('nah')
        # Grundfigur: beide Käfigpunkte bei z = 0 → Probe 0 ist 5 cm, Probe 1 12 cm entfernt (Reichweite 7 cm)
        befund = a.reichweite_festlegen(self._zwei_punkte(0.0, 0.0))
        self.assertEqual(a.kleid_nah.tolist(), [True, False])
        self.assertEqual((befund['proben'], befund['nah'], befund['reichweite_cm']), (2, 1, 7.0))

    def test_der_zug_waechst_nicht_mit_der_figur_mit(self):
        """Die Figur wächst nach dem Festlegen an die weit entfernte Probe heran: bei `nah` zieht sie nicht, bei `weich` schon."""
        nah, weich = self._abstand('nah'), self._abstand('weich')
        nah.reichweite_festlegen(self._zwei_punkte(0.0, 0.0))
        gewachsen = self._zwei_punkte(0.0, 0.04)              # Käfigpunkt 1 steht jetzt 8 cm vor Probe 1 (z = 0,12): vorher 12 cm
        nur_probe_0 = self._zug(nah, gewachsen)
        alle = self._zug(weich, gewachsen)
        self.assertGreater(alle, nur_probe_0)
        # Mit der festgelegten Maske zählt allein Probe 0: derselbe Wert wie mit nur einem ziehenden Punkt.
        ein_punkt = self._abstand('weich')
        ein_punkt.kleid_zieht = ein_punkt.kleid_zieht.clone()
        ein_punkt.kleid_zieht[1] = False
        self.assertAlmostEqual(nur_probe_0, self._zug(ein_punkt, gewachsen), places=6)

    def test_grundruhe_rechnet_die_regler_auf_die_grundwerte_zurueck(self):
        """`Meshfigurmodell.grundruhe`: die Grundfigur = der Stand dieser Runde, linear über die Ableitung auf `x_grund` zurückgerechnet (Punkte und Gelenke)."""
        from types import SimpleNamespace

        import torch

        from meshfigur_modell import Meshfigurmodell

        jp = torch.zeros(2, 3, 3)
        jp[0, :, 0] = 1.0                                        # Regler 0 schiebt jeden Punkt um 1 in x
        jg = torch.zeros(2, 1, 3)
        jg[1, 0, 1] = 2.0                                        # Regler 1 hebt das Gelenk um 2 in y
        m = SimpleNamespace(p0=torch.zeros(3, 3), c0=torch.zeros(1, 3), jp=jp, jg=jg, x_grund=torch.tensor([0.0, 0.0]), x_jetzt=torch.tensor([0.5, 1.0]))
        p, c = Meshfigurmodell.grundruhe(m)
        self.assertTrue(torch.allclose(p[:, 0], torch.full((3,), -0.5)))
        self.assertAlmostEqual(float(c[0, 1]), -2.0)
        m.x_jetzt = m.x_grund.clone()                            # Runde 1: Stand = Grund → nichts zurückzurechnen
        p, c = Meshfigurmodell.grundruhe(m)
        self.assertTrue(torch.equal(p, m.p0) and torch.equal(c, m.c0))

    def test_ohne_festlegung_zieht_nah_wie_weich(self):
        a, b = self._abstand('nah'), self._abstand('weich')
        v = self._zwei_punkte(0.0, 0.04)
        self.assertAlmostEqual(self._zug(a, v), self._zug(b, v), places=6)


if __name__ == '__main__':
    unittest.main()
