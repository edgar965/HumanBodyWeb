# -*- coding: utf-8 -*-
"""`Dazgeograftverfeinerung` — das angepasste Daz-Netz beidseitig an die Original-Scham heranziehen (10.10.2026), an Kunstflächen.

Gemessen nach dem ersten Schritt der Anpassung (Strahlen längs der Haut): das Daz-Netz lag zu 97 % auf dem Original, aber umgekehrt lag die Hälfte der Original-Punkte mehr als 1,7 mm vom Netz,
ein Prozent bis 17 mm — die tiefen Teile erreicht ein Strahl von vorn nicht. Hier ziehen auch die Punkte des Originals (rückwärts); jeder Durchgang prüft das Umklappen und halbiert den Schritt.

Kunstwelt: Netz = Quadrat 40 mm, 11 × 11 Punkte (Abstand 4 mm) in z = 0, Ring = Rand (fest); Original = feine Platte bei z = +4 mm (Abstand 1 mm), beide Normalen +z.

1. `verfeinern` zieht das Netz auf das Original: die Mitte liegt danach höchstens 1 mm daneben (vorher 4 mm), der Ring bleibt bei z = 0, kein Dreieck klappt um.
2. Der Bericht trägt die Durchgänge (Steifigkeit, Reichweite sinken), `original_zu_netz_mm` und `netz_zu_original_mm` als Perzentile.
3. `_umgeklappt`: tauscht man zwei Punkte eines Dreiecks, zählt genau dieses eine; ein unverändertes Netz hat null.
4. `_normalen` dreht die Normalen zur Seite von `aussen`: ein Netz mit umgekehrter Wicklung liefert trotzdem nach außen zeigende Normalen.
5. Die Normalenprüfung wirkt: steht das Original senkrecht zu den Normalen des Netzes (Platte um 90° gekippt), zieht das Netz nicht dorthin (`NORMALE_GRAD` 60°) — die Mitte bleibt bei z = 0.

Sabotage-Gegenprobe (11.10.2026 im Speicher gelaufen, `ProjektTemp/_wegwerf/sabotage.py`: mit der Sabotage rot, ohne grün — Wortlaut als Quelltext-Änderung ungelaufen): in `verfeinern` `w[rand], ziel[rand] = …` weglassen macht Fall 1 rot (der Ring wandert); `NORMALE_GRAD` auf 180 macht Fall 5 rot.
"""
from unittest import mock

import numpy as np
import trimesh
from django.test import SimpleTestCase

from core.dienste.dazgeograftanpassung import Dazgeograftanpassung
from core.dienste.dazgeograftverfeinerung import Dazgeograftverfeinerung


