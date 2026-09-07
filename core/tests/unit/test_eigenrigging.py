# -*- coding: utf-8 -*-
u"""Zuordnung und Hautgewichte fuer SMPL und MakeHuman.

WARUM (Edgar, 07.09.2026: „Das Rigging funktioniert wohl nicht fuer die
neuen Modelle SMPL, MakeHuman", und: „du hast doch retarget fuer das SMPL
skeleton, konfiguriere das")
====================================================================
Beide Ziele brauchen zweierlei: eine Zuordnung der BVH-Knochen auf ihre
eigenen Namen, und Hautgewichte, damit das Netz dem Skelett folgt. Beides
ist im Bestand vorhanden und wird nur umgekehrt bzw. gelesen — genau das
prueft dieser Test gegen die echten Listen und Dateien, nicht gegen
Konstanten in einer Tabelle.

DER GEFAEHRLICHE FEHLER IST DIE STILLE FEHLZUORDNUNG: Ein Knochenname, den
das Zielskelett gar nicht kennt, bekommt keine Spur; ein Gewicht auf der
falschen Spalte bewegt den Arm, wenn das Bein tritt. Weder das eine noch
das andere wirft irgendwo eine Ausnahme.
"""
import os
import unittest

import numpy as np
from django.conf import settings

from humanbody_core.skeleton.formats import (SkeletonAIST_SMPL, SkeletonCMU,
                                             SkeletonMocapNet)
from humanbody_core.skeleton.formats.mh_zuordnung import (DEF_ZU_MH,
                                                          Mhzuordnung)
from humanbody_core.skeleton.formats.smpl_knochen import (DEF_ZU_SMPL,
                                                          Smplzuordnung)
from SMPL.skelett import Smplskelett


class SmplzuordnungTest(unittest.TestCase):

    databases = []

    def test_jeder_name_steht_im_skelett(self):
        u"""Sonst bekaeme der Knochen keine Spur und bliebe stehen."""
        fremd = [n for n in DEF_ZU_SMPL.values() if n not in Smplskelett.NAMEN]
        self.assertEqual(fremd, [])

    def test_die_tabelle_ist_die_umkehrung_und_sonst_nichts(self):
        u"""Keine zweite Quelle: `SkeletonAIST_SMPL` bleibt massgeblich."""
        for bvh, defname in SkeletonAIST_SMPL.BONE_MAP_TO_RIGIFY.items():
            if defname:
                self.assertEqual(DEF_ZU_SMPL[defname], bvh)

    def test_kein_def_knochen_wird_doppelt_vergeben(self):
        u"""Bei zwei BVH-Namen auf einen DEF-Knochen faellt einer weg.

        Bei AIST/SMPL tritt der Fall nicht auf. Der Test haelt das fest,
        damit es beim naechsten Format nicht stillschweigend kippt.
        """
        ziele = [d for d in SkeletonAIST_SMPL.BONE_MAP_TO_RIGIFY.values() if d]
        self.assertEqual(len(ziele), len(set(ziele)))

    def test_ein_fremdes_format_trifft_die_wichtigen_gelenke(self):
        zuordnung = Smplzuordnung.fuer(SkeletonCMU)
        getroffen = {v for v in zuordnung.values() if v}
        for gelenk in ('Pelvis', 'Left_hip', 'Right_knee', 'Left_shoulder',
                       'Left_elbow', 'Head'):
            self.assertIn(gelenk, getroffen)

    def test_keine_ausnahmen_bei_smpl(self):
        u"""Gemessen: p90 82,7 -> 2,9 Grad (siehe `smpl_knochen.py`)."""
        for bauart in (SkeletonAIST_SMPL, SkeletonCMU, SkeletonMocapNet):
            self.assertEqual(Smplzuordnung.ausnahmen(bauart), [])


class MhzuordnungTest(unittest.TestCase):

    databases = []

    @classmethod
    def setUpClass(cls):
        from MakeHuman.skelett import Mhskelett
        if not Mhskelett.vorhanden():
            raise unittest.SkipTest('default.mhskel fehlt')
        cls.rig = set(Mhskelett.rig()['bones'])

    def test_jeder_name_steht_in_der_rig_datei(self):
        u"""Der Abgleich, der `lthumb` und `rthumb` gefunden hat.

        MocapNET nennt das erste Daumenglied `lthumb`, die Rig-Datei
        `finger1-1.L` — zwei von 80 Namen, die die Umkehrung falsch traefe.
        Gelesen haette man das nicht.
        """
        fehlt = sorted(v for v in DEF_ZU_MH.values() if v not in self.rig)
        self.assertEqual(fehlt, [])

    def test_die_spine_nummern_laufen_umgekehrt(self):
        u"""MakeHumans `spine05` liegt UNTEN, Rigifys `DEF-spine` auch.

        Wer die Zahlen paart (`DEF-spine.001` auf `spine01`), verdreht den
        ganzen Rumpf, ohne dass etwas rot wird.
        """
        self.assertEqual(DEF_ZU_MH['DEF-spine'], 'spine05')
        self.assertEqual(DEF_ZU_MH['DEF-spine.003'], 'spine02')

    def test_drehknochen_bleiben_ohne_ziel(self):
        u"""Sie behalten ihre Ruhelage — das ist die richtige Antwort."""
        for name in ('upperarm02.L', 'lowerleg02.R', 'pelvis.L', 'root'):
            self.assertNotIn(name, DEF_ZU_MH.values())

    def test_ein_fremdes_format_trifft_die_wichtigen_knochen(self):
        getroffen = {v for v in Mhzuordnung.fuer(SkeletonCMU).values() if v}
        for knochen in ('spine05', 'upperleg01.L', 'lowerleg01.R',
                        'upperarm01.L', 'lowerarm01.L', 'head'):
            self.assertIn(knochen, getroffen)


