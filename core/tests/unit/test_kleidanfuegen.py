"""Tests für `Kleidanfuegen` (neue Punkte und Flächen an ein Kleidstück der Stufe „Kleidungsregeln“),
21.11.2026. Kleine Tensoren, keine Karte nötig."""
import unittest
from types import SimpleNamespace

import torch

from core.dienste.meshgenesissuchpfad import Meshgenesissuchpfad

PUNKTE = ('ruhe', 'knochen', 'gewicht', 'uv', 'normalen', 'punktfarbe')
FLAECHEN = ('dreiecke', 'etikett', 'material')


def _t(werte, typ=None):
    """Tensor aus Werten."""
    return torch.tensor(werte, dtype=typ, device='cpu')  # cpu gewollt: Test mit drei Punkten


def _stueck():
    """Ein Dreieck mit den Feldern der Wege z, e, f (Typen wie in einer netz.pt der Bibliothek)."""
    felder = {
        'ruhe': _t([[0., 0., 0.], [1., 0., 0.], [0., 1., 0.]]),
        'knochen': _t([[1, 2], [3, 4], [5, 6]], torch.uint8),
        'gewicht': _t([[255, 0], [200, 55], [100, 155]], torch.uint8),
        'uv': _t([[0., 0.], [1., 0.], [0., 1.]]),
        'dreiecke': _t([[0, 1, 2]], torch.long),
        'etikett': _t([5], torch.uint8),
        'material': _t([3], torch.int16),
    }
    return SimpleNamespace(felder=felder, PUNKTE=PUNKTE, FLAECHEN=FLAECHEN)


class KleidanfuegenTest(unittest.TestCase):
    def setUp(self):
        Meshgenesissuchpfad.einhaengen()
        from meshgenesis_kleidanfuegen import Kleidanfuegen
        self.anfuegen = Kleidanfuegen.anfuegen

    def test_neue_punkte_erben_vom_quellpunkt_neue_flaechen_von_der_quellflaeche(self):
        st = _stueck()
        neu = _t([[2., 0., 0.], [2., 1., 0.]])
        a = self.anfuegen(st, neu, _t([[1, 3, 4]], torch.long), _t([1, 2]), _t([0]))
        f = st.felder
        self.assertEqual({'punkte': 2, 'flaechen': 1}, a)
        self.assertEqual((5, 3), tuple(f['ruhe'].shape))
        self.assertEqual([[3, 4], [5, 6]], f['knochen'][3:].tolist())
        self.assertEqual([[200, 55], [100, 155]], f['gewicht'][3:].tolist())
        self.assertEqual(torch.uint8, f['knochen'].dtype)
        self.assertEqual([[1., 0.], [0., 1.]], f['uv'][3:].tolist())
        self.assertEqual([[0, 1, 2], [1, 3, 4]], f['dreiecke'].tolist())
        self.assertEqual([5, 5], f['etikett'].tolist())
        self.assertEqual([3, 3], f['material'].tolist())

    def test_uv_neu_ersetzt_die_uv_des_quellpunkts(self):
        st = _stueck()
        self.anfuegen(st, _t([[2., 0., 0.]]), _t([[1, 3, 2]], torch.long), _t([1]), _t([0]),
                      uv_neu=_t([[0.5, 0.5]]))
        self.assertEqual([[0.5, 0.5]], st.felder['uv'][3:].tolist())

    def test_nummern_ausserhalb_werden_abgelehnt(self):
        st = _stueck()
        with self.assertRaises(ValueError):
            self.anfuegen(st, _t([[2., 0., 0.]]), _t([[1, 3, 9]], torch.long), _t([1]), _t([0]))
        with self.assertRaises(ValueError):
            self.anfuegen(st, _t([[2., 0., 0.]]), _t([[1, 3, 2]], torch.long), _t([3]), _t([0]))

    def test_normalen_der_neuen_punkte_aus_den_neuen_flaechen(self):
        st = _stueck()
        st.felder['normalen'] = torch.zeros((3, 3), device='cpu')  # cpu gewollt: Test mit drei Punkten
        self.anfuegen(st, _t([[1., 1., 0.]]), _t([[1, 3, 2]], torch.long), _t([1]), _t([0]))
        n = st.felder['normalen']
        self.assertEqual(4, len(n))
        self.assertAlmostEqual(1.0, float(n[3].norm()), places=5)
        self.assertEqual([0., 0., 1.], n[3].tolist())
        self.assertEqual(0.0, float(n[:3].abs().sum()))


if __name__ == '__main__':
    unittest.main()
