# -*- coding: utf-8 -*-
u"""Das Ende des Fusses im MakeHuman-Klon (`G9mhrahmen`, 18.10.2026).

Edgar: „Fitten von Schuhen funktioniert nicht für Matt1, … die Zehen gehen [durch] den Schuh". Der Fuss lief von `foot.L` zur
GROSSZEHE (`toe1-1.L`) und auf Genesis zur Mitte der Zehenreihe (`l_toes`) — 15 Grad Unterschied, jeder MakeHuman-Schuh stand nach
aussen gedreht. Jetzt endet er auf beiden Rigs in der Mitte der fuenf Zehengrundgelenke.

Kunstdaten, keine Bibliothek:

1. Die erste Achse des Fussrahmens zeigt auf die Mitte der fuenf Zehenkoepfe — auf beiden Rigs, auch wenn `l_toes` und die
   Grosszehe woanders liegen.
2. Die rechte Seite spiegelt auch die Tupel (`l_bigtoe1` -> `r_bigtoe1`, `toe1-1.L` -> `toe1-1.R`).
3. Fehlt einem Rig ein Zehenknochen, entfaellt das Glied (kein KeyError, kein Rahmen aus vier Zehen).
4. Die Finger (gleicher Tag, abends): das letzte Glied endet am `schwanz` des Knochens (`G9mhrahmen.ENDE`), links und rechts.
   Sabotage: in `kopf` das `ENDE` ignorieren (immer `kopf`) -> Laenge 0 -> Fall 4 rot.

Sabotage: in `GLIEDER['l_foot']` wieder `'l_toes'` / `'toe1-1.L'` eintragen -> Fall 1 rot.
Geschrieben 18.10.2026, nicht gelaufen.
"""
import numpy as np
from django.test import SimpleTestCase
from Genesis9.mhrahmen import G9mhrahmen


def rig(namen_koepfe):
    return {name: {'kopf': list(kopf)} for name, kopf in namen_koepfe.items()}


def zehen(namen, x0, z):
    u"""Fuenf Zehenkoepfe nebeneinander in x (Abstand 2 cm), alle auf derselben Hoehe."""
    return {name: (x0 + 0.02 * i, 0.02, z) for i, name in enumerate(namen)}


class G9mhrahmenFussTest(SimpleTestCase):

    def setUp(self):
        g9 = {'l_foot': (0.1, 0.07, -0.05), 'l_toes': (0.25, 0.02, 0.05)}       # l_toes absichtlich weit aussen
        g9.update(zehen(G9mhrahmen.ZEHEN_G9, 0.10, 0.09))
        mh = {'foot.L': (0.2, 0.07, 0.0)}
        mh.update(zehen(G9mhrahmen.ZEHEN_MH, 0.19, 0.14))
        self.g9, self.mh = rig(g9), rig(mh)

    def _achse_zeigt_auf(self, rahmen, kopf, ziel):
        weg = np.asarray(ziel) - np.asarray(kopf)
        np.testing.assert_allclose(rahmen[1][0], weg / np.linalg.norm(weg), atol=1e-9)
        self.assertAlmostEqual(rahmen[2], float(np.linalg.norm(weg)), places=9)

    def test_1_fussachse_endet_in_der_mitte_der_zehengrundgelenke(self):
        g, m = G9mhrahmen.glieder(self.g9, self.mh)['l_foot']
        mitte_g = np.mean([self.g9[n]['kopf'] for n in G9mhrahmen.ZEHEN_G9], axis=0)
        mitte_m = np.mean([self.mh[n]['kopf'] for n in G9mhrahmen.ZEHEN_MH], axis=0)
        self._achse_zeigt_auf(g, self.g9['l_foot']['kopf'], mitte_g)
        self._achse_zeigt_auf(m, self.mh['foot.L']['kopf'], mitte_m)

    def test_2_rechte_seite_spiegelt_auch_tupel(self):
        self.assertEqual(G9mhrahmen.rechts(('l_bigtoe1', 'toe1-1.L')), ('r_bigtoe1', 'toe1-1.R'))
        self.assertEqual(G9mhrahmen.rechts('foot.L'), 'foot.R')

    def test_3_fehlender_zeh_laesst_das_glied_weg(self):
        del self.mh['toe5-1.L']
        self.assertNotIn('l_foot', G9mhrahmen.glieder(self.g9, self.mh))

    def test_4_letztes_fingerglied_endet_am_ende_des_knochens(self):
        u"""Das letzte Glied laeuft vom Kopf bis zum `schwanz` (`ENDE`) — die Fingerspitze; beide Seiten."""
        g9 = {'l_index3': {'kopf': [0.60, 0.90, 0.06], 'schwanz': [0.62, 0.88, 0.06]}}
        mh = {'finger2-3.L': {'kopf': [0.45, 0.99, 0.30], 'schwanz': [0.45, 0.975, 0.315]}}
        g9.update({'r' + k[1:]: {kk: [-v[0], v[1], v[2]] for kk, v in w.items()} for k, w in g9.items()})
        mh.update({k.replace('.L', '.R'): {kk: [-v[0], v[1], v[2]] for kk, v in w.items()} for k, w in mh.items()})
        glieder = G9mhrahmen.glieder(g9, mh)
        for seite in ('l_index3', 'r_index3'):
            g, m = glieder[seite]
            self.assertAlmostEqual(g[2], float(np.linalg.norm([0.02, -0.02, 0.0])), places=9)
            self.assertAlmostEqual(m[2], float(np.linalg.norm([0.0, -0.015, 0.015])), places=9)
