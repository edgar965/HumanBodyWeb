# -*- coding: utf-8 -*-
"""Die Hauteinigung von `Meshfigurhautmodell._einig` (13.10.2026): neutral ist nie Haut, zwei Stufen (eng nach (a*, b*), weit nach Farbton und Buntheit), Sapiens-Gruppen mit niedrigerer Untergrenze.

Anlass (Edgar, Spiralballerina und Polstertänzer: „Textur der Haut falsch (ist weiß)“): die neutralen Gruppen (Ärmel, Strumpfhose, weißer Anzug) stellten die Mehrheit und überstimmten die einzige Haut.
Eine zweite Frage danach: ob die Einigung echte Haut aussortiert (Polstertänzer: die rötere rechte Hand 26,9/18,9 gegen 18,2/15,5 und 17,9/19,3). Alle Werte stammen aus `stand.json`
(`figur.kleidung.hautmodell.gruppen`), die Gegenprobe über ALLE 17 gespeicherten Fälle steht in `ProjektTemp/_wegwerf/mesh3d/haut_einigung_vergleich.py` (v1 = neu an allen 17).

Kunstdaten, ohne Datenbank und GPU. Sabotagen, die diese Fälle rot machen müssen: in `_einig` die Farbton-Bedingung der Kandidaten streichen (Fall 4), `BUNT_MIN` auf 0 setzen (Fälle 1, 2),
die Stufe 2 entfernen (Fall 5), `BUNT_MIN_SAPIENS` auf `BUNT_MIN` setzen (Fall 6). NICHT gelaufen, bis Edgar Tests ansagt.
"""

import unittest

import numpy as np

from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

from meshfigur_hautmodell import Meshfigurhautmodell as M  # noqa: E402


def einig(gruppen, bunt_min=None):
    mediane = {n: np.array(v[:2], dtype=float) for n, v in gruppen.items()}
    proben = {n: (v[2] if len(v) > 2 else 300) for n, v in gruppen.items()}
    return sorted(M._einig(mediane, proben, bunt_min))


class NeutralIstNieHautTest(unittest.TestCase):
    def test_1_spiralballerina_aermel_und_strumpfhose_stellen_nicht_die_mehrheit(self):
        gruppen = {'unterarm_r': (17.6, 19.0, 242), 'unterarm_l': (3.2, 2.2, 143), 'unterschenkel_r': (2.6, -1.5, 247), 'unterschenkel_l': (2.6, -1.5, 299), 'gesicht': (6.4, 7.1, 45)}
        gewaehlt = einig(gruppen)
        self.assertLess(len(gewaehlt), 2)          # eine Haut-Gruppe allein ergibt kein Modell
        self.assertFalse({'unterarm_l', 'unterschenkel_r', 'unterschenkel_l'} & set(gewaehlt))

    def test_2_polstertaenzer_weisser_anzug_ist_keine_haut(self):
        gruppen = {'unterarm_r': (0.0, 1.0, 382), 'unterarm_l': (1.2, 3.8, 239), 'unterschenkel_l': (0.0, 0.0, 99), 'gesicht': (11.2, 6.9, 127)}
        self.assertEqual(einig(gruppen), [])

    def test_3_graue_gruppen_bleiben_auch_mit_der_sapiens_grenze_grau(self):
        gruppen = {'arm_l': (0.5, 1.0), 'arm_r': (0.0, 0.2), 'bein_l': (1.0, 1.5)}
        self.assertEqual(einig(gruppen, M.BUNT_MIN_SAPIENS), [])


