# -*- coding: utf-8 -*-
"""Körper-Tor, 08.10.2026: Regler am Anschlag, die nur in abgewerteten Zonen wirken, zählen nicht (`Meshfigurrumpfpruefung.ausnahmen`).

Anlass (Hunyuan-Lauf „Hunyan-Best", TRELLIS-Lauf „Edgar - Trellis 1536"): je 9 Regler am Anschlag, Rumpftiefe 85–98 %. Gemessen an der Ableitung des Laufs lag von den 9 nur `MassHands` (99,8 %) in Zonen, die die Anpassung
unter Gewicht 1 setzt (Hand 0,1, Finger 0, Zehen 0,3 …); `MassWrist` 10,6 %, die Fuß-, Knöchel- und Halsregler 0–12,5 % — die wirken auf Haut mit vollem Gewicht und zählen weiter. Kunstdaten; Sabotage-Gegenprobe:
`SCHWACH_ANTEIL` über 1 setzen (nichts wird mehr ausgenommen) → `test_ein_schwacher_regler_wird_nicht_gezaehlt` muss rot werden.
"""

import unittest

import numpy as np

from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()


class _T:
    """Ein Tensor, soweit die Prüfung ihn liest: `detach().cpu().numpy()`."""

    def __init__(self, a):
        self.a = np.asarray(a)

    def detach(self):
        return self

    def cpu(self):
        return self

    def numpy(self):
        return self.a


class _JP:
    def __init__(self, a):
        self.a = np.asarray(a)

    def __getitem__(self, stelle):
        return _T(self.a[stelle])


class _Modell:
    """K Regler, alle aktiv und am oberen Anschlag (Δ = 1 bei Grenze 1), vom Grundwert weggelaufen."""

    def __init__(self, verschiebung):
        k = len(verschiebung)
        self.namen = ['regler_%d' % i for i in range(k)]
        self.jp = _JP(verschiebung)
        self.dx = _T(np.ones(k))
        self.unten, self.oben = _T(-np.ones(k)), _T(np.ones(k))
        self.aktiv = _T(np.ones(k, dtype=bool))
        self.x_jetzt, self.x_grund = _T(np.zeros(k)), _T(np.zeros(k))


def _rumpf(tiefe=0.24, breite=0.34):
    """Zylinder (Achse y) aus Ringen alle 2 cm — dicht genug für die Tiefenmessung."""
    ringe = []
    for y in np.arange(0.0, 1.7, 0.02):
        w = np.linspace(0, 2 * np.pi, 48, endpoint=False)
        ringe.append(np.c_[np.cos(w) * breite / 2, np.full(len(w), y), np.sin(w) * tiefe / 2])
    return np.concatenate(ringe)


def _netz(tiefe=0.27, breite=0.37):
    z = np.random.default_rng(3)
    w, y = z.uniform(0, 2 * np.pi, 60_000), z.uniform(0, 1.7, 60_000)
    return np.c_[np.cos(w) * breite / 2, y, np.sin(w) * tiefe / 2]


def _verschiebungen(zonen, wirkung_schwach):
    """(K, N, 3): Regler k wirkt zu `wirkung_schwach[k]` in den Punkten mit Gewicht < 1, der Rest in den Punkten mit Gewicht 1 (gleiche Energie je Regler)."""
    schwach, voll = zonen < 1.0, zonen >= 1.0
    aus = np.zeros((len(wirkung_schwach), len(zonen), 3))
    for k, anteil in enumerate(wirkung_schwach):
        aus[k, schwach, 0] = np.sqrt(anteil / schwach.sum())
        aus[k, voll, 0] = np.sqrt((1.0 - anteil) / voll.sum())
    return aus


ZONEN = np.array([1.0] * 80 + [0.1] * 20)           # 20 Punkte der Hand (Gewicht 0,1), 80 Haut


