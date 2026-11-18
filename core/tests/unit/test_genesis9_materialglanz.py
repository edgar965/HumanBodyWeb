"""Glanz, Rauheit, Klarlack, Bump und Höhe wie Iray (17.11.2026, Edgar: „Glanz und Rauheit je Material —
so wie im Original“, „Bump- und Höhenkarten … Nutze das!“) — an Kunst-Gruppen, ohne Bibliothek.

1. Iray Uber, Metallizität/Rauheit: F0 = 0,08 × `Glossy Reflectivity` × Farbe (linear), Gewicht, Rauheit 1:1,
   Karten aufgelöst.
2. Spiegel/Glanz-Modus: F0 = `Glossy Specular` (linear), Rauheit = 1 − Glanzheit; mit Glanzheitskarte
   `rauheitinvers`.
3. Kein Glanzlappen: Gewicht 0 (Iray spiegelt nicht), Metall behält die Glossy Roughness.
4. PBRSkin: Rauheit = Lappen 1 × ((1 − w₂) + w₂ × Mult), F0 = 0,08 × Reflectivity; Top Coat als Klarlack.
5. Ein Preset stellt `rauheitwert` — das bleibt; ohne Iray-Shader wird die Lappen-1-Karte `rauheit`,
   Rohkarten fallen weg.
6. Normalenstärke, Bump (nur mit Stärke), Höhe in Metern (Daz-Zentimeter, × Stärke).
7. `G9bumpnormalen.rechnen`: flache Höhe → (0, 0, 1); eine Rampe in u neigt nach −u wie `apply_bump`;
   über einer Normalenkarte addiert.
"""

import sys
import unittest

import torch
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))

from Genesis9.bumpnormalen import G9bumpnormalen  # noqa: E402
from Genesis9.materialglanz import G9materialglanz  # noqa: E402

R = G9materialglanz.ROH


def uber(**werte):
    return {R + 'shader': 'uber', **{R + k: v for k, v in werte.items()}}


