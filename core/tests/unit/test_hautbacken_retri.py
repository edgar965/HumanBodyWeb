# -*- coding: utf-8 -*-
"""Hautbackenretri — die Dreiecke der Vierecke in der Ruhelage, wie Blender sie dort bildet (Edgar, 10.10.2026: „ich möchte blender für alle Usecases ersetzt haben").

Blender zerlegt ein Viereck nach den Punkten, die der Körper beim Backen hat: (0, 1, 2) + (0, 2, 3), außer die Ecken liegen so, dass die Diagonale 0–2 aus dem Viereck fällt —
dann (0, 1, 3) + (1, 2, 3) (`corner_tris_calc`, `is_quad_flip_v3_first_third_fast`, v5.2.2). Der Export hat die Zerlegung der Pose, in der er entstand. Gemessen am 11.10.2026 an
hinako (1.328 von 41.112 Vierecken wechseln in der Ruhelage): ohne den Wechsel wichen 6 % der Texel von Blender ab (Rauheit, auch gegen Blender auf der CPU), mit ihm 0,002 %.

Der Test baut ein Netz aus zwei Vierecken und einem Dreieck wie der Export (`dreieck_poly`, `poly_start`, `poly_punkte`, Arrays je Dreiecksecke) und prüft:
1. Bleibt die Zerlegung gleich, kommen dieselben Arrays zurück (nichts wird kopiert, nichts verschoben).
2. Wechselt ein Viereck (die Ecke 2 über die Gegenseite hinaus gezogen = Diagonale 0–2 liegt außen), zeigen die neuen Dreiecke (0, 1, 3) + (1, 2, 3), und JEDES Array je Dreiecksecke (UV, Farbe,
   Schleifennummer) folgt seinen Ecken: der Wert einer Ecke hängt an der Schleife, nicht am Platz.
3. Der Weg zurück (Export in der gewechselten Zerlegung, Ruhelage wieder konvex) ergibt wieder (0, 1, 2) + (0, 2, 3).
4. Dreiecke und Polygone mit mehr als vier Ecken bleiben; ihre Zahl steht im Bericht (die Zerlegung mit `BLI_polyfill_calc` ist nicht nachgebaut).
5. Eine ungeordnete Zerlegung des Exports ist ein Fehler, keine stille Annahme.
6. Die Regel selbst (`wechselt`) an Hand gerechneten Fällen: konvexes Viereck nein, Ecke 2 nur nach innen gezogen nein, Ecke 2 über die Gegenseite hinaus gezogen ja.

Sabotage-Gegenprobe (11.10.2026, danach rückgängig): in `wechselt` `> 0` → `< 0` → Fall 1, 2, 3, 4 und 6 rot; in `ORT` die Quelle der Schleife 3 bei Zerlegung 0 von (Dreieck b, Ecke 2) auf
(b, 1) → Fall 2 rot.
"""

import numpy as np
from django.test import SimpleTestCase

from core.dienste.hautbacken.hautbackenretri import Hautbackenretri


def _netz(zerlegung):
    """Export-Arrays für Viereck A (Punkte 0–3), Dreieck (4, 5, 6) und Viereck B (7–10); `zerlegung`: (A, B) mit 0 = (0,1,2)+(0,2,3), 1 = (0,1,3)+(1,2,3)."""
    poly_start = np.array([0, 4, 7, 11])
    poly_punkte = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    schleifen = {0: [(0, 1, 2), (0, 2, 3)], 1: [(0, 1, 3), (1, 2, 3)]}
    tris, poly, loops = [], [], []
    for p, z in ((0, zerlegung[0]), (1, None), (2, zerlegung[1])):
        start = poly_start[p]
        if z is None:
            loops += [(start, start + 1, start + 2)]
            poly += [p]
        else:
            loops += [tuple(start + k for k in tri) for tri in schleifen[z]]
            poly += [p, p]
    loops = np.array(loops)
    return {
        'poly_start': poly_start, 'poly_punkte': poly_punkte, 'dreieck_poly': np.array(poly),
        'dreiecke': poly_punkte[loops], 'dreieck_ecken': loops,
        'uv_ecken': np.stack([loops.astype(np.float64), loops * 2.0], axis=-1),                    # der Wert einer Ecke trägt ihre Schleifennummer
        'uv_0': np.stack([loops.astype(np.float32), -loops.astype(np.float32)], axis=-1),
        'farbe_0': np.stack([loops, loops, loops, loops], axis=-1).astype(np.float32),
        'glatt': np.ones(len(loops), bool), 'material': np.zeros(len(loops), np.int64),
    }


def _punkte(a_konvex=True, b_konvex=True):
    """11 Punkte: Viereck A (0–3), Dreieck (4–6), Viereck B (7–10). Konkav = Ecke 2 über die Gegenseite hinaus gezogen (dann liegt die Diagonale 0–2 außerhalb)."""
    p = np.zeros((11, 3))
    quad = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], dtype=float)
    konkav = quad.copy()
    konkav[2] = [-0.5, 0.2, 0]                         # Ecke 2 über die Gegenseite hinaus gezogen: v2 und v4 liegen auf derselben Seite der Diagonale 0–2
    p[0:4] = quad if a_konvex else konkav
    p[4:7] = [[3, 0, 0], [4, 0, 0], [3, 1, 0]]
    p[7:11] = (quad if b_konvex else konkav) + [6, 0, 0]
    return p


