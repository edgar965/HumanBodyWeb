# -*- coding: utf-8 -*-
u"""Die Automatik für Körper und Textur (`IterationKoerper`, `IterationTextur`) und die neuen Befundzahlen
(`Befundmessung.koerper_huelle`, `kanten`, `farbbaender`), dazu die Mischung nach Ort (`G9haarmischung`) — Kunstdaten.

1. Körper: ein unbedecktes Band mit Hüllenabstand bewegt zuerst den Genesis-Regler, am Anschlag den Ortsregler; ein
   bedecktes Band (Stoff im Foto) rührt sich nicht.
2. Textur: Fototextur erst bei Stillstand, Falten nur mit Fototextur und Kantenüberschuss, Decal nur für ein Band, dessen
   Fotofarbe abweicht — und nichts doppelt.
3. Befund: Kantenenergie eines Streifenbilds größer als die einer Fläche; Farbbänder unten → oben; Bandbreite je Band
   unabhängig von der Beinstellung, die Hände außen zählen nicht.
4. Mischung nach Ort: `auswahl` mit Eignung, `eignung` je Insel, `ort_aus` aus den Reglern.
5. Reglerprüfung (01.10.2026): ein Schritt, der den Rest nicht verkleinert, geht zurück; danach steht das Band.
6. Umfärben: Tönung am Anschlag und Foto heller → `kleid_umfaerben` + Startton; einmal umgefärbt, nur noch Tönung.
7. Schicht `grau`: ein schwarzes Bild wird zum neutralen Grau mit Mittel 0,75; ohne Bild bleibt die Helligkeit.

Sabotage: in `IterationKoerper.form` die Prüfung `unbedeckt(band) is not True` entfernen → Fall 1 rot (Rumpf zieht trotz
Stoff); in `G9haarmischung.auswahl` `kandidaten[streu…]` durch `streu[…]` ersetzen → Fall 4 rot; in
`Reglerpruefung.urteil` `abs(m0) - self.besser` durch `abs(m0) + 100` ersetzen → Fall 5 rot; in `Bandbreite.breite`
`[:anzahl]` weglassen → Fall 3 rot (die Hände zählen mit).
"""
import numpy as np
from django.test import SimpleTestCase
from Genesis9.haarmischung import G9haarmischung
from Genesis9.modellmitkleidern import ModellMitKleidern
from Genesis9.modellrezept import G9rezept
from iterationen2d3d.bandbreite import Bandbreite
from iterationen2d3d.befundmessung import Befundmessung
from iterationen2d3d.farbangleich import Farbangleich
from iterationen2d3d.iterationkleider import IterationKleider
from iterationen2d3d.iterationkoerper import IterationKoerper
from iterationen2d3d.iterationmodell import IterationModell
from iterationen2d3d.iterationtextur import IterationTextur
from iterationen2d3d.reglerpruefung import Reglerpruefung


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
        # Körper- und Gesichtsregler führt `IterationModell` nur mit `form=True` nach (Option `iterationen.form`, Vorgabe aus: die Form kommt aus dem Schritt „Körper")
        self.assertIn("m.koerper_regler('eigen:ort_waden', 0.7)", IterationModell(m, befund, form=True).aufrufe())
        self.assertNotIn("m.koerper_regler('eigen:ort_waden', 0.7)", IterationModell(m, befund).aufrufe())

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
        # Bandbreite (seit 01.10.2026 statt des Abstands zum Sichtkörper): Foto-Beine 6 px, Render-Beine 4 px, an
        # anderer Stelle (breitbeinig gegen eng), dazu hängende Hände außen im Foto → +1 px je Seite = 10,64 mm bei 94 px/m.
        foto, render = np.zeros((100, 60), bool), np.zeros((100, 60), bool)
        foto[:, 14:20] = True
        foto[:, 40:46] = True
        foto[:, 2:5] = True
        foto[:, 55:58] = True
        render[:, 22:26] = True
        render[:, 34:38] = True
        baender = (('unterschenkel', 0.10, 0.25), ('rumpf', 0.55, 0.72))
        breite = Bandbreite.messen([(foto, render)], baender, 1.0)
        self.assertAlmostEqual(breite['unterschenkel'], 10.64, places=1)
        self.assertIsNone(Bandbreite.messen([(foto, np.zeros_like(render))], baender, 1.0)['unterschenkel'])

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

    def test_5_reglerpruefung(self):
        pruefung = Reglerpruefung(2.0)
        self.assertEqual(pruefung.urteil([((0.0,), -30.0), ((-0.5,), -20.0)]), (Reglerpruefung.FREI, None))
        self.assertEqual(pruefung.urteil([((0.0,), -30.0), ((-0.5,), -29.0)]), (Reglerpruefung.ZURUECK, (0.0,)))
        self.assertEqual(pruefung.urteil([((0.0,), -30.0), ((-0.5,), -31.0), ((0.0,), -30.0)]),
                         (Reglerpruefung.GESPERRT, None))
        m = ModellMitKleidern()
        m.koerper_regler('body_bs_CalvesSize', -0.35)
        verlauf = [{'regler': {}, 'koerper_huelle': {'unterschenkel': -20.0}},
                   {'regler': {'body_bs_CalvesSize': -0.35}, 'koerper_huelle': {'unterschenkel': -21.0}}]
        befund = {'koerper_huelle': {'unterschenkel': -21.0}, 'koerper_baender': {'unterschenkel': self.HAUT}}
        # Nur, was nicht schon auf dem Wert steht („schon zurück: nichts", `IterationKoerper.form`): der Ortsregler steht auf 0, seine Zeile entfällt.
        self.assertEqual(IterationKoerper(m, befund, verlauf).aufrufe(), ["m.koerper_regler('body_bs_CalvesSize', 0.0)"])
        m.koerper_regler('eigen:ort_waden', -0.2)                                      # steht auch der Ortsregler verstellt, gehen beide zurück
        self.assertEqual(IterationKoerper(m, befund, verlauf).aufrufe(),
                         ["m.koerper_regler('body_bs_CalvesSize', 0.0)", "m.koerper_regler('eigen:ort_waden', 0.0)"])
        verlauf.append({'regler': {'body_bs_CalvesSize': 0.0}, 'koerper_huelle': {'unterschenkel': -20.0}})
        self.assertEqual(IterationKoerper(m, befund, verlauf).aufrufe(), [])

    def test_6_umfaerben(self):
        self.assertTrue(Farbangleich.unerreichbar('#ffffff', [0.35, 0.34, 0.37], [0.15, 0.15, 0.15], 4708))
        self.assertFalse(Farbangleich.unerreichbar('#808080', [0.35, 0.34, 0.37], [0.3, 0.3, 0.3], 4708))
        self.assertEqual(Farbangleich.start_grau([0.35, 0.344, 0.368]), '#3b3a3f')
        m = ModellMitKleidern().kleid_nur('g9_base_shirt')
        m.kleid_farbe_je_stueck('g9_base_shirt', '#ffffff')
        teil = {'art': 'kleidung', 'foto_farbe': [0.35, 0.344, 0.368], 'render_farbe': [0.147, 0.147, 0.147],
                'pixel': 4708}
        zeilen = IterationKleider(m, {'teile': {'g9_base_shirt': teil}}).farbe()
        self.assertEqual(zeilen, ["m.kleid_umfaerben('g9_base_shirt')",
                                  "m.kleid_farbe_je_stueck('g9_base_shirt', '#3b3a3f')"])
        G9rezept.anwenden(m, '\n'.join(zeilen))
        self.assertEqual(m.kleidung['g9_base_shirt.bild.grau'], 1.0)
        self.assertNotIn('umfaerben', ' '.join(IterationKleider(m, {'teile': {'g9_base_shirt': teil}}).farbe()))

    def test_7_schicht_grau(self):
        from Genesis9.texturschicht import G9texturschicht
        schwarz = np.full((8, 8, 3), 0.07, np.float32)
        schwarz[0] = 0.1                                                            # eine Naht bleibt heller
        grau = G9texturschicht.grau(schwarz, 1.0)
        self.assertAlmostEqual(float(grau.mean()), 0.75, places=2)
        self.assertAlmostEqual(float(np.ptp(grau, axis=2).max()), 0.0)              # neutral
        self.assertGreater(float(grau[0].mean()), float(grau[1].mean()))
        blond = np.tile(np.asarray([1.0, 0.82, 0.62], np.float32), (4, 4, 1))
        flach = G9texturschicht.grau(blond, 1.0, flach=True)
        hell = float(blond[0, 0] @ np.asarray(G9texturschicht.HELLIGKEIT, np.float32))
        self.assertAlmostEqual(float(flach[0, 0, 0]), hell, places=3)
