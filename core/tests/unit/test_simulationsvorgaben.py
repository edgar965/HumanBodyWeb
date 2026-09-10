# -*- coding: utf-8 -*-
u"""Unsere eigenen Simulationsvorgaben gegen GarmentCodes.

Der Kollisionsabstand steht an DREI Stellen: als Wert in
`Simulationsvorgaben`, als Reglervorgabe in `Simulationsfelder` und
— nur als Zahl im Hinweis — in der Beschriftung. Laufen die ersten beiden
auseinander, zeigt der Regler etwas anderes an, als gebaut wird.
"""

from django.test import TestCase

from GarmentCode.drapierung import Drapierung
from GarmentCode.simulationsfelder import Simulationsfelder
from GarmentCode.simulationsvorgaben import Simulationsvorgaben


class DerReglerZeigtWasWirklichGilt(TestCase):
    u"""Vorgabeklasse und Feldkatalog nennen dieselbe Zahl."""

    def test_jede_eigene_vorgabe_steht_auch_im_feldkatalog(self):
        for schluessel, wert in Simulationsvorgaben.OPTIONEN.items():
            self.assertEqual(
                Simulationsfelder.vorgabe(schluessel), wert,
                u'%s: Feldkatalog und Simulationsvorgaben sind ungleich — '
                u'der Regler zeigt dann eine Zahl, die nie gebaut wird'
                % schluessel)

    def test_der_kollisionsabstand_ist_kleiner_als_bei_garmentcode(self):
        u"""Das ist der ganze Zweck der Klasse.

        GarmentCode gibt 0,25 cm vor — gemessen der groesste Einzelposten
        des Hautabstands auf unserem Netz (Brust 4,6 mm gegen 2,8 mm bei
        0,05).
        """
        self.assertLess(
            Simulationsvorgaben.OPTIONEN['body_collision_thickness'], 0.25)


class DerReglerGewinntGegenDieVorgabe(TestCase):
    u"""Wer von Hand stellt, bekommt seinen Wert — sonst waere es ein
    Regler, der nicht tut, was er anzeigt."""

    def test_eingestellter_wert_schlaegt_die_vorgabe(self):
        werte = Simulationsvorgaben.optionen_mit(
            {'body_collision_thickness': 0.25})
        self.assertEqual(werte['body_collision_thickness'], 0.25)

    def test_ohne_eingabe_gilt_die_vorgabe(self):
        werte = Simulationsvorgaben.optionen_mit(None)
        self.assertEqual(werte['body_collision_thickness'],
                         Simulationsvorgaben.OPTIONEN[
                             'body_collision_thickness'])

    def test_fremde_werte_bleiben_erhalten(self):
        werte = Simulationsvorgaben.optionen_mit({'body_friction': 0.8})
        self.assertEqual(werte['body_friction'], 0.8)
        self.assertIn('body_collision_thickness', werte)


class AufDemReferenzkoerperGiltGarmentCode(TestCase):
    u"""Der SMPL-Weg soll dem Online-Tool gleichen — das ist seine einzige
    Aufgabe. Eigene Vorgaben machten daraus einen Vergleich zweier
    verschiedener Programme."""

    SPEZ = 'egal_specification.json'

    def test_smpl_bekommt_die_eigenen_vorgaben_nicht(self):
        lauf = Drapierung(self.SPEZ, koerper='mean_all', smpl_body=True)
        self.assertNotIn('body_collision_thickness', lauf.optionen)

    def test_auf_der_figur_gelten_sie(self):
        lauf = Drapierung(self.SPEZ, koerper='figur_abc')
        self.assertEqual(lauf.optionen['body_collision_thickness'],
                         Simulationsvorgaben.OPTIONEN[
                             'body_collision_thickness'])

    def test_smpl_behaelt_trotzdem_was_der_nutzer_stellte(self):
        u"""Ausgenommen sind die VORGABEN, nicht die Regler."""
        lauf = Drapierung(self.SPEZ, koerper='mean_all', smpl_body=True,
                          optionen={'body_friction': 0.9})
        self.assertEqual(lauf.optionen, {'body_friction': 0.9})
