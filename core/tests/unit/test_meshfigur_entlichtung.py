# -*- coding: utf-8 -*-
"""Mesh to 3D — Licht aus der Netzfarbe (`Meshfigurentlichtung`, Option `entlichten`), 07.10.2026.

Edgar: „mach 1 bis 4" (Vorschlag 1 der Prüfung von Hilfe → Architektur → Andere Modelle). Kunstdaten statt eines Auftrags: Hautfarbe mit
einem Seitenlicht (Helligkeit linear in der Normalen), das die Rechnung herausteilen muss. Sabotage-Gegenprobe: `faktor` überall 1 setzen
(Zeile `summe += …` entfernen) → `test_seitenlicht_wird_herausgerechnet` muss rot werden.
"""

import unittest

import numpy as np

from core.dienste.meshfiguroptionen import Meshfiguroptionen

from ._wrappersuchpfad import WRAPPERS, Wrappersuchpfad

Wrappersuchpfad.setzen()

HAUT = np.array([0.45, 0.30, 0.22])


def _kugel(n, seed=5):
    """`n` Punkte mit gleichverteilten Normalen auf einer Kugel von 10 cm Radius um (0, 1, 0)."""
    z = np.random.default_rng(seed)
    r = z.normal(size=(n, 3))
    r /= np.linalg.norm(r, axis=1, keepdims=True)
    return (r * 0.1 + np.array([0.0, 1.0, 0.0])).astype(np.float32), r.astype(np.float32)


class EntlichtungTest(unittest.TestCase):
    def _teil(self, licht):
        from meshfigur_entlichtung import Meshfigurentlichtung as E

        lage, normale = _kugel(90_000)
        lin = HAUT[None, :] * licht(normale)[:, None]
        farbe = E.srgb(lin)
        wahl = np.arange(0, len(lage), 1)
        return E, {'farbe': farbe, 'wahl': wahl, 'lage': lage, 'normale': normale, 'haut': np.ones(len(lage), bool)}, normale

    @staticmethod
    def _seitenunterschied(E, farbe, normale):
        y = E.linear(farbe) @ np.array([0.2126, 0.7152, 0.0722])
        links, rechts = normale[:, 0] > 0.5, normale[:, 0] < -0.5
        return abs(float(y[links].mean()) - float(y[rechts].mean())) / float(y.mean())

    def test_seitenlicht_wird_herausgerechnet(self):
        E, teil, normale = self._teil(lambda n: 1.0 + 0.35 * n[:, 0])
        vorher = self._seitenunterschied(E, teil['farbe'], normale)
        E(1.0).anwenden([teil])
        nachher = self._seitenunterschied(E, teil['farbe'], normale)
        self.assertGreater(vorher, 0.3)
        self.assertLess(nachher, 0.4 * vorher)

    def test_gleichmaessiges_licht_bleibt(self):
        E, teil, _ = self._teil(lambda n: np.ones(len(n)))
        vorher = teil['farbe'].copy()
        befund = E(1.0).anwenden([teil])
        self.assertLessEqual(int(np.abs(teil['farbe'].astype(int) - vorher.astype(int)).max()), 3)
        self.assertAlmostEqual(befund['faktor']['median'], 1.0, delta=0.03)

    def test_nur_gueltige_texel_werden_veraendert(self):
        E, teil, _ = self._teil(lambda n: 1.0 + 0.35 * n[:, 0])
        teil['wahl'] = np.arange(0, len(teil['lage']), 2)
        for k in ('lage', 'normale', 'haut'):
            teil[k] = teil[k][teil['wahl']]
        vorher = teil['farbe'].copy()
        E(1.0).anwenden([teil])
        self.assertTrue(np.array_equal(teil['farbe'][1::2], vorher[1::2]))
        self.assertFalse(np.array_equal(teil['farbe'][0::2], vorher[0::2]))

    def test_befund_nennt_ansichten_und_faktoren(self):
        E, teil, _ = self._teil(lambda n: 1.0 + 0.35 * n[:, 0])
        befund = E(0.85).anwenden([teil])
        self.assertEqual(set(befund['ansichten']), {'vorn', 'hinten', 'links', 'rechts'})
        self.assertEqual(befund['texel'], 90_000)
        self.assertEqual(set(befund['faktor']), {'min', 'p5', 'median', 'p95', 'max'})
        self.assertAlmostEqual(befund['staerke'], 0.85)

    def test_fuellschicht_nur_mit_deckung(self):
        E, teil, normale = self._teil(lambda n: 1.0 + 0.35 * n[:, 0])
        e = E(1.0)
        e.anwenden([teil])
        farben = np.full((len(normale), 3), 0.5, np.float32)
        deckung = np.zeros(len(normale), np.float32)
        deckung[:10] = 1.0
        aus = e.punktfarben(teil['lage'], normale, farben, deckung)
        self.assertTrue(np.array_equal(aus[10:], farben[10:]))
        self.assertFalse(np.array_equal(aus[:10], farben[:10]))


class EntlichtungOptionTest(unittest.TestCase):
    def test_option_steht_hinter_kopfhaut_und_ist_aus(self):
        schluessel = [e['schluessel'] for e in Meshfiguroptionen.KATALOG]
        self.assertEqual(schluessel[schluessel.index('kopfhaut') + 1], 'entlichten')
        self.assertEqual(Meshfiguroptionen.pruefen({})['entlichten'], 0)

    def test_option_wird_geklemmt(self):
        self.assertEqual(Meshfiguroptionen.pruefen({'entlichten': 500})['entlichten'], 100)
        self.assertEqual(Meshfiguroptionen.pruefen({'entlichten': -4})['entlichten'], 0)
        self.assertEqual(Meshfiguroptionen.pruefen({'entlichten': 'x'})['entlichten'], 0)

    def test_runner_liest_die_option(self):
        quelle = (WRAPPERS / '_run_meshfigur.py').read_text(encoding='utf-8')
        self.assertIn("optionen.get('entlichten')", quelle)
        self.assertIn('entlichtung=', quelle)


if __name__ == '__main__':
    unittest.main()
