"""`Meshfigurregistrierungruhe._nachschub` (13.10.2026): die Untergrenze unter Stoff in mehreren Durchgängen.

Nach dem ersten Weg (Punkt auf `luft` unter die nächste Stofffläche) ist die nächste Probe mit passender Normale eine andere; ein Punkt, der über eine Kante wanderte, steht vor ihr noch heraus. Spiralballerina
(`idealschub.py`): erreichbare Punkte mehr als 5 mm vor dem Stoff 875 → 60 → 10 → 2 nach dem ersten, zweiten, dritten Durchgang. Die Attrappe des Abstands liefert Durchgang für Durchgang vorgegebene Werte
(Signatur gegen `Meshfigurabstand.figur_zu_netz` geprüft, `attrappen-signatur.md`).

Braucht torch (python10, `meshto3d`): in python14 übersprungen. NICHT gelaufen (Tests nur auf Ansage). Sabotagen: in `_nachschub` die Zeile `ragt = ragt | neu` entfernen → `test_wer_erst_im_zweiten_durchgang_herausragt_bekommt_eine_untergrenze` rot;
`schub = weg * einseitig[:, None]` durch `weg` ersetzen → `test_haut_und_punkte_ohne_stoff_bleiben` rot.
"""
import importlib.util
import inspect
import unittest

from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()


def _torch():
    return importlib.util.find_spec('torch') is not None


@unittest.skipUnless(_torch(), 'torch fehlt in diesem Interpreter (python10-Tests)')
class NachschubTest(unittest.TestCase):
    def _ruhe(self, durchgaenge, antworten):
        import torch
        from meshfigur_registrierungruhe import Meshfigurregistrierungruhe

        class Abstand:
            luft = 0.004
            rest_kandidaten = 16
            sn = torch.tensor([[0.0, 1.0, 0.0]] * 3)

            def __init__(self):
                self.aufrufe = 0

            def normalen(self, v):
                return torch.zeros_like(v)

            def figur_zu_netz(self, v, vn, grenze, kandidaten=None):
                r = torch.tensor(antworten[min(self.aufrufe, len(antworten) - 1)])
                self.aufrufe += 1
                return r, torch.tensor([True, True, False]), torch.tensor([True, True, True]), torch.zeros(3, dtype=torch.long)

        ruhe = Meshfigurregistrierungruhe.__new__(Meshfigurregistrierungruhe)
        ruhe.abstand = Abstand()
        ruhe.DURCHGAENGE = durchgaenge
        return ruhe

    def _lauf(self, ruhe):
        import torch

        v = torch.zeros(3, 3)
        weg = torch.tensor([[0.0, -0.024, 0.0], [0.0, 0.0, 0.0], [0.0, -0.005, 0.0]])   # Punkt 0: erster Weg, Punkt 1: ragte nicht, Punkt 2: Haut (beidseitig)
        ragt = torch.tensor([True, False, False])
        einseitig = torch.tensor([True, True, False])
        return ruhe._nachschub(v, weg, ragt, einseitig, 0.03)

    def test_ein_durchgang_ist_der_stand_bis_13_10_2026(self):
        ruhe = self._ruhe(1, [[0.01, -0.02, 0.5]])
        weg, ragt = self._lauf(ruhe)
        self.assertAlmostEqual(float(weg[0, 1]), -0.024)
        self.assertEqual(ragt.tolist(), [True, False, False])
        self.assertEqual(ruhe.abstand.aufrufe, 0)

    def test_der_zweite_durchgang_addiert_was_noch_fehlt(self):
        ruhe = self._ruhe(3, [[0.010, -0.02, 0.5], [-0.01, -0.02, 0.5]])
        weg, _ = self._lauf(ruhe)
        self.assertAlmostEqual(float(weg[0, 1]), -0.024 - 0.014, places=6)      # r + Luft = 10 mm + 4 mm kommen dazu
        self.assertEqual(ruhe.abstand.aufrufe, 2, 'der dritte Durchgang findet nichts mehr und beendet die Schleife')

    def test_wer_erst_im_zweiten_durchgang_herausragt_bekommt_eine_untergrenze(self):
        ruhe = self._ruhe(3, [[-0.02, 0.006, 0.5], [-0.02, -0.02, 0.5]])
        weg, ragt = self._lauf(ruhe)
        self.assertTrue(bool(ragt[1]))
        self.assertAlmostEqual(float(weg[1, 1]), -0.010, places=6)

    def test_haut_und_punkte_ohne_stoff_bleiben(self):
        ruhe = self._ruhe(3, [[-0.02, -0.02, 0.5], [-0.02, -0.02, 0.5]])
        weg, ragt = self._lauf(ruhe)
        self.assertAlmostEqual(float(weg[2, 1]), -0.005, msg='Haut (beidseitig): der Weg zum Netz bleibt')
        self.assertFalse(bool(ragt[2]))
        ruhe = self._ruhe(3, [[0.02, 0.02, 0.5], [0.02, 0.02, 0.5]])           # die Probe sagt, Punkt 2 rage — er ist aber Haut
        weg, _ = self._lauf(ruhe)
        self.assertAlmostEqual(float(weg[2, 1]), -0.005)

    def test_ohne_luft_gibt_es_keinen_nachschub(self):
        ruhe = self._ruhe(3, [[0.02, 0.02, 0.5]])
        ruhe.abstand.luft = 0.0
        weg, _ = self._lauf(ruhe)
        self.assertAlmostEqual(float(weg[0, 1]), -0.024)
        self.assertEqual(ruhe.abstand.aufrufe, 0)

    def test_die_attrappe_hat_die_signatur_des_abstands(self):
        from meshfigur_abstand import Meshfigurabstand

        echt = set(inspect.signature(Meshfigurabstand.figur_zu_netz).parameters) - {'self'}
        self.assertEqual(echt, {'v', 'vn', 'grenze', 'kandidaten'})
        self.assertEqual(self._ruhe(1, [[0.0, 0.0, 0.0]]).DURCHGAENGE, 1)


if __name__ == '__main__':
    unittest.main()
