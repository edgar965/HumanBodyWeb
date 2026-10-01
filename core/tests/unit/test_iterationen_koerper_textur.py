# -*- coding: utf-8 -*-
u"""Die Automatik für Körper und Textur (`IterationKoerper`, `IterationTextur`) und die neuen Befundzahlen
(`Befundmessung.koerper_huelle`, `kanten`, `farbbaender`), dazu die Mischung nach Ort (`G9haarmischung`) — Kunstdaten.

1. Körper: ein unbedecktes Band mit Hüllenabstand bewegt zuerst den Genesis-Regler, am Anschlag den Ortsregler; ein
   bedecktes Band (Stoff im Foto) rührt sich nicht.
2. Textur: Fototextur erst bei Stillstand, Falten nur mit Fototextur und Kantenüberschuss, Decal nur für ein Band, dessen
   Fotofarbe abweicht — und nichts doppelt.
3. Befund: Kantenenergie eines Streifenbilds größer als die einer Fläche; Farbbänder unten → oben; Körperhülle je Band
   an einem Sichtkörper aus Rechtecken.
4. Mischung nach Ort: `auswahl` mit Eignung, `eignung` je Insel, `ort_aus` aus den Reglern.

Sabotage: in `IterationKoerper.form` die Prüfung `unbedeckt(band) is not True` entfernen → Fall 1 rot (Rumpf zieht trotz
Stoff); in `G9haarmischung.auswahl` `kandidaten[streu…]` durch `streu[…]` ersetzen → Fall 4 rot.
"""
import numpy as np
from django.test import SimpleTestCase
from Genesis9.haarmischung import G9haarmischung
from Genesis9.modellmitkleidern import ModellMitKleidern
from Genesis9.modellrezept import G9rezept
from iterationen2d3d.befundmessung import Befundmessung
from iterationen2d3d.iterationkoerper import IterationKoerper
from iterationen2d3d.iterationmodell import IterationModell
from iterationen2d3d.iterationtextur import IterationTextur
from iterationen2d3d.sichtkoerper import Sichtkoerper


