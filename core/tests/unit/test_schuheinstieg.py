# -*- coding: utf-8 -*-
u"""Der Einstieg eines Halbschuhs ist so lang wie der Fuss dort — am Schnitt.

WARUM (11.09.2026, Edgar: „slipper sehen ja noch echte sehr schlecht aus.
Mach dir einen testcase, die sollen wie slipper und nicht wie ein
schmetterling ausschauen")
======================================================================
Der Schmetterling: Quartiere, deren Oberkante so lang ist wie ihre
Sohlennaht, stehen wie Flügel vom Fuss ab — der Einstieg war 49,9 cm lang,
der Fuss hat dort 38. Hier wird am SCHNITT geprüft, dass der Einstieg zum
Fuss passt (`schuh/einstieg.py`, `fusseinstieg.py`); ob die Simulation
daraus einen Schuh macht, prüft `longrunner/test_schuhform.py` am Netz.
"""
import numpy as np
from django.test import SimpleTestCase

from ._schuhbau import Schuhbau
from .test_schuhschnitt import SchuhschnittTest


class SchuheinstiegTest(SimpleTestCase):

    databases = []
    FUSS = SchuhschnittTest.FUSS

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Schuhbau.vorbereiten(cls.FUSS)

    def _halbschuh(self, **regler):
        return Schuhbau.bauen('Halbschuh', **regler).links

    # ---------------------------------------------------------- Einstieg

    def test_der_einstieg_ist_nicht_laenger_als_der_fuss_dort(self):
        u"""Slipper, Ballerina, Vorgabe: Ring aus zwei Quartier-Oberkanten
        und Blatt-Einstieg gegen Fersenweg plus Ristbogen auf der Höhe."""
        from GarmentCode.schuh.einstieg import Schuheinstieg
        for regler in ({'shoe.quarter_height': 0.33, 'shoe.opening': 1.5},
                       {'shoe.quarter_height': 0.22, 'shoe.opening': -2.0},
                       {}):
            s = self._halbschuh(**regler)
            fuss = s.fuss
            kappe = s.quartier_a.kappe
            soll = (fuss.fersenumfang((s.flanke + kappe) / 2.0)
                    + fuss.ristbogen(s.flanke)) * (1.0 - Schuheinstieg.SPANNUNG)
            # Der Einstieg des Blatts bekommt vom Regler `opening` einen
            # Bogen dazu — der liegt lose über dem Rist, nicht am Ring.
            bogen = s.blatt.interfaces['einstieg'].edges.length() - 2 * s.blatt.oben_halb
            self.assertLessEqual(s.einstiegsumfang() - bogen, soll + 0.3, regler)
            self.assertGreater(s.einstiegsumfang(), 0.8 * soll, regler)
            self.assertLess(s.einstiegsumfang(), 45.0, regler)   # vorher 49,9

    def test_die_quartiere_werden_nach_oben_schmaler(self):
        s = self._halbschuh(**{'shoe.quarter_height': 0.33})
        q = s.quartier_a
        self.assertLess(q.interfaces['oben'].edges.length(),
                        q.interfaces['sohle'].edges.length() - 1.0)
        self.assertLess(s.blatt.oben_halb, s.blatt.bogen_halb - 1.0)
        # Beide Flanken einer Naht sind gleich lang — auch schräg.
        self.assertAlmostEqual(q.flankenlaenge(),
                               s.blatt.interfaces['flanke_a'].edges.length(),
                               places=3)

    def test_die_blattnaht_ist_so_lang_wie_der_sohlenrand(self):
        u"""Vorher 22 % länger — die Simulation kräuselte den Überschuss
        in die Zehe."""
        s = self._halbschuh()
        self.assertAlmostEqual(s.blatt.nahtlaenge(),
                               s.sohlenrand.randlaenge_vorn(), delta=0.1)

    def test_die_flanke_reicht_hoechstens_bis_an_den_rist(self):
        u"""`quarter_height` 0,7 (9,6 cm) liegt über dem Fussrücken an der
        Vamplinie (5,8 cm): begrenzt, mit Hinweis; 0,33 nicht."""
        from GarmentCode.schuh.einstieg import Schuheinstieg
        hoch = Schuhbau.bauen('Halbschuh', **{'shoe.quarter_height': 0.7})
        self.assertTrue(any(u'begrenzt' in h for h in hoch.hinweise), hoch.hinweise)
        self.assertAlmostEqual(hoch.links.flanke,
                               Schuheinstieg.FLANKE_BIS * self.FUSS['vamp_height'],
                               places=3)
        flach = Schuhbau.bauen('Halbschuh', **{'shoe.quarter_height': 0.33})
        self.assertFalse(any(u'begrenzt' in h for h in flach.hinweise))
        self.assertAlmostEqual(flach.links.flanke, 0.33 * self.FUSS['ankle_height'],
                               places=3)
        # Der Stiefel schliesst über dem Rist — ihn begrenzt das nicht.
        stiefel = Schuhbau.bauen('Stiefel', **{'shoe.quarter_height': 0.7})
        self.assertFalse(any(u'begrenzt' in h for h in stiefel.hinweise))
        self.assertAlmostEqual(stiefel.links.flanke, 0.7 * self.FUSS['ankle_height'],
                               places=3)

    def test_die_masse_werden_zwischen_den_hoehen_gerechnet(self):
        from GarmentCode.schuh.fussvorgabe import Fussvorgabe
        f = Fussvorgabe(dict(self.FUSS, height=168.0))
        self.assertEqual(f.geschaetzt, ())
        h25, h50 = 0.25 * f.ankle_height, 0.5 * f.ankle_height
        self.assertAlmostEqual(f.fersenumfang(h25), self.FUSS['heel_girth_25'])
        self.assertAlmostEqual(f.fersenumfang((h25 + h50) / 2.0),
                               (self.FUSS['heel_girth_25'] + self.FUSS['heel_girth_50']) / 2.0)
        self.assertAlmostEqual(f.fersenumfang(0.0), self.FUSS['heel_girth_25'])
        self.assertAlmostEqual(f.ristbogen(0.3 * f.vamp_height), self.FUSS['instep_arc_30'])
        self.assertEqual(f.ristbogen(f.vamp_height + 1.0), 0.0)
        self.assertGreater(f.ristbogen(0.9 * f.vamp_height), 0.0)
        # Ohne Messung: aus der Körperhöhe, nahe an der Messung.
        ohne = Fussvorgabe({'height': 168.0})
        self.assertIn('heel_girth_50', ohne.geschaetzt)
        self.assertAlmostEqual(ohne.fersenumfang(h50), self.FUSS['heel_girth_50'], delta=0.5)

    # ----------------------------------------------------------- Messung

    def test_die_messung_findet_umfang_und_bogen_eines_runden_fusses(self):
        u"""Ein Zylinder (Radius 3 cm) als Fuss: Der Weg um die Ferse in
        Höhe h ist zweimal die Tiefe hinter der Vamplinie plus die Breite
        dort, der Ristbogen der Kreisbogen über h."""
        from GarmentCode.fusseinstieg import Fusseinstieg
        r, laenge = 0.03, 0.24
        winkel = np.linspace(0, 2 * np.pi, 120, endpoint=False)
        ys = np.linspace(-laenge, 0.0, 121)
        punkte = np.asarray([[r * np.sin(w), y, r + r * np.cos(w)]
                             for y in ys for w in winkel])
        # Der Boden des Zylinders als Scheibe, damit die Ferse hinten zu ist.
        knoechel_cm = 2 * r * 100.0
        messung = Fusseinstieg(punkte, 0.0, -laenge, 0.0, knoechel_cm).masse()
        self.assertAlmostEqual(messung['vamp_height'], 2 * r * 100.0, delta=0.2)
        tiefe = Fusseinstieg.VAMP_BEI * laenge
        for anteil in Fusseinstieg.FERSE_BEI:
            h = anteil * knoechel_cm / 100.0
            halb = (r * r - (h - r) ** 2) ** 0.5
            soll = (2 * tiefe + 2 * halb) * 100.0
            self.assertAlmostEqual(messung['heel_girth_%d' % round(anteil * 100)],
                                   soll, delta=0.06 * soll, msg=str(anteil))
        for anteil in Fusseinstieg.RIST_BEI:
            h = anteil * 2 * r
            soll = 2 * r * np.arccos((h - r) / r) * 100.0
            self.assertAlmostEqual(messung['instep_arc_%d' % round(anteil * 100)],
                                   soll, delta=0.08 * soll, msg=str(anteil))

    def test_der_oberschenkel_im_band_der_vamplinie_hebt_den_rist_nicht_an(self):
        u"""Das Bein reicht bis zur Hüfte, und an der Figur „FemaleWithHair"
        lagen drei Oberschenkelpunkte (69–75 cm hoch) im Band der Vamplinie:
        `vamp_height` wurde 74,9 cm, der Ristbogen unmessbar, der Ballerina
        stand 5,2 cm vom Fuss ab (Edgar, 11.09.2026: „rechts und links ist
        ein abstand von > 5 cm"). Was über dem Knöchel liegt, ist kein Rist."""
        from GarmentCode.fusseinstieg import Fusseinstieg
        r, laenge = 0.03, 0.24
        winkel = np.linspace(0, 2 * np.pi, 120, endpoint=False)
        ys = np.linspace(-laenge, 0.0, 121)
        fuss = [[r * np.sin(w), y, r + r * np.cos(w)] for y in ys for w in winkel]
        y_vamp = -Fusseinstieg.VAMP_BEI * laenge
        schenkel = [[0.145, y_vamp + dy, z] for dy in (-0.004, 0.0, 0.004)
                    for z in (0.69, 0.717, 0.749)]
        messung = Fusseinstieg(np.asarray(fuss + schenkel), 0.0, -laenge, 0.0,
                               2 * r * 100.0).masse()
        self.assertAlmostEqual(messung['vamp_height'], 2 * r * 100.0, delta=0.2)
        self.assertIn('instep_arc_50', messung)

    def test_zu_wenige_punkte_ergeben_keine_messung(self):
        from GarmentCode.fusseinstieg import Fusseinstieg
        punkte = np.zeros((5, 3))
        self.assertEqual(Fusseinstieg(punkte, 0.0, -0.24, 0.0, 13.0).masse(), {})