class DazgeograftverfeinerungTest(SimpleTestCase):
    databases = set()

    K = 11

    def _netz(self):
        k = self.K
        punkte = np.array([[(i - 5) * 0.004, (j - 5) * 0.004, 0.0] for j in range(k) for i in range(k)])
        dreiecke = []
        for j in range(k - 1):
            for i in range(k - 1):
                a = j * k + i
                dreiecke += [[a, a + 1, a + k + 1], [a, a + k + 1, a + k]]
        rand = np.array([i in (0, k - 1) or j in (0, k - 1) for j in range(k) for i in range(k)])
        return punkte, np.array(dreiecke, dtype=np.int64), rand

    @staticmethod
    def _original(hoehe=0.004, kippen_grad=0.0, versatz_y=0.0):
        """Feine Platte 80 × 80 mm (Abstand 1 mm), bei z = `hoehe`, um die x-Achse um `kippen_grad` gekippt (90°: eine Wand bei y = `versatz_y`)."""
        n = 81
        w = np.radians(kippen_grad)
        x, y = np.meshgrid((np.arange(n) - 40) * 0.001, (np.arange(n) - 40) * 0.001)
        punkte = np.column_stack([x.ravel(), versatz_y + y.ravel() * np.cos(w), hoehe + y.ravel() * np.sin(w)])
        dreiecke = []
        for j in range(n - 1):
            for i in range(n - 1):
                a = j * n + i
                dreiecke += [[a, a + 1, a + n + 1], [a, a + n + 1, a + n]]
        return trimesh.Trimesh(punkte, np.array(dreiecke), process=False)

    def _lauf(self, original, plan=((3.0, 0.012), (2.0, 0.009), (1.4, 0.007), (1.0, 0.005))):
        punkte, dreiecke, rand = self._netz()
        aussen = np.tile([0.0, 0.0, 1.0], (len(punkte), 1))
        laplace = Dazgeograftanpassung._laplace(dreiecke, len(punkte))
        q, bericht = Dazgeograftverfeinerung.verfeinern(punkte, punkte.copy(), dreiecke, rand, laplace, original, aussen, plan=plan)
        return punkte, dreiecke, rand, q, bericht

    def test_1_das_netz_geht_aufs_original_und_der_ring_bleibt(self):
        punkte, dreiecke, rand, q, _b = self._lauf(self._original())
        mitte = 5 * self.K + 5
        self.assertLess(abs(float(q[mitte, 2]) - 0.004), 0.001)
        self.assertLess(float(np.abs(q[rand, 2]).max()), 0.0002, 'der Ring bleibt, wo die Haut ist (Gewicht 100 gegen die Steifigkeit: bis 0,05 mm Spiel gemessen)')
        self.assertEqual(Dazgeograftverfeinerung._umgeklappt(q, dreiecke, punkte), 0)

    def test_2_der_bericht_traegt_durchgaenge_und_abstaende(self):
        _p, _d, _r, _q, bericht = self._lauf(self._original())
        self.assertEqual(len(bericht['durchgaenge']), 4)
        steif = [d['a'] for d in bericht['durchgaenge']]
        self.assertEqual(steif, sorted(steif, reverse=True))
        for schluessel in ('original_zu_netz_mm', 'netz_zu_original_mm'):
            self.assertEqual(len(bericht[schluessel]), 3)
            self.assertLessEqual(bericht[schluessel][0], bericht[schluessel][2])
        self.assertEqual(bericht['umgeklappt'], 0)

    def test_3_umgeklappte_dreiecke_werden_gezaehlt(self):
        punkte, dreiecke, _rand = self._netz()
        self.assertEqual(Dazgeograftverfeinerung._umgeklappt(punkte, dreiecke, punkte), 0)
        neu = punkte.copy()
        a, b = int(dreiecke[7, 0]), int(dreiecke[7, 1])
        neu[[a, b]] = neu[[b, a]]                              # zwei Ecken des Dreiecks 7 vertauscht: es zeigt nach unten
        self.assertGreaterEqual(Dazgeograftverfeinerung._umgeklappt(neu, dreiecke, punkte), 1)

    def test_4_die_normalen_zeigen_zur_seite_von_aussen(self):
        punkte, dreiecke, _rand = self._netz()
        aussen = np.tile([0.0, 0.0, 1.0], (len(punkte), 1))
        for d in (dreiecke, dreiecke[:, ::-1]):
            n = Dazgeograftverfeinerung._normalen(punkte, d, aussen)
            self.assertGreater(float(n[:, 2].min()), 0.99)

    def test_5_ein_senkrecht_stehendes_original_zieht_nicht(self):
        """Eine Wand 3 mm neben der Mitte (Normale ±y, senkrecht zur Normale +z des Netzes): innerhalb der Reichweite, aber um 90° verdreht."""
        mitte = 5 * self.K + 5
        wand = dict(hoehe=0.0, kippen_grad=90.0, versatz_y=0.003)
        _p, _d, _r, q, _b = self._lauf(self._original(**wand))
        self.assertLess(abs(float(q[mitte, 1])), 0.0005, 'Normalen um 90° auseinander: kein Treffer, das Netz bleibt')
        with mock.patch.object(Dazgeograftverfeinerung, 'NORMALE_GRAD', 180.0):
            _p, _d, _r, q2, _b = self._lauf(self._original(**wand))
        self.assertGreater(abs(float(q2[mitte, 1])), 0.001, 'die Gegenprobe: ohne Prüfung zieht die Wand das Netz zu sich')
