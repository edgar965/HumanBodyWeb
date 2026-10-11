# -*- coding: utf-8 -*-
"""`Dazgeograftmorphbasis` — die Regler `sch_*` vom angepassten Daz-Stück auf das Basis-Stück übertragen: die Zuordnung der Punkte (11.10.2026), an Kunststücken, ohne Garderobe und Daz.

Befund: die alte Zuordnung nahm die Dreiecke Ecke für Ecke und verlangte, dass 85 % der Dreiecke dieselben Punktnummern tragen. Das war Zufall — die Naht (`Blendimportschamnaht._einfuegen`) ersetzt ein
Dreieck durch mehrere und verschiebt damit die Dreiecksnummern danach: bei Nachformung 0,2 stimmten 90,5 %, bei 0 und 0,4 nur 45–46 %, und die Zuordnung gab je Basis-Punkt bis zu neun Partner (Spanne
bis 140 mm). Die Punkte der Stufe 1 haben dagegen in beiden Stücken dieselbe Nummer; die Naht hängt nur die fehlenden Ringecken hinten an.

Kunststücke: ein Gitter 9 × 9 Punkte (Stufe 1, 81 Punkte); das Basis-Stück hängt 3, das angepasste 8 Ringecken an (sie liegen auf dem Ring), das angepasste hat die Dreiecke in anderer Reihenfolge.

1. `_stufe_punkte` zählt die Punkte vor dem Schwanz aus Ringecken (81), gleich wie lang er ist; ein Stufe-1-Punkt MITTEN im Stück, der auf einer Ringecke liegt, zählt weiter mit.
2. Ohne Ring im Stück (kein Loch) ist es ein `ValueError`: keine Naht, keine Zuordnung.
3. Die Zuordnung ist `Punkt i ↔ Punkt i` für alle Stufe-1-Punkte, die angehängten Ringecken des Basis-Stücks haben kein Gegenstück (−1) — auch wenn die Dreiecke in anderer Reihenfolge stehen.
4. Tragen die Punkte nicht gleich viele Dreiecke (anders vernetzt), bricht die Klasse ab: es ist nicht dasselbe Geograft.

Sabotage-Gegenprobe (nicht gelaufen): in `__init__` `self.zu[:self.stufe] = np.arange(self.stufe)` durch die Ecke-für-Ecke-Zuordnung ersetzen macht Fall 3 rot (andere Dreiecksfolge); `LAGE_M` auf 1 stellen macht Fall 1 rot.
"""
from types import SimpleNamespace
from unittest import mock

import numpy as np
from django.test import SimpleTestCase

from core.dienste.dazgeograftmorphbasis import Dazgeograftmorphbasis


