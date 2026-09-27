# -*- coding: utf-8 -*-
"""Reiter „Mesh to 3D" — Augen: Irisfarbe des Netzes, eingefärbtes Augenbild, Augenpartie als Lücke im
Eigenmorph, Fingerabdruck einer Stellung mit neu abgelegtem Eigenmorph.

Edgar, 27.09.2026: „mach das mit der Iris" und „vergleiche doch Kopfform, Augenform, ist doch total
unterschiedlich!" — gemessen stach der starre Daz-Augapfel durch die Lider (sichtbar 419 statt 230 mm²),
weil der Rest die Augenhöhle in die Augenmulde des Hunyuan-Kopfs zog. Ohne Daz-Bibliothek: Kunstbilder,
Kunstnetze, die Maske von `Meshfiguraugenhoehle` wird gesetzt.
"""

import unittest
from unittest import mock

import numpy as np

from core.dienste.meshfiguraugenbild import Meshfiguraugenbild as A
from core.dienste.meshfiguraugenhoehle import Meshfiguraugenhoehle

from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()


class AugenbildTest(unittest.TestCase):
    KANTE = 256

    def _bild(self):
        """Lederhaut (175, 169, 163), Iris (108, 85, 66), Pupille (3, 3, 4) — Maße wie G9_Eyes01_D."""
        b = np.zeros((self.KANTE, self.KANTE, 3), np.uint8)
        b[:] = (175, 169, 163)
        yy, xx = np.mgrid[: self.KANTE, : self.KANTE] + 0.5
        for mx, my in A.MITTEN:
            r = np.hypot(xx - mx * self.KANTE, yy - my * self.KANTE) / self.KANTE
            b[r < A.LIMBUS[0]] = (108, 85, 66)
            b[r < A.PUPILLE[0]] = (3, 3, 4)
        return b

    def test_iris_bekommt_die_farbe_des_netzes(self):
        aus, _ = A.faerben_bild(self._bild(), (106, 75, 46))
        iris = np.median(aus[A.irismaske(self.KANTE)], axis=0)
        np.testing.assert_allclose(iris, (106, 75, 46), atol=2)

    def test_pupille_und_lederhaut_bleiben(self):
        b = self._bild()
        aus, _ = A.faerben_bild(b, (106, 75, 46))
        m = self.KANTE // 4
        self.assertEqual(tuple(aus[m, m]), tuple(b[m, m]))  # Pupillenmitte
        self.assertEqual(tuple(aus[self.KANTE - 5, 5]), tuple(b[self.KANTE - 5, 5]))  # Lederhaut/Rand

    def test_faktor_ist_begrenzt(self):
        _, faktor = A.faerben_bild(self._bild(), (255, 0, 0))
        self.assertTrue((faktor >= A.GRENZEN[0]).all() and (faktor <= A.GRENZEN[1]).all())


class IrisTest(unittest.TestCase):
    """`Meshfiguriris`: Median im Ring um die Irismitte, nicht Pupille, nicht Lederhaut."""

    class Scan:
        """Ebenes Gitter (1 mm) um die Irismitte, Farbe nach Abstand: Pupille, Iris, Lederhaut."""

        def __init__(self, mitte):
            self.mitte = np.asarray(mitte, dtype=float)
            x, y = np.meshgrid(np.linspace(-0.02, 0.02, 41), np.linspace(-0.02, 0.02, 41))
            self.punkte = np.stack([x.ravel(), y.ravel(), np.zeros(x.size)], axis=1) + self.mitte
            i = np.arange(40 * 41).reshape(40, 41)[:, :40].ravel()
            self.flaechen = np.concatenate(
                [np.stack([i, i + 1, i + 41], 1), np.stack([i + 1, i + 42, i + 41], 1)]
            )
            self.gueltig = np.ones(len(self.flaechen), dtype=bool)

        def flaecheninhalte(self):
            a, b, c = (self.punkte[self.flaechen[:, k]] for k in range(3))
            return 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1)

        def farben(self, flaeche, bary):
            p = np.einsum('mk,mkc->mc', bary, self.punkte[self.flaechen[flaeche]])
            r = np.linalg.norm(p - self.mitte, axis=1)
            aus = np.full((len(flaeche), 3), 240.0)
            aus[r < 0.0055] = (106, 75, 46)
            aus[r < 0.002] = (5, 5, 5)
            return aus

    def test_ringmedian_ist_die_irisfarbe(self):
        from meshfigur_iris import Meshfiguriris

        g = np.zeros((478, 3))
        g[468] = g[473] = (0.0, 1.6, 0.1)
        rand = ((0.006, 0, 0), (0, 0.006, 0), (-0.006, 0, 0), (0, -0.006, 0))
        for i, d in zip(range(469, 473), rand, strict=True):
            g[i] = g[468] + d
            g[i + 5] = g[473] + d
        aus = Meshfiguriris(self.Scan(g[468]), g).messen()
        self.assertEqual(aus['farbe'], [106, 75, 46])
        self.assertAlmostEqual(aus['rechts']['radius_mm'], 6.0, places=1)

    def test_ohne_irispunkte_nichts(self):
        from meshfigur_iris import Meshfiguriris

        self.assertIsNone(Meshfiguriris(None, np.zeros((468, 3))).messen())