class RetriTest(SimpleTestCase):
    databases = set()

    def test_1_gleiche_zerlegung_aendert_nichts(self):
        npz = _netz((0, 0))
        neu, bericht = Hautbackenretri.neu(npz, _punkte())
        self.assertEqual(bericht, {'vierecke': 2, 'gewechselt': 0, 'ngone': 0})
        self.assertIs(neu, npz)

    def test_2_ein_gewechseltes_viereck_nimmt_die_andere_diagonale_und_alle_arrays_folgen(self):
        npz = _netz((0, 0))
        original = {k: v.copy() for k, v in npz.items()}
        neu, bericht = Hautbackenretri.neu(npz, _punkte(b_konvex=False))
        self.assertEqual(bericht['gewechselt'], 1)
        # Viereck B hat die Dreiecke 3 und 4 (Schleifen 7–10 = Punkte 7–10): jetzt (0,1,3) + (1,2,3)
        self.assertEqual(neu['dreieck_ecken'][3].tolist(), [7, 8, 10])
        self.assertEqual(neu['dreieck_ecken'][4].tolist(), [8, 9, 10])
        self.assertEqual(neu['dreiecke'][3].tolist(), [7, 8, 10])
        self.assertEqual(neu['dreiecke'][4].tolist(), [8, 9, 10])
        # jedes Array trägt je Ecke die Schleifennummer: dieselben Zahlen wie `dreieck_ecken`
        self.assertTrue(np.array_equal(neu['uv_ecken'][..., 0], neu['dreieck_ecken'].astype(np.float64)))
        self.assertTrue(np.array_equal(neu['uv_ecken'][..., 1], neu['dreieck_ecken'] * 2.0))
        self.assertTrue(np.array_equal(neu['uv_0'][..., 0], neu['dreieck_ecken'].astype(np.float32)))
        self.assertTrue(np.array_equal(neu['farbe_0'][..., 2], neu['dreieck_ecken'].astype(np.float32)))
        # Viereck A, das Dreieck und die Zeilen je Polygon blieben, die Eingabe wurde nicht verändert
        for k in ('dreiecke', 'uv_ecken', 'dreieck_ecken'):
            self.assertTrue(np.array_equal(neu[k][:3], original[k][:3]), k)
            self.assertTrue(np.array_equal(npz[k], original[k]), 'die Eingabe bleibt: %s' % k)
        self.assertTrue(np.array_equal(neu['dreieck_poly'], original['dreieck_poly']))

    def test_3_der_weg_zurueck(self):
        npz = _netz((1, 1))
        neu, bericht = Hautbackenretri.neu(npz, _punkte())
        self.assertEqual(bericht['gewechselt'], 2)
        self.assertEqual(neu['dreieck_ecken'].tolist(), [[0, 1, 2], [0, 2, 3], [4, 5, 6], [7, 8, 9], [7, 9, 10]])
        self.assertTrue(np.array_equal(neu['uv_ecken'][..., 0], neu['dreieck_ecken'].astype(np.float64)))

    def test_4_mehr_als_vier_ecken_bleiben_und_werden_gezaehlt(self):
        npz = _netz((0, 0))
        npz['poly_start'] = np.array([0, 4, 7, 12])               # das dritte Polygon hat jetzt fünf Ecken
        npz['poly_punkte'] = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
        _, bericht = Hautbackenretri.neu(npz, _punkte())
        self.assertEqual(bericht, {'vierecke': 1, 'gewechselt': 0, 'ngone': 1})

    def test_5_ungeordnete_zerlegung_ist_ein_fehler(self):
        npz = _netz((0, 0))
        npz['dreieck_poly'] = npz['dreieck_poly'][::-1].copy()
        with self.assertRaises(ValueError):
            Hautbackenretri.neu(npz, _punkte())

    def test_6_die_regel_an_gerechneten_faellen(self):
        quad = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], dtype=np.float32)
        innen = quad.copy()
        innen[2] = [0.3, 0.3, 0]
        self.assertFalse(bool(Hautbackenretri.wechselt(*(quad[i][None] for i in range(4)))[0]))
        # Von Hand: v1 = (0,0), v2 = (1,0), v3 = (0,3, 0,3), v4 = (0,1): d12 = (1,0), d13 = (0,3, 0,3), d14 = (0,1): cross_a = d12 × d13 = (0, 0, 0,3); cross_b = d14 × d13 = (0, 0, −0,3);
        # dot = −0,09 → nicht > 0: NICHT wechseln (die Ecke 2 ist nach innen gezogen, die Diagonale 0–2 liegt noch im Viereck). Hinter der Gegenseite: d13 = (−0,5, 0,2): cross_a = 0,2, cross_b = 0,5 → dot > 0: wechseln.
        self.assertFalse(bool(Hautbackenretri.wechselt(*(innen[i][None] for i in range(4)))[0]))
        hinter = quad.copy()
        hinter[2] = [-0.5, 0.2, 0]                                  # Ecke 2 über die Gegenseite hinaus: v2 und v4 auf derselben Seite der Diagonale 0–2
        self.assertTrue(bool(Hautbackenretri.wechselt(*(hinter[i][None] for i in range(4)))[0]))
