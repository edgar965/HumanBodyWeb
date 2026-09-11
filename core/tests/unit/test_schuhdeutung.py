# -*- coding: utf-8 -*-
u"""Bibliotheksschuhe als Vorbilder: Fussmasse, Schuhdeutung, Schuhweg.

WARUM (11.09.2026, Edgar: „Die GarmentFit Schuhe sollen dann als verfügbare
Bibliothek Items in GarmentFit erscheinen.")
======================================================================
Drei Klassen, drei Prüfungen:

* `Fussmasse` misst am Netz — hier an einem KÜNSTLICHEN Fuss (Quader mit
  Zehenkeil), damit die Rechnung ohne die Figur nachprüfbar ist; die Zahlen
  der echten Figur stehen in `fussvorgabe.py` als Anteile.
* `Schuhdeutung` macht aus einem Schuhnetz Katalogstück und Regler — an
  drei künstlichen Schuhen (flach, Stiefelette, Kniestiefel).
* `Stueckueberfuehrung._ist_schuh` entscheidet, wer den Schuhweg nimmt:
  Kategorie führt, Geometrie springt ein. Ein einheitlicher Wert zog beim
  Messlauf 22 Miniröcke und Shorts zu den Stiefeln.
"""
import numpy as np
from django.test import SimpleTestCase

from ._humanbodypfad import Humanbodypfad

Humanbodypfad.assets()
from GarmentCode.fussmasse import Fussmasse                  # noqa: E402
from GarmentCode.schuh.fussvorgabe import Fussvorgabe        # noqa: E402
from GarmentCode.schuhdeutung import Schuhdeutung            # noqa: E402

from core.dienste.stueckueberfuehrung import Stueckueberfuehrung  # noqa: E402


def _quader(x0, x1, y0, y1, z0, z1, n=9):
    u"""Die Oberfläche eines Quaders als Punktwolke (Meter)."""
    xs, ys, zs = (np.linspace(a, b, n) for a, b in ((x0, x1), (y0, y1), (z0, z1)))
    punkte = []
    for x in xs:
        for y in ys:
            punkte += [[x, y, z0], [x, y, z1]]
    for x in xs:
        for z in zs:
            punkte += [[x, y0, z], [x, y1, z]]
    for y in ys:
        for z in zs:
            punkte += [[x0, y, z], [x1, y, z]]
    return np.asarray(punkte, dtype=np.float64)


class FussmasseTest(SimpleTestCase):

    databases = []

    def _figur(self):
        u"""Ein Bein als Säule, darunter ein Fuss als Quader — links (x > 0)."""
        fuss = _quader(0.17, 0.26, -0.20, 0.05, 0.0, 0.05)      # 25 x 9 x 5 cm
        bein = []
        for z in np.linspace(0.05, 0.9, 60):
            r = 0.04 if z < 0.15 else (0.06 if z < 0.45 else 0.05)
            for w in np.linspace(0, 2 * np.pi, 24, endpoint=False):
                bein.append([0.215 + r * np.cos(w), -0.07 + r * np.sin(w), z])
        kopf = _quader(-0.1, 0.1, -0.1, 0.1, 1.5, 1.68, n=4)
        return np.vstack([fuss, np.asarray(bein), kopf])

    def test_laenge_breite_und_lage_stimmen(self):
        m = Fussmasse(self._figur()).masse()
        self.assertAlmostEqual(m['foot_length'], 25.0, delta=0.6)
        self.assertAlmostEqual(m['foot_ball_width'], 9.0, delta=0.6)
        self.assertAlmostEqual(m['foot_x'], 21.5, delta=0.6)
        # Die Zehen zeigen nach -Y — im GarmentCode-Raum nach +Z.
        self.assertGreater(m['foot_toe_z'], m['foot_heel_z'])
        self.assertAlmostEqual(m['foot_toe_z'], 20.0, delta=0.6)

    def test_alle_namen_kommen_und_der_knoechel_ist_die_engste_scheibe(self):
        m = Fussmasse(self._figur()).masse()
        for name in Fussmasse.NAMEN:
            self.assertIn(name, m)
        self.assertLess(m['ankle_circ'], m['calf_circ'])
        self.assertLess(m['ankle_height'], m['calf_height'])

    def test_ohne_fuss_kommt_nichts_und_kein_fehler(self):
        self.assertEqual(Fussmasse(_quader(-0.1, 0.1, -0.1, 0.1, 1.0, 1.7, n=4)).masse(), {})


class FussvorgabeTest(SimpleTestCase):

    databases = []

    def test_gemessene_werte_gehen_vor(self):
        f = Fussvorgabe({'height': 168.0, 'foot_length': 30.0})
        self.assertEqual(f.foot_length, 30.0)
        self.assertIn('foot_length', {'foot_length'} - set(f.geschaetzt))

    def test_fehlende_werte_werden_geschaetzt_und_gemeldet(self):
        f = Fussvorgabe({'height': 168.0})
        self.assertAlmostEqual(f.foot_length, 168.0 * 0.1453, places=3)
        self.assertTrue(f.hinweise)
        self.assertEqual(len(f.geschaetzt),
                         len(Fussvorgabe.ANTEILE) + len(Fussvorgabe.WINKEL))

    def test_der_beinumfang_laeuft_zwischen_den_stuetzen(self):
        f = Fussvorgabe({'height': 168.0})
        mitte = (f.ankle_height + f.calf_height) / 2.0
        self.assertGreater(f.beinumfang(mitte), f.ankle_circ)
        self.assertLess(f.beinumfang(mitte), f.calf_circ)
        self.assertEqual(f.beinumfang(0.0), f.ankle_circ)


