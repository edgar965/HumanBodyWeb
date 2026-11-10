"""Starre Teile: `Kostuemrueckhaeutung.starrer_knochen`, `_griff` und `Kostuemstarrinseln` (roboter, 07.11.2026). Ohne Datenbank, ohne Karte."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / 'meshgenesis'))
from meshgenesis_kostuem_rueckhaeutung import Kostuemrueckhaeutung  # noqa: E402
from meshgenesis_kostuem_starrinseln import Kostuemstarrinseln  # noqa: E402


class StarrerKnochenTest(unittest.TestCase):
    databases = []

    def rueck(self):
        r = object.__new__(Kostuemrueckhaeutung)
        r.k = SimpleNamespace(t=torch)
        # Hautpunkte: 0 = Hand (Knochen 7), 1 = Kopf (Knochen 3), 2 = Hals (Knochen 2)
        r.kaefig = torch.tensor([[0.0, 0, 0], [0, 2.0, 0], [0, 1.8, 0]], dtype=torch.float64)
        r.kn_kaefig = torch.tensor([[7, 1, 0, 0], [3, 2, 0, 0], [2, 3, 0, 0]])
        r.gw_kaefig = torch.tensor([[200, 55, 0, 0], [255, 0, 0, 0], [200, 55, 0, 0]])
        r.griff = torch.arange(9)
        wahl = {None: [0, 1, 2], ('kopf',): [1]}

        def naechste(x, traeger, ohne=()):
            i = torch.tensor(wahl[traeger])
            return i[torch.cdist(x, r.kaefig[i]).argmin(1)]
        r._naechste = naechste
        return r

    def test_stab_neben_der_hand_haengt_an_ihrem_staerksten_knochen(self):
        x = torch.tensor([[0.09, 0, 0], [0.2, 0, 0], [0.4, 0, 0]], dtype=torch.float64)
        self.assertEqual(int(self.rueck().starrer_knochen(x, None)), 7)

    def test_hut_haengt_am_kopf_auch_wenn_der_hals_naeher_ist(self):
        x = torch.tensor([[0.0, 1.85, 0.05], [0.0, 1.9, 0.08], [0.1, 1.9, 0.1]], dtype=torch.float64)
        self.assertEqual(int(self.rueck().starrer_knochen(x, ('kopf', 'hals'))), 3)

    def test_ein_fingerknochen_wird_zur_hand(self):
        r = self.rueck()
        r.griff[7] = 4
        x = torch.tensor([[0.09, 0, 0]], dtype=torch.float64)
        self.assertEqual(int(r.starrer_knochen(x, None)), 4)


class GriffTest(unittest.TestCase):
    databases = []

    def test_finger_gehen_bis_zur_hand_nicht_weiter(self):
        kin = [{'name': 'l_forearm', 'gruppe': 'arm', 'eltern': -1}, {'name': 'l_hand', 'gruppe': 'hand', 'eltern': 0}, {'name': 'l_indexmetacarpal', 'gruppe': 'finger', 'eltern': 1},
               {'name': 'l_index1', 'gruppe': 'finger', 'eltern': 2}, {'name': 'l_index3', 'gruppe': 'finger', 'eltern': 3}, {'name': 'head', 'gruppe': 'kopf', 'eltern': -1}]
        self.assertEqual(Kostuemrueckhaeutung._griff(kin).tolist(), [0, 1, 1, 1, 1, 5])


class Karte:
    """Was `Kostuemstarrinseln` von `Kostuemgpu` braucht, auf dem Prozessor."""
    t = torch
    g = 'cpu'

    @staticmethod
    def feld(a, dtype=None):
        return torch.as_tensor(a, dtype=dtype)

    @staticmethod
    def verschweisst(punkte, dreiecke):
        return torch.as_tensor(dreiecke, dtype=torch.int64), None

    @staticmethod
    def komponenten(n, a, b):
        nr = torch.arange(n)
        for _ in range(n):
            for i, j in zip(a.tolist(), b.tolist(), strict=True):
                nr[i] = nr[j] = min(nr[i], nr[j])
        return nr

    @classmethod
    def flaecheninseln(cls, fs):
        n_f = len(fs)
        punkte, inv = torch.unique(fs.reshape(-1), return_inverse=True)
        nummer = cls.komponenten(n_f + len(punkte), torch.arange(n_f).repeat_interleave(3), n_f + inv)
        return torch.arange(n_f), torch.unique(nummer[:n_f], return_inverse=True)[1]

    @staticmethod
    def naechste(x, y):
        d = torch.cdist(x, torch.as_tensor(y, dtype=x.dtype))
        return d.min(1).values, d.argmin(1)


class StarrinselnTest(unittest.TestCase):
    databases = []

    #: Haut: ein Punkt im Ursprung
    KAEFIG = torch.zeros((1, 3), dtype=torch.float64)

    @staticmethod
    def dreieck(ursprung):
        return torch.tensor(ursprung, dtype=torch.float64) + torch.tensor([[0.0, 0, 0], [0.01, 0, 0], [0, 0.01, 0]], dtype=torch.float64)

    def test_nur_die_insel_fern_der_haut(self):
        nah, fern = self.dreieck([0.0, 0, 0]), self.dreieck([0.5, 0, 0])
        x = torch.cat([nah, fern])
        inseln = Kostuemstarrinseln.ferne(Karte, x, [[0, 1, 2], [3, 4, 5]], self.KAEFIG)
        self.assertEqual([i.tolist() for i in inseln], [[3, 4, 5]])

    def rechnen(self, *stuecke):
        rueck = SimpleNamespace(kaefig=self.KAEFIG, starrer_knochen=lambda x, traeger: torch.tensor(9 if traeger else int(1000 * x[:, 0].min())))
        s = object.__new__(Kostuemstarrinseln)
        s.rueck, s.k = rueck, Karte
        gehoben = {st['id']: (st['x'],) for st in stuecke}
        return s.rechnen(list(stuecke), gehoben, {st['id']: st['x'] for st in stuecke})

    def test_griff_und_spitze_haengen_am_selben_knochen(self):
        griff = {'id': 'griff', 'art': 'freie_form', 'x': self.dreieck([0.5, 0, 0]), 'dreiecke': [[0, 1, 2]]}
        spitze = {'id': 'oberteil', 'art': 'oberteil', 'x': torch.cat([self.dreieck([0.0, 0, 0]), self.dreieck([0.51, 0, 0])]), 'dreiecke': [[0, 1, 2], [3, 4, 5]]}
        aus = self.rechnen(griff, spitze)
        self.assertEqual(aus['oberteil'][0].tolist(), [False, False, False, True, True, True])
        self.assertEqual(int(aus['griff'][1][0]), int(aus['oberteil'][1][3]))

    def test_eine_weite_robe_ist_nicht_starr(self):
        """Fassung 2 (07.11.2026, Zauberer): Der Hauptteil eines Kleidungsstücks bleibt weich, auch wenn er fern der Haut liegt; ein Stück einer starren Art darf es ganz sein."""
        robe = {'id': 'robe', 'art': 'oberteil', 'x': torch.cat([self.dreieck([0.0, 0, 0]), self.dreieck([0.5, 0, 0]), self.dreieck([0.5, 0.02, 0])]),
                'dreiecke': [[0, 1, 2], [3, 4, 5], [5, 4, 7], [6, 7, 8]]}
        stab = {'id': 'stab', 'art': 'requisit', 'x': self.dreieck([0.9, 0, 0]), 'dreiecke': [[0, 1, 2]]}
        aus = self.rechnen(robe, stab)
        self.assertNotIn('robe', aus)
        self.assertTrue(bool(aus['stab'][0].all()))

    def test_getrennte_inseln_haben_jede_ihren_knochen(self):
        a = {'id': 'a', 'art': 'freie_form', 'x': self.dreieck([0.5, 0, 0]), 'dreiecke': [[0, 1, 2]]}
        b = {'id': 'b', 'art': 'requisit', 'x': self.dreieck([0.8, 0, 0]), 'dreiecke': [[0, 1, 2]]}
        aus = self.rechnen(a, b)
        self.assertNotEqual(int(aus['a'][1][0]), int(aus['b'][1][0]))

    def test_haar_bleibt_weich(self):
        self.assertEqual(self.rechnen({'id': 'h', 'art': 'haar', 'x': self.dreieck([0.5, 0, 0]), 'dreiecke': [[0, 1, 2]]}), {})

    def test_ein_hut_nimmt_seinen_traeger(self):
        hut = {'id': 'hut', 'art': 'kopfbedeckung', 'x': self.dreieck([0.5, 0, 0]), 'dreiecke': [[0, 1, 2]]}
        self.assertEqual(int(self.rechnen(hut)['hut'][1][0]), 9)


if __name__ == '__main__':
    unittest.main()
