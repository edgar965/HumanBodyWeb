# -*- coding: utf-8 -*-
u"""Ordner `2d3DIterationen` (30.09.2026): die automatischen Anpassungen der Iterationen von „2D3D Kleider" — alles auf
Kunstdaten, ohne Daz-Bibliothek, ohne Lauf, ohne Datenbank.

1. `Schrittsuche`: ohne Verlauf der Start, mit einem Punkt ein Schritt, weiter wenn es half, zurück mit halbem Schritt
   wenn nicht; Grenzen; Stillstand → None.
2. `Farbangleich`: das VERHÄLTNIS Foto ÷ Render gedämpft auf die Tönung, unter der Schwelle kein Aufruf, nie unter MIN.
3. `Kleiderwahl` und `Teilmasken`: Haut ↔ Stoff je Band; Kennfarben überleben eine Skalierung (Beleuchtung).
4. `Befundmessung.netz`: Vorzeichen (+ außen, − innen) und Höhenbänder an einer Probenwand.
5. `IterationModell.rezept`: aus Modell + Befund ein Rezept, das `G9rezept.pruefen` besteht und angewandt das Modell so
   ändert, wie der Befund verlangt (Haltung, Kleider, Farbe, Weite, Morph, Haarfarbe).

Sabotage-Gegenproben: in `Schrittsuche.naechster` „m1 < m0" umdrehen → Fall 1 rot; in `Befundmessung._signiert` das
Vorzeichen weglassen → Fall 4 rot; in `IterationKleider.morphe` `BAND_MM` auf 100 → Fall 5 rot (kein Morph).
"""
import numpy as np
from django.test import SimpleTestCase
from Genesis9.modellmitkleidern import ModellMitKleidern
from Genesis9.modellrezept import G9rezept
from iterationen2d3d.befundmessung import Befundmessung
from iterationen2d3d.farbangleich import Farbangleich
from iterationen2d3d.iterationmodell import IterationModell
from iterationen2d3d.kleiderwahl import Kleiderwahl
from iterationen2d3d.schrittsuche import Schrittsuche
from iterationen2d3d.teilmasken import Teilmasken