class SchuhdeutungTest(SimpleTestCase):

    databases = []

    def setUp(self):
        self.fuss = Fussvorgabe(dict(height=168.0, foot_length=24.41,
                                     foot_ball_width=9.14, ankle_height=13.78,
                                     knee_height=53.1))

    def _schuh(self, laenge, breite, hoehe):
        u"""Ein Schuh als Quader, Zehen nach -Y (Meter)."""
        return _quader(0.17, 0.17 + breite, -laenge, 0.0, 0.0, hoehe, n=13)

    def test_ein_flacher_schuh_wird_zur_ballerina(self):
        name, regler, bericht = Schuhdeutung(self._schuh(0.25, 0.095, 0.05),
                                             self.fuss).deuten()
        self.assertEqual(name, 'ballerina')
        self.assertAlmostEqual(regler['shoe.length'], 25.0 / 24.41, places=2)
        self.assertAlmostEqual(regler['shoe.width'], 9.5 / 9.14, places=2)
        self.assertNotIn('boot.height', regler)

    def test_ein_kniehoher_schuh_wird_zum_stiefel(self):
        name, regler, bericht = Schuhdeutung(self._schuh(0.27, 0.10, 0.45),
                                             self.fuss).deuten()
        self.assertEqual(name, 'stiefel')
        erwartet = (45.0 - 13.78) / (53.1 - 13.78)
        self.assertAlmostEqual(regler['boot.height'], erwartet, places=2)
        self.assertNotIn('shoe.quarter_height', regler)

    def test_eine_knoechelhohe_wird_zur_stiefelette(self):
        name, regler, _ = Schuhdeutung(self._schuh(0.26, 0.10, 0.20),
                                       self.fuss).deuten()
        self.assertEqual(name, 'stiefelette')
        self.assertLess(regler['boot.height'], Schuhdeutung.HOCH_AB)

    def test_ein_paar_wird_am_fuss_getrennt_auch_wenn_die_schaefte_sich_beruehren(self):
        u"""Zwei Overknee-Stiefel der Bibliothek (cortu_floppy_overknee,
        heroine_boots_1) wurden als EIN 45 cm langer Schuh gemessen: Über
        alle Punkte war die Lücke zwischen links und rechts nur 0,24 bzw.
        0,09 der Breite, weil sich die Schäfte an den Oberschenkeln berühren.
        Am Fuss ist sie 0,57 — dort wird jetzt gesucht."""
        links = np.vstack([self._schuh(0.27, 0.10, 0.15),
                           _quader(0.05, 0.27, -0.20, 0.0, 0.15, 0.45, n=13)])
        rechts = links * np.array([-1.0, 1.0, 1.0])
        deutung = Schuhdeutung(np.vstack([links, rechts]), self.fuss)
        self.assertEqual(len(deutung.p), len(links))
        name, regler, _ = deutung.deuten()
        self.assertEqual(name, 'stiefel')
        self.assertAlmostEqual(regler['shoe.length'], 27.0 / 24.41, places=2)

    def test_der_absatz_wird_gesagt_aber_nicht_gebaut(self):
        u"""Eine Stiefelette mit 3 cm Absatz: der Vorfuss steht 3 cm über
        dem tiefsten Punkt der Ferse, der Schaft hinten ist der höhere Teil."""
        vorn = self._schuh(0.25, 0.095, 0.06)
        vorn = vorn[vorn[:, 1] < -0.08]
        vorn[:, 2] += 0.03
        hinten = _quader(0.17, 0.265, -0.08, 0.0, 0.0, 0.16, n=13)
        deutung = Schuhdeutung(np.vstack([vorn, hinten]), self.fuss)
        name, regler, bericht = deutung.deuten()
        self.assertTrue(any('Absatz' in h for h in bericht['hinweise']))
        self.assertNotIn('absatz', ' '.join(regler))

    def test_zu_wenige_punkte_sind_ein_fehler_kein_schuh(self):
        with self.assertRaises(ValueError):
            Schuhdeutung(np.zeros((5, 3)), self.fuss).deuten()


class SchuhwegTest(SimpleTestCase):

    databases = []

    class _Gemessen:
        def __init__(self, oben_cm):
            self.oben_cm = oben_cm

    MASSE = {'height': 168.0}

    def test_im_schuhordner_zaehlt_bis_zur_huefte(self):
        self.assertTrue(Stueckueberfuehrung._ist_schuh(
            self._Gemessen(85.0), self.MASSE, 'shoes'))    # Overknee-Stiefel
        self.assertFalse(Stueckueberfuehrung._ist_schuh(
            self._Gemessen(94.0), self.MASSE, 'shoes'))    # bootyshorts

    def test_in_fremden_ordnern_nur_flaches(self):
        self.assertTrue(Stueckueberfuehrung._ist_schuh(
            self._Gemessen(6.0), self.MASSE, 'tops'))      # Ballerina
        self.assertTrue(Stueckueberfuehrung._ist_schuh(
            self._Gemessen(44.0), self.MASSE, 'tops'))     # Wasserstiefel
        self.assertFalse(Stueckueberfuehrung._ist_schuh(
            self._Gemessen(85.0), self.MASSE, 'skirts'))   # Minirock
        self.assertFalse(Stueckueberfuehrung._ist_schuh(
            self._Gemessen(85.0), self.MASSE, ''))
