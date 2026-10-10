# -*- coding: utf-8 -*-
"""Die Regler des Penis (`G9penismorphe`, Katalog `G9penismorphekatalog`) an einer KUNSTFLÄCHE (Edgar, 10.10.2026: „Genital in Genesis einbauen").

Die Fläche: eine ebene Platte (13 × 13 Punkte, Dreiecke — ihr Rand ist der offene Rand des Stücks), eine Walze (Radius 15 mm, 9 cm lang) schräg nach
vorn und unten aus der Platte (Achse (0, −0,3, 0,95), Wurzel (0, 0,02, 0)) und eine Kugel (Radius 3 cm) dahinter und darunter als Hoden. Die Zahlen
sind von der Fläche gemessen (Wegwerfskript `penis_kunstflaeche.py`, 10.10.2026), nicht an einem echten Penis — der erste Lauf mit der
BodyParts3D-Haut steht in `recherche-modelle-internet.md`.

1. Der Katalog führt 10 Regler, alle `pen_…`, mit bekannten Arten; jeder Regler hat Deltas der Länge der Punkte. (Der zehnte, `pen_hoden_asymmetrie`, kam
   am 10.10.2026 mit dem Daz-Geograft: Dazs „Testes Asymmetry" — der linke Hoden (+x) tiefer, der rechte höher; Fall 9.)
2. Die Form wird erkannt: Achse (unter 8° daneben), Länge (über 7,5 cm, höchstens 9,5), Radius (15 mm ± 4), Wurzel (unter 1 cm daneben).
3. Ohne offenen Rand und ohne Anbau gibt es `ValueError` statt stiller Nullen.
4. Die Platte (die Haut am Rand) bewegt sich bei KEINEM Regler.
5. Länge: kein Punkt wandert gegen die Achse, die Wurzel bleibt, die Spitze zieht um etwa 20 % der Länge mit.
6. Neigung plus hebt die Spitze.
7. Die Hoden-Regler bewegen den Schaft nicht (unter 1 mm), der Penis-Regler Länge nicht die Platte.
8. Erektion (Wert 1): die Spitze liegt im Winkel `ERKT_WINKEL` (74,3°, gegen senkrecht oben), der Schaft ist um das Verhältnis der Literatur länger (13,12 / 9,16 =
   1,43) und dicker (11,66 / 9,31 = 1,25); die Kugel (Hoden) und die Wurzel bleiben; der Regler läuft von 0 bis 1. Gemessen an der Kunstfläche
   (`penis_erekt_testzahlen.py`, 10.10.2026): Spitze 74,8°, Länge x1,448, Radius x1,274 (die Wurzel liegt 5 mm daneben), Kugel 0,0 mm, Wurzel 0,07 mm.
   Am BodyParts3D-Stück (`erekt_masse.py`): äußerster Punkt 64,8 → 92,7 mm (x1,43), 76,0°, Radius x1,254.

Sabotage-Gegenprobe: `anbau` in `gewichte` auf 1 setzen macht Fall 4 rot; `winkel = -np.radians` zu `+` macht Fall 6 rot; `AUSSCHLUSS_RADIEN` auf `WALZE_RADIEN`
macht Fall 7 rot; die Mitte der Kappe (`KAPPE_M`) durch den höchsten Einzelpunkt ersetzen macht Fall 2 rot (Achse 12–29° daneben).

Nicht gelaufen (Stand 10.10.2026) — läuft nur auf Ansage.
"""
import numpy as np
from django.test import SimpleTestCase
from Genesis9.penismorphe import G9penismorphe
from Genesis9.penismorphekatalog import G9penismorphekatalog as K

N = 13
PLATTE = N * N
WALZE = 25 * 10
ACHSE = np.array([0.0, -0.3, 0.95]) / np.linalg.norm([0.0, -0.3, 0.95])
WURZEL = np.array([0.0, 0.02, 0.0])
LAENGE = 0.09


