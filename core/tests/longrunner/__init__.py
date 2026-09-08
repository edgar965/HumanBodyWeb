# -*- coding: utf-8 -*-
u"""LongRunner — Tests über 5 Sekunden je Modul.

WARUM SIE HIER LIEGEN (Edgar, 08.09.2026: „strukturiere die testsuite um -
alles was länger dauert, weg in die Kategorie LongRunner", und genauer:
„alle tests die länger als 5 s brauchen kriegen die Kategorie LongRunner
und werden nicht jedes Mal ausgeführt bei einer automatischen Suite")
=====================================================================
Je Modul einzeln gestoppt (`ProjektTemp/testzeiten.txt`, 175 Module).
Elf lagen über 5 Sekunden und stehen jetzt hier:

    test_kleiderrigging   66,7 s     test_umafigur          10,9 s
    test_umabauer         39,5 s     test_uma_gegenprobe    10,7 s
    test_mhpfade          21,1 s     test_hilfe_kleidung     8,8 s
    test_charakterkanal   19,7 s     test_pipeline_process   8,6 s
    test_netzkette        (Bestand)  test_umatexturen        7,8 s
                                     test_endpunkte          7,4 s
                                     test_uma_gegenprobe_lauf 5,7 s

Gemessen vorher und nachher: „Unit" und „Component" liefen zusammen
**266 s**, jetzt **98 s** — bei 1.505 statt 1.534 Fällen. Die elf Module
sind 2 % der Dateien und waren zwei Drittel der Wartezeit.

SIE LAUFEN NUR, WENN SIE GEMEINT SIND
=====================================
`manage.py test` ohne Ziel entdeckt sonst auch dieses Paket — und der
Sammellauf „Alles" in Hilfe → Tests ruft genau das (`djangobase/
testkategorien.py`: `sammel(python, "alles", …, [])` mit leerer
Zielliste). Deshalb entscheidet dieses Paket selbst, ob seine Tests
eingesammelt werden: über das `load_tests`-Protokoll, das unittest bei
einem Paket mit dieser Funktion aufruft, statt selbst zu suchen.

Angefordert ist es, wenn `longrunner` in der Befehlszeile steht oder
`LONGRUNNER=1` gesetzt ist. Sonst kommt eine LEERE Suite zurück — und
das wird gemeldet, nicht verschwiegen: Ein Paket, das still nichts
liefert, sieht aus wie ein Paket ohne Tests
(`~/.claude/rules/analysewerkzeuge.md`: ein Prüfer, der nichts findet
und Entwarnung meldet, ist der teuerste).

DJANGOBASE BLEIBT UNBERUEHRT. Es ist in sechs Projekten als editable
Install eingebunden; eine Ausnahme für dieses Projekt dort einzubauen
wirkte sofort in allen (`A:/shared/djangoBase/CLAUDE.md`).
"""
import logging
import os
import sys
import unittest

logger = logging.getLogger('core')

#: Das Wort, an dem ein ausdrücklicher Aufruf zu erkennen ist.
MARKE = 'longrunner'

#: Damit lässt sich das Paket auch ohne Ziel im Aufruf einschalten —
#: etwa in einem nächtlichen Lauf, der wirklich alles fahren soll.
SCHALTER = 'LONGRUNNER'


def angefordert(argumente=None, umgebung=None):
    u"""Sind die LongRunner ausdrücklich gemeint?

    Als Funktion mit Parametern, damit ein Test sie ohne echtes `sys.argv`
    prüfen kann — sonst wäre gerade diese Entscheidung die einzige im
    Paket, die niemand nachrechnet.
    """
    argumente = sys.argv if argumente is None else argumente
    umgebung = os.environ if umgebung is None else umgebung
    if str(umgebung.get(SCHALTER, '')).strip() in ('1', 'true', 'ja'):
        return True
    return any(MARKE in str(a) for a in argumente[1:])


def load_tests(loader, standard_tests, pattern):
    u"""Das `load_tests`-Protokoll: Wir sammeln selbst — oder eben nicht."""
    if not angefordert():
        logger.info(
            'LongRunner uebersprungen (%d Module, rund 190 s). Zum Fahren: '
            'manage.py test core.tests.longrunner  oder  %s=1',
            len([n for n in os.listdir(os.path.dirname(__file__))
                 if n.startswith('test_')]), SCHALTER)
        return unittest.TestSuite()
    return loader.discover(os.path.dirname(__file__),
                           pattern=pattern or 'test*.py')
