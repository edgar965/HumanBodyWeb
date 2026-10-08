# -*- coding: utf-8 -*-
"""Mesh to 3D, 07.10.2026: die Mindestluft unter dem Stoff (Option `kleidungsluft_mm`) und das Körper-Tor mit dünn besetztem Figurschnitt.

Anlass 1 (Ten24-Lauf): Haut der Figur schien durch die Kleidung des Scans (359 Punkte außerhalb der Kleiderfläche, 80 über 3 mm) — der Rest-Schritt schob solche Punkte nur bis auf die
Oberfläche. Anlass 2 (Auftrag „Edgar - Hunyan"): Das Tor `Meshfigurrumpfpruefung` hielt den Lauf an („Rumpf 1 % so tief wie das Netz"), weil bei 0,55 der Höhe nur 8 Figurpunkte im Streifen lagen,
alle auf einer Seite des Rumpfes. Kunstdaten; die Sabotage-Gegenprobe steht in den Fällen (FIGUR_MINDESTENS = 0 stellt das alte Verhalten her).
"""

import unittest

import numpy as np

from core.dienste.meshfiguroptionen import Meshfiguroptionen

from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()


def _rumpf(abstand_ringe, tiefe=0.24, breite=0.34, punkte_je_ring=96):
    """Ein Zylinder (Ellipse `breite` × `tiefe`, Achse y) aus Ringen im Abstand `abstand_ringe` — der Käfig ist dünn besetzt.

    96 Punkte je Ring (gemessen 08.10.2026, `ProjektTemp/_wegwerf/cutegirl/rumpf_diag.py`): von einem Ring mit 48 liegen nur etwa 7 im Streifen `STREIFEN` (±4 cm um die Mitte) — unter `PUNKTE_MIN`
    (8); mit 96 sind es etwa 14, und ein einzelner Ring im Schnitt reicht für die Messung."""
    punkte = []
    for y in np.arange(0.0, 1.7, abstand_ringe):
        w = np.linspace(0, 2 * np.pi, punkte_je_ring, endpoint=False)
        punkte.append(np.c_[np.cos(w) * breite / 2, np.full(len(w), y), np.sin(w) * tiefe / 2])
    return np.concatenate(punkte)


def _netz(tiefe=0.27, breite=0.37):
    """Dicht abgetastete Netzproben desselben Rumpfes (etwas dicker)."""
    z = np.random.default_rng(3)
    w = z.uniform(0, 2 * np.pi, 80_000)
    y = z.uniform(0, 1.7, 80_000)
    return np.c_[np.cos(w) * breite / 2, y, np.sin(w) * tiefe / 2]


class RumpfpruefungTest(unittest.TestCase):
    def _tiefen(self, figur, mindestens):
        from meshfigur_rumpfpruefung import Meshfigurrumpfpruefung as P

        alt = P.FIGUR_MINDESTENS
        P.FIGUR_MINDESTENS = mindestens
        try:
            return P(figur, _netz()).tiefen()
        finally:
            P.FIGUR_MINDESTENS = alt

    def test_ein_duenner_kaefig_wird_mit_dickerem_schnitt_gemessen(self):
        """Ringe im Abstand 5 cm: ein Schnitt von ±6 mm trifft mal einen Ring, mal keinen — mit wachsender Dicke bekommt jede Höhe Punkte und die Tiefe stimmt."""
        figur = _rumpf(0.05)
        werte = [t['verhaeltnis'] for t in self._tiefen(figur, 250) if t['verhaeltnis'] is not None]
        self.assertEqual(len(werte), 4, 'jede der vier Höhen ist messbar')
        for v in werte:
            self.assertGreater(v, 0.85)
            self.assertLess(v, 1.0)

    def test_sabotage_ohne_wachsende_dicke_sind_weniger_hoehen_messbar(self):
        """FIGUR_MINDESTENS = 0 ist das Verhalten vor dem 07.10.2026: Der Schnitt bleibt ±6 mm — bei diesem Käfig (Ringe alle 5 cm, Höhen 0,9075 / 1,023 / 1,155 / 1,254 m) liegt bei den ersten zwei
        kein Ring darin (Ringe bei 0,90 und 1,00/1,05: 7,5 bis 27 mm daneben), die Höhe ist nicht messbar. (Am echten Lauf traf der Schnitt bei 0,55 acht Punkte einer Seite: Tiefe 4 mm.) Mit wachsender Dicke sind alle vier messbar."""
        figur = _rumpf(0.05)
        alt = [t['verhaeltnis'] for t in self._tiefen(figur, 0) if t['verhaeltnis'] is not None]
        neu = [t['verhaeltnis'] for t in self._tiefen(figur, 250) if t['verhaeltnis'] is not None]
        self.assertLess(len(alt), len(neu))
        self.assertEqual(len(neu), 4)
        self.assertGreaterEqual(min(neu), 0.85)

    def test_ein_dicht_besetzter_schnitt_bleibt_bei_der_alten_dicke(self):
        """Hat der Schnitt schon genug Punkte, ändert sich nichts: `_schnitt` liefert dieselbe Auswahl mit und ohne Mindestzahl."""
        from meshfigur_rumpfpruefung import Meshfigurrumpfpruefung as P

        figur = _rumpf(0.002)
        pruefer = P(figur, _netz())
        a = pruefer._schnitt(figur, 0.85)
        b = pruefer._schnitt(figur, 0.85, 250)
        self.assertEqual(len(a), len(b))


