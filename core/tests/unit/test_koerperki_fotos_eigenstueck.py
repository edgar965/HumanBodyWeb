# -*- coding: utf-8 -*-
"""Tests für Stufe K4 der eigenen Kleider (25.10.2026, Besitzer 2d-3d-AI): `KoerperKI_Fotos.Fotoeigenstueck.schnitt` (Säume aus der Foto-Schale), `Eigenstueckbau` (Sitz und
Schnitt wie der Shader `EigenkleidGLSL`/`EigenkleidschnittGLSL`) und `Flaechenabstand.naechster` (nächster Punkt auf einem Dreieck) — an Kunstwerten, ohne Figur und ohne Karte.

WARUM: Die Gegenprobe „Foto-Schale → eigenes Stück“ misst den Abstand und die Saumlage mit diesen drei Bausteinen. Ein Schnitt auf der falschen Seite, ein vertauschter Sitzwert
(oben ↔ unten) oder ein nächster Punkt außerhalb des Dreiecks ergäbe Millimeter, die nach Übereinstimmung aussehen.
"""
import math
import sys
import unittest

import torch
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT))

from KoerperKI_Fotos.eigenstueckbau import Eigenstueckbau  # noqa: E402
from KoerperKI_Fotos.flaechenabstand import Flaechenabstand  # noqa: E402
from KoerperKI_Fotos.fotoeigenstueck import Fotoeigenstueck  # noqa: E402

D = torch.float64


def koord(kette, anteil, hoehe, winkel=0.0, x=0.0):
    t = lambda v: torch.tensor(v if isinstance(v, list) else [v], dtype=D)  # noqa: E731
    return {'kette': torch.tensor(kette if isinstance(kette, list) else [kette]), 'anteil': t(anteil), 'hoehe': t(hoehe), 'winkel': t(winkel), 'x': t(x)}


class DerSchnitt(unittest.TestCase):

    def test_gedeckt_unter_dem_schnitt(self):
        w = torch.linspace(0, 1, 101, dtype=D)
        s = Fotoeigenstueck.schnitt(w, w < 0.605, True)
        self.assertAlmostEqual(s['s'], 0.605, places=3)
        self.assertEqual(s['fehler'], 0.0)

    def test_gedeckt_ueber_dem_schnitt_mit_einem_ausreisser(self):
        w = torch.linspace(0, 1, 101, dtype=D)
        g = w > 0.405
        g[10] = True                                       # ein Fleck weit oben: ein Fehlpunkt, der Schnitt bleibt
        s = Fotoeigenstueck.schnitt(w, g, False)
        self.assertAlmostEqual(s['s'], 0.405, places=3)
        self.assertAlmostEqual(s['fehler'], 1 / 101, places=4)


class DerBau(unittest.TestCase):
    """Längen Rumpf 0,6 m, Arm 0,55 m, Bein 0,8 m; Oberteil Saum 0,8, Ärmel 0,3, Ausschnitt rund 0,07 vorn, 0,02 hinten, Breite 180 mm."""

    U = {'saum': [0.8, 0.3, 0, 0], 'sitz': [0.003, 0.006, 0.009, 0.004], 'hals': [0, 0.07, 0.02, 0.18], 'kragen': [0, 0, 0, 0]}

    def setUp(self):
        self.b = Eigenstueckbau([0.6, 0.55, 0.8])

    def test_saum_und_aermel_in_metern(self):
        terme, kante = self.b.terme('oberteil', self.U, koord([1, 1, 2], [-0.5, -0.5, 0.5], [0.5, 0.9, 0.3], x=[0.15, 0.15, 0.3]))
        self.assertAlmostEqual(float(terme['saum'][0]), 0.3 * 0.6, places=9)
        self.assertLess(float(kante[1]), 0)                               # unter dem Saum
        self.assertAlmostEqual(float(terme['aermel'][2]), -0.2 * 0.55, places=9)
        self.assertTrue(math.isinf(float(terme['saum'][2])))               # der Arm hat keinen unteren Saum

    def test_ausschnitt_vorn_tief_seitlich_bis_zum_halsansatz(self):
        _t, kante = self.b.terme('oberteil', self.U, koord([1, 1, 1, 1], -0.5, [0.05, 0.1, 0.01, 0.01], winkel=[0.0, 0.0, 0.0, 0.5], x=[0.0, 0.0, 0.12, 0.0]))
        self.assertLess(float(kante[0]), 0)                               # vorn mitten über der Tiefe 0,07
        self.assertGreater(float(kante[1]), 0)                            # darunter Stoff
        self.assertGreater(float(kante[2]), 0)                            # außerhalb der halben Breite (9 cm) Stoff bis zum Halsansatz
        self.assertLess(float(kante[3]), 0)                               # hinten mitten über der Tiefe 0,02

    def test_sitz_oben_mitte_unten_aermel(self):
        s = self.b.sitz('oberteil', self.U, koord([1, 1, 1, 2], [-0.5, -0.5, -0.5, 0.3], [0.05, 0.5, 0.97, 0.2]))
        self.assertEqual([round(float(v), 6) for v in s], [0.003, 0.006, 0.009, 0.004])

    def test_hose_ueber_dem_bund_kein_stoff_und_oberteil_ueber_der_hose(self):
        uh = {'saum': [0.66, 0.3, 0, 0], 'sitz': [0.002, 0.005, 0.008, 0]}
        _t, kante = self.b.terme('hose', uh, koord([1, 1, 4, 4], [-0.5, -0.5, 0.2, 0.4], [0.6, 0.8, 1.2, 1.4]))
        self.assertEqual([float(v) > 0 for v in kante], [False, True, True, False])
        s = self.b.sitz('oberteil', self.U, koord([1, 1], -0.5, [0.5, 0.8]), lage=(0.015, 0.66))
        self.assertEqual([round(float(v), 6) for v in s], [0.006, 0.015])      # über dem Bund mindestens die Lage, darüber der eigene Sitz


class DerNaechstePunkt(unittest.TestCase):

    def test_innen_kante_und_ecke(self):
        a, b, c = (torch.tensor(v, dtype=D) for v in ([0.0, 0, 0], [1.0, 0, 0], [0.0, 1, 0]))
        q = torch.tensor([[0.2, 0.2, 0.005], [0.5, -0.3, 0.0], [-1.0, -1.0, 0.0]], dtype=D)
        bary = Flaechenabstand.naechster(q, a.expand(3, 3), b.expand(3, 3), c.expand(3, 3))
        fuss = bary[:, :1] * a + bary[:, 1:2] * b + bary[:, 2:] * c
        self.assertAlmostEqual(float((q[0] - fuss[0]).norm()), 0.005, places=9)     # ein Sitz von 5 mm über der Fläche
        self.assertEqual([round(float(v), 6) for v in fuss[1]], [0.5, 0.0, 0.0])
        self.assertEqual([round(float(v), 6) for v in fuss[2]], [0.0, 0.0, 0.0])