class Glanzprobe(unittest.TestCase):
    def test_1_metallizitaet(self):
        b = uber(
            **{
                'Glossy Layered Weight': 0.5,
                'Glossy Reflectivity': 0.25,
                'Glossy Roughness': 0.3,
                'Glossy Color': [1, 1, 1],
            }
        )
        b.update({'karte:glanz': 'R/g.jpg', 'karte:glanzfarbe': 'R/f.jpg'})
        G9materialglanz.aufloesen(b)
        self.assertEqual(b['glanzgewicht'], 0.5)
        self.assertEqual(b['rauheitwert'], 0.3)
        self.assertAlmostEqual(b['glanzf0'][0], 0.02, places=5)
        self.assertEqual(
            (b['glanzkarte'], b['glanzfarbkarte'], b['glanzfarbkarte_srgb']), ('R/g.jpg', 'R/f.jpg', True)
        )
        self.assertFalse([k for k in b if k.startswith(('iray:', 'karte:'))])

    def test_2_spiegel_glanz(self):
        b = uber(
            **{
                'Base Mixing': 1,
                'Glossy Layered Weight': 1.0,
                'Glossiness': 0.8,
                'Glossy Specular': [0.2313726] * 3,
            }
        )
        G9materialglanz.aufloesen(b)
        self.assertAlmostEqual(b['rauheitwert'], 0.2, places=4)
        self.assertNotIn('rauheitinvers', b)
        self.assertAlmostEqual(b['glanzf0'][1], 0.0437, places=3)
        k = uber(**{'Base Mixing': 1, 'Glossy Layered Weight': 1.0, 'Glossiness': 0.8})
        k['karte:glanzheit'] = 'R/gl.jpg'
        G9materialglanz.aufloesen(k)
        self.assertEqual((k['rauheit'], k['rauheitinvers'], k['rauheitwert']), ('R/gl.jpg', True, 0.8))

    def test_3_ohne_glanzlappen(self):
        b = uber(**{'Glossy Layered Weight': 0.0, 'Glossy Roughness': 0.4})
        G9materialglanz.aufloesen(b)
        self.assertEqual((b['glanzgewicht'], b['rauheitwert']), (0.0, 0.4))
        self.assertNotIn('glanzf0', b)

    def test_4_pbrskin(self):
        b = {
            R + 'shader': 'pbrskin',
            R + 'Specular Lobe 1 Roughness': 1.0,
            R + 'Dual Lobe Specular Ratio': 0.15,
            R + 'Specular Lobe 2 Roughness Mult': 0.55,
            R + 'Dual Lobe Specular Reflectivity': 0.25,
            R + 'Dual Lobe Specular Weight': 1.0,
            R + 'Top Coat Weight': 0.25,
            R + 'Top Coat Roughness': 0.6721,
            R + 'Top Coat Reflectivity': 0.5,
            'karte:rauheit1': 'R/r.jpg',
        }
        G9materialglanz.aufloesen(b)
        self.assertAlmostEqual(b['rauheitwert'], 0.9325, places=4)
        self.assertAlmostEqual(b['glanzf0'][2], 0.02, places=5)
        self.assertEqual((b['klarlack'], b['klarlackrauheit'], b['rauheit']), (0.25, 0.6721, 'R/r.jpg'))

    def test_5_preset_und_ohne_shader(self):
        b = uber(**{'Glossy Layered Weight': 1.0, 'Glossy Roughness': 0.3})
        b['rauheitwert'] = 0.42
        G9materialglanz.aufloesen(b)
        self.assertEqual(b['rauheitwert'], 0.42)
        o = {'karte:rauheit1': 'R/r.jpg', 'karte:glanz': 'R/g.jpg', 'bump': 'R/b.jpg'}
        G9materialglanz.aufloesen(o)
        self.assertEqual(o, {'rauheit': 'R/r.jpg'})

    def test_6_normalen_bump_hoehe(self):
        b = uber(
            **{
                'Glossy Layered Weight': 1.0,
                'Normal Map': 0.5,
                'Bump Strength': 2.0,
                'Displacement Strength': 0.5,
                'Minimum Displacement': -0.1,
                'Maximum Displacement': 0.3,
            }
        )
        b.update({'normalen': 'R/n.jpg', 'bump': 'R/b.jpg', 'hoehe': 'R/h.jpg'})
        G9materialglanz.aufloesen(b)
        self.assertEqual((b['normalstaerke'], b['bumpstaerke']), (0.5, 2.0))
        self.assertAlmostEqual(b['hoehe_skala'], 0.002, places=6)
        self.assertAlmostEqual(b['hoehe_versatz'], -0.0005, places=6)
        ohne = uber(**{'Glossy Layered Weight': 1.0, 'Bump Strength': 0.0})
        ohne['bump'] = 'R/b.jpg'
        G9materialglanz.aufloesen(ohne)
        self.assertNotIn('bump', ohne)


class Bumpprobe(unittest.TestCase):
    def test_7_bump_wie_iray(self):
        flach = G9bumpnormalen.rechnen(torch.full((8, 8), 0.5, device='cuda'), 3.0)
        self.assertTrue(torch.allclose(flach, torch.tensor([0.0, 0.0, 1.0], device='cuda').expand(8, 8, 3)))
        rampe = torch.arange(8, device='cuda', dtype=torch.float32).repeat(8, 1) / 8.0  # steigt mit u
        n = G9bumpnormalen.rechnen(rampe, 1.0)[4, 4]
        self.assertLess(float(n[0]), 0.0)  # neigt nach −u: n ∝ (−f·du, …), du = 2/8
        self.assertAlmostEqual(float(n[0] / n[2]), -0.25, places=5)
        self.assertAlmostEqual(float(n[1]), 0.0, places=6)
        nm = torch.tensor([0.0, 0.6, 0.8], device='cuda').expand(8, 8, 3).clone()
        n2 = G9bumpnormalen.rechnen(torch.full((8, 8), 0.5, device='cuda'), 1.0, nm)[2, 2]
        self.assertTrue(torch.allclose(n2, torch.tensor([0.0, 0.6, 0.8], device='cuda'), atol=1e-6))


if __name__ == '__main__':
    unittest.main()
