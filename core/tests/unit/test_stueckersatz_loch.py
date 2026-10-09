# -*- coding: utf-8 -*-
"""`G9stueckersatz.loch` — das Hautloch des verschweißten Scham-Stücks geht in die `.ersetzt.json` und von dort zurück.

Edgar, 09.10.2026, mit Bild: „… Schau nach, wie Genesis das mit der Nase und dem Mund macht, und mach es genau so." Das Stück bringt die
Dreiecke der Haut mit, die unter ihm entfallen (`loch`), samt Ring und Verschiebung der Ringpunkte; der Browser lässt genau diese Dreiecke
weg (`stueckloch.js`) und rückt den Rand des Stücks auf die Haut, wie sie jetzt ist (`stuecknaht.js`).

1. `schreiben(…, loch=…)` und `loch(duf)` / `loch_fuer(eintrag)` geben dasselbe zurück: Dreiecke sortiert und ohne Doppelte, `von`, die
   `verschiebung` (Punkte + `d`) und der `ring` (Lage, Punkte, `d`).
2. Ohne Angabe: `{}` — das Stück ist ein gewöhnliches Ersatzstück, der Browser rechnet das Loch selbst.
3. Unsinn wird beim Schreiben abgelehnt (Nummer ≥ `von`, negativ, Text, leer; Verschiebung mit ungleich vielen Punkten und Werten; Ring mit
   falscher Form) und beim Lesen ignoriert (`{}`), ohne dass etwas abstürzt.

Sabotage-Gegenprobe (nicht gelaufen): in `_loch_pruefen` die Prüfung `0 <= n < von` weglassen macht Fall 3 rot; `sorted(set(…))` durch
`list(…)` ersetzen macht Fall 1 rot.
"""

import json
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase
from Genesis9.stueckersatz import G9stueckersatz

from ._pruefablage import Pruefablage


class StueckersatzLochTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        gebaut = Pruefablage.ordner('loch_')
        self.ordner = Path(gebaut.__enter__())
        self.addCleanup(gebaut.__exit__, None, None, None)
        self.duf = self.ordner / 'Scham.duf'
        self.duf.write_text('{}', encoding='utf-8')

    def _eintrag(self):
        return mock.patch('Genesis9.garderobe.G9garderobe.datei', return_value=self.duf)

    LOCH = {'dreiecke': [7, 3, 3, 5], 'von': 10,
            'verschiebung': {'punkte': [2, 4], 'd': [[0.001, 0.0, -0.002], [0.0, 0.0005, 0.0]]},
            'ring': {'lage': [[0.0, 0.8, 0.0], [0.01, 0.8, 0.0], [0.0, 0.8, 0.01]], 'punkte': [4, 5, 6],
                     'd': [[0.0, 0.0, 0.0], [0.0001, 0.0, 0.0], [0.0, 0.0, 0.0002]]}}

    def test_1_loch_geht_hin_und_zurueck(self):
        pfad = G9stueckersatz.schreiben(self.duf, [], haut_tiefe_mm=30, loch=self.LOCH)
        daten = json.loads(pfad.read_text(encoding='utf-8'))
        self.assertEqual(daten['loch']['dreiecke'], [3, 5, 7])
        with self._eintrag():
            gelesen = G9stueckersatz.loch_fuer({})
        self.assertEqual(gelesen['dreiecke'], [3, 5, 7])
        self.assertEqual(gelesen['von'], 10)
        self.assertEqual(gelesen['verschiebung']['punkte'], [2, 4])
        self.assertEqual(gelesen['verschiebung']['d'][0], [0.001, 0.0, -0.002])
        self.assertEqual(gelesen['ring']['punkte'], [4, 5, 6])
        self.assertEqual(len(gelesen['ring']['lage']), 3)
        self.assertEqual(G9stueckersatz.loch(self.duf), gelesen)

    def test_2_ohne_angabe_ist_es_leer(self):
        G9stueckersatz.schreiben(self.duf, [], haut_tiefe_mm=30)
        self.assertEqual(G9stueckersatz.loch(self.duf), {})
        self.assertEqual(G9stueckersatz.loch_fuer({}), {}, 'Eintrag ohne Dateiangabe')
        G9stueckersatz.schreiben(self.duf, [], loch={})
        self.assertEqual(G9stueckersatz.loch(self.duf), {})

    def test_3_unsinn_wird_abgelehnt_und_beim_lesen_ignoriert(self):
        falsch = [
            {'dreiecke': [10], 'von': 10}, {'dreiecke': [-1], 'von': 10}, {'dreiecke': ['a'], 'von': 10},
            {'dreiecke': [True], 'von': 10}, {'dreiecke': [], 'von': 10}, {'dreiecke': [1], 'von': 0},
            {'dreiecke': [1], 'von': 10, 'verschiebung': {'punkte': [1, 2], 'd': [[0, 0, 0]]}},
            {'dreiecke': [1], 'von': 10, 'verschiebung': {'punkte': [1], 'd': [[0, 0]]}},
            {'dreiecke': [1], 'von': 10, 'verschiebung': {'punkte': [1], 'd': [[0, 0, 9.0]]}},
            {'dreiecke': [1], 'von': 10, 'ring': {'lage': [[0, 0, 0]], 'punkte': [1, 2], 'd': [[0, 0, 0]]}},
            {'dreiecke': [1], 'von': 10, 'ring': {'lage': [[0, 0]], 'punkte': [1], 'd': [[0, 0, 0]]}},
        ]
        for roh in falsch:
            with self.subTest(roh=str(roh)[:60]):
                with self.assertRaises(ValueError):
                    G9stueckersatz.schreiben(self.duf, [], loch=roh)
        pfad = G9stueckersatz.pfad(self.duf)
        pfad.write_text(json.dumps({'loch': {'dreiecke': [99], 'von': 10}}), encoding='utf-8')
        self.assertEqual(G9stueckersatz.loch(self.duf), {})
        pfad.write_text(json.dumps({'loch': 'unsinn'}), encoding='utf-8')
        self.assertEqual(G9stueckersatz.loch(self.duf), {})
