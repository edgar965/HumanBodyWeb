# -*- coding: utf-8 -*-
u"""Netzuebertrag — SMPL-Gelenke auf einem Netz fremder Topologie.

WARUM (Edgar, 07.09.2026: „SMPL modell zeigt immer noch kein Skeleton"):
Der Dialog bietet unter „SMPL" fuenf Koerper an, aber nur zwei sind
SMPL-Netze. `mean_all`, `mean_female` und `mean_male` sind GarmentCodes
eigene (23.752 Punkte), und `mean_all` ist der ERSTE Eintrag — wer eine
SMPL-Figur in die Szene stellt, bekommt normalerweise genau den.

DIE MESSLATTE IST DIE IDENTITAET
================================
Ordnet man ein SMPL-Netz sich selbst zu, muss exakt dasselbe herauskommen
wie ohne Uebertrag. Das ist die schaerfste Probe, die es hier gibt: Sie
faellt bei jedem Vorzeichen-, Index- oder Normierungsfehler.

DIE HALTUNG IST KEIN DETAIL
===========================
`test_falsche_haltung_verzieht_die_arme` ist die Gegenprobe zur
Angleichung: Mit einem T-Pose-Referenzkoerper wandert die Handflaeche um
177 mm, waehrend der Median bei 0,0 mm bleibt — der Rumpf sieht richtig
aus, die Arme sind falsch. Ohne diesen Fall koennte jemand die Angleichung
entfernen und alle anderen Tests blieben gruen.

Ohne die Modelldateien (`VideoToBVH/models/smpl`) wird uebersprungen.
"""
import os
import unittest

import numpy as np
from django.conf import settings

from SMPL.gelenke import Smplgelenke
from SMPL.koerper import Smplkoerper
from SMPL.uebertrag import Netzuebertrag


class NetzuebertragTest(unittest.TestCase):

    databases = set()

    @classmethod
    def setUpClass(cls):
        cls.ordner = str(settings.SMPL_MODELS_DIR)
        if not os.path.isfile(os.path.join(cls.ordner, 'SMPL_FEMALE.npz')):
            raise unittest.SkipTest('SMPL-Modelle fehlen')
        cls.gelenke = Smplgelenke.aus_modell('female', cls.ordner)
        cls.modell = Smplkoerper.laden('female', cls.ordner)
        cls.punkte = cls.modell.a40(None)
        cls.wahr = cls.gelenke.gelenke(cls.punkte)

    def _abweichung(self, netz, referenz=None):
        u"""mm je Gelenk gegenueber der Wahrheit."""
        referenz = self.punkte if referenz is None else referenz
        uebertrag = self.gelenke.uebertragen(netz, referenz)
        ist = self.gelenke.gelenke(uebertrag.punkte(netz))
        return np.linalg.norm(ist - self.wahr, axis=1) * 1000

    # ------------------------------------------------------- die Messlatte

    def test_identitaet_ist_exakt(self):
        u"""Dasselbe Netz auf sich selbst — kein Millimeter Abweichung."""
        abw = self._abweichung(self.punkte)
        self.assertLess(abw.max(), 1e-6)

    def test_gemischte_reihenfolge_aendert_nichts(self):
        u"""Die Zuordnung geht ueber die LAGE, nicht ueber den Index."""
        misch = np.random.default_rng(7).permutation(len(self.punkte))
        abw = self._abweichung(self.punkte[misch])
        self.assertLess(abw.max(), 1e-6)

    # ------------------------------------------------- fremde Topologien

    def test_groberes_netz_bleibt_nah(self):
        u"""Jeder dritte Punkt — gemessen 6,05 mm Median, max 14,9 mm."""
        abw = self._abweichung(self.punkte[::3])
        self.assertLess(np.median(abw), 12.0)
        self.assertLess(abw.max(), 30.0)

    def test_verrauschtes_netz_bleibt_nah(self):
        rng = np.random.default_rng(7)
        netz = self.punkte + rng.normal(0, 0.002, self.punkte.shape)
        abw = self._abweichung(netz)
        self.assertLess(np.median(abw), 5.0)

    # ---------------------------------------------------- die Gegenprobe

    def test_falsche_haltung_verzieht_die_arme(self):
        u"""Ohne Haltungsangleichung wandert die Hand um Zentimeter.

        Der Median bleibt dabei bei null — der Rumpf sieht richtig aus. Wer
        nur den Median prueft, uebersieht genau diesen Fehler.
        """
        tpose = self.modell.a40(None, grad=0.0)
        abw = self._abweichung(self.punkte, referenz=tpose)
        self.assertGreater(abw.max(), 100.0)
        hand = list(Smplgelenke.NAMEN).index('Right_palm')
        self.assertGreater(abw[hand], 100.0)

    # -------------------------------------------------------- Guetemass

    def test_guete_meldet_die_zuordnungsabstaende(self):
        u"""Der Wert ist die Warnlampe fuer eine schiefe Zuordnung."""
        gleich = Netzuebertrag.bauen(self.punkte, self.punkte)
        self.assertLess(gleich.guete['median'], 1e-9)
        self.assertLess(gleich.guete['max'], 1e-9)

        tpose = self.modell.a40(None, grad=0.0)
        schief = Netzuebertrag.bauen(tpose, self.punkte)
        self.assertGreater(schief.guete['max'], gleich.guete['max'])

    def test_normierung_gleicht_groesse_und_lage_an(self):
        u"""Ein doppelt so grosses, verschobenes Netz ordnet gleich zu.

        Ohne die Angleichung faende der Kopf des einen die Schulter des
        anderen — der Fehler waere ueber die ganze Figur verteilt und
        saehe wie ein schlechtes Modell aus, nicht wie ein Rechenfehler.
        """
        anders = self.punkte * 2.0 + np.array([3.0, 1.0, -2.0])
        a = Netzuebertrag.bauen(self.punkte, self.punkte)
        b = Netzuebertrag.bauen(self.punkte, anders)
        self.assertTrue(np.array_equal(a.zuordnung, b.zuordnung))

    def test_fremdes_referenznetz_wird_abgewiesen(self):
        with self.assertRaises(ValueError):
            self.gelenke.uebertragen(self.punkte, np.zeros((100, 3)))

    # -------------------------------------------------- Blockweg == KDTree

    def test_rueckfall_ohne_scipy_rechnet_dasselbe(self):
        u"""Der Blockweg ist der Ersatz, wenn scipy fehlt — er muss stimmen."""
        a = self.punkte[:400]
        b = self.punkte[::7]
        mit = Netzuebertrag._naechste(Netzuebertrag._normiert(a),
                                      Netzuebertrag._normiert(b))
        ohne = Netzuebertrag._naechste_blockweise(Netzuebertrag._normiert(a),
                                                  Netzuebertrag._normiert(b))
        self.assertTrue(np.array_equal(np.asarray(mit[0]), np.asarray(ohne[0])))