class SchrittsucheTest(SimpleTestCase):

    databases = set()

    def test_1_bergsuche(self):
        s = Schrittsuche(35.0, 5.0, 0.0, 43.0)
        self.assertEqual(s.naechster([]), 35.0)
        self.assertEqual(s.naechster([(35, 30.0)]), 40.0)
        self.assertEqual(s.naechster([(43, 30.0)]), 38.0)                      # am Anschlag: nach unten
        self.assertEqual(s.naechster([(35, 30.0), (40, 28.0)]), 43.0)          # half → weiter, an der Grenze gekappt
        self.assertEqual(s.naechster([(35, 30.0), (40, 31.0)]), 37.5)          # half nicht → zurück, halber Schritt
        self.assertIsNone(s.naechster([(40, 30.0), (40.5, 31.0)]))             # Schritt unter 20 % des Startschritts
        self.assertEqual(s.naechster([(None, 1.0), (35, 30.0)]), 40.0)        # Runden ohne Wert zählen nicht

    def test_2_farbangleich(self):
        # Render zu hell (0,6) gegen Foto 0,3: Verhältnis 0,5, gedämpft 0,7 → Faktor 0,65 auf die Tönung 0,5.
        self.assertEqual(Farbangleich.naechste('#808080', [0.3, 0.3, 0.3], [0.6, 0.6, 0.6], 500), '#535353')
        self.assertIsNone(Farbangleich.naechste('#808080', [0.3, 0.3, 0.3], [0.6, 0.6, 0.6], 10))   # zu wenig Pixel
        self.assertIsNone(Farbangleich.naechste('#808080', [0.31, 0.3, 0.3], [0.3, 0.3, 0.3], 500))  # nah genug
        self.assertEqual(Farbangleich.naechste('#101010', [0.0, 0.0, 0.0], [0.5, 0.5, 0.5], 500), '#080808')
        # MIN (0,03) erreicht: die Tönung bleibt, also kein Aufruf.
        self.assertIsNone(Farbangleich.naechste('#080808', [0.0, 0.0, 0.0], [0.5, 0.5, 0.5], 500))

    def test_3_kleiderwahl_und_teilmasken(self):
        haut, grau = [0.75, 0.55, 0.45], [0.3, 0.3, 0.32]
        self.assertTrue(Kleiderwahl.haut(haut))
        self.assertFalse(Kleiderwahl.haut(grau))
        self.assertEqual(Kleiderwahl.stuecke({'rumpf': grau, 'oberschenkel': haut}),
                         ['g9_base_shirt', 'g9_base_shorts'])
        self.assertEqual(Kleiderwahl.stuecke({'rumpf': haut, 'oberschenkel': grau}), ['angie_jeans'])
        self.assertEqual(Kleiderwahl.stuecke({}), ['g9_base_shirt', 'g9_base_shorts'])
        farben = Teilmasken.farben(3)
        bild = np.zeros((2, 3, 3), np.float32)
        for i in range(3):
            bild[0, i] = np.asarray(farben[i]) * 0.6                            # beleuchtet: nur skaliert
        bild[1, 0] = np.asarray(farben[0]) * 0.6 + 0.04                          # etwas Glanz auf den anderen Kanälen
        maske = np.ones((2, 3), bool)
        maske[1, 2] = False
        masken = Teilmasken.zuordnen(bild, maske, 3)
        self.assertEqual(masken[0].tolist(), [[True, False, False], [True, False, False]])
        self.assertEqual(masken[1].tolist(), [[False, True, False], [False, False, False]])
        self.assertEqual(masken[2].tolist(), [[False, False, True], [False, False, False]])

    def test_4_netzabstand_mit_vorzeichen(self):
        # Eine Probenwand bei x = 0 (Normale +x), Höhe 0…1; Punkte davor (+) und dahinter (−).
        y = np.linspace(0.0, 1.0, 41)
        proben = np.column_stack([np.zeros_like(y), y, np.zeros_like(y)])
        normalen = np.tile([1.0, 0.0, 0.0], (len(y), 1))
        messung = Befundmessung(proben, normalen)
        punkte = np.array([[0.01, 0.1, 0.0], [0.01, 0.3, 0.0], [-0.02, 0.5, 0.0], [-0.02, 0.7, 0.0], [0.03, 0.9, 0.0]])
        netz_mm, abs_mm, baender = messung.netz(punkte)
        self.assertAlmostEqual(netz_mm, 2.0)                                     # (10 + 10 − 20 − 20 + 30) / 5
        self.assertAlmostEqual(abs_mm, 18.0)
        self.assertEqual(baender, [10.0, 10.0, -20.0, -20.0, 30.0])
        self.assertEqual(Befundmessung(None, None).netz(punkte), (None, None, [None] * 5))
        # Grundlinie eines Stücks: nur die Körperpunkte in SEINEM Kasten (+2 cm) — der Arm weit draußen zählt nicht.
        koerper = np.array([[0.005, 0.475, 0.0], [0.005, 0.525, 0.0], [0.30, 0.5, 0.0]])     # Rumpf +5 mm, „Arm" +300
        stueck = np.array([[0.02, 0.48, 0.0], [0.02, 0.52, 0.0]])
        self.assertAlmostEqual(messung.grund(koerper, stueck), 5.0)
        befund = messung.befund([{'punkte': koerper, 'art': 'koerper', 'sorte': 'koerper'},
                                 {'punkte': stueck, 'art': 'kleidung', 'sorte': 'shirt'}], [])
        self.assertAlmostEqual(befund['teile']['shirt']['grund_mm'], 5.0)
        self.assertIsNone(befund['teile']['koerper']['grund_mm'])

    def test_5_rezept_aus_befund(self):
        m = ModellMitKleidern()
        # Erste automatische Runde: keine Kleider, kein Befund → die Stücke; die A-Pose bleibt (keine Haltung).
        rezept = IterationModell(m, {}, [], []).rezept()
        self.assertNotIn('m.haltung', rezept)
        self.assertIn("m.kleid_nur('g9_base_shirt', 'g9_base_shorts')", rezept)
        G9rezept.anwenden(m, rezept)
        # Eine gesenkte Haltung (von Hand oder aus alten Runden) wird auf die A-Pose zurückgenommen.
        m.haltung(35)
        self.assertEqual(IterationModell(m, {}, [], []).haltung(), ['m.haltung(0.0)'])
        m.haltung(0)
        # Befund: der Körper selbst liegt 10 mm außerhalb des Netzes (Grundlinie); das Shirt ist zu hell und im Mittel
        # 22 mm außerhalb, also 12 mm über der Grundlinie; unten (Band 0) 42 mm, oben (Band 4) −8 mm darüber; Haar zu
        # hell.
        koerper = {'art': 'koerper', 'netz_mm': 10.0, 'netz_abs_mm': 30.0, 'baender': [10.0] * 5, 'pixel': 3000,
                   'foto_farbe': [0.4, 0.3, 0.3], 'render_farbe': [0.9, 0.8, 0.8]}
        shirt = {'art': 'kleidung', 'netz_mm': 22.0, 'netz_abs_mm': 24.0, 'baender': [52.0, 22.0, 22.0, 22.0, -8.0],
                 'grund_mm': 10.0, 'pixel': 900, 'foto_farbe': [0.2, 0.2, 0.22], 'render_farbe': [0.4, 0.4, 0.44]}
        haar = {'art': 'haar', 'netz_mm': 3.0, 'netz_abs_mm': 4.0, 'baender': [None] * 5, 'pixel': 300,
                'foto_farbe': [0.5, 0.5, 0.5], 'render_farbe': [0.8, 0.7, 0.5]}
        m.haar_nur('kin_hair')
        befund = {'runde': 2, 'teile': {'koerper': koerper, 'g9_base_shirt': shirt, 'kin_hair': haar},
                  'koerper_baender': {'rumpf': [0.3, 0.3, 0.3], 'oberschenkel': [0.7, 0.5, 0.4]}}
        verlauf = [{'runde': 2, 'haltung': 0.0, 'koerper_mm': 30.0, 'frisur': 'kin_hair', 'haar_mm': 4.0,
                    'laenge': 0.0}]
        rezept = IterationModell(m, befund, verlauf, ['kin_hair', 'mavick_hair']).rezept()
        G9rezept.pruefen(rezept)
        zeilen = [z for z in rezept.splitlines() if z and not z.startswith('#')]
        self.assertTrue(zeilen[0].startswith('m.kleid_farbe('))                 # A-Pose: keine Haltungszeile
        self.assertIn('m.passform(weite_cm=-0.42)', zeilen)                     # −0,35 · 12 mm über der Grundlinie
        self.assertIn("m.morph_neu('kleidung', 'g9_base_shirt', 'netz_b0', richtung='aussen', weg_cm=1.0, von=0.0, "
                      "bis=0.2, wert=-1.47)", zeilen)                           # Band 0: 42 mm draußen → nach innen
        self.assertIn("m.morph_neu('kleidung', 'g9_base_shirt', 'netz_b4', richtung='aussen', weg_cm=1.0, von=0.8, "
                      "bis=1.0, wert=0.63)", zeilen)                            # Band 4: 18 mm drinnen → nach außen
        self.assertEqual(sum(1 for z in zeilen if 'morph_neu' in z), 5)        # jedes Band liegt über 8 mm
        self.assertTrue(any(z.startswith('m.haar_farbe(') for z in zeilen))
        self.assertFalse(any('haar_nur' in z for z in zeilen))                  # kein Stillstand → keine neue Frisur
        # Fehlt der Regler der Grundsorte (altes Modell), kommt zuerst ein ausdrückliches `haar_nur`.
        alt = ModellMitKleidern.aus(m.als_dict())
        alt.haar = {'sorte.mavick_hair': 1.0}
        self.assertEqual(IterationModell(alt, befund, verlauf).haare.aufrufe(), ["m.haar_nur('mavick_hair')"])
        # Haarlänge: der Verlauf enthält die letzte Runde schon — wurde es von 0,2 auf 0,4 schlechter, geht es zurück
        # auf 0,3 (nicht blind weiter, weil der Punkt doppelt stünde).
        m.haar_achse('kin_hair', 'laenge', 0.4)
        haar['netz_abs_mm'] = 9.0
        laenger = verlauf + [{'runde': 3, 'haltung': 40.0, 'koerper_mm': 30.0, 'frisur': 'kin_hair', 'haar_mm': 8.0,
                              'laenge': 0.2},
                             {'runde': 4, 'haltung': 40.0, 'koerper_mm': 30.0, 'frisur': 'kin_hair', 'haar_mm': 9.0,
                              'laenge': 0.4}]
        self.assertEqual(IterationModell(m, befund, laenger).haare.laenge(),
                         ["m.haar_achse('kin_hair', 'laenge', 0.3)"])
        m.haltung_werte['arme'] = 55.0                                          # alte Runde: zurück in die A-Pose
        self.assertEqual(IterationModell(m, befund, verlauf).haltung(), ['m.haltung(0.0)'])
