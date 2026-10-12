# -*- coding: utf-8 -*-
"""`Blendimportschamregister.beschneiden` lässt nur weg, was bis an den Rand des Stücks reicht (11.10.2026).

Gemessen an „cute girl" (alte und neue Figur): das Stück liegt hinter der Haut, der nächste Hautpunkt eines Stück-Punkts liegt dort oft neben dem Loch — so fielen auch Dreiecke MITTEN im Stück weg,
und es entstanden zusätzliche Randringe und offene Splitter am Rand (Randpunkte 119 statt 100, Normalenwinkel am Rand p90 48,7° statt 28,9°, 7 % statt 2 % umgekehrt). Kunstwelt: Haut und Stück sind
dasselbe ebene Gitter (17 × 17 Punkte, 16 × 16 Zellen von 4 mm), der nächste Hautpunkt ist also der Punkt selbst; das Loch ist ein quadratischer RAHMEN (Zellen mit Abstand 3,5 … 5,5 Zellen von der Mitte).

1. Die Zellen in der Mitte des Rahmens (4 × 4 Zellen, 32 Dreiecke) haben keinen Punkt im Loch, hängen aber mit keinem Rand zusammen: sie bleiben (`_innere_loecher`).
2. Die äußerste Zellenschicht (60 Zellen, 120 Dreiecke, dazu je eine Dreieckshälfte an zwei Ecken der zweiten Schicht) reicht bis an den Rand: sie entfällt, 122 Dreiecke und 66 Punkte.
3. Was übrig bleibt, hat genau einen Randring (54 Punkte).

Zahlen nachgerechnet am 11.10.2026 (`ProjektTemp/_wegwerf/beschneiden_erwartung.py`, kein Testlauf): 289 → 223 Punkte, 512 → 390 Dreiecke, entfernt 122.
Sabotage-Gegenprobe NICHT gemacht (erst auf Ansage): vorgesehen ist `_innere_loecher` leer lassen → Fälle 1 und 3 rot (154 statt 122 Dreiecke entfernt, zweiter Randring).

Nicht gelaufen (Stand 11.10.2026) — läuft nur auf Ansage.
"""
from types import SimpleNamespace

import numpy as np
from django.test import SimpleTestCase

from core.dienste.blendimportschamregister import Blendimportschamregister
from core.dienste.schamtiefenfeld import Schamtiefenfeld


class SchamregisterBeschneidenTest(SimpleTestCase):
    databases = set()

    ZELLEN, ZELLE = 16, 0.004

    @classmethod
    def _gitter(cls):
        """`(punkte, dreiecke, abstand je Dreieck)`: Gitter in y = 0; Abstand = Tschebyschow-Abstand der Zellenmitte von der Mitte, in Zellen."""
        n = cls.ZELLEN + 1
        punkte = np.array([[c * cls.ZELLE, 0.0, r * cls.ZELLE] for r in range(n) for c in range(n)])
        dreiecke, abstand = [], []
        for r in range(cls.ZELLEN):
            for c in range(cls.ZELLEN):
                a = r * n + c
                dreiecke += [[a, a + 1, a + n], [a + 1, a + n + 1, a + n]]
                abstand += [max(abs(r + 0.5 - cls.ZELLEN / 2), abs(c + 0.5 - cls.ZELLEN / 2))] * 2
        return punkte, np.array(dreiecke, dtype=np.int64), np.array(abstand)

    def _beschneiden(self):
        punkte, dreiecke, abstand = self._gitter()
        haut = SimpleNamespace(punkte=punkte, dreiecke=dreiecke)
        im_loch = (abstand >= 3.5) & (abstand <= 5.5)
        uv = np.zeros((len(dreiecke), 3, 2))
        return punkte, dreiecke, Blendimportschamregister.beschneiden(haut, im_loch, punkte, dreiecke, uv)

    def test_1_die_mitte_des_rahmens_bleibt(self):
        punkte, dreiecke, (neu_punkte, neu_dreiecke, neu_uv, entfernt) = self._beschneiden()
        mitte = np.array([self.ZELLEN // 2 * self.ZELLE] * 2)
        gefunden = np.flatnonzero(np.linalg.norm(neu_punkte[:, [0, 2]] - mitte, axis=1) < 1e-12)
        self.assertEqual(len(gefunden), 1, 'der Punkt in der Mitte ist noch da')
        self.assertEqual(len(neu_dreiecke), len(neu_uv))
        self.assertEqual(entfernt, 122, 'nur die äußerste Schicht (154 wären es mit den Dreiecken der Mitte)')

    def test_2_die_aeusserste_schicht_entfaellt_mit_ihren_randpunkten(self):
        punkte, dreiecke, (neu_punkte, neu_dreiecke, _uv, _entfernt) = self._beschneiden()
        self.assertEqual(len(punkte) - len(neu_punkte), 66)
        self.assertEqual(len(dreiecke) - len(neu_dreiecke), 122)

    def test_3_der_rest_hat_genau_einen_randring(self):
        _punkte, _dreiecke, (_np, neu_dreiecke, _uv, _entfernt) = self._beschneiden()
        ring, weitere = Schamtiefenfeld.aussenring(neu_dreiecke)
        self.assertEqual(weitere, 0, 'kein Loch im Innern')
        self.assertEqual(len(ring), 54)
