# -*- coding: utf-8 -*-
u"""Ortsmorph, Sichtkörper, Ringmaß, Hülle, Haar-Operationen als Rezept (30.09.2026) — Kunstdaten, keine Bibliothek.

1. `G9ortsmorph.gewicht`: Sektor (0 vorn, positiv links) mit Auslauf, Kugel um einen Punkt, Welle längs — multipliziert
   mit dem Höhenband; Landmarken-Kugel liest `landmarken()` (hier ersetzt).
2. `Sichtkoerper`: ein Rechteck als Silhouette in zwei Ansichten → `innen`, `rand` (Weg bis zum Rand in Metern),
   `netz` (Ringe × Schichten, Dreiecke schließen sich).
3. `G9kleidring.deltas`: ein Zylinder-Käfig, Körperring halb so breit, `weite` 1,0 → der Ring schrumpft auf den
   Körperring, außerhalb des Bands bleibt alles stehen.
4. `G9huellenmorph.deltas`: Punkte innerhalb des Sichtkörpers wandern nach außen an seinen Rand (× Stärke).
5. `ModellMitKleidern`: die neuen Funktionen stehen in `hilfe()` (über die Mixins), ein Rezept mit Wörterbuch als
   Argument geht durch `G9rezept`, `haltung_gelenk` landet in `drehung()`, `kleid_huelle` ohne Runde ist ein klarer
   ValueError.

Sabotage-Gegenproben: in `G9ortsmorph._sektor` das `% 360` weglassen → Fall 1 rot (Sektor über −180/180 zerfällt);
in `Sichtkoerper.rand` `weg[~drin[:, 0]] = 0.0` weglassen → Fall 2 rot (Start außerhalb liefert einen Weg).
"""
import numpy as np
from django.test import SimpleTestCase
from Genesis9.huellenmorph import G9huellenmorph
from Genesis9.kleidring import G9kleidring
from Genesis9.modellmitkleidern import ModellMitKleidern
from Genesis9.modellrezept import G9rezept
from Genesis9.ortsmorph import G9ortsmorph
from iterationen2d3d.sichtkoerper import Sichtkoerper