class SmplhautTest(unittest.TestCase):

    databases = []

    @classmethod
    def setUpClass(cls):
        cls.ordner = str(settings.SMPL_MODELS_DIR)
        if not os.path.isfile(os.path.join(cls.ordner, 'SMPL_FEMALE.npz')):
            raise unittest.SkipTest('SMPL-Modelle fehlen')
        from SMPL.haut import Smplhaut
        cls.haut = Smplhaut.aus_modell('female', cls.ordner)

    def test_hoechstens_vier_knochen_je_punkt_stehen_im_modell(self):
        u"""Es wird nichts weggeschnitten — das ist der Punkt.

        Waeren es mehr als vier, muesste die Kuerzung Gewicht umverteilen,
        und die Figur saehe an den Gelenken anders aus als in SMPL selbst.
        """
        belegt = (self.haut.gewichte > 1e-6).sum(axis=1)
        self.assertLessEqual(int(belegt.max()), 4)

    def test_die_vier_summieren_sich_auf_eins(self):
        index, gewicht = self.haut.fuer_punkte(len(self.haut.gewichte))
        self.assertEqual(index.shape, (len(self.haut.gewichte), 4))
        summe = gewicht.sum(axis=1)
        self.assertTrue(np.allclose(summe, 1.0, atol=1e-5))

    def test_ohne_zuordnung_kein_fremdes_netz(self):
        u"""Sonst laegen 6.890 Gewichte der Reihe nach auf 23.752 Punkten."""
        with self.assertRaises(ValueError):
            self.haut.fuer_punkte(23752)

    def test_zuordnung_muss_zum_netz_passen(self):
        with self.assertRaises(ValueError):
            self.haut.fuer_punkte(100, np.zeros(50, dtype=np.int64))

    def test_uebertragene_gewichte_haben_die_laenge_des_netzes(self):
        zuordnung = np.arange(100) % len(self.haut.gewichte)
        index, gewicht = self.haut.fuer_punkte(100, zuordnung)
        self.assertEqual(index.shape, (100, 4))
        self.assertTrue(np.allclose(gewicht.sum(axis=1), 1.0, atol=1e-5))

    def test_die_knochennamen_sind_die_des_skeletts(self):
        u"""Der Browser loest sie auf — ein fremder Name bindet gar nicht."""
        from SMPL.haut import Smplhaut
        self.assertEqual(Smplhaut.knochennamen(), list(Smplskelett.NAMEN))


class MhhautTest(unittest.TestCase):

    databases = []

    @classmethod
    def setUpClass(cls):
        from MakeHuman.haut import Mhhaut
        from MakeHuman.basisnetz import Mhbasisnetz
        if not Mhhaut.vorhanden() or not Mhbasisnetz.vorhanden():
            raise unittest.SkipTest('MakeHuman-Upstream fehlt')
        cls.Mhhaut = Mhhaut

    def test_die_spalten_sind_alle_knochen_des_rigs(self):
        u"""Nicht nur die 139 mit Gewichten.

        Sonst fehlte ausgerechnet `root` die Spalte, an die ein Punkt ohne
        jedes Gewicht gehaengt wird — er landete auf `breast.L`.
        """
        from MakeHuman.skelett import Mhskelett
        namen = self.Mhhaut.knochennamen()
        self.assertEqual(set(namen), set(Mhskelett.rig()['bones']))
        self.assertIn('root', namen)

    def test_jeder_punkt_traegt_gewicht_eins(self):
        from MakeHuman.koerpernetz import Mhkoerpernetz
        netz = Mhkoerpernetz(('koerper',), False).bauen()
        haut = netz['haut']
        self.assertEqual(len(haut['index']), len(netz['punkte']))
        self.assertTrue(np.allclose(haut['gewicht'].sum(axis=1), 1.0,
                                    atol=1e-5))

    def test_die_glaettung_zieht_die_gewichte_mit(self):
        u"""Catmull-Clark aendert Punktzahl UND Reihenfolge.

        Ohne dieselbe Matrix wie fuer die Punkte zeigt jedes Gewicht auf
        einen anderen Punkt — die Figur bewegt sich, nur verkehrt.
        """
        from MakeHuman.koerpernetz import Mhkoerpernetz
        netz = Mhkoerpernetz(('koerper',), True).bauen()
        self.assertEqual(len(netz['haut']['index']), len(netz['punkte']))
        self.assertGreater(len(netz['punkte']), 13380)

    def test_die_loeschmaske_zieht_die_gewichte_mit(self):
        u"""Nach dem Verdichten muss dieselbe Auswahl auf den Gewichten liegen."""
        from MakeHuman.garderobe import Mhgarderobe
        from MakeHuman.koerpernetz import Mhkoerpernetz
        stuecke = [s['id'] for s in Mhgarderobe.liste()]
        if not stuecke:
            raise unittest.SkipTest('keine MakeHuman-Garderobe')
        netz = Mhkoerpernetz(('koerper',), False, (stuecke[0],)).bauen()
        self.assertEqual(len(netz['haut']['index']), len(netz['punkte']))