class KoerperUndTexturTest(SimpleTestCase):
    databases = set()

    HAUT, STOFF = [0.75, 0.55, 0.45], [0.3, 0.3, 0.32]

    def test_1_koerper_regler_dann_ort(self):
        m = ModellMitKleidern()
        befund = {'koerper_huelle': {'rumpf': 30.0, 'unterschenkel': 20.0, 'oberschenkel': 4.0},
                  'koerper_baender': {'rumpf': self.STOFF, 'unterschenkel': self.HAUT, 'oberschenkel': self.HAUT}}
        zeilen = IterationKoerper(m, befund).aufrufe()
        self.assertEqual(zeilen, ["m.koerper_regler('body_bs_CalvesSize', 0.35)"])     # 0,35 · 20 / 20
        G9rezept.anwenden(m, '\n'.join(zeilen))
        m.koerper_regler('body_bs_CalvesSize', 1.0)                                    # am Anschlag → Ortsregler
        self.assertEqual(IterationKoerper(m, befund).aufrufe(), ["m.koerper_regler('eigen:ort_waden', 0.7)"])
        self.assertEqual(IterationKoerper(m, {}).aufrufe(), [])
        self.assertIn("m.koerper_regler('eigen:ort_waden', 0.7)", IterationModell(m, befund).aufrufe())

    def test_2_textur_regeln(self):
        m = ModellMitKleidern().kleid_nur('shirt')
        teil = {'art': 'kleidung', 'kanten_foto': 0.08, 'kanten_render': 0.02, 'foto_farbe': [0.2, 0.2, 0.2],
                'render_farbe': [0.3, 0.3, 0.3],
                'farbbaender': [[[0.2, 0.2, 0.2], [0.3, 0.3, 0.3]], [[0.9, 0.9, 0.1], [0.3, 0.3, 0.3]],
                                [[0.9, 0.9, 0.1], [0.9, 0.9, 0.1]], None, None]}
        befund = {'teile': {'shirt': teil}}
        unruhig = [{'stoff_mm': 10.0}, {'stoff_mm': 14.0}, {'stoff_mm': 10.5}, {'stoff_mm': 10.1}]
        still = [{'stoff_mm': 10.0}, {'stoff_mm': 10.5}, {'stoff_mm': 10.2}, {'stoff_mm': 10.1}]
        self.assertNotIn("m.kleid_fototextur('shirt')", IterationTextur(m, befund, unruhig).aufrufe())
        zeilen = IterationTextur(m, befund, still).aufrufe()
        self.assertEqual(zeilen[0], "m.kleid_fototextur('shirt')")
        self.assertEqual(sum('kleid_decal' in z for z in zeilen), 1)               # Band 2: der Render ist dort selbst bunt
        self.assertIn("m.kleid_decal('shirt', 'band1', {'band': (0.2, 0.4)}, farbe='#e6e61a', deckung=0.8)", zeilen)
        self.assertFalse(any('kleid_falten' in z for z in zeilen))                 # Falten erst mit Fototextur
        m.kleid_fototextur('shirt')
        m.kleidung['shirt.bild.decal_band1'] = 0.8
        zeilen = IterationTextur(m, befund, still).aufrufe()
        self.assertEqual(zeilen, ["m.kleid_falten('shirt', 'auto', abstand_cm=4.0, tiefe=0.5)"])
        m.kleidung['shirt.bild.falten_auto'] = 1.0
        self.assertEqual(IterationTextur(m, befund, still).aufrufe(), [])
        G9rezept.pruefen('\n'.join(zeilen))

    def test_3_befundzahlen(self):
        flaeche = np.full((20, 20, 3), 0.5, np.float32)
        streifen = flaeche.copy()
        streifen[::4] = 0.1                           # Streifen zwei Zeilen breit (jede zweite Zeile allein hätte im
        streifen[1::4] = 0.1                          # zentralen Differenzenquotienten Gradient 0)
        maske = np.ones((20, 20), bool)
        self.assertAlmostEqual(Befundmessung.kanten(flaeche, maske), 0.0)
        self.assertGreater(Befundmessung.kanten(streifen, maske), 0.1)
        self.assertIsNone(Befundmessung.kanten(flaeche, np.zeros((20, 20), bool)))
        bild = np.zeros((10, 4, 3), np.float32)
        bild[:5] = (1.0, 0.0, 0.0)                                                  # oben rot, unten blau
        bild[5:] = (0.0, 0.0, 1.0)
        baender = Befundmessung.farbbaender(bild, np.ones((10, 4), bool), anzahl=2)
        self.assertEqual(baender, [[0.0, 0.0, 1.0], [1.0, 0.0, 0.0]])
        # Körperhülle: Silhouette 0,5 m breit, Körperpunkte bei ±0,1 → der Umriss liegt ~0,15 m weiter außen.
        maske = np.zeros((60, 40), dtype=bool)
        maske[2:58, 10:30] = True
        sicht = Sichtkoerper([(0.0, maske), (90.0, maske)], hoehe=1.0)
        y = np.linspace(0.0, 1.0, 50)
        koerper = np.vstack([np.column_stack([np.full(50, 0.1), y, np.zeros(50)]),
                             np.column_stack([np.full(50, -0.1), y, np.zeros(50)])])
        huelle = Befundmessung(None, None, sicht).koerper_huelle(koerper)
        self.assertEqual(set(huelle), {'unterschenkel', 'oberschenkel', 'rumpf', 'kopf'})
        for wert in huelle.values():
            self.assertTrue(40.0 < wert < 130.0, huelle)
        self.assertEqual(Befundmessung(None, None, None).koerper_huelle(koerper), {})

    def test_4_mischung_nach_ort(self):
        eignung = np.array([True, False, True, True, False, True])
        wahl = G9haarmischung.auswahl(6, 1.0, 'saat', eignung)
        self.assertEqual(wahl.tolist(), [0, 2, 3, 5])
        halb = G9haarmischung.auswahl(6, 0.5, 'saat', eignung)
        self.assertEqual(len(halb), 2)
        self.assertTrue(set(halb.tolist()) <= {0, 2, 3, 5})
        # Zwei Inseln: eine vorn (+z), eine hinten — nur die vordere liegt im Sektor −45…45.
        punkte = np.array([[0.0, 0.5, 0.2], [0.01, 0.5, 0.2], [0.0, 0.5, -0.2], [0.01, 0.5, -0.2], [0, 0, 0], [0, 1, 0]])
        marken = np.array([0, 0, 1, 1, 0, 1])
        e = G9haarmischung.eignung(marken, 2, punkte, {'sektor': (-45, 45)})
        self.assertEqual(e.tolist(), [True, False])
        self.assertIsNone(G9haarmischung.eignung(marken, 2, punkte, None))
        self.assertEqual(G9haarmischung.ort_aus({'ort.sektor_a': 30, 'ort.sektor_b': 150}), {'sektor': (30.0, 150.0)})
        self.assertEqual(G9haarmischung.ort_aus({'ort.band_von': 0.5}), {'band': (0.5, 1.0)})
        self.assertIsNone(G9haarmischung.ort_aus({'ort.sektor_a': -180, 'ort.sektor_b': 180}))
        self.assertIsNone(G9haarmischung.ort_aus({}))