class OrtsmorphTest(SimpleTestCase):
    databases = set()

    def test_1_sektor_kugel_welle(self):
        mitte = np.zeros(3)
        # vorn (+z), links (+x), hinten (−z), rechts (−x), alle auf halber Höhe
        punkte = np.array([[0, 0.5, 0.2], [0.2, 0.5, 0], [0, 0.5, -0.2], [-0.2, 0.5, 0]])
        w = G9ortsmorph.gewicht({'ort': {'sektor': (-45, 45), 'sektor_weich': 5}}, punkte, 0.0, 1.0, mitte)
        self.assertEqual([round(float(x), 3) for x in w], [1.0, 0.0, 0.0, 0.0])
        # Sektor über die Naht −180/180: hinten drin, vorn nicht
        w = G9ortsmorph.gewicht({'ort': {'sektor': (150, -150), 'sektor_weich': 5}}, punkte, 0.0, 1.0, mitte)
        self.assertEqual([round(float(x), 3) for x in w], [0.0, 0.0, 1.0, 0.0])
        # Kugel um den vorderen Punkt, Radius 10 cm: nur er drin
        w = G9ortsmorph.gewicht({'ort': {'kugel': [0, 0.5, 0.2], 'radius_cm': 10}}, punkte, 0.0, 1.0, mitte)
        self.assertAlmostEqual(float(w[0]), 1.0)
        self.assertEqual(float(w[1]), 0.0)
        # Landmarke über eine ersetzte Tabelle
        alt = G9ortsmorph._landmarken
        G9ortsmorph._landmarken = {'bauch': [0.2, 0.5, 0.0]}
        try:
            w = G9ortsmorph.gewicht({'ort': {'landmarke': 'bauch', 'radius_cm': 10}}, punkte, 0.0, 1.0, mitte)
            self.assertAlmostEqual(float(w[1]), 1.0)
        finally:
            G9ortsmorph._landmarken = alt
        # Welle längs: Wellenlänge 1 m über die Höhe → bei y = 0,5 Gewicht 0, bei y = 0 und 1 Gewicht 1
        p = np.array([[0, 0.0, 0.1], [0, 0.5, 0.1], [0, 1.0, 0.1]])
        w = G9ortsmorph.gewicht({'ort': {'welle': {'laenge_cm': 100}}, 'weich': 0.01}, p, 0.0, 1.0, mitte)
        self.assertAlmostEqual(float(w[1]), 0.0, places=6)
        self.assertGreater(float(w[0]), 0.9)

    def _sicht(self):
        # Fläche 40 × 60, Figur: Rechteck Spalten 10…30 (x −0,25…+0,25 m bei 1 m Höhe → 0,5 m breit), volle Höhe
        maske = np.zeros((60, 40), dtype=bool)
        maske[2:58, 10:30] = True
        return Sichtkoerper([(0.0, maske), (90.0, maske)], hoehe=1.0)

    def test_2_sichtkoerper_innen_rand_netz(self):
        s = self._sicht()
        self.assertEqual(s.innen([[0.0, 0.5, 0.0]]).tolist(), [1.0])
        # Außerhalb in BEIDEN Ansichten (x = 0,6 sieht die 90°-Ansicht bei z = 0 noch innen: `innen` ist der Anteil).
        self.assertEqual(s.innen([[0.6, 0.5, 0.6]]).tolist(), [0.0])
        self.assertEqual(s.innen([[0.6, 0.5, 0.0]]).tolist(), [0.5])
        # Rand von der Mitte nach +x: die Maske reicht 10 Spalten = 10 / (60·0,94) m ≈ 0,177 m … gemessen in 5-mm-Schritten
        weg = s.rand([[0.0, 0.5, 0.0]], [[1.0, 0.0, 0.0]])
        self.assertTrue(0.16 < float(weg[0]) < 0.20, weg)
        # Start außerhalb → 0
        self.assertEqual(float(s.rand([[0.6, 0.5, 0.0]], [[1.0, 0.0, 0.0]])[0]), 0.0)
        punkte, dreiecke = s.netz(schicht_m=0.1, strahlen=12, raster_m=0.05, weite_m=1.0)
        self.assertGreater(len(punkte), 12 * 5)
        self.assertGreater(len(dreiecke), 0)
        self.assertLess(int(dreiecke.max()), len(punkte))

    def test_3_ringmass_setzt_den_ring_auf_den_koerperring(self):
        winkel = np.linspace(0, 2 * np.pi, 24, endpoint=False)
        ring = np.column_stack([0.2 * np.cos(winkel), np.zeros(24), 0.2 * np.sin(winkel)])
        kaefig = np.vstack([ring + [0, y, 0] for y in np.linspace(0.0, 1.0, 11)])
        alt = G9kleidring.koerperring
        G9kleidring.koerperring = classmethod(lambda cls, y, mitte, scheibe=None: (0.1, 0.1))
        try:
            deltas, brief = G9kleidring.deltas([kaefig], 0.0, 1.0, np.array([0.0, 0.5, 0.0]), hoehe=0.5, weite=1.0,
                                               band=0.1, weich=0.01)
        finally:
            G9kleidring.koerperring = alt
        d = deltas[0]
        mitte = np.abs(kaefig[:, 1] - 0.5) < 0.02
        # x schrumpft von 0,2 auf 0,1: Delta −0,1 in x-Richtung am Punkt (0,2, 0,5, 0)
        p = np.flatnonzero(mitte & (kaefig[:, 0] > 0.19))[0]
        self.assertAlmostEqual(float(d[p][0]), -0.1, places=6)
        self.assertAlmostEqual(float(np.abs(d[kaefig[:, 1] < 0.2]).max()), 0.0)
        self.assertAlmostEqual(brief['faktor_x'], 0.5, places=6)

    def test_4_huelle_zieht_an_den_sichtkoerper(self):
        s = self._sicht()
        kaefig = np.array([[0.05, 0.5, 0.0], [-0.05, 0.5, 0.0], [0.0, 0.5, 0.05]])
        deltas, brief = G9huellenmorph.deltas(s, [kaefig], 0.0, 1.0, np.array([0.0, 0.5, 0.0]), staerke=1.0, weich=0.01)
        d = deltas[0]
        self.assertGreater(float(d[0][0]), 0.1)                 # nach +x zum Rand (~0,18 − 0,05)
        self.assertLess(float(d[1][0]), -0.1)
        self.assertEqual(brief['gezogen'], 3)

    def test_5_rezept_mit_ort_und_neue_funktionen(self):
        namen = {n for n, _s, _t in ModellMitKleidern.hilfe()}
        for f in ('morph_ort', 'kleid_ring', 'kleid_huelle', 'kleid_welle', 'koerper_ort', 'koerper_huelle',
                  'haltung_gelenk', 'haar_trim', 'haar_clump', 'haar_noise', 'haar_straighten', 'haar_biegen',
                  'haar_anlegen'):
            self.assertIn(f, namen, f)
        m = ModellMitKleidern()
        G9rezept.anwenden(m, "m.haltung_gelenk('l_forearm', 'x', 30)")
        self.assertEqual(m.drehung(), {'l_forearm': {'rotation/x': 30.0}})
        self.assertEqual(ModellMitKleidern.aus(m.als_dict()).drehung(), m.drehung())
        aufrufe = G9rezept.pruefen("m.morph_ort('kleidung', 's', 'n', {'band': (0.3, 0.5), 'sektor': (-40, 40)}, weg_cm=1)")
        self.assertEqual(aufrufe[0][2][3], {'band': (0.3, 0.5), 'sektor': (-40, 40)})
        with self.assertRaises(ValueError) as fehler:
            m.kleid_huelle('shirt')
        self.assertIn(u'Sichtkörper', str(fehler.exception))
        with self.assertRaises(ValueError):
            m.haltung_gelenk('l_hand', 'x', 10)
        with self.assertRaises(ValueError) as fehler:
            m.kleid_drapieren('shirt')
        self.assertIn('Newton', str(fehler.exception))
        with self.assertRaises(ValueError):
            m.kleid_drapieren('shirt', motor='unity')
        # Die Lage für den Newton-Löser (Z oben) und zurück ist verlustfrei.
        from core.dienste.kleiddrapierung import Kleiddrapierung
        p = np.array([[0.1, 1.2, -0.3]])
        np.testing.assert_allclose(Kleiddrapierung.nach_y_oben(Kleiddrapierung.nach_z_oben(p)), p)
        self.assertEqual(Kleiddrapierung.nach_z_oben(p).tolist(), [[0.1, 0.3, 1.2]])


