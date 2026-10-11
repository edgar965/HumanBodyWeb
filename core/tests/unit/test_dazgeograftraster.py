# -*- coding: utf-8 -*-
"""`Dazgeograftraster` — die UV-Fläche eines Netzes in Texel zerlegen, mit dem Tangentenraum, den three.js beim Dekodieren einer Normalenkarte nimmt (11.10.2026), an einer Kunstplatte.

Befund am Daz-Stück „cute girl Daz Scham": der erste Bake nahm T = ∂p/∂u und B = N × T (eine Orthonormalbasis). three.js (r170, `getTangentFrame`, gelesen in `three.module.js`)
rechnet ohne Tangenten-Attribut je Dreieck T = (∂p/∂v) × N, B = N × (∂p/∂u), beide durch das Größere von |T|, |B| geteilt. Wo die UV gegen die Fläche geschert ist (am angepassten Stück
im Mittel 22°, p90 65°), liegen beide Räume weit auseinander: die Karte dekodierte um Median 9,6° (p90 27°) anders als gebacken — im Chrome die gefalteten Keile an der Naht.

Kunstplatte: Quadrat 40 mm in der Ebene z = 0, UV (x, y)/40 mm (v nach oben, wie Daz), Auflösung 32 × 32; geschert: u' = u + 0,5·v.

1. Bildpunkt (zeile, spalte) hat seine Mitte bei u = (spalte + 0,5)/R, v = 1 − (zeile + 0,5)/R: die Texelpositionen stimmen auf 1e-9 m; beinahe alle 1.024 Texel sind gedeckt.
2. Ohne Scherung ist der Tangentenraum die Standardbasis: T = (1, 0, 0), B = (0, 1, 0), N = (0, 0, 1).
3. Mit Scherung 0,5 rechnet three.js T = (0,894; 0,447; 0), B = (0; 0,894; 0) (von Hand: pu = (L, 0, 0), pv = (−L/2, L, 0) → T = pv × N = (L, L/2, 0), B = N × pu = (0, L, 0), durch 1,118·L geteilt) —
   und das ist 26,6° neben der alten Orthonormalbasis (T = (1, 0, 0)).
4. T und B stehen immer senkrecht auf N.
5. `dreieck` und `bary` gehören zu jedem Texel: die Schwerpunktkoordinaten ergeben 1 und die Lage zurück.
6. Ein Dreieck ohne UV-Fläche liefert keine Texel und keinen Fehler.
7. `auffuellen`: ein ungedeckter Texel nimmt den Wert des nächsten gedeckten.

Sabotage-Gegenprobe (11.10.2026 im Speicher gelaufen, `ProjektTemp/_wegwerf/sabotage.py`: mit der Sabotage rot, ohne grün — Wortlaut als Quelltext-Änderung ungelaufen): in `texel` `t_vek = pu` und `b_vek = cross(n, pu)` statt der three.js-Formel macht Fall 3 rot (die Scherung ist weg).
"""
import numpy as np
from django.test import SimpleTestCase

from core.dienste.dazgeograftraster import Dazgeograftraster

L = 0.040
R = 32


