# -*- coding: utf-8 -*-
"""`Meshfigurhandmass` (14.10.2026, Edgar1: „Hände … sind etwas kleiner als das Mesh“): der Regler `body_ctrl_ProportionHandSize` gleicht die Länge der Figurhand an die der Netzhand an — nur bei einer offenen Hand im Netz.

Kunstdaten: die Handpunkte liegen auf einer Geraden mit etwas Streuung; die Figurhand ist 18,3 cm lang und wächst mit dem Regler um 47 % je Einheit (gemessen `handregler_eichen.py`), die Netzhände sind 19,7 und 20,4 cm lang (Edgar3).
Sabotage-Gegenproben: `PLAUSIBEL = (0, 99)` → `test_eine_faust_im_netz_laesst_die_hand_der_figur_wie_sie_ist` rot; die `np.clip(…)` auf `GRENZE` streichen → `test_der_regler_bleibt_in_seinem_rahmen` rot.
"""

import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import numpy as np

from core.dienste.meshfigurhandmass import Meshfigurhandmass


def _hand(laenge, zufall=0):
    """Handpunkte mit der angegebenen (nominellen) Länge entlang der x-Achse."""
    rng = np.random.default_rng(zufall)
    x = np.linspace(0.0, laenge, 400)
    return np.c_[x, rng.normal(0, 0.01, len(x)), rng.normal(0, 0.01, len(x))]


def _figur(stellung):
    """Die Käfighände einer Stellung: 18,3 cm bei Regler 0, +47 % je Einheit."""
    faktor = 1.0 + 0.47 * float(stellung.get(Meshfigurhandmass.REGLER, 0.0))
    return [_hand(0.183 * faktor, 1), _hand(0.183 * faktor, 2)]


class HandmassTest(unittest.TestCase):
    def _anwenden(self, netz_laengen, stellung=None, optionen=None):
        stellung = {} if stellung is None else stellung
        job = SimpleNamespace(kennung='test', ergebnis={}, optionen=optionen or {})
        lauf = SimpleNamespace(job=job, ablage=None)
        masse = Meshfigurhandmass(lauf)
        with mock.patch.object(Meshfigurhandmass, 'haende_im_netz', lambda self: [_hand(x, 3 + i) for i, x in enumerate(netz_laengen)]), \
                mock.patch.object(Meshfigurhandmass, 'figurhand', staticmethod(_figur)):
            bericht = masse.anwenden(stellung)
        return bericht, stellung

    def test_die_figurhand_wird_so_lang_wie_die_netzhand(self):
        bericht, stellung = self._anwenden([0.197, 0.204])
        self.assertGreater(stellung[Meshfigurhandmass.REGLER], 0.15)
        self.assertLess(stellung[Meshfigurhandmass.REGLER], 0.30)
        self.assertAlmostEqual(bericht['figur_nachher_cm'], 20.05 * 0.96, delta=0.5)           # nominell 20,05 cm, die Perzentile messen 96 % davon
        self.assertAlmostEqual(bericht['faktor'], 1.099, delta=0.02)

    def test_ein_vorhandener_reglerwert_geht_ein(self):
        bericht, stellung = self._anwenden([0.197, 0.204], {Meshfigurhandmass.REGLER: 0.1})
        self.assertEqual(bericht['regler_vorher'], 0.1)
        self.assertAlmostEqual(bericht['figur_nachher_cm'], 20.05 * 0.96, delta=0.5, msg='auch von einem anderen Startwert aus gleich lang')

    def test_eine_faust_im_netz_laesst_die_hand_der_figur_wie_sie_ist(self):
        bericht, stellung = self._anwenden([0.118, 0.12])
        self.assertNotIn(Meshfigurhandmass.REGLER, stellung)
        self.assertIn('hinweis', bericht)

    def test_ist_eine_hand_keine_offene_hand_gilt_keine(self):
        """Die eine Hand ist offen, die andere eine Faust oder im Ärmel (Ballerina 1,26 gegen 1,15): die Messung der anderen ist dann auch unsicher."""
        bericht, stellung = self._anwenden([0.20, 0.118])
        self.assertNotIn(Meshfigurhandmass.REGLER, stellung)
        self.assertEqual(len(bericht['verhaeltnis']), 2)
        self.assertIn('hinweis', bericht)

    def test_zwei_uneinige_haende_aendern_nichts(self):
        bericht, stellung = self._anwenden([0.197, 0.215])                      # 1,077 gegen 1,175: 8,7 % auseinander
        self.assertNotIn(Meshfigurhandmass.REGLER, stellung)
        self.assertIn('verschieden lang', bericht['hinweis'])

    def test_eine_einzige_hand_im_netz_genuegt(self):
        _, stellung = self._anwenden([0.20])
        self.assertGreater(stellung[Meshfigurhandmass.REGLER], 0.1)

    def test_der_regler_bleibt_in_seinem_rahmen(self):
        with mock.patch.object(Meshfigurhandmass, 'PLAUSIBEL', (0.5, 5.0)):
            _, stellung = self._anwenden([0.60, 0.60])
        self.assertLessEqual(stellung[Meshfigurhandmass.REGLER], Meshfigurhandmass.GRENZE)

    def test_ohne_hand_im_netz_passiert_nichts(self):
        bericht, stellung = self._anwenden([])
        self.assertIn('hinweis', bericht)
        self.assertEqual(stellung, {})

    def test_die_option_aus_schaltet_ab(self):
        bericht, stellung = self._anwenden([0.20, 0.20], optionen={'handmass': 'aus'})
        self.assertEqual(bericht, {'aus': True})
        self.assertEqual(stellung, {})

    def test_sicher_wirft_nie(self):
        job = SimpleNamespace(kennung='test', ergebnis={}, optionen={})
        lauf = SimpleNamespace(job=job, ablage=None)
        with mock.patch.object(Meshfigurhandmass, 'anwenden', side_effect=RuntimeError('kaputt')):
            bericht = Meshfigurhandmass.sicher(lauf, {})
        self.assertIn('kaputt', bericht['fehler'])
        self.assertIs(job.ergebnis['handmass'], bericht)

    def test_laenge_ist_die_ausdehnung_entlang_der_hauptachse(self):
        self.assertAlmostEqual(Meshfigurhandmass.laenge(_hand(0.2)), 0.2 * 0.96, delta=0.004)
        gedreht = _hand(0.2) @ np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]], dtype=float)
        self.assertAlmostEqual(Meshfigurhandmass.laenge(gedreht), Meshfigurhandmass.laenge(_hand(0.2)), places=6)


class VerdrahtungTest(unittest.TestCase):
    def test_die_koerperkette_ruft_das_handmass_vor_dem_ablegen_der_stellung(self):
        quelle = (Path(__file__).resolve().parents[2] / 'dienste' / 'meshfigurkette.py').read_text(encoding='utf-8')
        self.assertIn('Meshfigurhandmass.sicher(self.lauf, stellung)', quelle)
        self.assertLess(quelle.index('Meshfigurhandmass.sicher(self.lauf, stellung)'), quelle.index("self.job.ergebnis['koerper'] = {'runden': verlauf"))


if __name__ == '__main__':
    unittest.main()
