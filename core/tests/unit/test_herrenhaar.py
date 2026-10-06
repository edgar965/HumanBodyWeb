# -*- coding: utf-8 -*-
"""Herrenhaar (05.10.2026, Edgar: „ein Haar für einen normalen mittelalten Mann mit normalem Haarschnitt"): Wuchsfeld (`Haarwuchs`), Röhren und Bänder (`Haarband`), Farben und Spreizung (`Herrenhaar.farben`).

Reine NumPy-Rechnung, kleine Zahlen, keine Datenbank, keine Dateien. Der Bau auf einem Kunstkopf steht im LongRunner (`longrunner/test_herrenhaar_kunstkopf.py`, über der 1-s-Schwelle).
Geschrieben, nicht gelaufen (`testsuite-nur-auf-ansage`).

Sabotage: in `Haarband.roehren` die Umkehr `d[nach_innen] = …` streichen → Fall 5 rot; in `Herrenhaar.farben` `faktoren / …` (Normierung auf Mittel 1) streichen → Fall 7 rot;
in `Haarwuchs.laufrichtung` `runter` auf `u` statt Tangente setzen → Fall 3 rot.
"""

from pathlib import Path
from types import SimpleNamespace

import numpy as np
from django.test import SimpleTestCase

from core.dienste.haarband import Haarband
from core.dienste.haarwuchs import Haarwuchs
from core.dienste.herrenhaar import Herrenhaar


def _kugelpunkte(n=300, el_von=-60.0, el_bis=85.0):
    """Zufällige Einheitsrichtungen zwischen zwei Höhenwinkeln (feste Saat)."""
    zufall = np.random.default_rng(5)
    return Haarwuchs.einheit(zufall.uniform(0.0, 360.0, n), zufall.uniform(el_von, el_bis, n))


class DasHaarwuchsfeld(SimpleTestCase):
    def test_1_die_einheit_aus_azimut_und_hoehe(self):
        np.testing.assert_allclose(Haarwuchs.einheit(0.0, 0.0), [0.0, 0.0, 1.0], atol=1e-12)         # Azimut 0 = vorn (+z)
        np.testing.assert_allclose(Haarwuchs.einheit(90.0, 0.0), [1.0, 0.0, 0.0], atol=1e-12)        # 90° = links (+x)
        np.testing.assert_allclose(Haarwuchs.einheit(0.0, 90.0), [0.0, 1.0, 0.0], atol=1e-12)        # Scheitel

    def test_2_das_rauschen_ist_begrenzt_wiederholbar_und_glatt(self):
        u = _kugelpunkte()
        r = Haarwuchs.rauschen(u, 3)
        self.assertLessEqual(float(np.abs(r).max()), 1.0)
        np.testing.assert_array_equal(r, Haarwuchs.rauschen(u, 3))                                   # gleiche Saat, gleiche Werte
        self.assertGreater(float(np.abs(r - Haarwuchs.rauschen(u, 4)).max()), 0.1)                   # andere Saat, anderes Feld
        nah = u + np.array([0.001, 0.0, 0.0])                                                         # ein Hundertstel des Radius (1 mm bei 0,1 m)
        nah /= np.linalg.norm(nah, axis=1, keepdims=True)
        self.assertLess(float(np.abs(Haarwuchs.rauschen(nah, 3) - r).max()), 0.15)                   # Strähnen: Nachbarn ähneln sich

    def test_3_die_wuchsrichtung_ist_eine_tangente_der_kugel(self):
        u = _kugelpunkte()
        t = Haarwuchs.laufrichtung(u, 7)
        np.testing.assert_allclose(np.linalg.norm(t, axis=1), 1.0, atol=1e-9)
        self.assertLess(float(np.abs((t * u).sum(axis=1)).max()), 1e-6)                               # senkrecht zur Richtung vom Kopfmittelpunkt: das Haar liegt am Kopf

    def test_4_an_den_seiten_unten_zieht_die_schwerkraft_das_haar_nach_unten(self):
        zufall = np.random.default_rng(2)
        u = Haarwuchs.einheit(zufall.uniform(60.0, 120.0, 200), zufall.uniform(-20.0, 5.0, 200))     # Seiten, unter der Waagerechten bis knapp darüber
        t = Haarwuchs.laufrichtung(u, 7)
        self.assertLess(float(t[:, 1].mean()), -0.9)


