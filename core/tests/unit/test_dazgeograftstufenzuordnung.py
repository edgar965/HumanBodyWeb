# -*- coding: utf-8 -*-
"""`Dazgeograftstufenzuordnung` — welcher Punkt der Stufe 2 ist welcher der Stufe 1 (11.10.2026), an Kunstpunkten, ohne Daz-Bibliothek.

Der Kern: `Dazgeograft.nahtfrei` sortiert die Punkte nach der Lage, die Nummer im Stück ist also NICHT die Rohnummer der Unterteilung. Die Zuordnung rechnet deshalb über die Rohnummer
(Punkt der groben Stufe → Rohnummer → derselbe Rohpunkt in der feinen Stufe → sein Punkt im Stück).

Kunstdaten: 6 grobe Rohpunkte (einer doppelt, wie an einer UV-Naht), die feine Stufe hat sie an denselben Rohnummern (um bis zu 0,3 mm verschoben, wie die Glättung der Unterteilung) und 10 weitere.

1. Jeder Punkt der groben Stufe findet seinen Punkt in der feinen — die Lage stimmt auf 1 mm, alle Ziele sind verschieden. Mit „gleicher Nummer" stimmt sie NICHT (das ist der Grund der Klasse).
2. Eine Naht-Kopie in der groben Stufe zählt als ein Punkt.
3. `_stufe_mit` nimmt bis zu `SCHWANZ_FEHLER` Punkte weniger an (Punkt auf einer Ringecke), mehr nicht.
4. Ist das „grobe" Stück nicht gröber, bricht die Rechnung ab.
5. Liegen die Punkte nicht an denselben Nummern (anderer Käfig), bricht die Rechnung ab.
"""
from types import SimpleNamespace

import numpy as np
from django.test import SimpleTestCase

from core.dienste.dazgeograft import Dazgeograft
from core.dienste.dazgeograftstufenzuordnung import Dazgeograftstufenzuordnung


class DazgeograftstufenzuordnungTest(SimpleTestCase):
    databases = set()

    @staticmethod
    def _nahtfrei(roh):
        return Dazgeograft.nahtfrei(SimpleNamespace(LAGE_M=Dazgeograft.LAGE_M), roh)

    def _stufen(self, verschiebung=0.0):
        """`{1: (roh, erste, rep), 2: (…)}` — die feine Stufe um `verschiebung` (m) in x verschoben (anderer Käfig)."""
        zufall = np.random.default_rng(11)
        grob = zufall.uniform(-0.05, 0.05, (5, 3))
        grob = np.vstack([grob, grob[1:2]])                                       # Rohpunkt 5 ist die Naht-Kopie von 1
        fein = np.vstack([grob + zufall.uniform(-0.0003, 0.0003, grob.shape), zufall.uniform(-0.05, 0.05, (10, 3))])
        fein[5] = fein[1]                                                           # dieselbe Naht-Kopie in der feinen Stufe
        fein[:, 0] += verschiebung
        return {1: (grob, *self._nahtfrei(grob)), 2: (fein, *self._nahtfrei(fein))}

    def test_1_jeder_grobe_punkt_findet_sein_gegenstueck(self):
        stufen = self._stufen()
        roh_g, erste_g, _ = stufen[1]
        roh_f, erste_f, _ = stufen[2]
        zu = Dazgeograftstufenzuordnung.aus_stufen(stufen, len(erste_g), len(erste_f))
        abstand = np.linalg.norm(roh_f[erste_f][zu] - roh_g[erste_g], axis=1) * 1000
        self.assertLess(abstand.max(), 1.0, 'über die Rohnummer liegen die Paare auf dem Millimeter')
        gleiche_nummer = np.linalg.norm(roh_f[erste_f][:len(erste_g)] - roh_g[erste_g], axis=1) * 1000
        self.assertGreater(gleiche_nummer.max(), 10.0, 'mit der gleichen Nummer im Stück läge mindestens ein Paar Zentimeter daneben (sortiert nach Lage)')

    def test_2_eine_naht_kopie_zaehlt_als_ein_punkt(self):
        stufen = self._stufen()
        zu = Dazgeograftstufenzuordnung.aus_stufen(stufen, len(stufen[1][1]), len(stufen[2][1]))
        self.assertEqual(len(zu), 5, 'fünf Punkte nach dem Verschweißen (der Rohpunkt 5 ist eine Naht-Kopie)')
        self.assertEqual(len(np.unique(zu)), 5, 'jedes Ziel nur einmal')

    def test_3_bis_zu_drei_punkte_weniger_zaehlen_noch_als_dieselbe_stufe(self):
        stufen = {1: (None, np.arange(4211), None), 2: (None, np.arange(16741), None)}
        for anzahl, erwartet in ((4211, 1), (4210, 1), (4208, 1), (16741, 2), (16739, 2)):
            self.assertEqual(Dazgeograftstufenzuordnung._stufe_mit(stufen, anzahl), erwartet, anzahl)
        for anzahl in (4207, 4212, 12000, 16742):
            with self.assertRaises(ValueError, msg=anzahl):
                Dazgeograftstufenzuordnung._stufe_mit(stufen, anzahl)

    def test_4_ein_gleich_feines_oder_groeberes_stueck_ist_keine_zuordnung(self):
        stufen = self._stufen()
        with self.assertRaises(ValueError) as fehler:
            Dazgeograftstufenzuordnung.aus_stufen(stufen, len(stufen[2][1]), len(stufen[1][1]))
        self.assertIn('nicht feiner', str(fehler.exception))

    def test_5_andere_lage_der_stufen_bricht_ab(self):
        stufen = self._stufen(verschiebung=0.02)                                    # 20 mm daneben: anderer Käfig
        with self.assertRaises(ValueError) as fehler:
            Dazgeograftstufenzuordnung.aus_stufen(stufen, len(stufen[1][1]), len(stufen[2][1]))
        self.assertIn('nicht an denselben Nummern', str(fehler.exception))
