# -*- coding: utf-8 -*-
"""`Exportleistehautmaske` — die Haut unter den Stücken fällt aus dem Körper des Renders (31.10.2026).

Am Kunstkörper (Zylinder 10 cm, Gruppe „unten“ und „oben“ je eine Hälfte): Ein Stück über die untere Hälfte nimmt dort die Dreiecke heraus, die
Gruppen zeigen danach auf ihre Abschnitte, ohne Stück bleibt das Netz, wie es war. Und die UV-Naht: Ein Stück aus einer GLB hat an jeder Naht
doppelte Punkte; unverschweißt ist die Naht ein lockerer Rand, und zwei Ringe Haut daneben blieben als Streifen unter dem Stoff stehen.

Sabotage-Gegenprobe: in `Exportleistehautmaske.koerper` `cls.verschweissen(p, d)` durch `(p, d)` ersetzt → `test_die_uv_naht_laesst_keinen_streifen` rot.
"""

import numpy as np
from django.test import SimpleTestCase

from core.dienste.exportleistehautmaske import Exportleistehautmaske

from ._kunstkoerper import Kunstkoerper


class ExportleistehautmaskeTest(SimpleTestCase):
    databases = set()
    RINGE, N = 51, 36

    def setUp(self):
        P, T = Kunstkoerper.zylinder(0.10, 0.0, 1.0, self.RINGE, self.N)
        haelfte = len(T) // 2 * 3                                        # die Dreiecke liegen Ring für Ring von unten nach oben
        self.netz = {'punkte': P, 'dreiecke': T.reshape(-1), 'gruppen': [{'material': 'unten', 'index_ab': 0, 'index_anzahl': haelfte},
                                                                         {'material': 'oben', 'index_ab': haelfte, 'index_anzahl': haelfte}]}

    @staticmethod
    def _naht_zylinder(radius, y0, y1, ringe, n):
        """Wie `Kunstkoerper.zylinder`, aber mit UV-Naht: je Ring n + 1 Punkte, der letzte liegt auf dem ersten."""
        P = [(radius * np.cos(2 * np.pi * i / n), y0 + (y1 - y0) * r / (ringe - 1), radius * np.sin(2 * np.pi * i / n)) for r in range(ringe) for i in range(n + 1)]
        T = []
        for r in range(ringe - 1):
            for i in range(n):
                a, c = r * (n + 1) + i, (r + 1) * (n + 1) + i
                T += [(a, c, a + 1), (a + 1, c, c + 1)]
        return np.array(P), np.array(T)

    def _mitte_weg(self, neu):
        """Bleibt ein Dreieck, das ganz unter der Mitte des Stücks liegt (y 0,15 … 0,35)?"""
        y = np.asarray(self.netz['punkte'])[:, 1]
        bleibt = np.asarray(neu['dreiecke']).reshape(-1, 3)
        return int(((y[bleibt] > 0.15) & (y[bleibt] < 0.35)).all(axis=1).sum())

    def test_ohne_stueck_bleibt_das_netz(self):
        neu, bericht = Exportleistehautmaske.koerper(self.netz, [])
        self.assertIs(neu, self.netz)
        self.assertEqual(bericht['dreiecke_weg'], 0)

    def test_das_stueck_nimmt_die_haut_darunter_heraus_und_die_gruppen_folgen(self):
        stoff = Kunstkoerper.zylinder(0.102, 0.05, 0.45, 41, self.N)
        neu, bericht = Exportleistehautmaske.koerper(self.netz, [stoff])
        T = np.asarray(self.netz['dreiecke']).reshape(-1, 3)
        bleibt = np.asarray(neu['dreiecke']).reshape(-1, 3)
        self.assertEqual(np.ndim(neu['dreiecke']), 1)
        self.assertGreater(bericht['dreiecke_weg'], 1000)
        self.assertEqual(len(bleibt) + bericht['dreiecke_weg'], len(T))
        self.assertEqual(self._mitte_weg(neu), 0)
        unten, oben = neu['gruppen']
        self.assertEqual((unten['index_ab'], oben['index_ab']), (0, unten['index_anzahl']))
        self.assertEqual(unten['index_anzahl'] + oben['index_anzahl'], len(bleibt) * 3)
        self.assertEqual(oben['material'], 'oben')
        # die obere Hälfte liegt nicht unter dem Stück: ihr Abschnitt ist Dreieck für Dreieck der alte
        np.testing.assert_array_equal(bleibt[oben['index_ab'] // 3:], T[len(T) // 2:])

    def test_die_uv_naht_laesst_keinen_streifen(self):
        stoff = self._naht_zylinder(0.110, 0.05, 0.45, 41, self.N)        # 10 mm über der Haut: die Kanten sind locker
        neu, bericht = Exportleistehautmaske.koerper(self.netz, [stoff])
        self.assertGreater(bericht['dreiecke_weg'], 1000)
        self.assertEqual(self._mitte_weg(neu), 0)
