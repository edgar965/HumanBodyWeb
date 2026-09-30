# -*- coding: utf-8 -*-
u"""Hautgewichte ohne Schleife je Punkt (30.09.2026, Edgar: „warum dauert das fitting an HB so lange??").

Das G9 Base Shirt auf HumanBody (Stufe 2, 129.964 Punkte) brauchte 14,7 s für die Hautgewichte; 178.000
Python-Aufrufe je Punkt und Summen über eine Achse der Länge 3 waren der Hauptteil. Jetzt rechnen
`Gewichtsuebertragung` / `Gewichtssumme` / `DreiecksProjektion` über ganze Blöcke, und das Ergebnis muss dasselbe
sein wie die Schleife, die als Referenz stehen bleibt (`_mischen`):

1. `uebertragen` liefert EXAKT dasselbe wie `_mischen` je Punkt — mit Gleichständen, doppelten Knochen,
   Kleinstgewichten, leeren Listen, Vertices außerhalb und Anteilen <= 0.
2. Ein Körper mit einem Knochen je Vertex (weniger Spalten als `MAX_KNOCHEN`) füllt die Felder trotzdem auf vier.
3. Gleichstand: Es gewinnt der Knochen, der zuerst vorkam (Wörterbuch-Reihenfolge der Schleife).
4. `G9hbteilhaut.gemischt` ist `(1 − a)·nah + a·fern` wie das Wörterbuch es tat.
5. `Anziehen.felder` = `Anziehen.anziehen` (Gewichte und Versatz).
6. `DreiecksProjektion.projizieren` hängt nicht von der Blockgröße ab; der Komponentenkern rechnet mit Vorachsen
   wie Stück für Stück.

Sabotage-Gegenproben: in `Gewichtssumme.staerkste` `kind='stable'` weglassen oder `spaeter` nicht setzen -> Fall 3 rot;
`zaehlt` in `Gewichtsuebertragung._block` ohne `~(bary <= 0.0)` -> Fall 1 rot; in `DreiecksProjektion._skalar` die
Summe als `u[0] * w[0] + (u[1] * w[1] + u[2] * w[2])` -> Fall 6 rot (letzte Stelle).
"""
import sys

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

if str(settings.ASSETS_ROOT) not in sys.path:  # pragma: no cover
    sys.path.insert(0, str(settings.ASSETS_ROOT))

from assetCreator.GarmentFitter.dreiecksprojektion import DreiecksProjektion  # noqa: E402
from GarmentCode.anziehen import Anziehen  # noqa: E402
from GarmentCode.gewichtsuebertragung import Gewichtsuebertragung  # noqa: E402

from core.dienste.g9hbteilhaut import G9hbteilhaut  # noqa: E402


class Gitter:
    u"""Ein ebenes Dreiecksgitter (4 x 4 Vierecke) und Gewichte mit einem Knochen je Zeile des Gitters."""

    def __init__(self):
        spalten = zeilen = 5
        self.punkte = np.array([[x * 0.1, y * 0.1, 0.0] for y in range(zeilen) for x in range(spalten)])
        self.dreiecke = []
        for y in range(zeilen - 1):
            for x in range(spalten - 1):
                a = y * spalten + x
                self.dreiecke += [[a, a + 1, a + spalten + 1], [a, a + spalten + 1, a + spalten]]
        self.dreiecke = np.array(self.dreiecke)
        self.gewichte = [[[y, 0.6], [y + 1, 0.4]] for y in range(zeilen) for _ in range(spalten)]


