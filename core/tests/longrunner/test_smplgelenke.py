# -*- coding: utf-8 -*-
u"""Smplgelenke — die 24 SMPL-Gelenke aus einem Netz.

WARUM (Edgar, 07.09.2026: „SMPL mit SMPL Skeleton"): Die SMPL-Figur der
Szene hatte kein Skelett, und der Rig-Schalter blieb fuer sie wirkungslos.
Die Gelenke kommen jetzt aus `J_regressor` — derselben Quelle, aus der
`Smplkoerper` seine Kinematik und seine Armlaenge nimmt.

WAS HIER GEPRUEFT WIRD, UND WARUM GENAU DAS
===========================================
1. **Die Namen kommen aus EINER Liste.** Es gab schon eine Klasse
   `Smplskelett` (in `VideoToBVH/wrappers/`), und die neue hiess zuerst
   genauso. `skelett.py` beschreibt in seinem eigenen Kopf, was daraus
   wird: „DIESELBEN LISTEN, ZWEIMAL, MIT UNTERSCHIEDLICHER LAENGE."
2. **Die Elternliste des Modells und die der Definition stimmen ueberein.**
   Waeren sie verschieden, haetten BVH-Ausgabe und Rig-Anzeige zwei
   verschiedene Skelette — ohne dass irgendwo etwas scheitert.
3. **Die Naeherung ist beziffert.** Der Regressor gilt fuer die Ruhelage;
   die Koerper der Szene sind A40-posiert. Der Test haelt die gemessenen
   Schranken fest, damit ein spaeterer Umbau sie nicht stillschweigend
   verschlechtert.
4. **Fremde Topologie wird abgewiesen.** GarmentCodes eigene Koerper haben
   23.752 Punkte. Ein Regressor mit 6.890 Spalten wuerde dort entweder
   scheitern oder — schlimmer — Unsinn liefern.

Ohne die Modelldateien (`VideoToBVH/models/smpl`) wird uebersprungen: Sie
stehen unter einer eigenen Lizenz und liegen nicht im Repo.
"""
import os
import unittest

import numpy as np
from django.conf import settings

from SMPL.gelenke import Smplgelenke
from SMPL.koerper import Smplkoerper
from SMPL.skelett import Smplskelett