def kunstflaeche():
    g = np.linspace(-0.06, 0.06, N)
    platte = np.array([[x, y, 0.0] for y in g for x in g])
    polys = []
    for j in range(N - 1):
        for i in range(N - 1):
            a, b, c, d = j * N + i, j * N + i + 1, (j + 1) * N + i + 1, (j + 1) * N + i
            polys += [[0, 0, a, b, c], [0, 0, a, c, d]]
    walze = [WURZEL + ACHSE * t + np.array([np.cos(w), np.sin(w), 0.0]) * 0.015
             for t in np.linspace(0.0, LAENGE, 25) for w in np.linspace(0, 2 * np.pi, 10, endpoint=False)]
    kugel = [np.array([0.0, -0.075, 0.032]) + 0.03 * np.array([np.sin(th) * np.cos(w), np.sin(th) * np.sin(w), np.cos(th)])
             for th in np.linspace(0, np.pi, 12) for w in np.linspace(0, 2 * np.pi, 12, endpoint=False)]
    return np.vstack([platte, walze, kugel]), polys


class PenismorpheTest(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.p, cls.polys = kunstflaeche()

    def _deltas(self, name):
        return G9penismorphe.deltas(self.p, self.polys, K.eintrag(name))

    def test_1_der_katalog_fuehrt_zehn_regler_mit_bekannten_arten(self):
        self.assertEqual(len(K.EINTRAEGE), 10)
        self.assertEqual(len({e[0] for e in K.EINTRAEGE}), 10, 'Namen eindeutig')
        for e in K.EINTRAEGE:
            self.assertTrue(K.ist_penis(e[0]), e[0])
            self.assertIn(e[4], K.ARTEN, e[0])
            self.assertIn(e[3], K.ZONEN, e[0])
            self.assertEqual(self._deltas(e[0]).shape, self.p.shape, e[0])
        with self.assertRaises(ValueError):
            K.eintrag('sch_gesamt_fuelle')

    def test_2_die_form_wird_erkannt(self):
        k = G9penismorphe.koordinaten(self.p, self.polys)
        winkel = np.degrees(np.arccos(np.clip(float(k['achse'] @ ACHSE), -1, 1)))
        self.assertLess(winkel, 8.0)
        # Gemessen an dieser Fläche: Achse 3,2° daneben, Länge 83,7 mm von 90 (der Kern beginnt erst 12 mm über der Haut, `_sockel` holt den Rest
        # bis 6 mm Höhe zurück; ohne das 70,5 mm), Radius 16,7 mm, Wurzel 5,4 mm daneben (ohne `_sockel` 16 mm).
        self.assertGreater(float(k['laenge']), 0.075)
        self.assertLess(float(k['laenge']), LAENGE + 0.005)
        self.assertAlmostEqual(k['radius'], 0.015, delta=0.004)
        self.assertLess(float(np.linalg.norm(k['wurzel'] - WURZEL)), 0.010)

    def test_3_ohne_rand_und_ohne_anbau_gibt_es_einen_fehler(self):
        with self.assertRaises(ValueError):
            G9penismorphe.koordinaten(self.p, [])                    # keine Vielecke = kein offener Rand
        with self.assertRaises(ValueError):
            G9penismorphe.koordinaten(self.p[:PLATTE], self.polys)   # nur die Platte: kein Anbau

    def test_4_die_platte_bewegt_sich_bei_keinem_regler(self):
        for e in K.EINTRAEGE:
            self.assertLess(float(np.abs(self._deltas(e[0])[:PLATTE]).max()), 1e-9, e[0])

    def test_5_laenge_zieht_die_spitze_mit_und_laesst_die_wurzel(self):
        d = self._deltas('pen_laenge')[PLATTE:PLATTE + WALZE]
        t = (self.p[PLATTE:PLATTE + WALZE] - WURZEL) @ ACHSE
        self.assertGreaterEqual(float((d @ ACHSE).min()), -1e-9, 'kein Punkt wandert gegen die Achse')
        self.assertLess(float(np.linalg.norm(d[t < 0.006], axis=1).max()), 0.001, 'die Wurzel bleibt')
        spitze = float(np.linalg.norm(d[t > LAENGE - 0.01], axis=1).mean())
        self.assertGreater(spitze, 0.008)                            # 20 % der gemessenen Länge (84 mm) wären 17 mm; die Punkte am Rand der Walze wiegen weniger (gemessen 12,7 mm)
        self.assertLess(spitze, 0.024)

    def test_6_neigung_plus_hebt_die_spitze(self):
        d = self._deltas('pen_neigung')[PLATTE:PLATTE + WALZE]
        t = (self.p[PLATTE:PLATTE + WALZE] - WURZEL) @ ACHSE
        self.assertGreater(float(d[t > LAENGE - 0.01][:, 1].mean()), 0.005)

    def test_7_die_hoden_regler_lassen_den_schaft_in_ruhe(self):
        t = (self.p[PLATTE:PLATTE + WALZE] - WURZEL) @ ACHSE
        for name in ('pen_hoden_groesse', 'pen_hoden_tiefer', 'pen_hoden_abstand', 'pen_hoden_vor'):
            d = self._deltas(name)[PLATTE:PLATTE + WALZE][t > 0.03]
            self.assertLess(float(np.linalg.norm(d, axis=1).max()), 0.001, name)

    def test_8_erektion_stellt_winkel_laenge_und_umfang_der_literatur_ein(self):
        d = self._deltas('pen_erektion')
        walze = slice(PLATTE, PLATTE + WALZE)
        t = (self.p[walze] - WURZEL) @ ACHSE
        neu = self.p + d
        vor = self.p[walze][t > LAENGE - 0.01].mean(axis=0) - WURZEL
        nach = neu[walze][t > LAENGE - 0.01].mean(axis=0) - WURZEL
        winkel = float(np.degrees(np.arccos(nach[1] / np.linalg.norm(nach))))
        self.assertAlmostEqual(winkel, G9penismorphe.ERKT_WINKEL, delta=3.0)
        self.assertAlmostEqual(float(np.linalg.norm(nach) / np.linalg.norm(vor)), 1.0 + G9penismorphe.ERKT_LAENGE, delta=0.06)
        mitte = (t > 0.03) & (t < 0.06)
        rel0, rel1 = self.p[walze][mitte] - WURZEL, neu[walze][mitte] - WURZEL
        ziel = np.array([0.0, np.cos(np.radians(G9penismorphe.ERKT_WINKEL)), np.sin(np.radians(G9penismorphe.ERKT_WINKEL))])
        r0 = np.linalg.norm(rel0 - np.outer(rel0 @ ACHSE, ACHSE), axis=1).mean()
        r1 = np.linalg.norm(rel1 - np.outer(rel1 @ ziel, ziel), axis=1).mean()
        self.assertAlmostEqual(float(r1 / r0), 1.0 + G9penismorphe.ERKT_UMFANG, delta=0.05)
        self.assertLess(float(np.linalg.norm(d[PLATTE + WALZE:], axis=1).max()), 0.001, 'die Hoden bleiben')
        self.assertLess(float(np.linalg.norm(d[walze][t < 0.006], axis=1).max()), 0.001, 'die Wurzel bleibt')
        grenzen = [(r['min'], r['max']) for r in G9penismorphe.regler() if r['name'].endswith('pen_erektion')]
        self.assertEqual(grenzen, [(0.0, 1.0)])

    def test_9_asymmetrie_senkt_den_linken_hoden_und_hebt_den_rechten(self):
        d = self._deltas('pen_hoden_asymmetrie')
        kugel = slice(PLATTE + WALZE, None)
        x = self.p[kugel][:, 0]
        self.assertLess(float(d[kugel][x > 0.015][:, 1].mean()), -0.003, 'links (+x) tiefer')
        self.assertGreater(float(d[kugel][x < -0.015][:, 1].mean()), 0.003, 'rechts höher')
        self.assertLess(float(np.abs(d[kugel]).max()), 0.0065, 'höchstens der Betrag des Katalogs (6 mm)')
        t = (self.p[PLATTE:PLATTE + WALZE] - WURZEL) @ ACHSE
        self.assertLess(float(np.linalg.norm(d[PLATTE:PLATTE + WALZE][t > 0.03], axis=1).max()), 0.001, 'der Schaft bleibt')
