# -*- coding: utf-8 -*-
"""Der Rand des Scham-Stücks liegt genau auf dem Kantenring des Hautlochs (`Blendimportschamnaht`, `Blendimportschamgeograft`) —
an einer Kunsthaut und einem Kunststück, ohne Django, Genesis und trimesh.

Edgar, 09.10.2026, mit Bild: „bei der Scham gibt es immer noch die Probleme an den Rändern. Schau nach, wie Genesis das mit der Nase und
dem Mund macht, und mach es genau so." Daz verschweißt das Geograft Punkt für Punkt mit einem Loch im Körper: die Randpunkte des Stücks
SIND Punkte der Haut. Gemessen am echten Stück („cute girl", 09.10.2026): Randpunkte 98, genau die 98 Ecken des Rings, jede Kante des Rings
genau einmal Randkante, keine fremde Randkante.

Kunstwelt: Ring = Achteck (Umkreis 30 mm) in der Ebene y = 0, im Uhrzeigersinn oder dagegen; Stück = Scheibe aus Mittelpunkt und vier Ringen
von 24 Punkten (7, 14, 21, 28 mm), UV je Ecke = (x, z) · 10 — der Rand liegt 1 mm ÜBER der Ebene und innerhalb der Ringecken.

1. Nach `anlegen` ist jeder Randpunkt eine Ecke des Rings (Abstand ≤ 1e-9 m), es gibt genau acht, und jede der acht Kanten des Rings ist
   genau einmal Randkante — kein Spalt, keine Überlappung, keine fremde Kante. Das gilt für beide Umlaufrichtungen des Rings.
2. Der Mittelpunkt des Stücks bleibt, wo er war (die Verschiebung läuft nur über `BAND_MM` aus); die Zahl der Dreiecke ist nicht kleiner
   als die Hälfte der alten; UV ist je Ecke vorhanden und endlich.
3. Ohne einen Randpunkt nahe einer Ecke (alles unter dem Ring) bricht nichts, die Ecken kommen durch `_einfuegen` dazu.
4. `Blendimportschamgeograft.verschweissen`: aus einer Kunsthaut (Ebene 24 × 24 Zellen von 4 mm, Schnittwert = Abstand − 30 mm) und dem
   Stück entsteht ein Stück, dessen Rand die Ecken des Rings des Lochs sind; `loch` nennt die Dreiecke der Haut, den Ring und die
   Verschiebung der Glättung. Ohne Loch (zu kleiner Schnittbereich) kommt `{'aus': Grund}`, das Stück bleibt unberührt.
5.–7. Die Grenze für den Rand (`MAX_RAND_WEG_MM`): ein zu großes Stück wird beschnitten (5), bleibt es darüber, kommt `aus` (6); mit einem Anbau
   gilt die weitere `MAX_RAND_WEG_ANBAU_MM` (7, gemessen 10.10.2026: ohne Anbau `aus`, mit Anbau Rand 15,96 mm daneben).

Sabotage-Gegenprobe (nicht gelaufen): `_zu_ecken` in `anlegen` weglassen macht Fall 1 rot (Randpunkte mitten auf den Kanten); in `_einfuegen`
die Kandidaten leeren macht Fall 1 rot (Ecken ohne Randpunkt); `_gleichlaeufig` ohne `np.maximum.accumulate` macht Fall 1 rot für eine der
beiden Umlaufrichtungen (Rand läuft rückwärts).
"""

from types import SimpleNamespace
from unittest import mock

import numpy as np
from django.test import SimpleTestCase

from core.dienste.blendimportschamgeograft import Blendimportschamgeograft
from core.dienste.blendimportschamnaht import Blendimportschamnaht


