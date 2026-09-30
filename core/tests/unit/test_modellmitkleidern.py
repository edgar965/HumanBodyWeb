# -*- coding: utf-8 -*-
u"""„2D3D Kleider" (30.09.2026): der Zustand `ModellMitKleidern`, das Rezept `G9rezept`, der Morphbauer `G9kleidmorphe`
und die Häutung `G9tanzhaut` — alles auf Kunstdaten, ohne Daz-Bibliothek, ohne Lauf.

1. `ModellMitKleidern`: Funktionen setzen die Regler der Sammeleinträge (`sorte.<kennung>`, `passform:laenge`, Achsen,
   eigene Morphe), Grenzen werden gezogen, `als_dict` ↔ `aus` ist verlustfrei, `hilfe` nennt jede öffentliche Funktion.
2. `G9rezept`: nur `m.<funktion>(literal, …)` — Importe, fremde Namen, unbekannte Funktionen und Ausdrücke als Argument
   werden mit Zeilennummer abgelehnt; ein Fehler mitten im Rezept lässt die Aufrufe davor wirksam.
3. `G9kleidmorphe._gewicht`/`_richtung`: 1 im Kern des Höhenbereichs, Hermite-Auslauf, Seite links = +x, „aussen" zeigt
   radial
   von der Achse weg.
4. `G9tanzhaut`: in Ruhe (Spuren = Ruhelage) bleibt jeder Punkt stehen; dreht ein Elternknochen um 90°, wandert ein
   Punkt
   des Kindknochens mit — um seinen Kopf, nicht um den Ursprung.

Sabotage-Gegenproben: in `G9rezept.pruefen` die Prüfung auf `ast.Name == OBJEKT` weglassen -> Fall 2 rot („x.kleid_nur"
durchgelassen); in `G9tanzhaut.haeuten` `ruhe_inv` durch die Einheit ersetzen -> Fall 4 rot (Ruhe bewegt alle Punkte).
"""
import numpy as np
from django.test import SimpleTestCase
from Genesis9.kleidmorphe import G9kleidmorphe
from Genesis9.modellmitkleidern import ModellMitKleidern
from Genesis9.modellrezept import G9rezept
from Genesis9.tanzhaut import G9tanzhaut