class SmplgelenkeTest(unittest.TestCase):

    #: Gemessen am 07.09.2026, beide Modelle, drei Formen. Grosszuegig
    #: gerundet — der Test soll eine VERSCHLECHTERUNG melden, nicht bei
    #: der dritten Nachkommastelle rot werden.
    MEDIAN_MM = 4.0
    MAX_MM = 15.0

    @classmethod
    def setUpClass(cls):
        cls.ordner = str(settings.SMPL_MODELS_DIR)
        if not os.path.isfile(os.path.join(cls.ordner, 'SMPL_FEMALE.npz')):
            raise unittest.SkipTest('SMPL-Modelle fehlen (%s)' % cls.ordner)

    # ------------------------------------------------------- eine Definition

    def test_namen_kommen_aus_der_skelettdefinition(self):
        u"""Keine zweite Namensliste — sonst driften BVH und Anzeige."""
        self.assertIs(Smplgelenke.NAMEN, Smplskelett.NAMEN)
        self.assertEqual(len(Smplgelenke.NAMEN), 24)

    def test_eltern_des_modells_gleich_der_definition(self):
        u"""`kintree_table` gegen die ausgeschriebene Elternliste."""
        for geschlecht in ('female', 'male'):
            with self.subTest(geschlecht=geschlecht):
                g = Smplgelenke.aus_modell(geschlecht, self.ordner)
                self.assertEqual(list(g.eltern), list(Smplskelett.ELTERN))

    def test_genau_eine_wurzel(self):
        g = Smplgelenke.aus_modell('female', self.ordner)
        self.assertEqual(list(g.eltern).count(-1), 1)
        self.assertEqual(g.eltern[0], -1)

    # --------------------------------------------------------- Topologie

    def test_fremde_topologie_wird_abgewiesen(self):
        u"""23.752 Punkte sind GarmentCodes Koerper, nicht SMPL."""
        g = Smplgelenke.aus_modell('female', self.ordner)
        self.assertFalse(Smplgelenke.passt(np.zeros((23752, 3))))
        self.assertFalse(Smplgelenke.passt(None))
        self.assertTrue(Smplgelenke.passt(np.zeros((6890, 3))))
        with self.assertRaises(ValueError):
            g.gelenke(np.zeros((23752, 3)))

    # ------------------------------------------------------ Knochenliste

    def test_knochenliste_hat_form_und_wurzel(self):
        g = Smplgelenke.aus_modell('female', self.ordner)
        modell = Smplkoerper.laden('female', self.ordner)
        knochen = g.knochen(modell.a40(None))

        self.assertEqual(len(knochen), 24)
        self.assertEqual([k for k in knochen if k['eltern'] is None][0]['name'],
                         Smplskelett.NAMEN[0])
        namen = {k['name'] for k in knochen}
        for k in knochen:
            self.assertEqual(len(k['kopf']), 3)
            self.assertEqual(len(k['schwanz']), 3)
            if k['eltern'] is not None:
                # Ein Elternteil, den es nicht gibt, haenge im Browser die
                # halbe Figur an den Ursprung.
                self.assertIn(k['eltern'], namen)

    def test_endgelenke_zeigen_vom_elternteil_weg(self):
        u"""Ohne Kind zeigt der `schwanz` in die Verlaengerung.

        Sonst faellt er auf das Gelenk selbst zusammen, und der Browser
        zeichnet eine Linie der Laenge null — Haende, Fuesse und Kopf
        blieben unsichtbar.
        """
        g = Smplgelenke.aus_modell('female', self.ordner)
        modell = Smplkoerper.laden('female', self.ordner)
        knochen = {k['name']: k for k in g.knochen(modell.a40(None))}
        for name in ('Left_palm', 'Right_palm', 'Head', 'Left_foot'):
            with self.subTest(gelenk=name):
                k = knochen[name]
                weg = np.linalg.norm(np.array(k['schwanz']) - np.array(k['kopf']))
                self.assertGreater(weg, 0.01, '%s: Schwanz auf dem Gelenk' % name)

    def test_versatz_zieht_auf_den_boden(self):
        g = Smplgelenke.aus_modell('female', self.ordner)
        modell = Smplkoerper.laden('female', self.ordner)
        punkte = modell.a40(None)
        ohne = g.knochen(punkte)[0]['kopf'][1]
        mit = g.knochen(punkte, versatz_y=0.25)[0]['kopf'][1]
        self.assertAlmostEqual(ohne - mit, 0.25, places=5)

    # ----------------------------------------------------- Guete der Zahl

    def test_ruhelage_ist_exakt(self):
        u"""In der Ruhelage IST der Regressor die Definition der Gelenke."""
        for geschlecht in ('female', 'male'):
            with self.subTest(geschlecht=geschlecht):
                g = Smplgelenke.aus_modell(geschlecht, self.ordner)
                modell = Smplkoerper.laden(geschlecht, self.ordner)
                v = modell.formen(None)
                abw = np.abs(g.gelenke(v) - (modell.J_regressor @ v)).max()
                self.assertLess(abw, 1e-9)

    def test_posierte_haltung_bleibt_in_den_gemessenen_schranken(self):
        u"""A40 gegen die echte Vorwaertskinematik.

        Gemessen am 07.09.2026: Median 2,1 mm, max 9,6 mm (Schulter). Die
        Schranken hier sind bewusst weiter — sie sollen eine
        Verschlechterung melden, nicht Rauschen.
        """
        for geschlecht in ('female', 'male'):
            with self.subTest(geschlecht=geschlecht):
                g = Smplgelenke.aus_modell(geschlecht, self.ordner)
                modell = Smplkoerper.laden(geschlecht, self.ordner)
                abw = self._abweichung(modell, g)
                self.assertLess(np.median(abw), self.MEDIAN_MM)
                self.assertLess(abw.max(), self.MAX_MM)

    def test_gegenprobe_ein_verschobenes_netz_faellt_auf(self):
        u"""Sabotage: Waeren die Schranken blind, taugte der Test nichts."""
        g = Smplgelenke.aus_modell('female', self.ordner)
        modell = Smplkoerper.laden('female', self.ordner)
        abw = self._abweichung(modell, g, stoerung=0.05)
        self.assertGreater(abw.max(), self.MAX_MM)

    def _abweichung(self, modell, gelenke, stoerung=0.0):
        u"""mm je Gelenk: Regressor auf dem posierten Netz gegen Kinematik."""
        v_rest = modell.formen(None)
        j_rest = modell.J_regressor @ v_rest
        winkel = np.radians(modell.A40_GRAD)
        drehungen = {modell.GELENKE['shoulder_l']: np.array([0.0, 0.0, -winkel]),
                     modell.GELENKE['shoulder_r']: np.array([0.0, 0.0, winkel])}
        v = modell.posieren(v_rest, drehungen)
        versatz = v[:, 1].min()
        v = v.copy()
        v[:, 1] -= versatz
        if stoerung:
            v[:, 1] += stoerung

        welt = [None] * len(j_rest)
        for i in range(len(j_rest)):
            eltern = int(modell.parents[i])
            lokal = np.eye(4)
            lokal[:3, :3] = SmplgelenkeTest.rodrigues(drehungen.get(i, np.zeros(3)))
            lokal[:3, 3] = j_rest[i] - (j_rest[eltern] if eltern >= 0
                                        else np.zeros(3))
            welt[i] = lokal if eltern < 0 else welt[eltern] @ lokal
        wahr = np.array([w[:3, 3] for w in welt])
        wahr[:, 1] -= versatz
        return np.linalg.norm(wahr - gelenke.gelenke(v), axis=1) * 1000

    @staticmethod
    def rodrigues(rv):
        laenge = np.linalg.norm(rv)
        if laenge < 1e-12:
            return np.eye(3)
        k = rv / laenge
        kreuz = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
        return (np.eye(3) + np.sin(laenge) * kreuz
                + (1 - np.cos(laenge)) * (kreuz @ kreuz))
