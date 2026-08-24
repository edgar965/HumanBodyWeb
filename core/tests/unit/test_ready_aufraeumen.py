# -*- coding: utf-8 -*-
"""`CoreConfig.ready()` — aufraeumen nur beim echten Server.

Eigene Datei, weil hier NICHT `Startaufraeumen` geprueft wird, sondern die
eine Bedingung darum: Laeuft ein `manage.py migrate`, darf nichts angefasst
werden. Die Gegenprobe (Bedingung entfernt) war zunaechst gruen, weil kein
Test `ready()` gerufen hat — deshalb steht sie hier fuer sich.
"""

import sys

from django.test import TestCase


class ReadyTest(TestCase):
    """`CoreConfig.ready()` darf NUR beim echten Server aufräumen.

    Ohne die `runserver`-Prüfung würde jedes `manage.py`-Kommando laufende
    Aufträge als gescheitert vermerken — auch ein `migrate` mitten in einem Lauf,
    und der Testlauf selbst. Die Gegenprobe (Prüfung entfernt) war zunächst
    grün, weil kein Test `ready()` gerufen hat; deshalb dieser hier.
    """

    def laufen(self, argv):
        from core.apps import CoreConfig
        from core.dienste import startaufraeumen as modul
        gerufen = []

        class Attrappe:
            def zwischendateien(self):
                gerufen.append('zwischendateien')

            def durchgehen(self):
                gerufen.append('durchgehen')
                return {}

        echt, altes_argv = modul.Startaufraeumen, sys.argv
        modul.Startaufraeumen = Attrappe
        sys.argv = argv
        try:
            CoreConfig.ready(CoreConfig.__new__(CoreConfig))
        finally:
            modul.Startaufraeumen = echt
            sys.argv = altes_argv
        return gerufen

    def test_mit_runserver_wird_aufgeraeumt(self):
        self.assertEqual(self.laufen(['manage.py', 'runserver', '8081']),
                         ['zwischendateien', 'durchgehen'])

    def test_bei_migrate_passiert_nichts(self):
        self.assertEqual(self.laufen(['manage.py', 'migrate']), [])

    def test_beim_testlauf_passiert_nichts(self):
        self.assertEqual(self.laufen(['manage.py', 'test', 'core.tests']), [])