class FarbtonTest(unittest.TestCase):
    def test_4_ein_blaues_oder_gruenes_tuch_ist_keine_haut_auch_wenn_es_bunt_ist(self):
        # Drei blaue Gruppen (Jeans, Jacke) stellen die Mehrheit: ohne Farbton-Bedingung läge die Mitte im Blau und die Haut fiele heraus.
        gruppen = {'arm_l': (17.9, 19.3), 'arm_r': (18.1, 20.3), 'bein_l': (-5.0, -20.0), 'bein_r': (-5.5, -19.0), 'torso': (-4.5, -21.0)}
        self.assertEqual(einig(gruppen), ['arm_l', 'arm_r'])

    def test_5_die_weite_stufe_rettet_zwei_hautgruppen_wo_der_abstand_fuenf_keine_findet(self):
        # Hand und Arm derselben Person, die Hand deutlich roter: Abstand ≈ 13,9 (Stufe 1 findet nichts), Farbton 33,7° und 41,4°, Buntheit 36 gegen 22,7.
        gruppen = {'hand_r': (30.0, 20.0), 'arm_l': (17.0, 15.0)}
        self.assertEqual(einig(gruppen), ['arm_l', 'hand_r'])

    def test_5b_die_weite_stufe_nimmt_weder_grauen_bart_noch_geschminktes_gesicht(self):
        # Bart: Farbton 70,7° (außerhalb 20° von der Mitte) und 0,37-fache Buntheit — zusammen mit nur EINER Haut-Gruppe bleibt es bei weniger als zwei.
        gruppen = {'arm_l': (17.9, 19.3), 'bart': (2.7, 7.7)}
        self.assertLess(len(einig(gruppen)), 2)

    def test_5c_die_enge_stufe_bleibt_unveraendert_wenn_sie_zwei_findet(self):
        # Polstertänzer neu (Sapiens): die rötere Hand rechts (26,9/18,9) bleibt draußen, solange Hand links und Arm (Abstand ≤ 5 von der Mitte) das Modell tragen — kein vorhandenes Ergebnis ändert sich.
        gruppen = {'gesicht': (11.7, 9.3, 193), 'hand_l': (18.2, 15.5, 213), 'hand_r': (26.9, 18.9, 343), 'arm_l': (17.9, 19.3, 51)}
        self.assertEqual(einig(gruppen, M.BUNT_MIN_SAPIENS), ['arm_l', 'hand_l'])


class SapiensGrenzeTest(unittest.TestCase):
    def test_6_blasse_haut_zaehlt_mit_der_sapiens_grenze_aber_nicht_an_den_landmarken(self):
        gruppen = {'gesicht': (2.5, 3.5), 'hand_l': (3.0, 3.8), 'arm_l': (2.8, 3.6)}   # Buntheit 4,3 … 4,8, Farbton 52–54°
        self.assertEqual(einig(gruppen), [])                                           # Landmarken: BUNT_MIN 6
        self.assertEqual(einig(gruppen, M.BUNT_MIN_SAPIENS), ['arm_l', 'gesicht', 'hand_l'])


class GemesseneFaelleTest(unittest.TestCase):
    """Die Auswahl der gespeicherten Läufe ändert sich nicht (Gegenprobe über 17 Fälle: `haut_einigung_vergleich.py`)."""

    def test_7_edgar_29_09_alle_sieben_gruppen(self):
        gruppen = {'gesicht': (8.4, 4.7), 'unterarm_r': (8.8, 8.7), 'unterarm_l': (11.6, 11.5), 'unterschenkel_r': (8.9, 8.8), 'unterschenkel_l': (9.8, 9.7), 'hand_r': (10.5, 8.2), 'hand_l': (12.5, 10.7)}
        self.assertEqual(einig(gruppen), sorted(gruppen))

    def test_8_edgar_04_10_hand_und_unterarm_nicht_die_grauen_beine(self):
        gruppen = {'gesicht': (17.8, 24.2, 300), 'hand': (22.2, 27.3, 592), 'unterarm': (23.5, 27.4, 2052), 'ub_l': (1.1, 2.1, 1276), 'ub_r': (1.3, 2.2, 1116)}
        self.assertEqual(einig(gruppen), ['hand', 'unterarm'])

    def test_9_zauberer_die_haende_nicht_der_graue_bart(self):
        gruppen = {'gesicht': (2.7, 7.7, 41288), 'hand_l': (14.4, 16.5, 12500), 'hand_r': (14.4, 16.5, 12500)}
        self.assertEqual(einig(gruppen), ['hand_l', 'hand_r'])
