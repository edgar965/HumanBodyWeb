# -*- coding: utf-8 -*-
"""UMA-Regler lesen und auf Genesis abbilden: `Umaregler`, `Umaabbildung`, `Umamorpheaufgenesis` (17.10.2026). Geschrieben, nicht gelaufen (Tests nur auf Ansage).

WARUM: Aus 62 DNA-Reglern und drei Kinder-Posen (Unity-Assets, Text-YAML) werden Knochenoperationen auf Genesis-Knochen. Drei Stellen, an denen stumm etwas Falsches
herauskaeme: die Kurve (Unitys AnimationCurve ausserhalb der Schluessel: konstant — als Schleife gelesen lieferte `breastSize` bei 0 den Wert fuer 1), die Zuordnung (ein
Knochen ohne Genesis-Gegenstueck bewegt nichts, ohne Meldung) und die Spiegelung (Unity: x = rechts der Figur, Genesis: x = links). Geprueft:

1. Die Kurve: Hermite zwischen den Schluesseln (Mitte bei linearen Tangenten), konstant ausserhalb, ohne Schluessel `x` selbst; `wert` bildet auf `[min, max]` ab.
2. Die Zuordnung: Links/Rechts, die Namen ohne „Adjust“ (Posen), Mitte, der Gluteus (nur Links traegt), unbekannte Knochen → None.
3. Die Operationen: Skalieren `1 + Faktor·m`, Verschieben mit gespiegeltem x, Drehen mit gespiegelter Achse UND umgekehrtem Winkel (`M·R(a, θ)·M = R(M·a, −θ)`), Posen mit
   `1 + (Skala − 1)·Gewicht`.
4. Die Dateien des UMA-Projekts, wenn vorhanden: 62 Regler, 160 Wirkungen, jeder Knochen der Posen und Regler zugeordnet (ausser dem Gluteus rechts).
"""
import unittest

import numpy as np
from django.test import SimpleTestCase

from core.dienste.umaabbildung import Umaabbildung
from core.dienste.umamorpheaufgenesis import Umamorpheaufgenesis
from core.dienste.umaregler import Umaregler


class _Feld:
    kopf = {'l_upperarm': np.array([0.2, 1.3, 0.0]), 'hip': np.array([0.0, 0.97, 0.0]), 'l_nostril': np.array([0.01, 1.55, 0.1]),
            'r_nostril': np.array([-0.01, 1.55, 0.1]), 'l_thigh': np.array([0.07, 0.89, 0.0]), 'r_thigh': np.array([-0.07, 0.89, 0.0]), 'pelvis': np.array([0.0, 0.99, 0.0])}


def bauer():
    b = Umamorpheaufgenesis()
    b.feld = _Feld()
    return b


class KurveTest(SimpleTestCase):
    databases = set()

    def test_1_hermite_konstant_ausserhalb_und_ohne_kurve_der_wert_selbst(self):
        gerade = [(0.0, 0.0, 1.0, 1.0), (1.0, 1.0, 1.0, 1.0)]
        self.assertAlmostEqual(Umaregler.abbilden(gerade, 0.25), 0.25, places=6)
        self.assertAlmostEqual(Umaregler.abbilden(gerade, -3.0), 0.0, msg='vor dem ersten Schluessel konstant, keine Schleife')
        self.assertAlmostEqual(Umaregler.abbilden(gerade, 7.0), 1.0)
        self.assertAlmostEqual(Umaregler.abbilden([], 0.3), 0.3)
        knick = [(0.0, 0.2, 0.6, 0.6), (0.5, 0.5, 0.8, 0.8), (1.0, 1.0, 1.0, 1.0)]       # armLength
        self.assertAlmostEqual(Umaregler.abbilden(knick, 0.5), 0.5)
        self.assertAlmostEqual(Umaregler.abbilden(knick, 0.0), 0.2)

    def test_2_wert_bildet_auf_min_max_ab(self):
        effekt = {'kurve': [(0.0, 0.2, 0.6, 0.6), (0.5, 0.5, 0.8, 0.8), (1.0, 1.0, 1.0, 1.0)], 'min': -1.0, 'max': 1.0}
        self.assertAlmostEqual(Umaregler.wert(effekt, 0.5), 0.0, places=6, msg='Mitte = kein Effekt')
        self.assertAlmostEqual(Umaregler.wert(effekt, 1.0), 1.0, places=6)
        self.assertAlmostEqual(Umaregler.wert(effekt, 0.0), -0.6, places=6)
        pose = {'kurve': [], 'min': 0.0, 'max': 1.0}
        self.assertAlmostEqual(Umaregler.wert(pose, 0.5), 0.5, msg='Posen-Regler haben bei Vorgabe Gewicht 0,5')


