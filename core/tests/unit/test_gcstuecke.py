# -*- coding: utf-8 -*-
u"""GarmentCode-Stapellauf: Aufträge, Kennungen, Fingerabdruck (ohne Drapierung).

Sabotagen, die rot werden müssen: in `G9gcstuecke._eindeutig` den Zähler
streichen (Fall 2); `FASSUNG` aus dem Fingerabdruck nehmen (Fall 3).
"""
import unittest
from unittest import mock

from Genesis9.gcstuecke import G9gcstuecke


class GcstueckeTest(unittest.TestCase):
    databases = []

    def test_1_jede_form_und_jedes_katalogstueck_ohne_form(self):
        auftraege = G9gcstuecke.auftraege()
        quellen = {a['quelle'] for a in auftraege}
        self.assertIn('form_bleistiftrock', quellen)
        self.assertIn('hose', quellen)                  # Hose hat keine Formen
        self.assertTrue(all(a['kennung'].startswith('GC_') for a in auftraege))
        self.assertTrue(all(a['name'].startswith('GC ') for a in auftraege))

    def test_2_doppelte_titel_bekommen_einen_zaehler(self):
        roh = [{'titel': u'Trägertop'}, {'titel': u'Trägertop'}]
        aus = G9gcstuecke._eindeutig(roh)
        self.assertEqual([a['kennung'] for a in aus], ['GC_Traegertop', 'GC_Traegertop_2'])
        self.assertEqual(aus[0]['name'], u'GC Trägertop')

    def test_3_fingerabdruck_haengt_an_werten_und_fassung(self):
        a = {'vorlage': 'rock', 'werte': {'x': 1}, 'material': {}}
        b = dict(a, werte={'x': 2})
        self.assertNotEqual(G9gcstuecke.fingerabdruck(a), G9gcstuecke.fingerabdruck(b))
        with mock.patch.object(G9gcstuecke, 'FASSUNG', G9gcstuecke.FASSUNG + 1):
            neu = G9gcstuecke.fingerabdruck(a)
        self.assertNotEqual(neu, G9gcstuecke.fingerabdruck(a))

    def test_4_anzug_ist_full_body_socke_sind_socken(self):
        self.assertEqual(G9gcstuecke._kategorie({'vorlage': 'anzug', 'titel': 'Jumpsuit',
                                                 'quelle': 'form_jumpsuit'}), G9gcstuecke.ANZUG)
        self.assertIn('Socks', G9gcstuecke._kategorie({'vorlage': 'schuh', 'titel': 'Socke',
                                                        'quelle': 'form_socke'})[0])

    def test_5_struempfe_liegen_an_und_hosen_bekommen_nacharbeit(self):
        auftraege = {a['kennung']: a for a in G9gcstuecke.auftraege()}
        strumpf = next(a for k, a in auftraege.items() if 'Stocking' in k)
        self.assertEqual(strumpf['werte'].get('bau.anliegen_mm'), 2.0)
        hose = dict(strumpf, werte={}, material={})
        rock = dict(hose, vorlage='rock')
        # Der Abdruck trägt den Weg: dieselben Werte mit und ohne Nacharbeit unterscheiden sich.
        self.assertNotEqual(G9gcstuecke.fingerabdruck(hose), G9gcstuecke.fingerabdruck(rock))

    def test_6_lfs_zeiger_ist_keine_textur(self):
        from Genesis9.gcstueckmaterial import G9gcstueckmaterial
        auftrag = {'material': {'textur': 'x.png'}, 'bild': ''}
        # Ohne Ordner ist die Textur nicht da — die Farbe kommt dann vom Vorschaubild.
        self.assertTrue(G9gcstueckmaterial.textur_fehlt(auftrag))
        self.assertFalse(G9gcstueckmaterial.textur_fehlt({'material': {}, 'bild': ''}))

    def test_7_ein_zur_haut_gewickeltes_teil_wird_umgedreht(self):
        import numpy as np
        from scipy.spatial import cKDTree

        from Genesis9.stoffwicklung import G9stoffwicklung
        # Zwei getrennte Quadrate über einer Haut bei y = 0: das erste zeigt nach oben
        # (weg von der Haut), das zweite nach unten (zur Haut).
        punkte = np.array([[0, 1, 0], [1, 1, 0], [1, 1, 1], [0, 1, 1],
                           [3, 1, 0], [4, 1, 0], [4, 1, 1], [3, 1, 1]], dtype=float)
        flaechen = [[0, 3, 2, 1], [4, 5, 6, 7]]
        haut = np.array([[x, 0.0, z] for x in range(5) for z in (0, 1)], dtype=float)
        aus, uv, bilanz = G9stoffwicklung.ausrichten(punkte, flaechen, [[0, 1, 2, 3]] * 2,
                                                     haut, cKDTree(haut))
        self.assertEqual(aus[0], [0, 3, 2, 1])
        self.assertEqual(aus[1], [7, 6, 5, 4])
        self.assertEqual(uv[1], [3, 2, 1, 0])
        self.assertEqual(bilanz['umgedreht_bereiche'], 1)

    def test_8_beinmitte_ist_die_umrissmitte(self):
        import numpy as np

        from GarmentCode.beinmitte import Beinmitte
        # Ein Ring um (x 0,11, y 0,05) m, Z oben, dichter hinten besetzt.
        w = np.concatenate([np.linspace(0, np.pi, 40), np.linspace(np.pi, 2 * np.pi, 8)])
        ring = np.column_stack([0.11 + 0.04 * np.cos(w), 0.05 + 0.04 * np.sin(w),
                                np.full(len(w), 0.25)])
        mitte = Beinmitte.messen(ring, 0.0, 10.0, 40.0)
        self.assertAlmostEqual(mitte['shin_x'], 11.0, places=1)
        self.assertAlmostEqual(mitte['shin_z'], -5.0, places=1)

    def test_9_dreiecksnetz_wird_nicht_unterteilt(self):
        from Genesis9.dsonschreiber import G9dsonschreiber
        # GarmentCode liefert Dreiecke: Catmull-Clark machte den Rücken beulig.
        self.assertEqual(G9dsonschreiber.netzart([[0, 1, 2]] * 3 + [[0, 1, 2, 3]]), 'polygon_mesh')
        self.assertEqual(G9dsonschreiber.netzart([[0, 1, 2, 3]] * 3 + [[0, 1, 2]]),
                         'subdivision_surface')

    def test_10_morphuebertrag_folgt_dem_schnittteil(self):
        import numpy as np

        from Genesis9.gcmorphuebertrag import G9gcmorphuebertrag

        def teil(laenge, uv_versatz):
            # Ein Streifen 2 × 4 Punkte, 0,2 m breit, `laenge` hoch; UV im Atlas verschoben.
            p = np.array([[x * 0.2, y * laenge / 3, 0] for y in range(4) for x in range(2)], float)
            f = np.array([[2 * y, 2 * y + 1, 2 * y + 3] for y in range(3)]
                         + [[2 * y, 2 * y + 3, 2 * y + 2] for y in range(3)])
            uv = (p[:, :2] * 0.5 + uv_versatz)[f]
            return {'punkte': p, 'flaechen': f, 'uv': uv, 'teil': np.array(['rumpf'] * len(f))}

        grund, lang = teil(0.6, 0.1), teil(0.9, 0.4)
        selbst, ohne = G9gcmorphuebertrag.uebertragen(grund, grund)
        self.assertEqual(ohne, 0)
        self.assertLess(np.abs(selbst - grund['punkte']).max(), 1e-9)
        # Die längere Fassung: der Saum (y = 0) bleibt, die Oberkante wandert auf 0,9 m.
        gemorpht, _ohne = G9gcmorphuebertrag.uebertragen(grund, lang)
        self.assertAlmostEqual(gemorpht[:, 1].max(), 0.9, places=6)
        self.assertAlmostEqual(gemorpht[:, 1].min(), 0.0, places=6)


if __name__ == '__main__':
    unittest.main()
