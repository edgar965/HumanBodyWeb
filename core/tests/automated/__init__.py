# -*- coding: utf-8 -*-
u"""Grundabsicherung — laeuft nur, wenn sie ausdruecklich gemeint ist.

GEMESSEN (09.09.2026): 31,8 s in SECHS Faellen, der laengste Posten des
ganzen Sammellaufs. `test_keine_seite_wirft_5xx` allein braucht 29,9 s —
es ruft jede Seite des Projekts auf.

Edgar, 09.09.2026: „alles was mehr als 1 s dauert soll in die Longrunner
hinein, das dauert mir alles zu lange". Verschieben laesst sich das Paket
nicht: Die Testklassen kommen aus `djangobase.grundtests` (geteiltes Paket,
sechs Projekte), und ohne dieses Paket zeigte der Reiter
„Grundabsicherung" in Hilfe -> Tests 0 Faelle. Deshalb derselbe Waechter
wie beim longrunner-Paket — Begruendung dort und in `nurgemeint.py`.

Gefahren wird es weiter uber seinen eigenen Eintrag:

    manage.py test core.tests.automated        oder  LONGRUNNER=1
"""
import os

from ..nurgemeint import Nurgemeint

WAECHTER = Nurgemeint('automated', os.path.dirname(__file__), dauer='32 s')


def load_tests(loader, standard_tests, pattern):
    return WAECHTER.sammeln(loader, pattern)
