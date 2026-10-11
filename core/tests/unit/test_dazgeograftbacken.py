# -*- coding: utf-8 -*-
"""`Dazgeograftbacken` — Farbe, Rauheit und Normalen der Original-Scham auf das angepasste Daz-Stück übertragen (10./11.10.2026), an Kunstplatten ohne Daz-Bibliothek.

Die Normalenkarte muss im Browser (three.js, `normalize(tbn · mapN)`, Tangentenraum aus `Dazgeograftraster`) dieselbe Normale ergeben, auf der sie gebacken wurde; sonst stehen am Stück
Keile und Facetten (Chrome, 11.10.2026: Sprung an Ringpunkt 7 und 69 von 56 und 126 auf unter 5, nachdem der Tangentenraum stimmte).

1. `_glatt` ist 0 unter 0, 1 über 1, in der Mitte 0,5 und nie fallend.
2. `_begrenzen`: eine Normale, die um weniger als `MAX_NEIGUNG_GRAD` von der glatten abweicht, bleibt; eine um 80° geneigte wird auf 60° gekappt, in derselben Richtung, mit Länge 1.
3. `_kodieren` ist die Umkehrung der Dekodierung in three.js: für beliebige Normalen innerhalb von 60° um N ergibt `normalize(T·x + B·y + N·z)` mit dem kodierten Texel wieder die Normale — auch mit geschertem
   UV (Scherung 0,5, T und B nicht senkrecht). Der alte Tangentenraum (Orthonormalbasis) ergäbe dort über 5° Fehler: die Gegenprobe zeigt, dass der Test den Befund sieht.
4. Ein entarteter Tangentenraum (UV ohne Fläche: T = B = 0) kodiert „flach" (0, 0, 1).
5. `_randweg`: der Weg über die Kanten vom Rand: in der Mitte eines Streifens 8 mm (zwei Reihen zu 4 mm), weit im Innern der Ersatzwert 1,0; verschweißte und aufgespaltene Punkte (UV-Nähte) geben dasselbe.
6. Ganzer Lauf an einer um 5° geneigten Original-Platte (Stück flach, 80 mm): die Normalenkarte dekodiert in der Mitte zur Normale des Originals (Fehler unter 1°, 8-Bit-Rundung), die Farbe links ist rot und
   rechts blau, die Dateien sind da. Ohne Hauttextur-Ordner füllt der Rand mit Grau (128).

Sabotage-Gegenprobe (nicht gelaufen): in `_kodieren` `t['bitangente']` durch `np.cross(t['normale'], t['tangente'])` ersetzen macht Fall 3 rot (geschert); `RAND_NORMALEN_M` auf 0 stellt Fall 6 nicht rot
(die Mitte liegt weit vom Rand), aber `_randweg` Fall 5.
"""
from pathlib import Path

import numpy as np
from django.test import SimpleTestCase
from PIL import Image

from core.dienste.dazgeograftbacken import Dazgeograftbacken
from core.dienste.dazgeograftraster import Dazgeograftraster

from ._dazkunstziel import Dazkunstziel
from ._pruefablage import Pruefablage


def _dekodieren(ts, t):
    """Was three.js aus dem Texelwert `ts` (−1 … 1) macht: `normalize(T·x + B·y + N·z)`."""
    n = ts[:, :1] * t['tangente'] + ts[:, 1:2] * t['bitangente'] + ts[:, 2:3] * t['normale']
    return n / np.linalg.norm(n, axis=1, keepdims=True)


