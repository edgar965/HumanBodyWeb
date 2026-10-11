# -*- coding: utf-8 -*-
"""`Meshfigurschammessung` — die Scham-Messung von „Mesh to 3D" (11.10.2026), an Kunstflächen ohne Netz, ohne GPU, ohne Ablage.

Edgar: „Ich hatte schon extra beauftragt, dass die Messung bei jedem Import ausgeführt wird. Und auch bei jedem Mesh-to-3D Auftrag." Die Kunstfigur ist eine Platte (Vorder- und Rückseite, damit der Kasten
„nur die Vorderseite" etwas findet), 1,75 m hoch; der Beckenkasten liegt bei 44–55,5 % der Höhe, ±7 cm.

1. Dieselbe Fläche als Figur und als Netz → Abstände ≈ 0, keine Abweichung.
2. Das Netz 3 mm vor der Figur → beide Richtungen messen 3 mm (±0,2), und die Schwelle von `Schammessung` schlägt an.
3. Nur im oberen Drittel des Kastens weicht das Netz ab → das obere Drittel zeigt es, das untere nicht.
4. Ein Netz, das das Becken nicht enthält → ein Hinweis statt einer Zahl, keine Abweichung.
5. `sicher` wirft nie: fehlt die Ablage, kommt `{'fehler': …}` zurück.
6. `zeilen` für Messung, Hinweis und Fehler.

Sabotage-Gegenproben: `Schammessung.FORM_MEDIAN_MM` auf 5 → Fall 2 verliert die Abweichung (rot); die Zeile `kasten & front` in `Blendimportnachformung.kasten` entfernen → Fall 1 misst die Rückseite mit.
"""
from types import SimpleNamespace

import numpy as np
from django.test import SimpleTestCase

from core.dienste.meshfigurschammessung import Meshfigurschammessung


class MeshfigurschammessungTest(SimpleTestCase):
    HOEHE = 1.75

    @classmethod
    def _platte(cls, z, schritt=0.01, y_bis=None, huegel=None):
        """Eine senkrechte Platte bei `z` (x ±0,2 m, y 0 … `y_bis`) als Punkte und Dreiecke; `huegel=(y_von, mm)` hebt die Punkte ab `y_von` um `mm` nach vorn."""
        xs = np.arange(-0.2, 0.2 + 1e-9, schritt)
        ys = np.arange(0.0, (y_bis or cls.HOEHE) + 1e-9, schritt)
        gx, gy = np.meshgrid(xs, ys)
        punkte = np.column_stack([gx.ravel(), gy.ravel(), np.full(gx.size, float(z))])
        if huegel is not None:
            punkte[punkte[:, 1] >= huegel[0], 2] += huegel[1] / 1000.0
        n = len(xs)
        dreiecke = []
        for j in range(len(ys) - 1):
            for i in range(n - 1):
                a = j * n + i
                dreiecke += [[a, a + 1, a + n], [a + 1, a + n + 1, a + n]]
        return punkte, np.asarray(dreiecke, dtype=np.int64)

    @classmethod
    def _koerper(cls, vorn_z, **platte):
        """Vorder- und Rückseite zusammen (hinten fest bei −0,10 m): der Median der Tiefe liegt zwischen beiden, die Vorderseite ist `z > Median`."""
        pv, dv = cls._platte(vorn_z, **platte)
        ph, dh = cls._platte(-0.10, **platte)
        return np.vstack([pv, ph]), np.vstack([dv, dh + len(pv)])

    def _messen(self, netz_vorn_z, **netz):
        figur_p, figur_d = self._koerper(0.10)
        netz_p, netz_d = self._koerper(netz_vorn_z, schritt=0.0123, **netz)
        return Meshfigurschammessung.flaechen(figur_p, figur_d, netz_p, netz_d)

    def test_1_dieselbe_flaeche_misst_null_und_meldet_nichts(self):
        b = self._messen(0.10)
        self.assertGreater(b['kasten']['figur_punkte'], Meshfigurschammessung.MINDEST_PUNKTE)
        self.assertGreater(b['kasten']['netz_punkte'], Meshfigurschammessung.MINDEST_PUNKTE)
        self.assertLess(b['netz_zu_figur']['p90'], 0.2)
        self.assertLess(b['figur_zu_netz']['p90'], 0.2)
        self.assertEqual(b['abweichungen'], [])

    def test_2_drei_millimeter_davor_messen_drei_millimeter_und_schlagen_an(self):
        b = self._messen(0.103)
        for richtung in ('netz_zu_figur', 'figur_zu_netz'):
            self.assertAlmostEqual(b[richtung]['median'], 3.0, delta=0.2, msg=richtung)
            self.assertEqual(b[richtung]['innerhalb_1mm'], 0.0)
        self.assertEqual(len(b['abweichungen']), 2, b['abweichungen'])
        self.assertIn('Median 3.00', b['abweichungen'][0])

    def test_3_eine_abweichung_nur_oben_zeigt_das_obere_drittel(self):
        # Der Kasten reicht von 0,77 bis 0,971 m; das obere Drittel beginnt bei ≈ 0,904 m: ab 0,905 m steht das Netz 8 mm weiter vorn.
        b = self._messen(0.10, huegel=(0.905, 8.0))
        unten, mitte, oben = b['netz_zu_figur']['drittel']
        self.assertLess(unten['median'], 0.2)
        self.assertGreater(oben['median'], 3.0)
        self.assertGreater(oben['median'], 10 * max(unten['median'], 0.01))

    def test_4_ohne_becken_im_netz_kommt_ein_hinweis_statt_einer_zahl(self):
        figur_p, figur_d = self._koerper(0.10)
        netz_p, netz_d = self._koerper(0.10, y_bis=0.30)         # nur Beine: der Kasten bei 0,77–0,97 m bleibt leer
        b = Meshfigurschammessung.flaechen(figur_p, figur_d, netz_p, netz_d)
        self.assertIn('hinweis', b)
        self.assertEqual(b['abweichungen'], [])
        self.assertNotIn('netz_zu_figur', b)

    def test_5_sicher_wirft_nie_und_nennt_den_grund(self):
        class Kaputt:
            def arbeit(self, *_a):
                raise OSError('Ablage fehlt')

            def netzdatei(self):
                return None

        lauf = SimpleNamespace(ablage=Kaputt(), job=SimpleNamespace(kennung='x'))
        b = Meshfigurschammessung.sicher(lauf)
        self.assertIn('fehler', b)
        self.assertIn('Ablage fehlt', b['fehler'])

    def test_6_zeilen_fuer_messung_hinweis_und_fehler(self):
        z = Meshfigurschammessung.zeilen(self._messen(0.103))
        self.assertTrue(z[0].startswith('Beckenkasten:'))
        self.assertTrue(any(s.startswith('Netz → Figur: Median 3.0') for s in z), z)
        self.assertTrue(any(s.startswith('ABWEICHUNG') for s in z))
        gut = Meshfigurschammessung.zeilen(self._messen(0.10))
        self.assertEqual(gut[-1], 'keine Abweichung über den Schwellen')
        self.assertIn('Messung gescheitert', Meshfigurschammessung.zeilen({'fehler': 'x'})[0])
        hinweis = Meshfigurschammessung.zeilen({'kasten': {'figur_punkte': 1, 'netz_punkte': 0}, 'hinweis': 'zu wenige'})
        self.assertEqual(hinweis[-1], 'zu wenige')
