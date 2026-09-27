# -*- coding: utf-8 -*-
"""`Meshfigurtexelpruefung` an einer Kunstkachel (128 × 128, ohne Daz-Bibliothek): Befund Edgar
27.09.2026 „ich brauche das Ergebnis in der 3D-Ansicht, nur richtig!" — weiße Füllstreifen, braune
Schattenklumpen und eine fleckige Kopfhaut kamen aus dem Netz in die Kacheln.

1. Ein weißlicher Streifen in der Haut wird verworfen und aus der Umgebung gefüllt.
2. Entsättigte dunkle Schattentreffer und nie getroffene Hauttexel bekommen den örtlichen Hautton.
3. Der Gesichtskern bleibt, wie er ist (Lippen sind keine Hautfarbe).
4. Die Kopfhaut bekommt die Haarfarbe — graue Füllzellen fallen weg, eine abgetrennte Insel (Ohr)
   bleibt unberührt.
"""

import unittest
from unittest import mock

import numpy as np

from core.dienste.meshfigurtexelpruefung import Meshfigurtexelpruefung

HAUT, KOPFHAUT, KERN = 0, 1, 2
S = 128


class _Abtastung:
    """Eine Kachel 1001: Käfigpunkt i = Texel i der Insel (ein Punkt je Texel)."""

    def __init__(self, drin):
        self.seite = S
        self.kacheln = [1001]
        self.drin = drin

    def stellen(self, kachel):
        n = int(self.drin.sum())
        ecken = np.repeat(np.arange(n)[:, None], 3, axis=1)
        return self.drin, ecken, np.tile([1.0, 0.0, 0.0], (n, 1))


class MeshfigurtexelpruefungTest(unittest.TestCase):
    HAUTFARBE = (200, 140, 110)

    def _pruefen(self, drin, bereich, kern, farbe, gewicht):
        netzbereiche = mock.MagicMock(HAUT=HAUT, KOPFHAUT=KOPFHAUT, ZEHEN=9, HAND=3, FINGER=2)
        netzbereiche.bereiche.return_value = bereich
        netzbereiche.gesichtskern.return_value = kern
        modul = mock.MagicMock(G9netzbereiche=netzbereiche)
        with mock.patch.dict('sys.modules', {'Genesis9.netzbereiche': modul}):
            pruefung = Meshfigurtexelpruefung(_Abtastung(drin))
        rausch = np.random.default_rng(3).normal(0, 3, farbe.shape)
        hd = {'farbe_1001': np.clip(farbe + rausch, 0, 255).astype(np.uint8), 'gewicht_1001': gewicht}
        neu, befund = pruefung.pruefen(hd)
        return neu, befund, hd['farbe_1001']

    def test_streifen_schatten_kern_und_kopfhaut(self):
        drin = np.zeros((S, S), dtype=bool)
        drin[:, :96] = True          # Hauptinsel
        drin[:16, 112:] = True       # „Ohr": eigene Insel
        yy, xx = np.nonzero(drin)
        n = len(yy)
        haupt = xx < 96
        bereich = np.full(n, HAUT, dtype=np.int8)
        bereich[(yy < 24) & haupt] = KOPFHAUT
        bereich[~haupt] = KOPFHAUT
        kern = (yy >= 80) & (yy < 88) & (xx >= 40) & (xx < 48)
        farbe = np.tile(np.array(self.HAUTFARBE, dtype=float), (n, 1))
        gewicht = np.ones(n, dtype=np.float32)
        streifen = (xx >= 60) & (xx < 64) & (yy >= 40)
        farbe[streifen] = (238, 222, 214)                      # weißlich
        schatten = (xx >= 10) & (xx < 16) & (yy >= 40)
        farbe[schatten] = (70, 62, 58)                          # entsättigt, dunkel
        loch = (xx >= 24) & (xx < 30) & (yy >= 40)
        gewicht[loch] = 0.0
        farbe[kern] = (170, 40, 60)                             # Lippe
        oben = (bereich == KOPFHAUT) & haupt
        farbe[oben & (xx % 2 == 0)] = (70, 45, 30)              # braunes Haar
        farbe[oben & (xx % 2 == 1)] = (150, 150, 152)           # graue Füllzellen

        neu, befund, eingabe = self._pruefen(drin, bereich, kern, farbe, gewicht)
        f = neu['farbe_1001'].astype(float)
        g = neu['gewicht_1001']
        haut = np.array(self.HAUTFARBE, dtype=float)
        for name, maske in (('Streifen', streifen), ('Schatten', schatten), ('Loch', loch)):
            self.assertLess(np.abs(f[maske] - haut).max(axis=1).mean(), 20, name)
            self.assertTrue((g[maske] == 1).all(), name + ' gefüllt')
        np.testing.assert_array_equal(neu['farbe_1001'][kern], eingabe[kern], 'Lippe unverändert')
        self.assertLess(np.abs(np.median(f[oben], axis=0) - (70, 45, 30)).max(), 15, 'Haarfarbe, nicht Grau')
        np.testing.assert_array_equal(neu['farbe_1001'][~haupt], eingabe[~haupt], 'Ohr-Insel unberührt')
        self.assertGreater(befund['1001']['verworfen'], 0)
        self.assertGreater(befund['1001']['kopfhaut']['gemalt'], 0)


if __name__ == '__main__':
    unittest.main()
