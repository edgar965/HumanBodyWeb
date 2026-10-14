# -*- coding: utf-8 -*-
"""Weiche Hautgewichte für lose Kleidung (13.10.2026, `Hautnaehe`) und die Messung der Dehnung (`Dehnungsmessung`). Nicht gelaufen — läuft nur auf Ansage.

Hintergrund: am Zauberer rissen im Tanz Kanten bis zum 718fachen ihrer Länge, 0,1 % über 38×; die Ursache waren Gewichtssprünge zwischen Nachbarpunkten (Bein gegen Finger der linken Hand). `Hautnaehe` gibt dem Stoff in Abstand zum Körper die
weich gemischten Gewichte aller Käfigzellen im Umkreis; Finger, Zehen und Gesicht gehen in ihr Gelenk über. Kunstdaten: ein Käfig aus zwei Stäben (zwei Knochen) und ein Stoffstreifen, der erst anliegt und dann wegläuft.

    EltternTest        Finger/Hand → Unterarm, Zehen/Fuß → Unterschenkel, Twist → Glied, Gesicht → Kopf; ohne `lose_glieder` bleibt die Hand
    NaeheTest          anliegender Stoff behält seine Gewichte bitgleich, Stoff in Abstand bekommt eine Mischung (Summe 1, mehr als ein Knochen), Gewichte sind stetig im Ort (kein Sprung zwischen Nachbarpunkten), die Zahl der Einflüsse stimmt
    MessungTest        Einheit → alles 1; eine auf das Vierfache gestreckte Kante meldet 4; `punkte` ordnet die Lage mit der langen Kante schlechter; `bilder` verteilt gleichmäßig

Sabotage: in `Hautnaehe._kern` `sigma` auf 1e-6 setzen → `test_gewichte_sind_stetig_im_ort` rot; in `eltern` die Finger-Zeile streichen → `test_finger_gehen_in_den_unterarm` rot.
"""

import unittest

import numpy as np
from Kleidung.dehnungsmessung import Dehnungsmessung
from Kleidung.hautnaehe import Hautnaehe

KNOCHEN = ['hip', 'l_thigh', 'l_forearm', 'l_hand', 'l_thumb1', 'l_thightwist1', 'l_bigtoe1', 'l_foot', 'l_shin', 'head', 'l_eye']


class EltternTest(unittest.TestCase):
    def test_finger_gehen_in_den_unterarm(self):
        self.assertEqual(Hautnaehe.eltern('l_thumb1'), 'l_forearm')
        self.assertEqual(Hautnaehe.eltern('r_pinky3'), 'r_forearm')
        self.assertEqual(Hautnaehe.eltern('l_indexmetacarpal'), 'l_forearm')
        self.assertEqual(Hautnaehe.eltern('l_hand'), 'l_forearm')

    def test_zehen_und_fuss_gehen_in_den_unterschenkel(self):
        self.assertEqual(Hautnaehe.eltern('l_bigtoe1'), 'l_shin')
        self.assertEqual(Hautnaehe.eltern('r_toes'), 'r_shin')
        self.assertEqual(Hautnaehe.eltern('l_foot'), 'l_shin')

    def test_twist_geht_in_sein_glied_und_das_gesicht_in_den_kopf(self):
        self.assertEqual(Hautnaehe.eltern('l_thightwist2'), 'l_thigh')
        self.assertEqual(Hautnaehe.eltern('r_forearmtwist1'), 'r_forearm')
        self.assertEqual(Hautnaehe.eltern('l_eye'), 'head')
        self.assertEqual(Hautnaehe.eltern('lowerjaw'), 'head')
        self.assertEqual(Hautnaehe.eltern('l_pectoral'), 'spine4')

    def test_ohne_lose_glieder_bleibt_die_hand(self):
        self.assertEqual(Hautnaehe.eltern('l_hand', lose_glieder=False), 'l_hand')
        self.assertEqual(Hautnaehe.eltern('l_thumb1', lose_glieder=False), 'l_hand')
        self.assertEqual(Hautnaehe.eltern('l_foot', lose_glieder=False), 'l_foot')

    def test_andere_knochen_bleiben(self):
        for n in ('hip', 'l_thigh', 'spine2', 'head', 'l_forearm'):
            self.assertEqual(Hautnaehe.eltern(n), n)

    def test_nummern_bleiben_im_bereich_und_zeigen_auf_vorhandene_ziele(self):
        z = Hautnaehe.eltern_nummern(KNOCHEN)
        self.assertEqual(KNOCHEN[z[KNOCHEN.index('l_thumb1')]], 'l_forearm')
        self.assertEqual(KNOCHEN[z[KNOCHEN.index('l_eye')]], 'head')
        # fehlt der Zielknochen (hier `l_thigh` für Twist 2 nicht in der Liste), bleibt der Knochen er selbst
        self.assertEqual(Hautnaehe.eltern_nummern(['l_thightwist1', 'hip'])[0], 0)