class AbbildungTest(SimpleTestCase):
    databases = set()

    def test_3_links_rechts_und_namen_ohne_adjust(self):
        links, rechts = Umaabbildung.ziel('LeftArm'), Umaabbildung.ziel('RightArm')
        self.assertEqual((links['knochen'], rechts['knochen']), ('l_upperarm', 'r_upperarm'))
        self.assertFalse(links['welt'], 'Glieder rechnen im Knochenrahmen')
        self.assertEqual(Umaabbildung.ziel('LeftForeArmAdjust')['wirkt'], ['l_forearm', 'l_forearmtwist1', 'l_forearmtwist2'])
        self.assertEqual(Umaabbildung.ziel('LeftEyebrowLow')['knochen'], 'l_browinner', 'die Posen nennen den Knochen ohne Adjust')
        self.assertEqual(Umaabbildung.ziel('NoseBase')['mitte'], ['l_nostril', 'r_nostril'])

    def test_4_gluteus_traegt_nur_links_und_unbekanntes_faellt_weg(self):
        self.assertEqual(Umaabbildung.ziel('LeftGluteus')['knochen'], 'pelvis')
        self.assertIsNone(Umaabbildung.ziel('RightGluteus'))
        self.assertIsNone(Umaabbildung.ziel('LeftToeBase_end'))
        self.assertIsNone(Umaabbildung.ziel('IrgendEinKnochen'))
        self.assertEqual(Umaabbildung.ziel('Position')['pivot'], (0.0, 0.0, 0.0))


class OperationenTest(SimpleTestCase):
    databases = set()

    def test_5_skalieren_ist_eins_plus_faktor_mal_wert(self):
        b = bauer()
        effekt = {'art': 'skalieren', 'knochen': 'LeftArm', 'wert': (0.5, 0.5, 0.5), 'kurve': [], 'min': -1.0, 'max': 1.0}
        ops = b.effekt_ops(effekt, 1.0)                                    # m = 1 → Faktor 1,5
        self.assertEqual(len(ops), 1)
        np.testing.assert_allclose(ops[0]['wert'], (1.5, 1.5, 1.5))
        np.testing.assert_allclose(b.effekt_ops(effekt, 0.5)[0]['wert'], (1.0, 1.0, 1.0), err_msg='Vorgabe: kein Effekt')

    def test_6_verschieben_spiegelt_x(self):
        b = bauer()
        effekt = {'art': 'verschieben', 'knochen': 'Hips', 'wert': (0.07, 0.0, 0.01), 'kurve': [], 'min': -1.0, 'max': 1.0}
        op = b.effekt_ops(effekt, 1.0)[0]
        np.testing.assert_allclose(op['wert'], (-0.07, 0.0, 0.01), err_msg='Unity x = rechts, Genesis x = links')
        self.assertTrue(op['welt'])

    def test_7_drehen_spiegelt_achse_und_kehrt_den_winkel_um(self):
        b = bauer()
        (ax, ay, az), grad = b.drehung((1.0, 0.0, 0.0), 30.0)
        self.assertEqual((ax, ay, az, grad), (-1.0, 0.0, 0.0, -30.0))
        # Gegenprobe mit Matrizen: M·R_unity·M == R_genesis
        from Genesis9.knochenfeld import G9knochenfeld
        m = np.diag([-1.0, 1.0, 1.0])
        for achse in ((1, 0, 0), (0, 1, 0), (0.3, -0.5, 0.8)):
            (gx, gy, gz), gg = b.drehung(achse, 40.0)
            np.testing.assert_allclose(m @ G9knochenfeld.drehmatrix(achse, 40.0) @ m, G9knochenfeld.drehmatrix((gx, gy, gz), gg), atol=1e-9)

    def test_8_pose_skaliert_mit_dem_gewicht(self):
        b = bauer()
        pose = [{'knochen': 'LeftArm', 'position': (0.0, 0.0, 0.0), 'rotation': (0, 0, 0, 1), 'skala': (1.25, 1.17, 1.4)}]
        ops = b.pose_ops(pose, 0.5)
        np.testing.assert_allclose(ops[0]['wert'], (1.125, 1.085, 1.2), atol=1e-9)
        self.assertEqual(len(ops), 1, 'Identitaet bei Position und Rotation erzeugt keine Operation')
        self.assertEqual(b.pose_ops([{'knochen': 'GibtEsNicht', 'position': (1, 0, 0), 'rotation': (0, 0, 0, 1), 'skala': (2, 2, 2)}], 1.0), [])

    def test_9_mitte_setzt_den_drehpunkt_zwischen_die_knochen(self):
        b = bauer()
        op = b.op('NoseBase', 'skalieren', (1.2, 1.2, 1.2))
        np.testing.assert_allclose(op['pivot'], [0.0, 1.55, 0.1], atol=1e-9)
        self.assertEqual(op['wirkt'], ['l_nostril', 'r_nostril'])


@unittest.skipUnless(Umaregler.vorhanden(), 'UMA-Projekt nicht da')
class UmaDateienTest(SimpleTestCase):
    databases = set()

    def test_10_alle_regler_und_posen_sind_gelesen_und_zugeordnet(self):
        regler = Umaregler.regler()
        self.assertEqual(len(regler), 62)
        self.assertEqual(sum(len(r['effekte']) for r in regler), 160)
        nicht = set()
        for r in regler:
            for e in r['effekte']:
                for k in ([e['knochen']] if e['art'] != 'pose' else [p['knochen'] for p in e['pose']]):
                    if Umaabbildung.ziel(k) is None:
                        nicht.add(k)
        self.assertEqual(nicht, {'RightGluteus'})
        posen = Umaregler.kinderposen()
        self.assertEqual([p['kennung'] for p in posen], ['Kind_UMA3', 'Maedchen_UMA2', 'Junge_UMA2'])
        self.assertGreaterEqual(len(posen[0]['pose']), 20)
