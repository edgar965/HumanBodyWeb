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

SEIT DEM 09.09.2026 GILT DASSELBE FÜR ZWEI WEITERE PAKETE
=========================================================
Die Schwelle liegt bei 1 Sekunde je Modul (Edgar: „alles was mehr als 1 s
dauert soll in die Longrunner hinein"). `core/tests/automated` (31,8 s in
6 Fällen) und `core/tests/performance` (26,5 s in 2) ließen sich nicht
verschieben — ihre Klassen kommen aus djangoBase. Sie benutzen denselben
Wächter mit ihrer eigenen Marke, und die Verwechslungsgefahr ist echt:
Wäre die Marke überall „longrunner", liefe `manage.py test
core.tests.automated` ins Leere und meldete grün.
"""
import os
import unittest
from unittest import mock

from core.tests.longrunner import MARKE, SCHALTER, angefordert
from core.tests.nurgemeint import Nurgemeint


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


class WeitereWaechter(unittest.TestCase):
    u"""`automated` und `performance` — je eigene Marke, gleicher Mechanismus."""

    databases = []

    #: Paket -> Marke. Absichtlich hier ausgeschrieben: Nimmt ein Paket die
    #: falsche Marke, laeuft es nie und alles bleibt grün.
    PAKETE = {'automated': 'core/tests/automated',
              'performance': 'core/tests/performance'}

    def _waechter(self, marke):
        ordner = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                              marke)
        return Nurgemeint(marke, ordner)

    def test_jedes_paket_laeuft_bei_seinem_eigenen_ziel(self):
        for marke, ziel in self.PAKETE.items():
            waechter = self._waechter(marke)
            self.assertTrue(waechter.angefordert(
                ['manage.py', 'test', ziel.replace('/', '.')], {}), marke)

    def test_keines_laeuft_beim_sammellauf(self):
        for marke in self.PAKETE:
            self.assertFalse(self._waechter(marke).angefordert(
                ['manage.py', 'test'], {}), marke)

    def test_keines_haengt_an_der_marke_des_anderen(self):
        u"""`longrunner` im Aufruf darf `automated` NICHT mitziehen.

        Sonst waere die Trennung nur scheinbar: Wer die Longrunner faehrt,
        zahlte weiter die 58 s der beiden djangoBase-Pakete.
        """
        for marke in self.PAKETE:
            self.assertFalse(self._waechter(marke).angefordert(
                ['manage.py', 'test', 'core.tests.longrunner'], {}), marke)

    def test_der_gemeinsame_schalter_zieht_alle(self):
        u"""Ein naechtlicher Lauf soll wirklich alles fahren."""
        for marke in self.PAKETE:
            self.assertTrue(self._waechter(marke).angefordert(
                ['manage.py', 'test'], {Nurgemeint.SCHALTER: '1'}), marke)

    def test_die_pakete_fuehren_ihren_waechter_wirklich(self):
        u"""Der Test prueft sonst nur seine eigene Kopie der Entscheidung."""
        from core.tests import automated, performance
        for paket, marke in ((automated, 'automated'),
                             (performance, 'performance')):
            self.assertTrue(hasattr(paket, 'load_tests'), marke)
            self.assertEqual(paket.WAECHTER.marke, marke)

    def test_jedes_paket_findet_seine_module(self):
        u"""Ein leeres `module()` machte die Meldung zur Falschauskunft."""
        for marke in self.PAKETE:
            self.assertTrue(self._waechter(marke).module(), marke)


class DiscoveryMitPaketnamen(unittest.TestCase):
    u"""Der Waechter muss die Module IM Paket laden, nicht als Skript.

    DER BEFUND (09.09.2026): `loader.discover(ordner)` ohne
    `top_level_dir` nimmt den Startordner als oberste Ebene. `test_mhpfade`
    kam damit als Top-Level-Modul an, und sein

        from ..unit._humanbodypfad import Humanbodypfad

    brach mit „attempted relative import with no known parent package" ab.
    Betroffen waren zehn Module — zwei davon lagen seit dem 08.09.2026 im
    longrunner-Paket und waren die ganze Zeit unlaufbar. Gesehen hat es
    niemand, weil das Paket im Sammellauf stumm ist.

    Der Test laedt NUR (keine Ausfuehrung) und nimmt das Modul, an dem es
    aufgefallen ist.
    """

    databases = []

    def _laden(self, muster):
        from core.tests.longrunner import WAECHTER
        lader = unittest.TestLoader()
        with mock.patch.dict(os.environ, {Nurgemeint.SCHALTER: '1'}):
            suite = WAECHTER.sammeln(lader, muster)
        return lader, list(suite)

    def test_ein_modul_mit_import_ueber_die_paketgrenze_laedt(self):
        lader, gefunden = self._laden('test_mhpfade.py')
        self.assertEqual(lader.errors, [],
                         u'Der Loader konnte das Modul nicht importieren.')
        namen = str(gefunden)
        self.assertNotIn('_FailedTest', namen)
        self.assertIn('test_mhpfade', namen,
                      u'Das Muster hat gar nichts getroffen — dann prueft '
                      u'dieser Fall nichts.')

    def test_ohne_anforderung_kommt_nichts(self):
        u"""Die Gegenprobe zum Fall darueber: derselbe Aufruf, kein Schalter."""
        from core.tests.longrunner import WAECHTER
        with mock.patch.dict(os.environ, {Nurgemeint.SCHALTER: ''}),                 mock.patch('sys.argv', ['manage.py', 'test']):
            suite = WAECHTER.sammeln(unittest.TestLoader(), 'test_mhpfade.py')
        self.assertEqual(list(suite), [])