class DazgeograftbackenTest(SimpleTestCase):
    databases = set()

    L, R = 0.040, 24

    def _platte(self, scherung):
        punkte = np.array([[0.0, 0.0, 0.0], [self.L, 0.0, 0.0], [self.L, self.L, 0.0], [0.0, self.L, 0.0]])
        dreiecke = np.array([[0, 1, 2], [0, 2, 3]])
        uv = np.column_stack([punkte[:, 0] / self.L + scherung * punkte[:, 1] / self.L, punkte[:, 1] / self.L])
        return Dazgeograftraster.texel(punkte, dreiecke, uv[dreiecke], self.R, np.tile([0.0, 0.0, 1.0], (4, 1)))

    @staticmethod
    def _winkel_grad(a, b):
        return np.degrees(np.arccos(np.clip(np.einsum('ij,ij->i', a, b), -1.0, 1.0)))

    def test_1_glatt_ist_eine_stufe_ohne_knick_und_ohne_ruecklauf(self):
        x = np.linspace(-0.5, 1.5, 101)
        y = Dazgeograftbacken._glatt(x)
        self.assertEqual((float(y[0]), float(y[-1])), (0.0, 1.0))
        self.assertAlmostEqual(float(Dazgeograftbacken._glatt(np.array([0.5]))[0]), 0.5, places=12)
        self.assertGreaterEqual(float(np.diff(y).min()), 0.0)

    def test_2_die_neigung_gegen_die_glatte_normale_ist_begrenzt(self):
        glatt = np.array([[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]])
        w = np.radians([30.0, 80.0])
        n = np.column_stack([np.sin(w) * np.cos(0.7), np.sin(w) * np.sin(0.7), np.cos(w)])
        aus = Dazgeograftbacken._begrenzen(n, glatt)
        self.assertAlmostEqual(float(self._winkel_grad(aus, glatt)[0]), 30.0, places=6)
        self.assertAlmostEqual(float(self._winkel_grad(aus, glatt)[1]), Dazgeograftbacken.MAX_NEIGUNG_GRAD, places=6)
        self.assertLess(float(np.abs(np.arctan2(aus[1, 1], aus[1, 0]) - 0.7)), 1e-9, 'die Richtung der Neigung bleibt')
        self.assertLess(float(np.abs(np.linalg.norm(aus, axis=1) - 1.0).max()), 1e-9)

    def test_3_die_kodierung_ist_die_umkehrung_der_dekodierung_in_three_js(self):
        rng = np.random.default_rng(3)
        for scherung in (0.0, 0.5, -0.9):
            with self.subTest(scherung=scherung):
                t = self._platte(scherung)
                w = np.radians(rng.uniform(0.0, 55.0, len(t['zeile'])))
                a = rng.uniform(0.0, 2 * np.pi, len(t['zeile']))
                n = np.column_stack([np.sin(w) * np.cos(a), np.sin(w) * np.sin(a), np.cos(w)])
                ts = Dazgeograftbacken._kodieren(n, t)
                self.assertLessEqual(float(np.abs(ts).max()), 1.0 + 1e-12)
                self.assertLess(float(self._winkel_grad(_dekodieren(ts, t), n).max()), 1e-3, 'Grad; arccos nahe 1 rundet auf 1e-6° ungenau')
                acht_bit = np.round((ts * 0.5 + 0.5) * 255.0) / 255.0 * 2.0 - 1.0
                self.assertLess(float(self._winkel_grad(_dekodieren(acht_bit, t), n).max()), 2.0, 'auch nach der Rundung auf 8 Bit')

    def test_3b_die_alte_orthonormalbasis_haette_hier_ueber_5_grad_fehler(self):
        t = self._platte(0.5)
        alt = dict(t, tangente=np.tile([1.0, 0.0, 0.0], (len(t['zeile']), 1)), bitangente=np.tile([0.0, 1.0, 0.0], (len(t['zeile']), 1)))
        n = np.tile([np.sin(np.radians(40.0)), 0.0, np.cos(np.radians(40.0))], (len(t['zeile']), 1))
        ts_alt = Dazgeograftbacken._kodieren(n, alt)
        fehler = self._winkel_grad(_dekodieren(ts_alt, t), n)
        self.assertGreater(float(fehler.mean()), 5.0, 'in der geschertem UV dekodiert three.js die alte Karte anders')

    def test_4_ein_entarteter_tangentenraum_kodiert_flach(self):
        t = {'tangente': np.zeros((2, 3)), 'bitangente': np.zeros((2, 3)), 'normale': np.tile([0.0, 0.0, 1.0], (2, 1))}
        ts = Dazgeograftbacken._kodieren(np.array([[0.6, 0.0, 0.8], [0.0, 0.6, 0.8]]), t)
        self.assertEqual(ts.tolist(), [[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]])

    def _streifen(self, spalten, zeilen, abstand=0.004, aufgespalten=False):
        """Gitter `spalten × zeilen` Punkte, Abstand 4 mm, mit Diagonalen; `aufgespalten`: jedes Dreieck mit eigenen Punkten (wie ein OBJ mit UV-Nähten)."""
        punkte = np.array([[i * abstand, j * abstand, 0.0] for j in range(zeilen) for i in range(spalten)])
        dreiecke = []
        for j in range(zeilen - 1):
            for i in range(spalten - 1):
                a = j * spalten + i
                dreiecke += [[a, a + 1, a + spalten + 1], [a, a + spalten + 1, a + spalten]]
        dreiecke = np.array(dreiecke)
        if aufgespalten:
            return punkte[dreiecke].reshape(-1, 3), np.arange(len(dreiecke) * 3).reshape(-1, 3), dreiecke
        return punkte, dreiecke, dreiecke

    def _weg(self, aufgespalten):
        spalten, zeilen = 11, 5
        punkte, d, original = self._streifen(spalten, zeilen, aufgespalten=aufgespalten)
        mitte = (zeilen // 2) * spalten + spalten // 2
        t_index = int(np.flatnonzero(original[:, 0] == mitte)[0])
        t = {'bary': np.array([[1.0, 0.0, 0.0]]), 'dreieck': np.array([t_index])}
        return Dazgeograftbacken.__new__(Dazgeograftbacken)._randweg(punkte, d, t)[0]

    def test_5_der_weg_vom_rand_ist_der_kuerzeste_ueber_die_kanten(self):
        self.assertAlmostEqual(float(self._weg(False)), 0.008, places=9, msg='Mitte des Streifens: zwei Reihen zu 4 mm bis zum Rand')
        self.assertAlmostEqual(float(self._weg(True)), 0.008, places=9, msg='UV-Nähte (aufgespaltene Punkte) trennen die Fläche nicht')
        punkte, d, _ = self._streifen(21, 21)
        mitte = 10 * 21 + 10
        t = {'bary': np.array([[1.0, 0.0, 0.0]]), 'dreieck': np.array([int(np.flatnonzero(d[:, 0] == mitte)[0])])}
        self.assertEqual(float(Dazgeograftbacken.__new__(Dazgeograftbacken)._randweg(punkte, d, t)[0]), 1.0, 'weiter als zweimal RAND_NORMALEN_M: Ersatzwert')

    def test_6_ganzer_lauf_die_karte_ergibt_im_browser_die_normale_des_originals(self):
        ziel = Dazkunstziel.geneigte_platte(5.0)
        punkte, dreiecke, _ = self._streifen(21, 21)                         # 80 × 80 mm, Punktabstand 4 mm wie am echten Stück: nur so gibt es Punkte weit vom Rand
        punkte = punkte - np.array([0.040, 0.040, 0.0])
        uv = (punkte[:, :2] / 0.080 + 0.5)[dreiecke]
        figur = {'punkte': punkte, 'dreiecke': dreiecke, 'uv': punkte[:, :2], 'kachel': np.zeros(len(dreiecke), dtype=np.int64)}
        with Pruefablage.ordner('bake_') as ordner:
            dateien, bericht = Dazgeograftbacken(ziel, figur, Path(ordner) / 'ohne_haut', 64).backen(punkte, dreiecke, uv, Path(ordner) / 'aus')
            farbe = np.asarray(Image.open(dateien['farbe']).convert('RGB'), dtype=np.float64)
            karte = np.asarray(Image.open(dateien['normalen']).convert('RGB'), dtype=np.float64)
            self.assertTrue(dateien['rauheit'].is_file())
        self.assertGreater(bericht['texel'], 0.9 * 64 * 64)
        w = np.radians(5.0)
        soll = np.array([0.0, -np.sin(w), np.cos(w)])
        t = Dazgeograftraster.texel(punkte, dreiecke, uv, 64, np.tile([0.0, 0.0, 1.0], (len(punkte), 1)))
        x, y = t['position'][:, 0], t['position'][:, 1]
        mitte = (np.abs(x) < 0.010) & (np.abs(y) < 0.010)
        self.assertGreater(int(mitte.sum()), 20)
        ts = karte[t['zeile'][mitte], t['spalte'][mitte]] / 255.0 * 2.0 - 1.0
        fehler = self._winkel_grad(_dekodieren(ts, {k: v[mitte] for k, v in t.items() if k in ('tangente', 'bitangente', 'normale')}), np.tile(soll, (int(mitte.sum()), 1)))
        self.assertLess(float(fehler.max()), 1.0, 'die Karte ergibt in three.js die Normale der geneigten Original-Platte')
        links = farbe[t['zeile'][(np.abs(x + 0.020) < 0.002) & (np.abs(y) < 0.010)], t['spalte'][(np.abs(x + 0.020) < 0.002) & (np.abs(y) < 0.010)]].mean(axis=0)
        rechts = farbe[t['zeile'][(np.abs(x - 0.020) < 0.002) & (np.abs(y) < 0.010)], t['spalte'][(np.abs(x - 0.020) < 0.002) & (np.abs(y) < 0.010)]].mean(axis=0)
        self.assertGreater(float(links[0] - links[2]), 100.0, 'links rot')
        self.assertGreater(float(rechts[2] - rechts[0]), 100.0, 'rechts blau')
