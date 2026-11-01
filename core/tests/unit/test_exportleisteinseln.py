# -*- coding: utf-8 -*-
"""`Exportleisteinseln` — freie Inseln schließen wie der Browser (`maskeninseln.js`; 31.10.2026).

Kunstnetz: ein Gitter 60 × 60 Punkte (Abstand 1 mm bzw. 1 cm), dazu ein eigenes kleines Teil ohne Verbindung (Zähne, Nägel hinter einer Naht). Verdeckt ist ein Rahmen im Gitter,
frei bleibt sein Inneres (die Achselfalte unter dem Ärmel) und alles außen.

Sabotage-Gegenprobe (31.10.2026): in `Exportleisteinseln.schliessen` `& kueste` gestrichen → `test_ein_teil_ohne_kueste_bleibt_frei` rot; `klein |= …` (Fläche) gestrichen →
`test_eine_grosse_insel_mit_kleiner_flaeche_schliesst` rot.
"""

import numpy as np
from django.test import SimpleTestCase

from core.dienste.exportleisteinseln import Exportleisteinseln


class ExportleisteinselnTest(SimpleTestCase):
    databases = set()
    N = 60

    @classmethod
    def _gitter(cls, abstand):
        n = cls.N
        P = np.array([(i * abstand, j * abstand, 0.0) for j in range(n) for i in range(n)])
        T = []
        for j in range(n - 1):
            for i in range(n - 1):
                a = j * n + i
                T += [(a, a + 1, a + n), (a + 1, a + n + 1, a + n)]
        return P, np.array(T)

    @classmethod
    def _netz(cls, abstand, innen):
        """Gitter mit verdecktem Rahmen um ein freies Inneres von `innen` × `innen` Punkten, dazu ein freies Teil (3 × 3 Punkte) ohne Verbindung."""
        P, T = cls._gitter(abstand)
        n, a = cls.N, (cls.N - innen) // 2
        ij = np.stack(np.meshgrid(np.arange(n), np.arange(n), indexing='xy'), -1).reshape(-1, 2)
        rahmen = ((ij >= a - 2) & (ij < a + innen + 2)).all(axis=1) & ~((ij >= a) & (ij < a + innen)).all(axis=1)
        teil_p, teil_t = cls._gitter(abstand)
        waehle = (np.arange(len(teil_p)) % n < 3) & (np.arange(len(teil_p)) // n < 3)
        alt = np.flatnonzero(waehle)
        neu = np.full(len(teil_p), -1)
        neu[alt] = np.arange(len(alt)) + len(P)
        tt = neu[teil_t[waehle[teil_t].all(axis=1)]]
        P = np.vstack([P, teil_p[alt] + [0, 0, 1.0]])
        T = np.vstack([T, tt])
        maske = np.concatenate([rahmen, np.zeros(len(alt), dtype=bool)])
        innen_wahl = np.concatenate([((ij >= a) & (ij < a + innen)).all(axis=1), np.zeros(len(alt), dtype=bool)])
        teil = np.concatenate([np.zeros(n * n, dtype=bool), np.ones(len(alt), dtype=bool)])
        return P, T, maske, innen_wahl, teil

    def test_eine_kleine_insel_im_verdeckten_schliesst(self):
        P, T, maske, innen, _ = self._netz(0.01, 10)                     # 100 Punkte, 0,8 dm²
        Exportleisteinseln.schliessen(maske, P, T)
        self.assertTrue(maske[innen].all())

    def test_ein_teil_ohne_kueste_bleibt_frei(self):
        P, T, maske, _, teil = self._netz(0.01, 10)
        Exportleisteinseln.schliessen(maske, P, T)
        self.assertFalse(maske[teil].any())

    def test_die_groesste_freie_gruppe_bleibt(self):
        P, T, maske, _, _ = self._netz(0.01, 10)
        vorher = maske.copy()
        Exportleisteinseln.schliessen(maske, P, T)
        self.assertEqual(int((~maske).sum()), int((~vorher).sum()) - 100)

    def test_eine_grosse_insel_mit_kleiner_flaeche_schliesst(self):
        P, T, maske, innen, _ = self._netz(0.001, 20)                    # 400 Punkte, aber nur 3,6 cm²
        nur_punkte = maske.copy()
        Exportleisteinseln.schliessen(nur_punkte, P, T, flaeche_max=0)
        self.assertFalse(nur_punkte[innen].any())
        Exportleisteinseln.schliessen(maske, P, T)
        self.assertTrue(maske[innen].all())

    def test_eine_grosse_insel_mit_grosser_flaeche_bleibt(self):
        P, T, maske, innen, _ = self._netz(0.01, 20)                     # 400 Punkte, 3,6 dm²
        Exportleisteinseln.schliessen(maske, P, T)
        self.assertFalse(maske[innen].any())
