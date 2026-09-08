# -*- coding: utf-8 -*-
u"""Wann laufen die LongRunner — und wann nicht?

WARUM DAS EINEN TEST BRAUCHT (Edgar, 08.09.2026: „alle tests die länger
als 5 s brauchen kriegen die Kategorie LongRunner und werden nicht jedes
Mal ausgeführt bei einer automatischen Suite")
=====================================================================
Die Entscheidung liegt in `core/tests/longrunner/__init__.py` und wirkt
über das `load_tests`-Protokoll. Sie ist damit die einzige Stelle im
Projekt, die Tests VERSCHWINDEN lässt — und genau so etwas gehört
geprüft. Kippt sie in die eine Richtung, laufen elf langsame Module
wieder bei jedem Sammellauf; kippt sie in die andere, laufen sie NIE
mehr, und niemand merkt es, weil alles grün bleibt.

Dieser Test liegt bewusst NICHT im longrunner-Paket: Dort würde er sich
selbst überspringen.
"""
import unittest

from core.tests.longrunner import MARKE, SCHALTER, angefordert


class Auswahl(unittest.TestCase):

    databases = []

    def test_ausdruecklich_genannt_laeuft(self):
        self.assertTrue(angefordert(
            ['manage.py', 'test', 'core.tests.longrunner'], {}))

    def test_teilweise_genannt_laeuft_auch(self):
        u"""Ein einzelnes Modul daraus ist auch eine Anforderung."""
        self.assertTrue(angefordert(
            ['manage.py', 'test',
             'core.tests.longrunner.test_umafigur.Figurbau'], {}))

    def test_sammellauf_ohne_ziel_laeuft_nicht(self):
        u"""Der Fall, um den es geht: `manage.py test` ohne Ziel.

        Genau so ruft djangoBases Reiter „Alles" — mit LEERER Zielliste
        (`testkategorien.sammel(python, 'alles', …, [])`).
        """
        self.assertFalse(angefordert(['manage.py', 'test'], {}))

    def test_andere_ziele_laufen_nicht_mit(self):
        self.assertFalse(angefordert(
            ['manage.py', 'test', 'core.tests.unit', 'core.tests.component'],
            {}))

    def test_der_schalter_zieht(self):
        for wert in ('1', 'true', 'ja'):
            self.assertTrue(angefordert(['manage.py', 'test'],
                                        {SCHALTER: wert}), wert)

    def test_ein_leerer_schalter_zieht_nicht(self):
        for wert in ('', '0', 'nein'):
            self.assertFalse(angefordert(['manage.py', 'test'],
                                         {SCHALTER: wert}), repr(wert))

    def test_das_eigene_programm_zaehlt_nicht(self):
        u"""`argv[0]` ist der Programmpfad.

        Läge das Projekt in einem Ordner mit „longrunner" im Namen, wäre
        sonst jeder Lauf ein ausdrücklicher — die Umstellung hätte nichts
        gebracht, und die Ursache wäre nirgends zu sehen.
        """
        self.assertFalse(angefordert(
            ['/pfad/mit/longrunner/manage.py', 'test'], {}))

    def test_die_marke_ist_der_paketname(self):
        self.assertIn(MARKE, 'core.tests.longrunner')