class DieHaarbaender(SimpleTestCase):
    @staticmethod
    def _reihen(s=3, k=4):
        """`s` Strähnen entlang +x, nebeneinander in z, Außenrichtung +y."""
        reihen = np.zeros((s, k, 3))
        reihen[:, :, 0] = 0.01 * np.arange(k)[None, :]
        reihen[:, :, 2] = 0.02 * np.arange(s)[:, None]
        return reihen, np.tile([0.0, 1.0, 0.0], (s, k, 1))

    def test_5_roehren_haben_drei_ecken_je_reihenpunkt_und_sechs_dreiecke_je_segment_nach_aussen(self):
        reihen, aussen = self._reihen()
        punkte, dreiecke = Haarband.roehren(reihen, aussen, np.full((3, 4), 0.001))
        self.assertEqual(punkte.shape, (3 * 3 * 4, 3))
        self.assertEqual(dreiecke.shape, (3 * 6 * 3, 3))
        self.assertLess(int(dreiecke.max()), len(punkte))
        achse = reihen[:, :-1].reshape(-1, 3).repeat(6, axis=0)                                       # der Reihenpunkt vor dem Segment, je Dreieck
        a, b, c = punkte[dreiecke[:, 0]], punkte[dreiecke[:, 1]], punkte[dreiecke[:, 2]]
        nach_aussen = (np.cross(b - a, c - a) * ((a + b + c) / 3.0 - achse)).sum(axis=1)
        self.assertTrue((nach_aussen > 0.0).all())                                                    # jedes Dreieck zeigt von der Strähne weg

    def test_6_baender_haben_zwei_punkte_je_reihenpunkt_und_zwei_dreiecke_je_segment(self):
        reihen, aussen = self._reihen()
        punkte, dreiecke, normalen = Haarband.baender(reihen, aussen, np.full((3, 4), 0.001))
        self.assertEqual((punkte.shape, dreiecke.shape, normalen.shape), ((3 * 2 * 4, 3), (3 * 2 * 3, 3), (3 * 2 * 4, 3)))
        np.testing.assert_allclose(np.abs(punkte[0::2, 2] - punkte[1::2, 2]), 0.002, atol=1e-9)       # die Breite des Bands (quer zur Strähne und zur Außennormale: z)

    def test_6b_die_straehne_je_eckpunkt(self):
        np.testing.assert_array_equal(Haarband.eckpunkte(2, 4, 3), np.repeat([0, 1], 12))
        np.testing.assert_array_equal(Haarband.eckpunkte(2, 4), np.repeat([0, 1], 8))


class DieHaarfarben(SimpleTestCase):
    def test_7_die_strahnenfarben_haben_im_mittel_die_haarfarbe_abzueglich_der_kappe(self):
        kappe, gruppen = Herrenhaar.farben([0.4, 0.4, 0.4])
        self.assertEqual(len(gruppen), len(Herrenhaar.GRUPPEN))
        self.assertAlmostEqual(sum(a for _c, a in gruppen), 1.0, places=9)
        mittel = sum(np.asarray(c) * a for c, a in gruppen) / sum(a for _c, a in gruppen)
        np.testing.assert_allclose(0.7 * mittel + 0.3 * np.asarray(kappe), 0.4 * Herrenhaar.HELL, atol=1e-6)     # sichtbar: Strähnen und Kappe im Verhältnis 70 : 30 treffen die Haarfarbe
        np.testing.assert_allclose(kappe, 0.4 * Herrenhaar.HELL * Herrenhaar.KAPPE_ANTEIL, atol=1e-9)
        hell = [float(c[0]) for c, _a in gruppen]
        self.assertEqual(hell, sorted(hell))                                                              # von dunkel nach hell
        self.assertGreater(hell[-1] / hell[0], 1.5)                                                       # graues Haar meliert deutlich

    def test_8_die_spreizung_ist_bei_grau_gross_und_bei_dunklem_braun_klein(self):
        self.assertAlmostEqual(Herrenhaar.spreizung([0.5, 0.5, 0.5]), 0.7, places=6)                      # unbunt und mittelhell
        self.assertAlmostEqual(Herrenhaar.spreizung([0.3, 0.1, 0.05]), 0.25, places=6)                    # bunt: kaum Streuung
        dunkel = Herrenhaar.spreizung([0.02, 0.02, 0.02])
        self.assertGreater(dunkel, 0.25)
        self.assertLess(dunkel, 0.35)                                                                     # sehr dunkles Grau streut wenig

    def test_9_ohne_quelle_der_huelle_gibt_es_keinen_fingerabdruck(self):
        ablage = SimpleNamespace(ergebnis=lambda name: Path('/gibt/es/nicht') / name)
        self.assertIsNone(Herrenhaar.fingerabdruck(ablage))