class DazgeograftmorphbasisTest(SimpleTestCase):
    databases = set()

    K = 9
    RING = np.array([[0.100 + 0.001 * j, 0.100, 0.0] for j in range(8)])

    def _gitter(self, andere_diagonale=False):
        k = self.K
        punkte = np.array([[(i - 4) * 0.004, (j - 4) * 0.004, 0.0] for j in range(k) for i in range(k)])
        dreiecke = []
        for j in range(k - 1):
            for i in range(k - 1):
                a = j * k + i
                schachbrett = andere_diagonale and (i + j) % 2 == 0          # abwechselnde Diagonalen: die Punkte tragen 4 oder 8 statt 6 Dreiecke
                dreiecke += [[a, a + 1, a + k], [a + 1, a + k + 1, a + k]] if schachbrett else [[a, a + 1, a + k + 1], [a, a + k + 1, a + k]]
        return punkte, np.array(dreiecke)

    def _stueck(self, angehaengt, umordnen=False, andere_diagonale=False):
        """`(teile, kaefige, y0, y1, mitte, eintrag)` wie `G9kleidmorphe.kaefige`: das Gitter plus `angehaengt` Ringecken; acht Dreiecke an den Gitterpunkten 0 und 1 verbinden sie
        (immer acht, so wie beide echten Stücke 8.320 Dreiecke haben, gleich wie viele Ecken die Naht eingefügt hat)."""
        punkte, dreiecke = self._gitter(andere_diagonale)
        n0 = len(punkte)
        punkte = np.vstack([punkte, self.RING[:angehaengt]])
        if angehaengt:
            dreiecke = np.vstack([dreiecke, [[n0 + j % angehaengt, 0, 1] for j in range(8)]])
        if umordnen:
            dreiecke = dreiecke[np.random.default_rng(5).permutation(len(dreiecke))]
        teil = SimpleNamespace(polys=[[0, 0, int(a), int(b), int(c)] for a, b, c in dreiecke], kennung='x')
        return [(teil, None)], [punkte], 0.0, 1.0, np.zeros(3), {'ring': self.RING.tolist()}

    def _bauen(self, basis, angepasst):
        def kaefige(kennung):
            return basis if kennung == 'basis' else angepasst

        with mock.patch('Genesis9.kleidmorphe.G9kleidmorphe.kaefige', side_effect=kaefige), mock.patch('Genesis9.stueckersatz.G9stueckersatz.loch_fuer', side_effect=self._loch_fuer), \
                mock.patch('Genesis9.schammorphe.G9schammorphe.normalen', return_value=np.zeros((1, 3))):
            return Dazgeograftmorphbasis('angepasst', 'basis')

    @staticmethod
    def _loch_fuer(eintrag):
        return {'ring': {'lage': eintrag['ring']}} if eintrag.get('ring') else {}

    def test_1_der_schwanz_aus_ringecken_wird_abgezaehlt(self):
        with mock.patch('Genesis9.stueckersatz.G9stueckersatz.loch_fuer', side_effect=self._loch_fuer):
            for angehaengt in (0, 3, 8):
                _teile, kaefige, _y0, _y1, _m, eintrag = self._stueck(angehaengt)
                self.assertEqual(Dazgeograftmorphbasis._stufe_punkte(kaefige[0], eintrag), 81, '%d angehängt' % angehaengt)
            _teile, kaefige, _y0, _y1, _m, eintrag = self._stueck(3)
            mitten = kaefige[0].copy()
            mitten[20] = self.RING[4]                                # ein Stufe-1-Punkt mitten im Stück liegt auf einer Ringecke
            self.assertEqual(Dazgeograftmorphbasis._stufe_punkte(mitten, eintrag), 81)
            mit_ende = kaefige[0].copy()
            mit_ende[80] = self.RING[2]                              # der LETZTE Stufe-1-Punkt liegt auf einer Ringecke: er zählt zum Schwanz (bekannt, ein Punkt)
            self.assertEqual(Dazgeograftmorphbasis._stufe_punkte(mit_ende, eintrag), 80)

    def test_2_ohne_ring_gibt_es_keine_zuordnung(self):
        _teile, kaefige, _y0, _y1, _m, _eintrag = self._stueck(3)
        with mock.patch('Genesis9.stueckersatz.G9stueckersatz.loch_fuer', return_value={}), self.assertRaises(ValueError):
            Dazgeograftmorphbasis._stufe_punkte(kaefige[0], {})

    def test_3_die_zuordnung_ist_punkt_i_zu_punkt_i_auch_bei_anderer_dreiecksfolge(self):
        b = self._bauen(self._stueck(3), self._stueck(8, umordnen=True))
        self.assertEqual(b.stufe, 81)
        self.assertEqual(b.zu[:81].tolist(), list(range(81)))
        self.assertEqual(b.zu[81:].tolist(), [-1, -1, -1], 'die angehängten Ringecken des Basis-Stücks haben kein Gegenstück')
        self.assertGreaterEqual(b.gleich, 0.95, 'nur die zwei Gitterpunkte, an die die Ringecken gebunden sind, tragen verschieden viele Dreiecke')

    def test_4_andere_vernetzung_ist_nicht_dasselbe_geograft(self):
        with self.assertRaises(ValueError) as fehler:
            self._bauen(self._stueck(3), self._stueck(8, andere_diagonale=True))
        self.assertIn('gleich viele Dreiecke', str(fehler.exception))
