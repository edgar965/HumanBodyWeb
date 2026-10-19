# -*- coding: utf-8 -*-
u"""Das Loch eines verschweißten Stücks auf der ULTRAFEINEN Stufe (`G9stuecklochultrafein`, 19.10.2026) — gegen die echte Bibliothek und das Stück
„Daz Anatomie Frau" (LongRunner: Unterteiler der Stufe 2 laden ~1,2 s, Rechnung ~0,7 s).

Edgar, 19.10.2026: „ultrafein soll auch eigenes Loch kriegen". Gemessen offline (`ProjektTemp/_wegwerf/scham_grob/probe_ultra.py`) und im Chrome (DamiraAlt):
1.440 Dreiecke der Stufe 1 → 5.760 der Stufe 2; die Haut zeigte 799.232 von 804.992; Ecken und Kantenpunkte 0,0000–0,0001 mm auf der Randlinie des Stücks.

1. Mit Unterteilung des Stücks: 5.760 Dreiecke, Ring 200 Ecken (100 + 100 auf den Kantenmitten), jeder Punkt der Lochkante ist eine Ringecke.
2. Ohne (`polygon_mesh`, wie dieses Stück): Ring 100 Ecken, 100 `zwischen` (`[Kantenpunkt, Ecke a, Ecke b]`), jeder Kantenpunkt liegt auf der Lochkante.
3. `ring.d` ist die Verschiebung der Haut der Stufe 2 an der Ringecke (`verschiebung`) — mit dem `d` der Stufe 1 lagen die Ecken im Chrome bis 1,2 mm daneben.

Sabotage (nicht gelaufen): in `_ring` die Zeile `d = d2[ecken]` streichen → Fall 3 rot; `if not unterteilt:` umkehren → Fälle 1 und 2 rot. Geschrieben, nicht gelaufen.
"""
import unittest
from pathlib import Path

import numpy as np
from django.test import SimpleTestCase

try:
    from Genesis9.basisnetz import G9basisnetz
    from Genesis9.stueckersatz import G9stueckersatz
    from Genesis9.stuecklochstufen import G9stuecklochstufen
    from Genesis9.pfade import G9pfade
    STUECK = Path(G9pfade.eigene()) / 'People' / 'Genesis 9' / 'Clothing' / 'EIGEN' / 'Daz Anatomie Frau.duf'
    DA = G9pfade.vorhanden() and STUECK.is_file()
except Exception:  # noqa: BLE001 — ohne Bibliothek übersprungen
    DA = False


@unittest.skipUnless(DA, 'Daz-Bibliothek oder „Daz Anatomie Frau" fehlt')
class StuecklochUltrafeinTest(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loch = G9stueckersatz.loch(STUECK)
        cls.ultra = G9basisnetz.netzstufe(2)
        cls.e2 = np.concatenate([np.arange(cls.ultra._cc.geo_vertex_count), cls.ultra._cc.kopien_eltern]).astype(np.int64)

    def fassung(self, stueck_stufe):
        voll = G9stuecklochstufen.mit_stufen(self.loch, 2, stueck_stufe)
        return next(f for f in voll['weitere'] if f['von'] == len(self.ultra.dreiecke))

    def kante(self, dreiecke):
        d = self.e2[np.asarray(self.ultra.dreiecke)[np.asarray(dreiecke)]]
        k = np.sort(np.concatenate([d[:, [0, 1]], d[:, [1, 2]], d[:, [2, 0]]]), axis=1)
        k, z = np.unique(k, axis=0, return_counts=True)
        return set(k[z == 1].ravel().tolist())

    def test_1_mit_unterteilung(self):
        f = self.fassung(2)
        self.assertEqual(len(f['dreiecke']), 4 * len(self.loch['dreiecke']))
        self.assertEqual((len(f['ring']['punkte']), f['ring']['neu']), (200, 100))
        self.assertEqual(self.kante(f['dreiecke']) - set(self.e2[np.asarray(f['ring']['punkte'])].tolist()), set())

    def test_2_ohne_unterteilung(self):
        f = self.fassung(0)
        self.assertEqual((len(f['ring']['punkte']), len(f['ring']['zwischen'])), (100, 100))
        kante = self.kante(f['dreiecke'])
        self.assertTrue(all(e in kante for e, _a, _b in f['ring']['zwischen']))

    def test_3_d_ist_die_verschiebung_der_stufe_2(self):
        f = self.fassung(2)
        v = {p: np.asarray(d) for p, d in zip(f['verschiebung']['punkte'], f['verschiebung']['d'])}
        abw = [np.linalg.norm(np.asarray(d) - v.get(p, np.zeros(3))) for p, d in zip(f['ring']['punkte'], f['ring']['d'])]
        self.assertLess(max(abw), 1e-6)