class AugenhoehleTest(unittest.TestCase):
    def test_augenpartie_wird_luecke(self):
        maske = np.array([False, True, True, False])
        rest = np.ones((4, 3)) * 0.01
        gewicht = np.ones(4)
        with mock.patch.object(Meshfiguraugenhoehle, '_maske', maske):
            r, g, n = Meshfiguraugenhoehle.luecke(rest, gewicht)
        self.assertEqual(n, 2)
        np.testing.assert_array_equal(g, [1, 0, 0, 1])
        np.testing.assert_array_equal(r[1], [0, 0, 0])
        self.assertEqual(rest[1, 0], 0.01)  # Eingabe bleibt unberührt

    def test_fremde_punktzahl_bleibt_unveraendert(self):
        with mock.patch.object(Meshfiguraugenhoehle, '_maske', np.ones(5, bool)):
            _, g, n = Meshfiguraugenhoehle.luecke(np.zeros((3, 3)), np.ones(3))
        self.assertEqual(n, 0)
        np.testing.assert_array_equal(g, [1, 1, 1])


class BereicheTest(unittest.TestCase):
    """Die Augenpartie zählt im Flächenabgleich nicht (INNEN) — die Textur sieht sie weiter als Haut."""

    def test_augenpartie_ist_innen(self):
        from Genesis9.netzbereiche import G9netzbereiche

        from core.dienste.meshfigurgenesis import Meshfigurgenesis

        roh = np.array([G9netzbereiche.HAUT] * 4, dtype=np.int8)
        with (
            mock.patch.object(G9netzbereiche, 'bereiche', return_value=roh),
            mock.patch.object(Meshfiguraugenhoehle, '_maske', np.array([False, True, False, True])),
        ):
            aus = Meshfigurgenesis.bereiche()
        np.testing.assert_array_equal(aus, [0, G9netzbereiche.INNEN, 0, G9netzbereiche.INNEN])
        np.testing.assert_array_equal(roh, [0, 0, 0, 0])  # Vorlage bleibt unberührt


class FingerabdruckTest(unittest.TestCase):
    """Ein Eigenmorph, der unter demselben Namen neu abgelegt wird, ist eine andere Stellung."""

    def test_neuer_dateistand_neuer_fingerabdruck(self):
        from Genesis9.eigenmorphe import G9eigenmorphe
        from Genesis9.formung import G9formung

        regler = {'eigen:probe_mesh': 1.0, 'body_bs_BodyMass': 0.2}
        with mock.patch.object(G9eigenmorphe, 'dateistand', return_value=1):
            alt = G9formung(regler).fingerabdruck()
        with mock.patch.object(G9eigenmorphe, 'dateistand', return_value=2):
            neu = G9formung(regler).fingerabdruck()
        self.assertNotEqual(alt, neu)

    def test_ohne_eigenmorph_unveraendert(self):
        from Genesis9.eigenmorphe import G9eigenmorphe
        from Genesis9.formung import G9formung

        with mock.patch.object(G9eigenmorphe, 'dateistand', side_effect=AssertionError('gefragt')):
            G9formung({'body_bs_BodyMass': 0.2}).fingerabdruck()


if __name__ == '__main__':
    unittest.main()