class NaeheTest(unittest.TestCase):
    def setUp(self):
        # Käfig: zwei Stäbe (x = ±0,2), je 100 Punkte von y 0 bis 1; links Knochen 1 (`l_thigh`), rechts Knochen 0 (`hip`).
        y = np.linspace(0, 1, 100)
        links = np.c_[np.full(100, 0.2), y, np.zeros(100)]
        rechts = np.c_[np.full(100, -0.2), y, np.zeros(100)]
        self.kaefig = np.vstack([links, rechts])
        self.index = np.zeros((200, 4), dtype=np.int64)
        self.gewicht = np.zeros((200, 4))
        self.index[:100, 0] = KNOCHEN.index('l_thigh')
        self.gewicht[:100, 0] = 1.0
        self.index[100:, 0] = KNOCHEN.index('hip')
        self.gewicht[100:, 0] = 1.0
        self.naehe = Hautnaehe(self.kaefig, self.index, self.gewicht, KNOCHEN, adaptiv=0.5)

    def _stoff(self, abstand_x):
        """Ein Stoffstreifen quer über beide Stäbe auf Höhe 0,5, mit dem Abstand `abstand_x` vor der Ebene der Stäbe (z)."""
        x = np.linspace(-0.3, 0.3, 61)
        punkte = np.c_[x, np.full(61, 0.5), np.full(61, abstand_x)]
        # die alten Gewichte: Sprung in der Mitte (links Oberschenkel, rechts Hüfte)
        index = np.zeros((61, 4), dtype=np.int64)
        gewicht = np.zeros((61, 4))
        index[:, 0] = np.where(x > 0, KNOCHEN.index('l_thigh'), KNOCHEN.index('hip'))
        gewicht[:, 0] = 1.0
        return punkte, index, gewicht, np.full(61, abstand_x)

    def test_anliegender_stoff_behaelt_seine_gewichte_bitgleich(self):
        punkte, index, gewicht, abstand = self._stoff(0.01)
        i, g = self.naehe.berechnen(punkte, index, gewicht, abstand)
        self.assertTrue(np.array_equal(i[:, 0], index[:, 0]))
        self.assertTrue(np.allclose(g[:, 0], 1.0))

    def test_stoff_in_abstand_bekommt_eine_mischung(self):
        punkte, index, gewicht, abstand = self._stoff(0.20)
        i, g = self.naehe.berechnen(punkte, index, gewicht, abstand)
        self.assertTrue(np.allclose(g.sum(axis=1), 1.0))
        mitte = 30
        self.assertGreater(g[mitte, 1], 0.2, 'in der Mitte zwischen den Stäben zählen beide Knochen')
        self.assertEqual(set(i[mitte, :2]), {KNOCHEN.index('l_thigh'), KNOCHEN.index('hip')})

    def test_gewichte_sind_stetig_im_ort(self):
        punkte, index, gewicht, abstand = self._stoff(0.20)
        i, g = self.naehe.berechnen(punkte, index, gewicht, abstand)
        dicht = np.zeros((61, len(KNOCHEN)))
        for q in range(4):
            np.add.at(dicht, (np.arange(61), i[:, q]), g[:, q])
        sprung = np.abs(np.diff(dicht, axis=0)).sum(axis=1).max()
        alt = np.zeros((61, len(KNOCHEN)))
        for q in range(4):
            np.add.at(alt, (np.arange(61), index[:, q]), gewicht[:, q])
        sprung_alt = np.abs(np.diff(alt, axis=0)).sum(axis=1).max()
        self.assertEqual(sprung_alt, 2.0)
        self.assertLess(sprung, 0.5, 'zwischen Nachbarpunkten springen die weichen Gewichte nicht')

    def test_die_zahl_der_einfluesse_stimmt(self):
        punkte, index, gewicht, abstand = self._stoff(0.20)
        i, g = self.naehe.berechnen(punkte, index, gewicht, abstand, einfluesse=3)
        self.assertEqual(i.shape, (61, 3))
        self.assertEqual(g.shape, (61, 3))

    def test_stoff_ohne_freie_punkte_bleibt_unveraendert(self):
        punkte, index, gewicht, abstand = self._stoff(0.01)
        i, g = self.naehe.berechnen(punkte, index, gewicht, abstand)
        self.assertEqual(self.naehe.befund['frei_punkte'], 0)
        self.assertTrue(np.array_equal(i, index))
        self.assertTrue(np.array_equal(g, gewicht))