class GewichtssummeTest(SimpleTestCase):

    databases = set()

    def koerper_zufall(self, zufall, knoten=400):
        koerper = []
        for _ in range(knoten):
            n = int(zufall.integers(0, 7))
            bones = zufall.integers(0, 12, size=n)            # darf doppelt vorkommen
            w = zufall.choice([0.5, 0.25, 0.25, 0.1, 0.0005, 0.0], size=n)
            koerper.append([[int(b), float(x)] for b, x in zip(bones, w, strict=True)])
        koerper[5] = None
        return koerper

    def test_1_uebertragen_ist_die_schleife(self):
        zufall = np.random.default_rng(7)
        koerper = self.koerper_zufall(zufall)
        dreiecke = zufall.integers(-2, len(koerper) + 3, size=(300, 3))     # auch ausserhalb
        tri = zufall.integers(0, 300, size=3000)
        bary = zufall.random((3000, 3))
        bary[zufall.random((3000, 3)) < 0.15] = 0.0
        bary[zufall.random((3000, 3)) < 0.03] = -0.1
        bary[:100] = 1.0 / 3.0                                              # Gleichstaende
        ueb = Gewichtsuebertragung(koerper)
        ecken = dreiecke[tri]
        erwartet = [ueb._mischen(e, b) for e, b in zip(ecken, bary, strict=True)]
        self.assertEqual(ueb.uebertragen(dreiecke, tri, bary), erwartet)
        self.assertGreater(sum(1 for z in erwartet if not z), 0, 'die Probe braucht auch leere Punkte')
        ueb.BLOCK = 7                                                       # Blockgrenzen ändern nichts
        self.assertEqual(ueb.uebertragen(dreiecke, tri, bary), erwartet)

    def test_2_ein_knochen_je_vertex_fuellt_vier_spalten(self):
        ueb = Gewichtsuebertragung([[[2, 1.0]], [[5, 1.0]], [[2, 1.0]]])
        knochen, gewicht, anzahl = ueb.uebertragen_felder(
            np.array([[0, 1, 2]]), np.array([0, 0]), np.array([[0.5, 0.5, 0.0], [0.0, 0.0, 1.0]]))
        self.assertEqual(knochen.shape, (2, 4))
        self.assertEqual(anzahl.tolist(), [2, 1])
        self.assertEqual(knochen[0, :2].tolist(), [2, 5])
        self.assertAlmostEqual(float(gewicht[0].sum()), 1.0)
        self.assertEqual(Gewichtsuebertragung([]).uebertragen(np.array([[0, 1, 2]]), np.array([0]),
                                                              np.array([[1.0, 0.0, 0.0]])), [[]])

    def test_3_gleichstand_gewinnt_der_zuerst_vorkam(self):
        bary = np.array([[0.5, 0.5, 0.0]])
        vorne_drei = Gewichtsuebertragung([[[3, 0.5], [7, 0.5]], [[7, 0.5], [3, 0.5]], [[9, 1.0]]])
        vorne_sieben = Gewichtsuebertragung([[[7, 0.5], [3, 0.5]], [[3, 0.5], [7, 0.5]], [[9, 1.0]]])
        ecken, tri = np.array([[0, 1, 2]]), np.array([0])
        self.assertEqual([k for k, _w in vorne_drei.uebertragen(ecken, tri, bary)[0]], [3, 7])
        self.assertEqual([k for k, _w in vorne_sieben.uebertragen(ecken, tri, bary)[0]], [7, 3])
        unter_schwelle = Gewichtsuebertragung([[[1, 0.0005], [2, 0.9995]], [[2, 1.0]], [[2, 1.0]]])
        self.assertEqual([k for k, _w in unter_schwelle.uebertragen(ecken, tri, np.array([[1.0, 0.0, 0.0]]))[0]], [2])

    def test_4_gemischt_wie_das_woerterbuch(self):
        zufall = np.random.default_rng(11)

        def felder(n):
            ids = np.zeros((n, 4), dtype=np.int64)
            w = np.zeros((n, 4))
            for i in range(n):
                k = int(zufall.integers(0, 5))
                ids[i, :k] = zufall.choice(12, size=k, replace=False)
                w[i, :k] = np.sort(zufall.random(k) + 0.01)[::-1]
                w[i, :k] /= w[i, :k].sum() if k else 1.0
            return ids, w

        nah, fern = felder(500), felder(500)
        anteil = zufall.random(500) * 0.9 + 0.05
        knochen, summen = G9hbteilhaut.gemischt(nah, fern, anteil)
        for i in range(500):
            summe = {}
            for ids, w, faktor in ((nah[0][i], nah[1][i], 1.0 - anteil[i]), (fern[0][i], fern[1][i], anteil[i])):
                for k, x in zip(ids, w, strict=True):
                    if x > 0:
                        summe[int(k)] = summe.get(int(k), 0.0) + faktor * float(x)
            beste = sorted(((k, w) for k, w in summe.items() if w > 0), key=lambda p: -p[1])[:4]
            self.assertEqual([int(k) for k in knochen[i][:len(beste)]], [k for k, _w in beste])
            self.assertEqual([float(w) for w in summen[i][:len(beste)]], [w for _k, w in beste])

    def test_5_felder_sind_anziehen(self):
        gitter = Gitter()
        anziehen = Anziehen(gitter.punkte, gitter.dreiecke, gitter.gewichte, ['b%d' % i for i in range(6)])
        zufall = np.random.default_rng(5)
        punkte = gitter.punkte[zufall.integers(0, 25, size=60)] + zufall.normal(size=(60, 3)) * 0.03
        liste = anziehen.anziehen(punkte)
        felder = anziehen.felder(punkte)
        nachgebaut = [[[int(k), float(w)] for k, w in zip(ks[:n], ws[:n], strict=True)] for ks, ws, n in
                      zip(felder['knochen'], felder['gewicht'], felder['anzahl'], strict=True)]
        self.assertEqual(nachgebaut, liste['gewichte'])
        self.assertEqual(felder['versatz'].tolist(), liste['anker']['versatz'])


class ProjektionTest(SimpleTestCase):

    databases = set()

    def test_6_block_und_komponentenkern(self):
        gitter = Gitter()
        zufall = np.random.default_rng(3)
        punkte = zufall.normal(size=(120, 3)) * 0.2 + np.array([0.2, 0.2, 0.0])
        projektion = DreiecksProjektion(gitter.punkte, gitter.dreiecke)
        ganz = projektion.projizieren(punkte)
        projektion.BLOCK = 7
        stueckweise = projektion.projizieren(punkte)
        for a, b in zip(ganz, stueckweise, strict=True):
            self.assertTrue(np.array_equal(a, b))
        # Vorachsen (B, K): jede (Punkt, Dreieck)-Stelle wie einzeln gerechnet
        ecken = zufall.normal(size=(6, 5, 3, 3))
        p = zufall.normal(size=(6, 1, 3)) * 2.0
        fuss, bary = DreiecksProjektion._naechster_punkt_im_dreieck(p, ecken)
        for i in range(6):
            for k in range(5):
                f1, b1 = DreiecksProjektion._naechster_punkt_im_dreieck(p[i, 0], ecken[i, k])
                self.assertTrue(np.array_equal(fuss[i, k], f1))
                self.assertTrue(np.array_equal(bary[i, k], b1))