class ModellTest(SimpleTestCase):

    databases = set()

    def test_1_funktionen_setzen_die_regler(self):
        m = ModellMitKleidern()
        m.kleid_nur('shirt', 'jeans').kleid_anteil('kleid', 2.0).passform(laenge_cm=-40, weite_cm=3).uebergang(1.5)
        m.haar_nur('kin').haar_achse('kin', 'laenge', 0.7).haar_farbe('#A0B0C0')
        m.morph_wert('kleidung', 'shirt', 'saum', 0.5)
        self.assertEqual(m.kleidung['sorte.shirt'], 1.0)
        self.assertEqual(m.kleidung['sorte.kleid'], 1.0)                    # gekappt auf 1
        self.assertEqual(m.kleidung['passform:laenge'], -20.0)              # Grenze
        self.assertEqual(m.kleidung['mischung:uebergang'], 1.5)
        self.assertEqual(m.kleidung['shirt.eigen.saum'], 0.5)
        self.assertEqual(m.haar['kin.achse.laenge'], 0.7)
        # Die Grundsorte der Bibliothek bekommt einen ausdrücklichen Regler 0 — sonst gälte sie als 1,0 und würde mit
        # gebaut („Edgar - Hoch", 30.09.2026: Kin UND Mavick).
        self.assertEqual(m.haar['sorte.' + ModellMitKleidern.HAAR_VORGABE], 0.0)
        self.assertEqual(m.farben['haar'], '#a0b0c0')
        m.kleid_nur('rock')
        self.assertEqual(m.kleidung['sorte.shirt'], 0.0)
        with self.assertRaises(ValueError):
            m.haar_achse('kin', 'quatsch', 1)
        with self.assertRaises(ValueError):
            m.kleid_farbe('rot')
        # Haltung: die Oberarme aus der A-Pose senken — links um −Grad um z, rechts +Grad (gemessen 30.09.2026).
        self.assertEqual(m.drehung(), {})
        m.haltung(40)
        self.assertEqual(m.drehung(), {'l_upperarm': {'rotation/z': -40.0}, 'r_upperarm': {'rotation/z': 40.0}})
        m.haltung(55)                                            # über der A-Pose (43°) wandern die Hände in den Rumpf
        self.assertEqual(m.haltung_werte['arme'], ModellMitKleidern.ARME_HOECHSTENS)
        self.assertEqual(ModellMitKleidern.aus(m.als_dict()).als_dict(), m.als_dict())
        self.assertEqual(ModellMitKleidern.aus(m.als_dict()).drehung(), m.drehung())
        namen = {n for n, _s, _t in ModellMitKleidern.hilfe()}
        self.assertIn('kleid_nur', namen)
        self.assertIn('morph_neu', namen)
        self.assertNotIn('als_dict', namen)

    def test_2_rezept_nur_erlaubte_aufrufe(self):
        m = ModellMitKleidern()
        aus = G9rezept.anwenden(m, "m.haar_nur('kin')\n# Kommentar\nm.kleid_anteil('shirt', anteil=0.5)\n")
        self.assertEqual([t for _z, t in aus], ["m.haar_nur('kin')", "m.kleid_anteil('shirt', anteil=0.5)"])
        self.assertEqual(m.kleidung['sorte.shirt'], 0.5)
        for schlecht in ('import os', 'x.kleid_nur(1)', 'm.kaputt()', 'm.kleid_nur(os.sep)',
                         'm.kleid_nur("a"); print(1)',
                         'm.als_dict()'):
            with self.assertRaises(ValueError, msg=schlecht):
                G9rezept.pruefen(schlecht)
        with self.assertRaises(ValueError) as fehler:
            G9rezept.anwenden(m, "m.kleid_nur('rock')\nm.haar_achse('kin', 'falsch', 1)")
        self.assertIn('Zeile 2', str(fehler.exception))
        self.assertEqual(m.kleidung['sorte.rock'], 1.0)          # Zeile 1 war wirksam

    def test_3_morphgewicht_und_richtung(self):
        punkte = np.array([[0.1, 0.0, 0.0], [0.1, 0.5, 0.0], [-0.1, 0.5, 0.0], [0.1, 1.0, 0.0]])
        w = G9kleidmorphe._gewicht({'von': 0.4, 'bis': 0.6, 'weich': 0.1}, punkte, 0.0, 1.0)
        self.assertAlmostEqual(float(w[1]), 1.0)
        self.assertAlmostEqual(float(w[0]), 0.0)
        self.assertAlmostEqual(float(w[3]), 0.0)
        links = G9kleidmorphe._gewicht({'von': 0.0, 'bis': 1.0, 'seite': 'links'}, punkte, 0.0, 1.0)
        self.assertEqual(links.tolist()[1:3], [1.0, 0.0])
        r = G9kleidmorphe._richtung({'richtung': 'aussen'}, punkte, np.zeros(3))
        self.assertAlmostEqual(float(r[1][0]), 1.0)
        self.assertAlmostEqual(float(r[2][0]), -1.0)
        unten = G9kleidmorphe._richtung({'richtung': 'unten'}, punkte, np.zeros(3))[0].tolist()
        self.assertEqual(unten, [0.0, -1.0, 0.0])
        with self.assertRaises(ValueError):
            G9kleidmorphe._richtung({'richtung': 'schraeg'}, punkte, np.zeros(3))


class Spuren:
    def __init__(self, tracks, frames=1):
        self.tracks = tracks
        self.position_track = None
        self.frame_count = frames


class TanzhautTest(SimpleTestCase):

    databases = set()

    def bauplan(self):
        # Wurzel bei 0, Kind bei (0, 1, 0), beide in Ruhe ohne Drehung.
        return [{'name': 'huefte', 'eltern': None, 'pos': [0, 0, 0], 'quat': [0, 0, 0, 1], 'ende': False},
                {'name': 'bein', 'eltern': 'huefte', 'pos': [0, 1, 0], 'quat': [0, 0, 0, 1], 'ende': False},
                {'name': 'bein_ende', 'eltern': 'bein', 'pos': [0, 1, 0], 'quat': [0, 0, 0, 1], 'ende': True}]

    def test_4_ruhe_bleibt_und_kind_dreht_um_seinen_kopf(self):
        haut = G9tanzhaut(self.bauplan())
        punkte = np.array([[0.0, 1.5, 0.0], [0.2, 0.2, 0.0]])
        bindung = {'knochen': ['huefte', 'bein'], 'index': np.array([[1, 0, 0, 0], [0, 0, 0, 0]]),
                   'gewicht': np.array([[1.0, 0, 0, 0], [1.0, 0, 0, 0]])}
        ruhe = haut.haeuten(punkte, bindung, haut.matrizen(Spuren({}), 0))
        np.testing.assert_allclose(ruhe, punkte, atol=1e-12)
        # `bein` um 90° um z (x -> y): der Punkt 0,5 über dem Kopf des Beins geht auf x = −0,5 in Kopfhöhe.
        s = np.sqrt(0.5)
        bewegt = haut.haeuten(punkte, bindung, haut.matrizen(Spuren({'bein': [0, 0, s, s]}), 0))
        np.testing.assert_allclose(bewegt[0], [-0.5, 1.0, 0.0], atol=1e-9)
        np.testing.assert_allclose(bewegt[1], punkte[1], atol=1e-12)   # hängt an der Hüfte
