# -*- coding: utf-8 -*-
u"""`G9hautausgleich` an Kunstdaten (18.11.2026): Werte, Merkmal statt Fleck, Wirkung der vier Regler auf Texelwerte.

Keine Bibliothek, kein Bild: eine Analyse aus vier Texeln (zwei Spiegelpaare) mit gesetzten Bändern. Sabotage: `_beidseitig` ohne Richtungsfaktor →
`test_gegenlaeufig_ist_kein_merkmal` rot; `texelwerte` ohne `frei` → `test_schutz_haelt_gleichmaessigkeit_ab` rot.
"""
import torch
from django.test import SimpleTestCase
from Genesis9.hautausgleich import G9hautausgleich


class _Texel:
    def __init__(self, partner):
        self.partner = partner


def _analyse(x, f4, f8, f32, f128, partner, schutz=None, fleck=None, flecken=None):
    n = len(x)
    null = torch.zeros(n)
    return {'x': x, 'tief': [f4, f8, f32, f128], 'texel': _Texel(partner), 'mal': null, 'merkmal_fleck': null,
            'merkmal': null if schutz is None else schutz, 'fleck': null if fleck is None else fleck,
            'flecken': null if flecken is None else flecken}


class HautausgleichTest(SimpleTestCase):
    def test_werte_geklemmt_und_gerundet(self):
        w = G9hautausgleich.werte({'gleich': 0.43, 'symmetrie': 2, 'schatten': -1, 'retusche': 'x'})
        self.assertEqual(w, {'gleich': 0.45, 'symmetrie': 1.0, 'schatten': 0.0, 'retusche': 0.0, 'behalten': 1.0})

    def test_behalten_haelt_kleine_flecken(self):
        a = self._fleckpaar()
        a['flecken'] = torch.tensor([1.0, 0.0])
        ohne = G9hautausgleich.texelwerte(a, G9hautausgleich.werte({}))
        mit = G9hautausgleich.texelwerte(a, G9hautausgleich.werte({'gleich': 1.0}))                 # behalten = 1 (Vorgabe)
        self.assertTrue(torch.allclose(ohne, mit, atol=1e-6))
        frei = G9hautausgleich.texelwerte(a, G9hautausgleich.werte({'gleich': 1.0, 'behalten': 0.0}))
        self.assertTrue(torch.allclose(frei[0], frei[1], atol=1e-4))

    def test_gleichgerichtet_beidseitig_ist_merkmal(self):
        v = torch.tensor([[-0.5, -0.5, -0.5], [-0.5, -0.5, -0.5]])
        m = G9hautausgleich._beidseitig(v, torch.tensor([1, 0]))
        self.assertTrue(torch.allclose(m, torch.ones(2)))

    def test_gegenlaeufig_ist_kein_merkmal(self):
        v = torch.tensor([[-0.5, -0.5, -0.5], [0.5, 0.5, 0.5]])
        self.assertTrue(torch.allclose(G9hautausgleich._beidseitig(v, torch.tensor([1, 0])), torch.zeros(2)))

    def test_einseitig_ist_kein_merkmal(self):
        v = torch.tensor([[-0.5, -0.5, -0.5], [0.0, 0.0, 0.0]])
        self.assertTrue(torch.allclose(G9hautausgleich._beidseitig(v, torch.tensor([1, 0])), torch.zeros(2)))

    def _fleckpaar(self, schutz=None):
        # Texel 0: dunkler Fleck im Band 4 … 32 mm (log −0,3), Texel 1 (Spiegel): glatt
        x = torch.tensor([[-1.3, -1.3, -1.3], [-1.0, -1.0, -1.0]])
        f4 = x.clone()
        tief = torch.full_like(x, -1.0)
        return _analyse(x, f4, f4.clone(), tief, tief.clone(), torch.tensor([1, 0]), schutz=schutz)

    def test_gleichmaessigkeit_hebt_den_fleck_auf(self):
        a = self._fleckpaar()
        aus = G9hautausgleich.texelwerte(a, G9hautausgleich.werte({'gleich': 1.0}))
        self.assertTrue(torch.allclose(aus[0], aus[1], atol=1e-4))

    def test_schutz_haelt_gleichmaessigkeit_ab(self):
        a = self._fleckpaar(schutz=torch.tensor([1.0, 0.0]))
        ohne = G9hautausgleich.texelwerte(a, G9hautausgleich.werte({}))
        mit = G9hautausgleich.texelwerte(a, G9hautausgleich.werte({'gleich': 1.0}))
        self.assertTrue(torch.allclose(ohne, mit, atol=1e-6))

    def test_symmetrie_zieht_nur_die_staerkere_seite(self):
        a = self._fleckpaar()
        ohne = G9hautausgleich.texelwerte(a, G9hautausgleich.werte({}))
        mit = G9hautausgleich.texelwerte(a, G9hautausgleich.werte({'symmetrie': 1.0}))
        self.assertGreater(float(mit[0].mean()), float(ohne[0].mean()))      # der Fleck wird heller
        self.assertTrue(torch.allclose(mit[1], ohne[1], atol=1e-6))          # die glatte Seite bleibt

    def test_schatten_hebt_grau_aber_nicht_farbig(self):
        x = torch.tensor([[-1.3, -1.3, -1.3], [-1.0, -1.6, -1.0]])         # 0: grauer Abzug (Schatten), 1: Grün sinkt (Pigment)
        tief = torch.full_like(x, -1.0)
        a = _analyse(x, x.clone(), x.clone(), tief, tief.clone(), torch.tensor([-1, -1]))
        ohne = G9hautausgleich.texelwerte(a, G9hautausgleich.werte({}))
        mit = G9hautausgleich.texelwerte(a, G9hautausgleich.werte({'schatten': 1.0}))
        self.assertGreater(float(mit[0].mean()), float(ohne[0].mean()) + 0.02)
        self.assertLess(abs(float(mit[1].mean()) - float(ohne[1].mean())), 0.02)