class DazgeograftrasterTest(SimpleTestCase):
    databases = set()

    def _platte(self, scherung=0.0):
        """`(punkte, dreiecke, uv_ecken, normalen)` der Kunstplatte; `scherung`: u' = u + scherung · v."""
        punkte = np.array([[0.0, 0.0, 0.0], [L, 0.0, 0.0], [L, L, 0.0], [0.0, L, 0.0]])
        dreiecke = np.array([[0, 1, 2], [0, 2, 3]])
        uv = np.column_stack([punkte[:, 0] / L + scherung * punkte[:, 1] / L, punkte[:, 1] / L])
        return punkte, dreiecke, uv[dreiecke], np.tile([0.0, 0.0, 1.0], (4, 1))

    def _texel(self, scherung=0.0):
        punkte, dreiecke, uv, normalen = self._platte(scherung)
        return Dazgeograftraster.texel(punkte, dreiecke, uv, R, normalen)

    def test_1_die_texelmitten_liegen_dort_wo_u_und_v_sie_hinlegen(self):
        t = self._texel()
        self.assertGreater(len(t['zeile']), 0.95 * R * R)
        erwartet_x = (t['spalte'] + 0.5) / R * L
        erwartet_y = (1.0 - (t['zeile'] + 0.5) / R) * L
        self.assertLess(float(np.abs(t['position'][:, 0] - erwartet_x).max()), 1e-9)
        self.assertLess(float(np.abs(t['position'][:, 1] - erwartet_y).max()), 1e-9)

    def test_2_ohne_scherung_ist_der_tangentenraum_die_standardbasis(self):
        t = self._texel()
        self.assertLess(float(np.abs(t['tangente'] - [1.0, 0.0, 0.0]).max()), 1e-9)
        self.assertLess(float(np.abs(t['bitangente'] - [0.0, 1.0, 0.0]).max()), 1e-9)
        self.assertLess(float(np.abs(t['normale'] - [0.0, 0.0, 1.0]).max()), 1e-9)

    def test_3_mit_scherung_gilt_die_formel_von_three_js_nicht_die_orthonormalbasis(self):
        t = self._texel(0.5)
        durch = np.sqrt(1.25)
        self.assertLess(float(np.abs(t['tangente'] - [1.0 / durch, 0.5 / durch, 0.0]).max()), 1e-9)
        self.assertLess(float(np.abs(t['bitangente'] - [0.0, 1.0 / durch, 0.0]).max()), 1e-9)
        winkel = np.degrees(np.arccos(np.clip(t['tangente'] @ np.array([1.0, 0.0, 0.0]), -1, 1)))
        self.assertAlmostEqual(float(winkel.mean()), 26.565, places=2, msg='so weit liegt die alte Orthonormalbasis daneben')

    def test_4_tangente_und_bitangente_stehen_senkrecht_auf_der_normale(self):
        for scherung in (0.0, 0.5, -1.2):
            with self.subTest(scherung=scherung):
                t = self._texel(scherung)
                self.assertLess(float(np.abs(np.einsum('ij,ij->i', t['tangente'], t['normale'])).max()), 1e-9)
                self.assertLess(float(np.abs(np.einsum('ij,ij->i', t['bitangente'], t['normale'])).max()), 1e-9)

    def test_5_dreieck_und_schwerpunktkoordinaten_gehoeren_zu_jedem_texel(self):
        punkte, dreiecke, uv, normalen = self._platte()
        t = Dazgeograftraster.texel(punkte, dreiecke, uv, R, normalen)
        self.assertLess(float(np.abs(t['bary'].sum(axis=1) - 1.0).max()), 1e-9)
        zurueck = np.einsum('mk,mkj->mj', t['bary'], punkte[dreiecke[t['dreieck']]])
        self.assertLess(float(np.abs(zurueck - t['position']).max()), 1e-9)
        self.assertEqual(set(np.unique(t['dreieck']).tolist()), {0, 1})

    def test_6_ein_dreieck_ohne_uv_flaeche_gibt_keine_texel(self):
        punkte, dreiecke, uv, normalen = self._platte()
        uv = uv.copy()
        uv[1] = np.array([[0.2, 0.2], [0.2, 0.2], [0.2, 0.2]])
        t = Dazgeograftraster.texel(punkte, dreiecke, uv, R, normalen)
        self.assertEqual(set(np.unique(t['dreieck']).tolist()), {0})

    def test_7_ungedeckte_texel_nehmen_den_wert_des_naechsten_gedeckten(self):
        bild = np.zeros((6, 6, 3))
        bild[2, 2] = (10.0, 20.0, 30.0)
        bild[2, 3] = (200.0, 100.0, 50.0)
        aus = Dazgeograftraster.auffuellen(bild, np.array([2, 2]), np.array([2, 3]))
        self.assertEqual(aus[2, 2].tolist(), [10.0, 20.0, 30.0])
        self.assertEqual(aus[0, 0].tolist(), [10.0, 20.0, 30.0], 'der nächste gedeckte Texel zu (0, 0) ist (2, 2)')
        self.assertEqual(aus[5, 5].tolist(), [200.0, 100.0, 50.0], 'der nächste gedeckte Texel zu (5, 5) ist (2, 3)')