class StandardreglerTest(SimpleTestCase):
    u"""Die festen Regler (`G9standardmorphe`, `G9koerperstandardmorphe`) und die Automatik mit Zellen/Hülle —
    ohne Bibliothek: Kataloge, Namen, Rezeptzeilen. Sabotage: in `G9standardmorphe.KLEIDUNG` einen Namen ohne
    `form_` eintragen → Fall 6 rot."""
    databases = set()

    def test_6_kataloge_und_reglerlisten(self):
        from Genesis9.koerperstandardmorphe import G9koerperstandardmorphe
        from Genesis9.standardmorphe import G9standardmorphe
        for art in ('kleidung', 'haar'):
            namen = G9standardmorphe.namen(art)
            self.assertGreaterEqual(len(namen), 10, art)
            self.assertEqual(len(set(namen)), len(namen))
            for n in namen:
                self.assertTrue(G9standardmorphe.ist_standard(n), n)
                self.assertEqual(G9standardmorphe.art_von(n), art, n)
            regler = G9standardmorphe.regler(art)
            self.assertEqual([r['name'] for r in regler], ['eigen.' + n for n in namen])
            self.assertEqual({r['gruppe'] for r in regler}, {G9standardmorphe.GRUPPE[art]})
        self.assertFalse(G9standardmorphe.ist_standard('netz_b0'))
        for name, _a, operation, ort, _p in G9standardmorphe.HAAR:
            self.assertIn(operation, ('trim', 'clump', 'noise', 'straighten', 'biegen', 'anlegen'), name)
            self.assertTrue(ort is None or isinstance(ort, dict), name)
        bereich = G9koerperstandardmorphe.bereich()
        self.assertEqual(bereich['schluessel'], 'ort')
        self.assertEqual(len(bereich['regler']), len(G9koerperstandardmorphe.KATALOG))
        for r in bereich['regler']:
            self.assertTrue(r['name'].startswith('eigen:ort_'), r)
            self.assertTrue(G9koerperstandardmorphe.ist_standard(r['name'][len('eigen:'):]), r)
            self.assertEqual(r['min'], -2.0)
        self.assertFalse(G9koerperstandardmorphe.ist_standard('ort_quatsch'))
        form = G9koerperstandardmorphe.form('ort_bauch')
        self.assertEqual(form['ort']['landmarke'], 'bauch')

    def test_7_automatik_schreibt_ortsmorphe_und_huelle(self):
        from iterationen2d3d.befundmessung import Befundmessung
        from iterationen2d3d.iterationkleider import IterationKleider
        m = ModellMitKleidern().kleid_nur('shirt')
        zellen = [[0.0] * 8 for _ in range(5)]
        zellen[2][0] = 30.0                                     # Band 2, Sektor 0: 30 mm zu weit außen
        befund = {'teile': {'shirt': {'art': 'kleidung', 'netz_mm': 5.0, 'netz_abs_mm': 5.0, 'grund_mm': 0.0,
                                      'baender': [0.0] * 5, 'zellen': zellen, 'huelle_mm': [20.0] * 5,
                                      'pixel': 100, 'foto_farbe': [0.5] * 3, 'render_farbe': [0.5] * 3}}}
        zeilen = IterationKleider(m, befund).aufrufe()
        text = '\n'.join(zeilen)
        self.assertIn("m.morph_ort('kleidung', 'shirt', 'netz_b2s0'", text)
        self.assertIn("'sektor': %r" % (Befundmessung.sektor(0),), text)
        self.assertIn("m.kleid_huelle('shirt', staerke=0.5)", text)
        self.assertEqual(sum('netz_b' in z for z in zeilen), 1)
        m.kleidung['shirt.eigen.huelle'] = 0.5
        m.kleidung['shirt.eigen.netz_b2s0'] = -1.0
        zeilen = IterationKleider(m, befund).aufrufe()
        self.assertIn("m.morph_wert('kleidung', 'shirt', 'huelle', 0.75)", zeilen)
        self.assertTrue(any(z.startswith("m.morph_wert('kleidung', 'shirt', 'netz_b2s0'") for z in zeilen))

    def test_8_blender_dreiecke_auf_daz_punkten(self):
        from core.dienste.engine2d3dkleiderblender import Engine2d3dKleiderblender

        class Folger:
            dreiecke = np.array([[0, 1, 2, -1], [3, 4, 5, 6]])
            ursprung = np.array([10, 11, 12, 13, 14, 15, 16])
        d = Engine2d3dKleiderblender._dreiecke(Folger())
        self.assertEqual(d.tolist(), [[10, 11, 12], [13, 14, 15], [13, 15, 16]])
