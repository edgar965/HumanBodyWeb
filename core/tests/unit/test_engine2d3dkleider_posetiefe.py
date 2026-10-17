# -*- coding: utf-8 -*-
"""Tiefe der SAM-Gelenke entlang der Kette (`Engine2d3dKleiderposetiefe`, 17.10.2026) — Kunstdaten, ohne SAM und ohne Netz.

Anlass: an zwei Mesh3D-AI-Posen zeigte der Fuß der Rig-Figur 124° bzw. 151° falsch, weil die Mitte der Netzpunkte im Strahl Ferse und Zehe eines zur Kamera zeigenden Fußes auf einen Punkt legt
(`.claude/rules/mesh3dai-vorstufe.md`, Abschnitt „Füße"). Geschrieben, nicht gelaufen (Tests nur auf Ansage).
Sabotage-Gegenproben (gedacht, nicht gelaufen): Vorzeichen der SAM-Tiefe umdrehen → `test_langes_glied_nimmt_die_vorhersage` rot; `KURZ` auf 0 → `test_kurzes_glied_behaelt_die_mitte` rot;
`WEIT` sehr groß → `test_weit_daneben_faellt_weg` rot; Knie aus `KETTE` → `test_welche_gelenke` rot.
"""

import unittest

import numpy as np


class PosetiefeTest(unittest.TestCase):
    NAMEN = ['left-hip', 'left-knee', 'left-ankle', 'left-big-toe-tip', 'left-heel']

    def _tiefe(self, k3_z, radius=0.03, massstab=1.0):
        from core.dienste.engine2d3dkleiderposetiefe import Engine2d3dKleiderposetiefe as T

        k3 = np.zeros((len(self.NAMEN), 3))
        for name, z in k3_z.items():
            k3[self.NAMEN.index(name), 2] = z
        return T(k3, self.NAMEN, radius, massstab)

    def test_kurzes_glied_behaelt_die_mitte(self):
        """Fuß quer zum Strahl: Bereich 6 cm (2 Radien) → Mitte, auch wenn SAM etwas anderes sagt."""
        t = self._tiefe({'left-ankle': 0.0, 'left-big-toe-tip': -0.2})
        z, art, _v = t.tiefe('left-big-toe-tip', np.linspace(-0.03, 0.03, 50), 0.0)
        self.assertEqual(art, 'mitte')
        self.assertAlmostEqual(z, 0.0, places=3)

    def test_langes_glied_nimmt_die_vorhersage(self):
        """Der Fuß zeigt zur Kamera: Bereich 0,25 m (Ferse bis Zehe), die Zehe liegt 0,19 m vor dem Knöchel (SAM-z kleiner = näher an der Kamera = Netz-z größer)."""
        t = self._tiefe({'left-ankle': 0.0, 'left-big-toe-tip': -0.19})
        z, art, v = t.tiefe('left-big-toe-tip', np.linspace(-0.05, 0.25, 200), 0.0)
        self.assertEqual(art, 'sam')
        self.assertAlmostEqual(v, 0.19, places=6)
        self.assertAlmostEqual(z, 0.19, places=6)

    def test_ferse_und_zehe_getrennt(self):
        """Gegenprobe zum Befund: Mitte hätte Ferse und Zehe auf denselben Punkt gelegt — die Kette legt die Zehe vor, die Ferse hinter den Knöchel."""
        t = self._tiefe({'left-ankle': 0.0, 'left-big-toe-tip': -0.19, 'left-heel': 0.03})
        strahl = np.linspace(-0.05, 0.25, 200)
        zeh = t.tiefe('left-big-toe-tip', strahl, 0.0)[0]
        ferse = t.tiefe('left-heel', strahl, 0.0)[0]
        self.assertGreater(zeh - ferse, 0.15)

    def test_vorhersage_wird_in_den_bereich_geklemmt(self):
        t = self._tiefe({'left-ankle': 0.0, 'left-big-toe-tip': -0.3})
        z, art, _v = t.tiefe('left-big-toe-tip', np.linspace(-0.05, 0.25, 200), 0.0)
        self.assertEqual(art, 'sam')
        self.assertLessEqual(z, 0.25 + 1e-9)

    def test_weit_daneben_faellt_weg(self):
        """Der Strahl der Zehenspitze trifft das Schienbein (z −0,44 … −0,13), SAM sagt −0,69: das Gelenk fällt weg."""
        t = self._tiefe({'left-ankle': 0.6, 'left-big-toe-tip': 0.69})
        z, art, v = t.tiefe('left-big-toe-tip', np.linspace(-0.44, -0.13, 100), -0.6)
        self.assertEqual(art, 'verworfen')
        self.assertTrue(np.isnan(z))
        self.assertAlmostEqual(v, -0.69, places=6)

    def test_welche_gelenke(self):
        """Hüften (an den Schultern), Knie, Knöchel, Ferse, Zehe rechnet die Kette — nur die Spitzen ließen den laufenden Fuß 151° verdreht; Schultern behalten die Mitte."""
        t = self._tiefe({})
        tiefen = {'left-shoulder': 0.0, 'left-hip': 0.0, 'left-knee': 0.0, 'left-ankle': 0.0}
        for name in ('left-hip', 'left-knee', 'left-ankle', 'left-heel', 'left-big-toe-tip'):
            self.assertTrue(t.zaehlt(name, tiefen), name)
        self.assertFalse(t.zaehlt('left-shoulder', tiefen))
        self.assertFalse(t.zaehlt('left-heel', {}))

    def test_huefte_faellt_nie_weg(self):
        """Hüften werden geklemmt, nie verworfen (ohne Hüfte hätte die Anpassung kein Becken)."""
        k3 = np.zeros((2, 3))
        k3[1, 2] = -2.0
        from core.dienste.engine2d3dkleiderposetiefe import Engine2d3dKleiderposetiefe as T

        t = T(k3, ['left-shoulder', 'left-hip'], 0.03, 1.0)
        z, art, _v = t.tiefe('left-hip', np.linspace(-0.1, 0.1, 50), 0.0)
        self.assertNotEqual(art, 'verworfen')
        self.assertTrue(np.isfinite(z))

    def test_massstab_aus_der_bildebene_ist_drehungsfrei(self):
        from core.dienste.engine2d3dkleiderposetiefe import Engine2d3dKleiderposetiefe as T

        xy = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 2.0], [1.0, 2.0]])
        drehung = np.array([[0.0, -1.0], [1.0, 0.0]])
        self.assertAlmostEqual(T.massstab_aus(xy * 0.5, xy @ drehung.T), 0.5, places=9)


if __name__ == '__main__':
    unittest.main()
