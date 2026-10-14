# -*- coding: utf-8 -*-
"""`Meshfigurtexeldetail` (14.10.2026, Edgar1: „Textur bei Beinen unterhalb und oberhalb der Unterhose schlecht“): gefüllte Hauttexel bekommen die Zeichnung (Härchen, Poren) der echten Haut daneben.

Kunstkachel 256 × 256 mit EINER Insel: links echte Haut mit Härchen (jede vierte Spalte 30 % dunkler), rechts die glatte Füllung im Ton des Mittels.
Sabotage-Gegenproben: `Meshfigurtexelpruefung.DETAIL_UEBERTRAGEN = False` im Wächter → `test_die_pruefung_ruft_die_uebertragung` rot; die Bedingung `insel[...] == eigene[...]` streichen → `test_eine_quelle_aus_einer_anderen_insel_zaehlt_nicht` rot.
"""

import unittest
from pathlib import Path

import numpy as np

from core.dienste.meshfigurtexeldetail import Meshfigurtexeldetail
from core.dienste.meshfigurtexelpruefung import Meshfigurtexelpruefung

S = 256
GRUND = 180.0


def _kachel(gut_bis=200):
    """`(drin, ziel, gut, farbe, fuellung)` für eine Insel über die ganze Kachel; links von `gut_bis` Haut mit Härchen, rechts die glatte Füllung."""
    drin = np.ones((S, S), dtype=bool)
    spalte = np.tile(np.arange(S), (S, 1))
    gut = spalte < gut_bis
    farbe = np.full((S, S, 3), GRUND)
    farbe[:, ::4] *= 0.7
    fuellung = np.full((S, S, 3), GRUND)
    return drin, (~gut).reshape(-1), gut.reshape(-1), farbe.reshape(-1, 3), fuellung.reshape(-1, 3)


class DetailTest(unittest.TestCase):
    def _anwenden(self, drin, ziel, gut, farbe, fuellung):
        return Meshfigurtexeldetail(S, Meshfigurtexelpruefung.glatt).anwenden(drin, ziel, gut, farbe, fuellung)

    def test_die_fuellung_bekommt_die_zeichnung_der_nachbarschaft(self):
        drin, ziel, gut, farbe, fuellung = _kachel()
        zahl = self._anwenden(drin, ziel, gut, farbe, fuellung)
        self.assertGreater(zahl, 0.5 * int(ziel.sum()), 'die meisten Texel der Füllung finden eine Quelle in Reichweite')
        glatt_vorher = np.full(fuellung[ziel].shape, GRUND)
        self.assertGreater(float(fuellung[ziel][:, 0].std()), 2.0, 'die Füllung ist nicht mehr glatt')
        self.assertTrue((fuellung[~ziel] == GRUND).all(), 'echte Hauttexel bleiben, wie sie sind')
        self.assertLess(abs(float(fuellung[ziel][:, 0].mean()) - float(glatt_vorher[:, 0].mean())) / GRUND, 0.08, 'das Mittel (der Ton) bleibt das der Füllung')

    def test_die_grenzen_halten(self):
        drin, ziel, gut, farbe, fuellung = _kachel()
        self._anwenden(drin, ziel, gut, farbe, fuellung)
        self.assertGreaterEqual(float(fuellung.min()), 0.0)
        self.assertLessEqual(float(fuellung.max()), 255.0)
        # Das Verhältnis der Quelle liegt in `GRENZEN`; mehrere Quellen überlagern sich, die Summe wird wieder begrenzt.
        self.assertGreaterEqual(float(fuellung[ziel].min()) / GRUND, Meshfigurtexeldetail.GRENZEN[0] - 1e-6)
        self.assertLessEqual(float(fuellung[ziel].max()) / GRUND, Meshfigurtexeldetail.GRENZEN[1] + 1e-6)

    def test_ohne_gute_texel_bleibt_alles(self):
        drin, ziel, gut, farbe, fuellung = _kachel()
        gut[:] = False
        self.assertEqual(self._anwenden(drin, ziel, gut, farbe, fuellung), 0)
        self.assertTrue((fuellung == GRUND).all())

    def test_eine_quelle_aus_einer_anderen_insel_zaehlt_nicht(self):
        """Die Härchen einer anderen UV-Insel (andere Körperstelle) sind keine Zeichnung für diese Füllung."""
        drin = np.zeros((S, S), dtype=bool)
        drin[:, :100] = True                                    # Insel A: nur Füllung
        drin[:, 140:] = True                                    # Insel B: echte Haut mit Härchen
        spalte = np.tile(np.arange(S), (S, 1))
        gut_bild = spalte >= 140
        farbe_bild = np.full((S, S, 3), GRUND)
        farbe_bild[:, ::4] *= 0.7
        n = int(drin.sum())
        ziel = (~gut_bild)[drin]
        gut = gut_bild[drin]
        fuellung = np.full((n, 3), GRUND)
        self.assertEqual(Meshfigurtexeldetail(S, Meshfigurtexelpruefung.glatt).anwenden(drin, ziel, gut, farbe_bild[drin], fuellung), 0)
        self.assertTrue((fuellung == GRUND).all())

    def test_dasselbe_ergebnis_beim_zweiten_aufruf(self):
        a = _kachel()
        b = _kachel()
        self._anwenden(*a)
        self._anwenden(*b)
        self.assertTrue(np.array_equal(a[4], b[4]), 'kein Zufall: die Versätze kommen aus einer festen Spirale')

    def test_die_versaetze_liegen_in_der_reichweite(self):
        v = Meshfigurtexeldetail.versaetze()
        weite = np.hypot(v[:, 0], v[:, 1])
        self.assertEqual(len(v), Meshfigurtexeldetail.VERSAETZE)
        self.assertGreaterEqual(float(weite.min()), Meshfigurtexeldetail.NAHE_PX - 1.5)
        self.assertLessEqual(float(weite.max()), Meshfigurtexeldetail.FERNE_PX + 1.5)


class VerdrahtungTest(unittest.TestCase):
    def test_die_pruefung_ruft_die_uebertragung(self):
        quelle = (Path(__file__).resolve().parents[2] / 'dienste' / 'meshfigurtexelpruefung.py').read_text(encoding='utf-8')
        self.assertIn('Meshfigurtexeldetail(self.abtastung.seite, self.glatt).anwenden(drin, ziel, gut, farbe, fuellung) if self.DETAIL_UEBERTRAGEN', quelle)
        self.assertTrue(Meshfigurtexelpruefung.DETAIL_UEBERTRAGEN, 'seit 14.10.2026 Vorgabe an')
        self.assertLess(quelle.index('Meshfigurtexeldetail(self.abtastung.seite'), quelle.index('farbe[ziel] = fuellung[ziel]'), 'die Zeichnung kommt vor dem Schreiben der Füllung')


if __name__ == '__main__':
    unittest.main()
