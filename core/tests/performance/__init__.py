# -*- coding: utf-8 -*-
u"""Ladezeiten — laufen nur, wenn sie ausdruecklich gemeint sind.

GEMESSEN (09.09.2026): 26,5 s in ZWEI Faellen —
`test_ladezeiten_messen_und_protokollieren` 16,1 s und
`test_keine_seite_stellt_uebermaessig_viele_abfragen` 10,4 s. Beide rufen
reihum alle Seiten auf; das IST ihre Aufgabe, und deshalb sind sie im
Sammellauf am falschen Platz.

Begruendung und Waechter: `core/tests/nurgemeint.py` (Edgar, 09.09.2026:
„alles was mehr als 1 s dauert soll in die Longrunner hinein").

    manage.py test core.tests.performance      oder  LONGRUNNER=1
"""
import os

from ..nurgemeint import Nurgemeint

WAECHTER = Nurgemeint('performance', os.path.dirname(__file__), dauer='27 s')


def load_tests(loader, standard_tests, pattern):
    return WAECHTER.sammeln(loader, pattern)