class UntergrenzeTest(unittest.TestCase):
    """`G9restmorph.untergrenze`: nach dem Glätten behält ein Punkt unter Stoff mindestens seinen Weg nach innen (Ten24: 359 → 25 Punkte außerhalb der Kleiderfläche).
    Sabotage-Gegenprobe: die Zeile `feld[aktiv] += …` entfernen → `test_der_weg_wird_wiederhergestellt` muss rot werden."""

    def test_der_weg_wird_wiederhergestellt(self):
        from Genesis9.restmorph import G9restmorph

        feld = np.zeros((4, 3))
        feld[0] = [0.0, 0.0, -0.001]            # das Glätten hat von 4 mm nur 1 mm übrig gelassen
        mindest = np.zeros((4, 3))
        mindest[0] = [0.0, 0.0, -0.004]
        neu, n = G9restmorph.untergrenze(feld, mindest)
        self.assertEqual(n, 1)
        self.assertAlmostEqual(neu[0, 2], -0.004)
        self.assertTrue((neu[1:] == 0).all(), 'Punkte ohne Mindestweg bleiben, wie das Glätten sie ließ')
        self.assertAlmostEqual(feld[0, 2], -0.001, msg='das Eingabefeld wird nicht verändert')

    def test_ein_groesserer_weg_bleibt(self):
        from Genesis9.restmorph import G9restmorph

        feld = np.array([[0.0, 0.0, -0.006], [0.0, 0.002, 0.0]])
        mindest = np.array([[0.0, 0.0, -0.004], [0.0, 0.0, 0.0]])
        neu, n = G9restmorph.untergrenze(feld, mindest)
        self.assertEqual(n, 1)
        np.testing.assert_allclose(neu, feld)

    def test_ohne_mindestweg_aendert_sich_nichts(self):
        from Genesis9.restmorph import G9restmorph

        feld = np.random.default_rng(1).normal(size=(10, 3)) * 0.001
        neu, n = G9restmorph.untergrenze(feld, np.zeros((10, 3)))
        self.assertEqual(n, 0)
        np.testing.assert_array_equal(neu, feld)


class KleidungsluftOptionTest(unittest.TestCase):
    def test_vorgabe_null_und_grenzen(self):
        katalog = {e['schluessel']: e for e in Meshfiguroptionen.katalog()['optionen']}
        self.assertIn('kleidungsluft_mm', katalog)
        self.assertEqual(katalog['kleidungsluft_mm']['vorgabe'], 0)
        self.assertTrue(katalog['kleidungsluft_mm']['fein'])
        self.assertEqual(Meshfiguroptionen.pruefen({})['kleidungsluft_mm'], 0)
        self.assertEqual(Meshfiguroptionen.pruefen({'kleidungsluft_mm': 4})['kleidungsluft_mm'], 4)
        self.assertEqual(Meshfiguroptionen.pruefen({'kleidungsluft_mm': 99})['kleidungsluft_mm'], 20)      # Zahlen werden geklemmt
        self.assertEqual(Meshfiguroptionen.pruefen({'kleidungsluft_mm': 'x'})['kleidungsluft_mm'], 0)

    def test_die_luft_steht_hinter_dem_abstand_und_vor_der_genitalform(self):
        schluessel = [e['schluessel'] for e in Meshfiguroptionen.katalog()['optionen']]
        self.assertEqual(schluessel.index('kleidungsluft_mm'), schluessel.index('kleidungsabstand_mm') + 1)
        self.assertEqual(schluessel.index('genitalform'), schluessel.index('kleidungsluft_mm') + 1)

    def test_der_runner_reicht_sie_an_den_abstand_weiter(self):
        """Die Kette ist erst dicht, wenn die letzte Schicht sie liest (`meshfigur.md`): Runner → `Meshfigurabstand(kleidung_luft)` → `ruhe_rest`."""
        from pathlib import Path

        wrapper = Path(__file__).resolve().parents[4] / 'VideoToBVH' / 'wrappers'
        runner = (wrapper / '_run_meshfigur.py').read_text(encoding='utf-8')
        abstand = (wrapper / 'meshfigur_abstand.py').read_text(encoding='utf-8')
        rest = (wrapper / 'meshfigur_registrierung.py').read_text(encoding='utf-8')
        self.assertIn("kleidung_luft=float(self.daten.optionen.get('kleidungsluft_mm') or 0) / 1000.0", runner)
        self.assertIn('self.luft = float(kleidung_luft)', abstand)
        self.assertIn('torch.relu(r + self.abstand.luft) * passt', rest)


if __name__ == '__main__':
    unittest.main()