class SchamnahtTest(SimpleTestCase):
    databases = set()

    N = 24
    RADIEN = (0.007, 0.014, 0.021, 0.028)

    @classmethod
    def _achteck(cls, uhrzeigersinn=True, radius=0.030):
        winkel = np.arange(8) * (2 * np.pi / 8) * (-1.0 if uhrzeigersinn else 1.0)
        return np.stack([radius * np.cos(winkel), np.zeros(8), radius * np.sin(winkel)], axis=1)

    @classmethod
    def _scheibe(cls, hoehe=0.001):
        """`(punkte, dreiecke, uv_ecken)`: Mittelpunkt, `RADIEN` mit je `N` Punkten, Dreiecke dazwischen."""
        punkte = [[0.0, hoehe, 0.0]]
        for r in cls.RADIEN:
            for k in range(cls.N):
                w = 2 * np.pi * k / cls.N
                punkte.append([r * np.cos(w), hoehe, r * np.sin(w)])
        punkte = np.array(punkte)
        ring = lambda i, k: 1 + i * cls.N + (k % cls.N)                       # noqa: E731
        dreiecke = [[0, ring(0, k), ring(0, k + 1)] for k in range(cls.N)]
        for i in range(len(cls.RADIEN) - 1):
            for k in range(cls.N):
                a, b, c, d = ring(i, k), ring(i, k + 1), ring(i + 1, k), ring(i + 1, k + 1)
                dreiecke += [[a, c, b], [b, c, d]]
        dreiecke = np.array(dreiecke)
        uv = punkte[dreiecke][:, :, [0, 2]] * 10.0
        return punkte, dreiecke, uv

    @staticmethod
    def _rand(naht, dreiecke):
        folge, _ = naht._randfolge(dreiecke)
        return folge

    def _pruefen(self, ring, punkte, dreiecke, uv):
        naht = Blendimportschamnaht(ring)
        p, d, u, bericht = naht.anlegen(punkte, dreiecke, uv)
        rand = self._rand(naht, d)
        abstand = np.array([np.min(np.linalg.norm(ring - p[i], axis=1)) for i in rand])
        self.assertLessEqual(float(abstand.max()), 1e-9, 'jeder Randpunkt ist eine Ecke des Rings')
        self.assertEqual(len(rand), len(ring))
        kanten = {}
        for a, b in zip(rand, np.roll(rand, -1), strict=True):
            ka = int(np.argmin(np.linalg.norm(ring - p[a], axis=1)))
            kb = int(np.argmin(np.linalg.norm(ring - p[b], axis=1)))
            schluessel = tuple(sorted((ka, kb)))
            kanten[schluessel] = kanten.get(schluessel, 0) + 1
        soll = {tuple(sorted((i, (i + 1) % len(ring)))): 1 for i in range(len(ring))}
        self.assertEqual(kanten, soll, 'jede Kante des Rings genau einmal als Randkante, keine fremde')
        return p, d, u, bericht

    def test_1_der_rand_hat_genau_die_ecken_des_rings_in_beiden_richtungen(self):
        punkte, dreiecke, uv = self._scheibe()
        for uhrzeigersinn in (True, False):
            with self.subTest(uhrzeigersinn=uhrzeigersinn):
                self._pruefen(self._achteck(uhrzeigersinn), punkte, dreiecke, uv)

    def test_2_die_mitte_bleibt_und_uv_ist_je_ecke_da(self):
        punkte, dreiecke, uv = self._scheibe()
        p, d, u, bericht = self._pruefen(self._achteck(), punkte, dreiecke, uv)
        mitte = np.flatnonzero(np.linalg.norm(p - np.array([0.0, 0.001, 0.0]), axis=1) < 1e-12)
        self.assertEqual(len(mitte), 1, 'der Mittelpunkt ist noch da, an derselben Stelle')
        self.assertGreaterEqual(len(d), len(dreiecke) // 2)
        self.assertEqual(u.shape, (len(d), 3, 2))
        self.assertTrue(np.isfinite(u).all())
        self.assertGreaterEqual(bericht['ecken_eingefuegt'] + bericht['zu_ecken'], 1)

    def test_3_ein_stueck_ganz_unter_dem_ring_bekommt_die_ecken_dazu(self):
        punkte, dreiecke, uv = self._scheibe()
        klein = punkte.copy()
        klein[:, [0, 2]] *= 0.5                                   # Rand bei 14 mm, der Ring bei 28 mm (Inkreis) — alles innen
        self._pruefen(self._achteck(), klein, dreiecke, uv)

    def test_4_geograft_verschweisst_haut_und_stueck(self):
        zellen, zelle = self.N, 0.004
        halb = zellen // 2
        n = zellen + 1
        punkte = np.array([[(c - halb) * zelle, 0.0, (r - halb) * zelle] for r in range(n) for c in range(n)])
        dreiecke = []
        for r in range(zellen):
            for c in range(zellen):
                a = r * n + c
                dreiecke += [[a, a + 1, a + n], [a + 1, a + n + 1, a + n]]
        haut = SimpleNamespace(vertices=punkte, faces=np.array(dreiecke))
        werte = np.linalg.norm(punkte[:, [0, 2]], axis=1) - 0.030
        stueck, flaechen, uv = self._scheibe(hoehe=0.0)
        stueck[:, [0, 2]] *= 30.0 / 28.0                          # der Rand etwa auf dem Radius des Lochs
        ergebnis = Blendimportschamgeograft.verschweissen(haut, werte, stueck, flaechen, uv)
        self.assertNotIn('aus', ergebnis, ergebnis.get('aus'))
        loch = ergebnis['loch']
        self.assertEqual(loch['von'], len(dreiecke))
        self.assertGreater(len(loch['dreiecke']), 100)
        self.assertEqual(len(loch['ring']), len(loch['ring_punkte']))
        self.assertEqual(len(loch['ring_d']), len(loch['ring']))
        self.assertIn('halbiert', loch['verschiebung'])
        naht = Blendimportschamnaht(loch['ring'])
        rand = self._rand(naht, ergebnis['dreiecke'])
        abstand = np.array([np.min(np.linalg.norm(loch['ring'] - ergebnis['punkte'][i], axis=1)) for i in rand])
        self.assertLessEqual(float(abstand.max()), 1e-9)
        self.assertEqual(len(rand), len(loch['ring']))
        kaputt = Blendimportschamgeograft.verschweissen(haut, np.full(len(punkte), 1.0), stueck, flaechen, uv)
        self.assertIn('aus', kaputt)

    def _zu_grosses_stueck(self):
        """`(haut, werte, stueck, flaechen, uv)`: ein Stück doppelt so groß wie das Loch (Rand bei 56 statt 30 mm)."""
        zellen, zelle = self.N, 0.004
        halb = zellen // 2
        n = zellen + 1
        punkte = np.array([[(c - halb) * zelle, 0.0, (r - halb) * zelle] for r in range(n) for c in range(n)])
        dreiecke = []
        for r in range(zellen):
            for c in range(zellen):
                a = r * n + c
                dreiecke += [[a, a + 1, a + n], [a + 1, a + n + 1, a + n]]
        haut = SimpleNamespace(vertices=punkte, faces=np.array(dreiecke))
        werte = np.linalg.norm(punkte[:, [0, 2]], axis=1) - 0.030
        stueck, flaechen, uv = self._scheibe(hoehe=0.0)
        stueck[:, [0, 2]] *= 2.0
        return haut, werte, stueck, flaechen, uv

    def test_5_ein_stueck_das_ueber_das_loch_hinausreicht_wird_beschnitten(self):
        """„Asian Female", 09.10.2026: Rand bis 62,6 mm neben dem Ring → Keile. Seit `Blendimportschamregister.beschneiden` (abends, vor dem Ring)
        schneidet das Verschweißen Teile ab, die nicht über dem Loch liegen: das Stück bekommt seine Naht, und der Rand hält die Grenze.
        (Gemessen 10.10.2026 am Kunststück: abgeschnitten 48, Rand höchstens 16,0 mm neben dem Ring bei Grenze 20; vorher erwartete dieser Fall
        `aus` — die Erwartung stammte aus der Fassung ohne Beschneiden.)"""
        ergebnis = Blendimportschamgeograft.verschweissen(*self._zu_grosses_stueck())
        self.assertNotIn('aus', ergebnis, ergebnis.get('aus'))
        self.assertGreater(ergebnis['bericht']['abgeschnitten'], 0)
        self.assertLessEqual(ergebnis['bericht']['rand_weg_max_mm'], Blendimportschamgeograft.MAX_RAND_WEG_MM)

    def test_6_bleibt_der_rand_ueber_der_grenze_bleibt_das_stueck_ohne_naht(self):
        """Das Netz unter dem Beschneiden: liegt der Rand trotzdem weiter als `MAX_RAND_WEG_MM` vom Ring, kommt `{'aus': Grund}`."""
        with mock.patch.object(Blendimportschamgeograft, 'MAX_RAND_WEG_MM', 5.0):
            ergebnis = Blendimportschamgeograft.verschweissen(*self._zu_grosses_stueck())
        self.assertIn('aus', ergebnis)
        self.assertIn('neben dem Ring', ergebnis['aus'])

    def test_7_ein_anbau_darf_weiter_vom_ring_liegen(self):
        """Penis und Hoden (BodyParts3D, 10.10.2026): der Rand lag bis 22,3 mm neben dem Ring, Grenze 20 → das Stück blieb ohne Naht. Mit `anbau`
        gilt `MAX_RAND_WEG_ANBAU_MM`; ohne ihn bleibt die engere Grenze (hier auf 5 mm gestellt, das Kunststück liegt bis 16 mm daneben)."""
        with mock.patch.object(Blendimportschamgeograft, 'MAX_RAND_WEG_MM', 5.0):
            ohne = Blendimportschamgeograft.verschweissen(*self._zu_grosses_stueck())
            mit = Blendimportschamgeograft.verschweissen(*self._zu_grosses_stueck(), anbau=True)
        self.assertIn('aus', ohne)
        self.assertNotIn('aus', mit, mit.get('aus'))
        self.assertLessEqual(mit['bericht']['rand_weg_max_mm'], Blendimportschamgeograft.MAX_RAND_WEG_ANBAU_MM)