class MessungTest(unittest.TestCase):
    def _dreiecke(self):
        return np.array([[0, 1, 2], [1, 3, 2]])

    def _punkte(self):
        return np.array([[0, 0, 0], [0.01, 0, 0], [0, 0.01, 0], [0.01, 0.01, 0]], dtype=float)

    def test_einheit_dehnt_nichts(self):
        verf = np.tile(np.eye(4)[:3], (2, 1, 1, 1))              # 2 Stellungen, 1 Knochen
        index = np.zeros((4, 1), dtype=np.int64)
        gewicht = np.ones((4, 1))
        m = Dehnungsmessung.messen(self._punkte(), self._punkte(), self._dreiecke(), index, gewicht, verf)
        self.assertAlmostEqual(m['max'], 1.0, places=5)
        self.assertEqual(m['ueber_3'], 0.0)
        self.assertEqual(m['spitzen'], 0.0)

    def test_gestreckte_kante_wird_gemeldet(self):
        # Knochen 0 bleibt, Knochen 1 wandert um 0,04 m in x: Punkt 3 hängt an Knochen 1, die übrigen an Knochen 0
        verf = np.zeros((1, 2, 3, 4))
        verf[0, :, :, :3] = np.eye(3)
        verf[0, 1, 0, 3] = 0.04
        index = np.array([[0], [0], [0], [1]])
        gewicht = np.ones((4, 1))
        m = Dehnungsmessung.messen(self._punkte(), self._punkte(), self._dreiecke(), index, gewicht, verf)
        self.assertGreater(m['max'], 4.0)
        self.assertGreater(m['ueber_3'], 0.0)

    def test_punkte_ordnet_die_lage_mit_den_langen_kanten_schlechter(self):
        gut = {'spitzen': 0.0005}
        schlecht = {'spitzen': 0.004}
        self.assertLess(Dehnungsmessung.punkte(gut), Dehnungsmessung.punkte(schlecht))

    def test_bilder_verteilen_gleichmaessig_und_bleiben_im_bereich(self):
        b = Dehnungsmessung.bilder(8, 1004)
        self.assertEqual(len(b), 8)
        self.assertGreater(b[0], 0)
        self.assertLess(b[-1], 1004)
        self.assertEqual(b, sorted(b))