class TorAnschlagTest(unittest.TestCase):
    def _pruefer(self, zonen=ZONEN):
        from meshfigur_rumpfpruefung import Meshfigurrumpfpruefung as P

        return P(_rumpf(), _netz(), zonen)

    def test_anteile_in_abgewerteten_zonen(self):
        from meshfigur_rumpfpruefung import Meshfigurrumpfpruefung as P

        a = P.schwache_anteile(_verschiebungen(ZONEN, [1.0, 0.0, 0.5]), ZONEN)
        np.testing.assert_allclose(a, [1.0, 0.0, 0.5], atol=1e-9)

    def test_ein_regler_ohne_wirkung_hat_den_anteil_null(self):
        from meshfigur_rumpfpruefung import Meshfigurrumpfpruefung as P

        self.assertEqual(float(P.schwache_anteile(np.zeros((1, 100, 3)), ZONEN)[0]), 0.0)

    def test_ausnahmen_ab_dem_halben_anteil(self):
        modell = _Modell(_verschiebungen(ZONEN, [0.998, 0.106, 0.51, 0.49]))
        aus = self._pruefer().ausnahmen(modell, modell.namen)
        self.assertEqual(sorted(aus), ['regler_0', 'regler_2'])          # 99,8 % und 51 % (nicht 10,6 % und 49 %)
        self.assertAlmostEqual(aus['regler_0'], 0.998, places=3)

    def test_ohne_zonengewicht_zaehlt_jeder_regler(self):
        modell = _Modell(_verschiebungen(ZONEN, [1.0, 1.0]))
        self.assertEqual(self._pruefer(zonen=None).ausnahmen(modell, modell.namen), {})

    def test_ein_schwacher_regler_wird_nicht_gezaehlt(self):
        """9 Regler am Anschlag, einer davon nur an der Hand: 8 zählen, das Tor bleibt offen. Mit 10 am Anschlag (einer davon an der Hand) sind es 9 > 8 → zu."""
        modell = _Modell(_verschiebungen(ZONEN, [1.0] + [0.0] * 8))
        e = self._pruefer().pruefen(modell)
        self.assertEqual((e['anschlag_zahl'], e['anschlag_gezaehlt']), (9, 8))
        self.assertEqual(list(e['anschlag_ausgenommen']), ['regler_0'])
        self.assertTrue(e['gueltig'], e['grund'])
        zehn = _Modell(_verschiebungen(ZONEN, [1.0] + [0.0] * 9))
        e = self._pruefer().pruefen(zehn)
        self.assertFalse(e['gueltig'])
        self.assertIn('9 Regler am Anschlag (Soll ≤ 8) (10 am Anschlag, 1 in abgewerteten Zonen nicht gezählt)', e['grund'])

    def test_sabotage_ohne_ausnahme_waere_das_tor_zu(self):
        from meshfigur_rumpfpruefung import Meshfigurrumpfpruefung as P

        alt = P.SCHWACH_ANTEIL
        P.SCHWACH_ANTEIL = 2.0
        try:
            e = self._pruefer().pruefen(_Modell(_verschiebungen(ZONEN, [1.0] + [0.0] * 8)))
        finally:
            P.SCHWACH_ANTEIL = alt
        self.assertEqual(e['anschlag_gezaehlt'], 9)
        self.assertFalse(e['gueltig'])

    def test_die_rumpftiefe_gilt_weiter(self):
        """Die Ausnahme betrifft nur die Zählung: ein zu flacher Rumpf hält das Tor zu."""
        from meshfigur_rumpfpruefung import Meshfigurrumpfpruefung as P

        modell = _Modell(_verschiebungen(ZONEN, [0.0]))
        e = P(_rumpf(tiefe=0.10), _netz(tiefe=0.27), ZONEN).pruefen(modell)
        self.assertFalse(e['gueltig'])
        self.assertIn('so tief wie das Netz', e['grund'])

    def test_der_runner_reicht_die_zonen_durch(self):
        """Die Kette ist erst dicht, wenn die letzte Schicht sie liest: Runner → `Meshfigurrumpfpruefung(…, zonen)`."""
        from pathlib import Path

        runner = (Path(__file__).resolve().parents[4] / 'VideoToBVH' / 'wrappers' / '_run_meshfigur.py').read_text(encoding='utf-8')
        self.assertIn('Meshfigurabstand.GEWICHT.get(int(b), 1.0) for b in genesis[\'bereich\']', runner)
        self.assertIn('Meshfigurrumpfpruefung(self.posiert, self.daten.proben()[0], zonen)', runner)


if __name__ == '__main__':
    unittest.main()
